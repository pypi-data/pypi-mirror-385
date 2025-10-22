import collections.abc
import json
import os
import sys
from typing import Dict, List
from unittest import TestCase

import pytest
from hydra.errors import InstantiationException
from omegaconf import OmegaConf
from omegaconf.errors import InterpolationKeyError
from pydantic import ConfigDict

from ccflow import BaseModel, ModelRegistry, RegistryLookupContext, RootModelRegistry, model_alias
from ccflow.base import RegistryKeyError, resolve_str


class MyTestModel(BaseModel):
    a: str
    b: float
    c: List[str] = []
    d: Dict[str, float] = {}


class MyTestModel2(BaseModel):
    v: int


class MyTestModelSubclass(MyTestModel):
    pass


class MyClass:
    def __init__(self, p="p", q=10.0):
        self.p = p
        self.q = q


class MyNestedModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)  # To allow z = MyClass, even though there is no validator

    x: MyTestModel
    y: MyTestModel
    z: MyClass = MyClass()


class DoubleNestedModel(BaseModel):
    a: Dict[str, MyNestedModel] = {}
    b: List[MyTestModel] = []


class TestRegistry(TestCase):
    def setUp(self) -> None:
        ModelRegistry.root().clear()

    def tearDown(self) -> None:
        ModelRegistry.root().clear()

    def test_root(self):
        self.assertIsInstance(ModelRegistry.root(), RootModelRegistry)
        self.assertIs(ModelRegistry.root(), ModelRegistry.root())
        self.assertIs(ModelRegistry.root(), RootModelRegistry.root())

        r = ModelRegistry.root()
        self.assertListEqual(r.get_registrations(), [])
        self.assertListEqual(r.get_registered_names(), [""])
        self.assertListEqual(r.get_registry_dependencies(), [])

        # Test that you can't construct your own
        self.assertRaises(ValueError, RootModelRegistry)

    def test_add_root(self):
        m = MyTestModel(a="test", b=0.0)
        r = ModelRegistry.root()
        r.add("foo", m)
        self.assertEqual(r.models, {"foo": m})
        self.assertRaises(ValueError, r.add, "foo", None)
        self.assertRaises(TypeError, r.add, "bar", None)
        self.assertListEqual(m.get_registrations(), [(r, "foo")])
        self.assertListEqual(m.get_registered_names(), ["/foo"])

        m2 = MyTestModel(a="test2", b=0.0)
        r.add("foo", m2, overwrite=True)
        self.assertEqual(r.models, {"foo": m2})
        self.assertListEqual(m.get_registrations(), [])
        self.assertListEqual(m.get_registered_names(), [])
        self.assertListEqual(m2.get_registrations(), [(r, "foo")])
        self.assertListEqual(m2.get_registered_names(), ["/foo"])

        r.remove("foo")
        self.assertListEqual(m2.get_registrations(), [])
        self.assertListEqual(m2.get_registered_names(), [])
        self.assertRaises(ValueError, r.remove, "foo")

    def test_init(self):
        m = MyTestModel(a="test", b=0.0)
        r = ModelRegistry(name="test", models={"foo": m})
        self.assertEqual(r.models, {"foo": m})
        self.assertListEqual(m.get_registrations(), [(r, "foo")])

    def test_dict(self):
        m = MyTestModel(a="test", b=0.0)
        r = ModelRegistry(name="test", models={"foo": m})
        target = {
            "_target_": "ccflow.base.ModelRegistry",
            "name": "test",
            "models": {
                "foo": {
                    "_target_": "ccflow.tests.test_base_registry.MyTestModel",
                    "a": "test",
                    "b": 0.0,
                    "c": [],
                    "d": {},
                }
            },
        }
        self.assertDictEqual(r.model_dump(by_alias=True), target)

        # Test round-trip
        r2 = ModelRegistry(name="test")
        r2.load_config(target["models"])
        self.assertEqual(r.models, r2.models)

    def test_json(self):
        m = MyTestModel(a="test", b=0.0)
        r = ModelRegistry(name="test", models={"foo": m})
        target = (
            '{"_target_": "ccflow.base.ModelRegistry", "name": "test", '
            '"models": {"foo": {"_target_": "ccflow.tests.test_base_registry.MyTestModel", '
            '"a": "test", "b": 0.0, "c": [], "d": {}}}}'
        )
        self.assertEqual(json.loads(r.model_dump_json(by_alias=True)), json.loads(target))

    def test_equality(self):
        # Make sure equality doesn't pass just because two registries have the same name
        # i.e. there is a risk of this because "models" isn't a pydantic field on the ModelRegistry object.
        m = MyTestModel(a="test", b=0.0)
        r = ModelRegistry(name="test")
        r.add("foo", m)
        r2 = ModelRegistry(name="test")
        self.assertNotEqual(r, r2)

    def test_get(self):
        m = MyTestModel(a="test", b=0.0)
        r = ModelRegistry(name="test")
        r.add("foo", m)
        self.assertIs(r["foo"], m)
        self.assertIs(r.get("foo"), m)
        self.assertIsNone(r.get("bar"))
        self.assertRaises(KeyError, lambda: r["bar"])

        self.assertRaisesRegex(
            KeyError,
            "No registered model found by the name 'garbage' in registry 'test'",
            lambda: r["garbage"],
        )

    def test_add_twice(self):
        m = MyTestModel(a="test", b=0.0)
        r = ModelRegistry.root()
        r.add("foo", m)
        r.add("bar", m)
        self.assertEqual(r["foo"], m)
        self.assertEqual(r["foo"], r["bar"])
        self.assertListEqual(m.get_registrations(), [(r, "foo"), (r, "bar")])
        self.assertListEqual(m.get_registered_names(), ["/foo", "/bar"])

        r2 = ModelRegistry(name="test")
        r2.add("foo2", m)
        r2.add("bar2", m)
        self.assertEqual(r2["foo2"], m)
        self.assertEqual(r2["foo2"], r2["bar2"])
        self.assertListEqual(m.get_registrations(), [(r, "foo"), (r, "bar"), (r2, "foo2"), (r2, "bar2")])
        self.assertListEqual(m.get_registered_names(), ["/foo", "/bar"])

    def test_add_two_places(self):
        m = MyTestModel(a="test", b=0.0)
        r1 = ModelRegistry(name="test")
        r2 = ModelRegistry.root()
        r1.add("foo", m)
        r2.add("bar", m)
        self.assertEqual(r1["foo"], m)
        self.assertEqual(r1["foo"], r2["bar"])
        self.assertListEqual(m.get_registrations(), [(r1, "foo"), (r2, "bar")])
        self.assertListEqual(m.get_registered_names(), ["/bar"])

    def test_nested_registry(self):
        m = MyTestModel(a="test", b=0.0)
        r = ModelRegistry.root()
        r2 = ModelRegistry(name="test")
        r2.add("bar", m)
        r.add("foo", r2)
        # Test that r2's name didn't get changed (i.e. to "foo")
        self.assertEqual(r2.name, "test")

        self.assertIs(r["foo/bar"], m)
        self.assertIs(r["/foo/bar"], m)
        self.assertIs(r.get("foo/bar"), m)
        self.assertIs(r.get("/foo/bar"), m)

        self.assertIs(r2["bar"], m)
        self.assertIs(r2["/foo/bar"], m)
        self.assertRaises(KeyError, lambda: r2["foo/bar"])

    def test_str_coercion(self):
        m = MyTestModel(a="test", b=0.0)
        r = ModelRegistry.root()
        r.add("foo", m)
        self.assertEqual(resolve_str("foo"), m)
        self.assertEqual(BaseModel.model_validate("foo"), m)

        m2 = MyNestedModel(x="foo", y=MyTestModel(a="test2", b=1.0))
        self.assertEqual(m2.x, m)

        self.assertEqual(model_alias("foo"), m)
        self.assertEqual(model_alias(model_name="foo"), m)

    def test_str_coercion_error(self):
        msg = ".*Could not resolve model 'foo' in registry 'RootModelRegistry'.*"
        self.assertRaisesRegex(ValueError, msg, BaseModel.model_validate, "foo")
        self.assertRaisesRegex(RegistryKeyError, msg, resolve_str, "foo")

    def test_mapping_interface(self):
        # Test that len and __items__ implemented correctly
        r = ModelRegistry.root()
        self.assertIsInstance(r, collections.abc.Mapping)

        m = MyTestModel(a="test", b=0.0)
        r.add("foo", m)
        r.add("foo2", m)
        r2 = ModelRegistry(name="reg")
        r2.add("bar", MyTestModel(a="test2", b=1.0))
        r.add("subreg", r2)
        self.assertListEqual(list(r), ["foo", "foo2", "subreg", "subreg/bar"])
        self.assertEqual(len(r), 4)

        # Functionality from collections.abc.Mapping
        self.assertIn("subreg/bar", r)
        self.assertEqual(len(r.keys()), 4)
        self.assertEqual(len(r.values()), 4)
        self.assertEqual(len(r.items()), 4)
        self.assertTrue(r != r2)

    def test_get_registry_dependencies(self):
        m = MyTestModel(a="test", b=0.0)
        self.assertListEqual(m.get_registry_dependencies(), [])

        r = ModelRegistry.root()
        r.add("foo", m)
        m3 = MyNestedModel(x="foo", y=MyTestModel(a="test2", b=1.0))

        self.assertListEqual(m3.get_registry_dependencies(), [["/foo"]])
        r.add("foo2", m)
        self.assertListEqual(m3.get_registry_dependencies(), [["/foo", "/foo2"]])

        r2 = ModelRegistry(name="test")
        r2.add("bar", m3.y)
        r.add("subreg", r2)
        self.assertListEqual(m3.get_registry_dependencies(), [["/foo", "/foo2"], ["/subreg/bar"]])

        r.add("foo", MyTestModel(a="test3", b=2.0), overwrite=True)
        self.assertListEqual(m3.get_registry_dependencies(), [["/foo2"], ["/subreg/bar"]])

        m4 = DoubleNestedModel(a={}, b=["/foo"])
        self.assertIs(m4.b[0], r["/foo"])
        self.assertListEqual(m4.get_registry_dependencies(), [["/foo"]])

        # Mutate the dict so as not to trigger copy on validation
        m4.a["nested"] = m3
        self.assertIs(m4.a["nested"], m3)

        # Make sure dependencies are picked up, even though m3 is not registered
        self.assertListEqual(m4.get_registry_dependencies(), [["/foo2"], ["/subreg/bar"], ["/foo"]])
        r.add("nested", m4.a["nested"])
        self.assertListEqual(
            m4.get_registry_dependencies(),
            [["/nested"], ["/foo2"], ["/subreg/bar"], ["/foo"]],
        )
        self.assertListEqual(m4.get_registry_dependencies(types=(MyNestedModel,)), [["/nested"]])

        r3 = ModelRegistry(name="other_registry")
        r3.add("foo2", r["foo2"])
        self.assertListEqual(m3.get_registry_dependencies(), [["/foo2"], ["/subreg/bar"]])


