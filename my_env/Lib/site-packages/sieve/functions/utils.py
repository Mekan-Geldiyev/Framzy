import typing
from ..types.base import Struct
import inspect
from typing import Dict, Any, Literal
import os
import importlib
from pydantic.v1 import BaseModel
from pydantic import BaseModel as V2BaseModel
import jsonref


def _issubclass(t1, t2):
    """Return if t1 is a subclass of t2, or if t1 and t2 are the same type."""

    try:
        return issubclass(t1, t2)
    except TypeError:
        return repr(t1).startswith(repr(t2)) or repr(t2).startswith(repr(t1))


def strip_pydantic_fields(d: Dict[str, Any]) -> Dict[str, Any]:
    """
    Strip Pydantic fields from a schema.

    :param d: Schema to strip Pydantic fields from
    :type d: Dict[str, Any]
    :return: Schema with Pydantic fields stripped
    :rtype: Dict[str, Any]
    """

    for key, value in d.items():
        if value["type"] == "object":
            d[key] = {
                "type": "object",
                "properties": strip_pydantic_fields(value["properties"]),
            }
        elif value["type"] == "array":
            d[key] = {
                "type": "array",
                "items": strip_pydantic_fields(value["items"]["properties"]),
            }
            d[key]["type"] = "array"
    return d


def type_to_schema(t: type) -> Dict[str, Any]:
    """This function converts a type to a schema."""

    # TODO: add more types to this, including numpy array
    # FIXME: work for v1 AND v2
    if _issubclass(t, BaseModel) or _issubclass(t, V2BaseModel):
        # For Pydantic models, including Sieve types
        # Note: Initially, we just generate a simple schema for custom structs,
        # ignoring descriptions, etc. We can add more advanced features later.
        # The current schema's purpose will just be for validation. Sample inputs
        # and descriptions will handle the rest for now.

        schema = t.schema()
        resolved_schema = jsonref.JsonRef.replace_refs(schema)
        stripped_schema = strip_pydantic_fields(resolved_schema["properties"])
        return stripped_schema
    elif typing.get_origin(t) == typing.Literal:
        return {"options": typing.get_args(t)}
    return None


def type_to_str(t: type) -> str:
    """This function converts a type to a string."""

    if t is None:
        return "any"
    if isinstance(t, str):  # For references that send in types as strings
        return t
    if typing.get_origin(t) == typing.Literal:
        return "Literal"  # __name__ doesn't work with Literals < 3.9.1

    prefix = "sieve." if t.__module__.startswith("sieve.") else ""
    if hasattr(t, "__name__"):
        prefix += t.__name__
    elif hasattr(t, "_name"):
        prefix += t._name
    else:
        raise TypeError(
            f"Sieve does not currently support type checks for: {t}. Please remove those type annotations."
        )

    # TODO: consider adding this back, but it's only added complexity thus far
    # if hasattr(t, "__args__"):
    #     joined_args = ", ".join([type_to_str(arg) for arg in t.__args__])
    #     return f"{prefix}[{joined_args}]"
    return prefix


def get_class(s: str) -> type:
    """This function gets a class from a string, if possible."""

    module_name, class_name = s.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


def load(config: Dict[str, Any]):
    """
    Load a Function from a config dict. It will load the function or model appropriately, and will import it into memory.

    :param config: Config dict
    :type config: Dict[str, Any]
    :return: Function
    :rtype: Function
    """

    if "type" not in config:
        raise ValueError("Config must have a type")
    from sieve.functions.function import _Function

    if config["type"] == "function":
        _Function.prevent_run = True
        module_path = os.path.basename(config["filepath"])
        module_name = os.path.basename(module_path).split(".py", 1)[0]
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        assert spec is not None
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        function = getattr(module, config["local_name"])
        _Function.prevent_run = False
        return function
    elif config["type"] == "model":
        _Function.prevent_run = True
        module_path = os.path.basename(config["filepath"])
        module_name = os.path.basename(module_path).split(".py", 1)[0]
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        assert spec is not None
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        model = getattr(module, config["local_name"])
        _Function.prevent_run = False
        return model