class TestRegistryLoading(TestCase):
    def setUp(self) -> None:
        ModelRegistry.root().clear()

    def tearDown(self) -> None:
        ModelRegistry.root().clear()

    def test_load_config(self):
        cfg = OmegaConf.create(
            {
                "bar": "test",  # i.e. a helper parameter
                "foo": {
                    "_target_": "ccflow.tests.test_base_registry.MyTestModel",
                    "a": "${bar}",
                    "b": 0.0,
                    "c": ["i", "j"],
                    "d": {"k": 2.0},
                },
                "baz": {"qux": "garbage"},  # i.e. a helper dictionary (not a subregistry!)
            }
        )
        r = ModelRegistry(name="test")
        r.load_config(cfg)
        self.assertNotIn("bar", r.models)
        self.assertNotIn("baz", r.models)

        m = MyTestModel(a="test", b=0.0, c=["i", "j"], d={"k": 2.0})
        self.assertEqual(r["foo"], m)

        path = os.path.join(os.path.dirname(__file__), "config", "conf.yaml")
        cfg2 = OmegaConf.load(path)
        r.load_config({"foo2": cfg2.foo})
        self.assertEqual(r["foo2"], m)

        self.assertRaises(ValueError, r.load_config, cfg)
        r.load_config(cfg, overwrite=True)
        self.assertEqual(r["foo"], m)

    def test_config_round_trip(self):
        cfg = {
            "foo": {
                "_target_": "ccflow.tests.test_base_registry.MyTestModel",
                "a": "test",
                "b": 0.0,
                "c": ["i", "j"],
                "d": {"k": 2.0},
            }
        }
        r = ModelRegistry(name="test")
        r.load_config(cfg)
        # Can't do r.dict because of private _models. Need to fix
        cfg2 = {name: model.model_dump(by_alias=True) for name, model in r.models.items()}
        # print(cfg2)
        # return
        r2 = ModelRegistry(name="test")
        r2.load_config(cfg2)
        self.assertEqual(r, r2)

    def test_load_config_from_path(self):
        path = os.path.join(os.path.dirname(__file__), "config", "conf.yaml")
        r = ModelRegistry.root()
        r.load_config_from_path(path)

    def test_load_config_nested(self):
        path = os.path.join(os.path.dirname(__file__), "config", "conf.yaml")
        r = ModelRegistry.root()
        r.load_config_from_path(path, overrides=["foo.a='test_override'"])
        self.assertEqual(list(r.models.keys()), ["foo", "bar", "baz"])
        # Check that the override gets passed through on "foo"
        m = MyTestModel(a="test_override", b=0.0, c=["i", "j"], d={"k": 2.0})
        self.assertEqual(r["foo"], m)
        self.assertIs(r["bar"].x, r["foo"])  # Exactly the same instance
        # "bar" gets auto-converted to parent
        self.assertIsInstance(r["bar"].y, BaseModel)

        # Make sure baz picks up the subclass type (i.e. doesn't coerce to parent type)
        self.assertIsInstance(r["baz"].y, MyTestModelSubclass)

        # Make sure the arbitrary class was instantiated properly
        self.assertEqual(r["baz"].z.p, "pp")
        self.assertEqual(r["baz"].z.q, 100.0)

        self.assertEqual(r["bar"].get_registry_dependencies(), [["/foo"]])
        self.assertEqual(r["baz"].get_registry_dependencies(), [["/foo"]])

    def test_load_config_nested_round_trip(self):
        path = os.path.join(os.path.dirname(__file__), "config", "conf.yaml")
        r = ModelRegistry.root()
        r.load_config_from_path(path)

        cfg2 = {name: model.model_dump(by_alias=True) for name, model in r.models.items()}
        r2 = ModelRegistry(name="replica")
        r2.load_config(cfg2)
        self.assertEqual(r.models, r2.models)

    def test_load_subregistries(self):
        path = os.path.join(os.path.dirname(__file__), "config", "conf_sub.yaml")
        r = ModelRegistry.root()
        r.load_config_from_path(path)
        self.assertEqual(list(r.models.keys()), ["subregistry1", "subregistry2"])
        self.assertEqual(list(r["subregistry1"].models.keys()), ["foo", "bar"])
        self.assertEqual(list(r["subregistry2"].models.keys()), ["baz"])

        # Make sure the references work
        self.assertEqual(r["subregistry1"]["bar"].x, r["subregistry1"]["foo"])
        self.assertEqual(r["subregistry2"]["baz"].x, r["subregistry1"]["foo"])

        # Make sure composite paths get resolved properly
        self.assertEqual(r["subregistry1/bar"], r["subregistry1"]["bar"])
        self.assertEqual(r["subregistry2"]["/subregistry1/bar"], r["subregistry1"]["bar"])

        self.assertRaisesRegex(
            KeyError,
            "No registered model found by the name 'garbage' in registry '/subregistry1'",
            lambda: r["subregistry2"]["/subregistry1/garbage"],
        )

        # Make sure dependencies are correct
        self.assertEqual(r["subregistry1/bar"].get_registry_dependencies(), [["/subregistry1/foo"]])
        self.assertEqual(r["subregistry2/baz"].get_registry_dependencies(), [["/subregistry1/foo"]])

    def test_load_subregistries_not_root(self):
        path = os.path.join(os.path.dirname(__file__), "config", "conf_sub.yaml")
        r = ModelRegistry()
        r.load_config_from_path(path)
        self.assertEqual(list(r.models.keys()), ["subregistry1", "subregistry2"])
        self.assertEqual(list(r["subregistry1"].models.keys()), ["foo", "bar"])
        self.assertEqual(list(r["subregistry2"].models.keys()), ["baz"])

    def test_load_subregistries_round_trip(self):
        path = os.path.join(os.path.dirname(__file__), "config", "conf_sub.yaml")
        r = ModelRegistry.root()
        r.load_config_from_path(path)

        # cfg2 = {name: model.dict(by_alias=True) for name, model in r.models.items()}
        cfg2 = r.model_dump(by_alias=True)
        self.assertIn("_target_", cfg2)
        r2 = ModelRegistry(name="replica")
        r2.load_config(cfg2["models"])
        self.assertEqual(r.models.keys(), r2.models.keys())
        for k in r.models:
            self.assertEqual(r.models[k].models, r2.models[k].models)
        self.assertEqual(r.models, r2.models)

    def test_load_out_of_order(self):
        path = os.path.join(os.path.dirname(__file__), "config", "conf_out_of_order.yaml")
        r = ModelRegistry.root()
        r.load_config_from_path(path)
        self.assertEqual(list(r.models.keys()), ["subregistry2", "subregistry1"])
        self.assertEqual(list(r["subregistry1"].models.keys()), ["foo", "bar"])
        self.assertEqual(list(r["subregistry2"].models.keys()), ["qux", "baz"])

        # Make sure the references work
        self.assertEqual(r["subregistry1"]["bar"].x, r["subregistry1"]["foo"])
        self.assertEqual(r["subregistry1"]["bar"].y, r["subregistry2"]["qux"])
        self.assertEqual(r["subregistry2"]["baz"].x, r["subregistry1"]["foo"])
        self.assertEqual(r["subregistry2"]["baz"].y, r["subregistry2"]["qux"])

        # Make sure composite paths get resolved properly
        self.assertEqual(r["subregistry1/bar"], r["subregistry1"]["bar"])
        self.assertEqual(r["subregistry2"]["/subregistry1/bar"], r["subregistry1"]["bar"])

        self.assertRaisesRegex(
            KeyError,
            "No registered model found by the name 'garbage' in registry '/subregistry1'",
            lambda: r["subregistry2"]["/subregistry1/garbage"],
        )

        # Make sure dependencies are correct
        self.assertEqual(
            r["subregistry1/bar"].get_registry_dependencies(),
            [["/subregistry1/foo"], ["/subregistry2/qux"]],
        )
        self.assertEqual(
            r["subregistry2/baz"].get_registry_dependencies(),
            [["/subregistry1/foo"], ["/subregistry2/qux"]],
        )


class TestRegistryLoadingErrors(TestCase):
    def setUp(self) -> None:
        ModelRegistry.root().clear()

    def tearDown(self) -> None:
        ModelRegistry.root().clear()

    def test_interpolation_error(self):
        cfg = OmegaConf.create(
            {
                "foo": {
                    "_target_": "ccflow.tests.test_base_registry.MyTestModel",
                    "a": "${bar}",
                    "b": 0.0,
                },
            }
        )
        r = ModelRegistry(name="test")
        with self.assertRaises(InterpolationKeyError) as cm:
            r.load_config(cfg)
        self.assertIn("Interpolation key 'bar' not found", str(cm.exception))

    def test_model_lookup_error(self):
        cfg = OmegaConf.create(
            {
                "subregistry": {
                    "bar": {
                        "_target_": "ccflow.tests.test_base_registry.MyNestedModel",
                        "x": "foo",  # Model which does not exist
                        "y": {"a": "test2", "b": 2.0},
                    },
                }
            }
        )
        r = ModelRegistry(name="test")
        with self.assertRaises(InstantiationException) as cm:
            r.load_config(cfg)

        self.assertIn("Could not resolve model 'foo' in registry 'subregistry'", str(cm.exception))
        self.assertNotIn("Did you mean", str(cm.exception))  # No helpful suggestions because there is no "foo" anywhere
        self.assertIn("full_key: subregistry.bar", str(cm.exception))

    @pytest.mark.skipif(sys.version_info < (3, 11), reason="Skipping on python<3.11 because ExceptionGroup not supported")
    def test_two_model_lookup_errors(self):
        cfg = OmegaConf.create(
            {
                "subregistry": {
                    "bar": {
                        "_target_": "ccflow.tests.test_base_registry.MyNestedModel",
                        "x": "foo",  # Model which does not exist
                        "y": {"a": "test2", "b": 2.0},
                    },
                    "baz": {
                        "_target_": "ccflow.tests.test_base_registry.MyNestedModel",
                        "x": "foo",  # Model which does not exist
                        "y": {"a": "test3", "b": 3.0},
                    },
                }
            }
        )
        r = ModelRegistry(name="test")

        with self.assertRaises(ExceptionGroup) as cm:  # noqa: F821
            r.load_config(cfg)
        group = cm.exception
        self.assertEqual(len(group.exceptions), 2)
        for ex in group.exceptions:
            self.assertIsInstance(ex, InstantiationException)
            self.assertIn("Could not resolve model 'foo' in registry 'subregistry'", str(ex))
        self.assertIn("full_key: subregistry.bar", str(group.exceptions[0]))
        self.assertIn("full_key: subregistry.baz", str(group.exceptions[1]))

    def test_model_lookup_error_relative(self):
        cfg = OmegaConf.create(
            {
                "foo": {
                    "_target_": "ccflow.tests.test_base_registry.MyTestModel",
                    "a": "test",
                    "b": 0.0,
                },
                "subregistry": {
                    "bar": {
                        "_target_": "ccflow.tests.test_base_registry.MyNestedModel",
                        "x": "foo",  # Relative path, should be ../foo or /foo, so should raise
                        "y": {"a": "test2", "b": 2.0},
                    },
                },
            }
        )
        r = ModelRegistry(name="test")
        with self.assertRaises(InstantiationException) as cm:
            r.load_config(cfg)
        self.assertIn("Could not resolve model 'foo' in registry 'subregistry'", str(cm.exception))
        self.assertIn("Did you mean '/foo' for an absolute lookup from the root registry?", str(cm.exception))
        self.assertIn("full_key: subregistry.bar", str(cm.exception))

    def test_model_lookup_wrong_type_error(self):
        cfg = OmegaConf.create(
            {
                "foo": {"_target_": f"{MyTestModel2.__module__}.MyTestModel2", "v": 0},
                "subregistry": {
                    "bar": {
                        "_target_": f"{MyNestedModel.__module__}.MyNestedModel",
                        "x": "/foo",
                        "y": {"a": "test2", "b": 2.0},
                    },
                },
            }
        )
        r = ModelRegistry(name="test")
        with self.assertRaises(InstantiationException) as cm:
            r.load_config(cfg)
        self.assertIn("Input should be a valid dictionary or instance of MyTestModel", str(cm.exception))
        self.assertIn("full_key: subregistry.bar", str(cm.exception))

    def test_bad_class_error(self):
        cfg = OmegaConf.create(
            {
                "foo": {
                    "_target_": "ccflow.tests.test_base_registry.BadClass",
                    "a": "test",
                    "b": 0.0,
                },
            }
        )
        r = ModelRegistry(name="test")
        msg = "Error locating target 'ccflow.tests.test_base_registry.BadClass', set env var HYDRA_FULL_ERROR=1 to see chained exception."
        with self.assertRaises(InstantiationException) as cm:
            r.load_config(cfg)
        self.assertIn(msg, str(cm.exception))
        self.assertIn("full_key: foo", str(cm.exception))

    def test_validation_error(self):
        cfg = OmegaConf.create(
            {
                "foo": {
                    "_target_": "ccflow.tests.test_base_registry.MyTestModel",
                    "a": "test",
                    "b": "string_that_should_be_a_float",
                },
            }
        )
        r = ModelRegistry(name="test")
        msg = "b\n  Input should be a valid number, unable to parse string as a number [type=float_parsing, input_value='string_that_should_be_a_float', input_type=str]"
        with self.assertRaises(InstantiationException) as cm:
            r.load_config(cfg)
        self.assertIn("Error in call to target 'ccflow.tests.test_base_registry.MyTestModel':", str(cm.exception))
        self.assertIn(msg, str(cm.exception))
        self.assertIn("full_key: foo", str(cm.exception))

    @pytest.mark.skipif(sys.version_info < (3, 11), reason="Skipping on python<3.11 because ExceptionGroup not supported")
    def test_two_validation_errors(self):
        cfg = OmegaConf.create(
            {
                "foo": {
                    "_target_": "ccflow.tests.test_base_registry.MyTestModel",
                    "a": "test",
                    "b": "string_that_should_be_a_float",
                },
                "bar": {
                    "_target_": "ccflow.tests.test_base_registry.MyTestModel",
                    "a": "test",
                    "b": "another_string",
                },
            }
        )
        r = ModelRegistry(name="test")
        with self.assertRaises(ExceptionGroup) as cm:  # noqa: F821
            r.load_config(cfg)
        group = cm.exception
        self.assertEqual(len(group.exceptions), 2)
        for ex in group.exceptions:
            self.assertIsInstance(ex, InstantiationException)
            self.assertIn("Error in call to target 'ccflow.tests.test_base_registry.MyTestModel':", str(ex))

        msg0 = "b\n  Input should be a valid number, unable to parse string as a number [type=float_parsing, input_value='string_that_should_be_a_float', input_type=str]"
        msg1 = "b\n  Input should be a valid number, unable to parse string as a number [type=float_parsing, input_value='another_string', input_type=str]"
        self.assertIn(msg0, str(group.exceptions[0]))
        self.assertIn(msg1, str(group.exceptions[1]))
        self.assertIn("full_key: foo", str(group.exceptions[0]))
        self.assertIn("full_key: bar", str(group.exceptions[1]))

    def test_lookup_and_validation_error(self):
        cfg = OmegaConf.create(
            {
                "bar": {  # This produces a resolution error, which is skipped to highlight the underlying validation error
                    "_target_": "ccflow.tests.test_base_registry.MyNestedModel",
                    "x": "foo",  # Model which does not exist because it failed to load
                    "y": {"a": "test2", "b": 2.0},
                },
                "foo": {
                    "_target_": "ccflow.tests.test_base_registry.MyTestModel",
                    "a": "test",
                    "b": "string_that_should_be_a_float",
                },
            }
        )
        r = ModelRegistry(name="test")
        msg = "b\n  Input should be a valid number, unable to parse string as a number [type=float_parsing, input_value='string_that_should_be_a_float', input_type=str]"
        with self.assertRaises(InstantiationException) as cm:
            r.load_config(cfg)
        self.assertIn("Error in call to target 'ccflow.tests.test_base_registry.MyTestModel':", str(cm.exception))
        self.assertIn(msg, str(cm.exception))
        self.assertIn("full_key: foo", str(cm.exception))

    def test_misspelling_warning(self):
        cfg = OmegaConf.create(
            {
                "foo": {
                    "_target": "ccflow.tests.test_base_registry.MyTestModel",
                    "a": "test",
                    "b": "string_that_should_be_a_float",
                },
            }
        )
        r = ModelRegistry(name="test")
        msg = "Found config value containing `_target`, are you sure you didn't mean '_target_'?"
        with self.assertWarnsRegex(SyntaxWarning, msg):
            r.load_config(cfg)


class TestRegistryLookupContext(TestCase):
    def setUp(self) -> None:
        ModelRegistry.root().clear()

    def tearDown(self) -> None:
        ModelRegistry.root().clear()

    def test_registry_paths(self):
        r = ModelRegistry.root()
        r2 = ModelRegistry(name="r2")
        r3 = ModelRegistry(name="r3")
        r2.add("bar", r3)
        r.add("foo", r2)
        with RegistryLookupContext([r, r2]):
            paths = RegistryLookupContext.registry_search_paths()
            self.assertEqual(paths, [r, r2])
            with RegistryLookupContext([r, r2, r3]):
                paths = RegistryLookupContext.registry_search_paths()
                self.assertEqual(paths, [r, r2, r3])
            paths = RegistryLookupContext.registry_search_paths()
            self.assertEqual(paths, [r, r2])

        paths = RegistryLookupContext.registry_search_paths()
        self.assertEqual(paths, [])

    def test_validation(self):
        m = MyTestModel(a="test", b=0.0)
        m2 = MyTestModel(a="test2", b=0.0)
        r = ModelRegistry.root()
        r2 = ModelRegistry(name="r2")
        r3 = ModelRegistry(name="r3")
        r3.add("baz", m)
        r2.add("bar", r3)
        r.add("foo", r2)

        # Does not work in the base context
        self.assertRaises((KeyError, ValueError), BaseModel.model_validate, "baz")

        # Add m2 to root
        r.add("baz", m2)
        # All of below work in root context
        self.assertIs(BaseModel.model_validate("baz"), m2)
        self.assertIs(BaseModel.model_validate("baz"), m2)
        self.assertIs(BaseModel.model_validate("./baz"), m2)  # From root

        # Validation works in the context where "registry" is foo/bar
        with RegistryLookupContext([r3]):
            self.assertIs(BaseModel.model_validate("baz"), m)
            self.assertIs(BaseModel.model_validate("./baz"), m)

        # Also works in nested contexts
        with RegistryLookupContext([r2, r3]):
            self.assertIs(BaseModel.model_validate("baz"), m)

        with RegistryLookupContext([r2]):
            self.assertIs(BaseModel.model_validate("bar"), r3)
        with RegistryLookupContext([r2, r3]):
            self.assertIs(BaseModel.model_validate("../bar"), r3)
        with RegistryLookupContext([r2, r3, r]):
            self.assertIs(BaseModel.model_validate("../baz"), m)
            self.assertIs(BaseModel.model_validate("foo"), r2)
            self.assertIs(BaseModel.model_validate("./foo/bar/baz"), m)
