"""Helper methods used by the MADSci node module implementations."""

import inspect
from pathlib import Path
from typing import Annotated, Any, Callable, Type, get_args, get_origin

import regex
from madsci.common.types.action_types import (
    ActionDatapoints,
    ActionFiles,
    ActionJSON,
    ActionResultDefinition,
    DatapointActionResultDefinition,
    FileActionResultDefinition,
    JSONActionResultDefinition,
)
from pydantic import BaseModel, create_model


def action(
    *args: Any,
    **kwargs: Any,
) -> Callable:
    """
    Decorator to mark a method as an action handler.

    This decorator adds metadata to the decorated function, indicating that it is
    an action handler within the MADSci framework. The metadata includes the action
    name, description, and whether the action is blocking.

    Keyword Args:
        name (str, optional): The name of the action. Defaults to the function name.
        description (str, optional): A description of the action. Defaults to the function docstring.
        blocking (bool, optional): Indicates if the action is blocking. Defaults to False.

    Returns:
        Callable: The decorated function with added metadata.
    """

    def decorator(func: Callable) -> Callable:
        if not isinstance(func, Callable):
            raise ValueError("The action decorator must be used on a callable object")
        func.__is_madsci_action__ = True

        # *Use provided action_name or function name
        name = kwargs.get("name")
        if not name:
            name = kwargs.get("action_name", func.__name__)
        # * Use provided description or function docstring
        description = kwargs.get("description", func.__doc__)
        blocking = kwargs.get("blocking", False)
        func.__madsci_action_name__ = name
        func.__madsci_action_description__ = description
        func.__madsci_action_blocking__ = blocking
        func.__madsci_action_result_definitions__ = parse_results(func)
        return func

    # * If the decorator is used without arguments, return the decorator function
    if len(args) == 1 and callable(args[0]):
        return decorator(args[0])
    return decorator


def split_top_level(s: str) -> list[str]:  # noqa C901
    """
    Splits a string into top-level key-value pairs while keeping
    nested braces/parentheses intact.
    """
    parts = []
    current = []
    depth_curly = 0
    depth_paren = 0
    in_string = False
    escape = False

    for ch in s:
        if escape:
            current.append(ch)
            escape = False
            continue

        if ch == "\\":
            current.append(ch)
            escape = True
            continue

        if ch in {'"', "'"}:  # toggle string state
            in_string = not in_string
            current.append(ch)
            continue

        if not in_string:
            if ch == "{":
                depth_curly += 1
            elif ch == "}":
                depth_curly -= 1
            elif ch == "(":
                depth_paren += 1
            elif ch == ")":
                depth_paren -= 1
            elif ch == "," and depth_curly == 0 and depth_paren == 0:
                # Top-level comma → split
                parts.append("".join(current).strip())
                current = []
                continue

        current.append(ch)

    if current:
        parts.append("".join(current).strip())

    return parts


def get_named_input(main_string: str, plural: str) -> list[str]:
    """gets a named input to an action_result constructor and returns a list of the keys provided"""
    result_list = []
    data = regex.search(plural + r"=(\{(?:[^{}]|(?1))*\})", main_string)
    singular = plural[:-1] if plural[-1] == "s" else plural
    if data is not None:
        data = data.group(0)[len(plural) + 2 : -1]
        data = split_top_level(data)
        if len(data) > 0:
            for datum in data:
                name = datum.split(":")[0]
                if (name[0] == '"' and name[-1] == '"') or (
                    name[0] == "'" and name[-1] == "'"
                ):
                    result_list.append(name[1:-1])
                else:
                    string1 = f"{singular} label : "
                    string2 = f"{name} threw an error, default {singular} labels should be a constant string, not parameterized or variables"
                    raise ValueError(string1.capitalize() + string2)
    return result_list


def _parse_action_files(returned: Any) -> list[ActionResultDefinition]:
    """Parse ActionFiles subclass into result definitions."""
    for key, value in returned.__annotations__.items():
        if value is not Path:
            raise ValueError(
                f"All fields in an ActionFiles subclass must be of type Path, but field {key} is of type {value}",
            )
    return [
        FileActionResultDefinition(result_label=key) for key in returned.__annotations__
    ]


def _parse_action_json(returned: Any) -> list[ActionResultDefinition]:
    """Parse ActionJSON subclass into result definitions."""
    model = create_dynamic_model(
        returned, field_name="data", model_name=returned.__name__
    )
    json_schema = model.model_json_schema()
    return [
        JSONActionResultDefinition(result_label="json_result", json_schema=json_schema)
    ]


def _parse_action_datapoints(returned: Any) -> list[ActionResultDefinition]:
    """Parse ActionDatapoints subclass into result definitions."""
    for key, value in returned.__annotations__.items():
        if value is not str:
            raise ValueError(
                f"All fields in an ActionDatapoints subclass must be str (datapoint IDs) but field {key} is of type {value}",
            )
    return [
        DatapointActionResultDefinition(result_label=key)
        for key in returned.__annotations__
    ]


def _parse_custom_pydantic_model(returned: Any) -> list[ActionResultDefinition]:
    """Parse custom pydantic model into result definitions."""
    json_schema = returned.model_json_schema()
    return [
        JSONActionResultDefinition(result_label="json_result", json_schema=json_schema)
    ]


def _extract_underlying_type(type_hint: Any) -> Any:
    """Extract the underlying type from Annotated types."""
    if get_origin(type_hint) is Annotated:
        # Return the first type argument from Annotated[T, metadata...]
        return get_args(type_hint)[0]
    return type_hint


def parse_result(returned: Any) -> list[ActionResultDefinition]:
    """Parse a single result from an Action"""

    # First extract the underlying type if it's an Annotated type
    returned = _extract_underlying_type(returned)

    # Handle tuple types by recursively parsing each element
    if getattr(returned, "__origin__", None) is tuple:
        result_definitions = []
        for result in returned.__args__:
            result_definitions.extend(parse_result(result))
        return result_definitions

    # Handle Path type specifically
    if returned is Path:
        return [FileActionResultDefinition(result_label="file")]

    # Handle ActionFiles, ActionJSON, ActionDatapoints, and custom pydantic subclasses
    try:
        return _parse_pydantic_class(returned)
    except TypeError:
        # issubclass() raises TypeError if returned is not a class
        pass

    # Handle basic types
    return _parse_basic_type(returned)


def _parse_pydantic_class(returned: Any) -> list[ActionResultDefinition]:
    """Parse pydantic classes (ActionFiles, ActionJSON, ActionDatapoints, custom models)."""
    if issubclass(returned, ActionFiles):
        return _parse_action_files(returned)
    if issubclass(returned, ActionJSON):
        return _parse_action_json(returned)
    if issubclass(returned, ActionDatapoints):
        return _parse_action_datapoints(returned)
    # Handle custom pydantic models
    if issubclass(returned, BaseModel):
        return _parse_custom_pydantic_model(returned)

    # If none of the above, fall through to basic type handling
    raise TypeError("Not a recognized pydantic class")


def _parse_basic_type(returned: Any) -> list[ActionResultDefinition]:
    """Parse basic Python types."""
    # Check basic types directly
    basic_types = [str, int, float, bool, dict, list]

    # For generic types like dict[str, str], check the origin type
    origin_type = get_origin(returned)
    if origin_type is not None:
        # Generic type - check if its origin is a basic type
        if origin_type not in basic_types:
            raise ValueError(
                f"Action return type must be a subclass of ActionFiles, ActionJSON, ActionDatapoints, Path, a Pydantic BaseModel, str, int, float, bool, dict, or list but got {returned}",
            )
    elif returned not in basic_types:
        # Non-generic type - check directly
        raise ValueError(
            f"Action return type must be a subclass of ActionFiles, ActionJSON, ActionDatapoints, Path, a Pydantic BaseModel, str, int, float, bool, dict, or list but got {returned}",
        )

    # Generate model name safely for both basic types and generic types
    origin_type = get_origin(returned)
    if origin_type is not None:
        model_name = f"{origin_type.__name__}Model"
    else:
        model_name = f"{returned.__name__}Model"

    model = create_dynamic_model(returned, field_name="data", model_name=model_name)
    json_schema = model.model_json_schema()
    return [
        JSONActionResultDefinition(result_label="json_result", json_schema=json_schema)
    ]


def parse_results(func: Callable) -> list[ActionResultDefinition]:
    """Get the resulting data from an Action"""
    returned = inspect.signature(func).return_annotation

    if returned is inspect.Signature.empty or returned is None:
        return []
    if getattr(returned, "__origin__", None) is tuple:
        result_definitions = []
        for result in returned.__args__:
            result_definitions.extend(parse_result(result))
    elif returned is Path:
        result_definitions = [FileActionResultDefinition(result_label="file")]
    else:
        result_definitions = parse_result(returned)
    return result_definitions


def create_dynamic_model(
    type_hint: Type[Any],
    field_name: str = "data",
    model_name: str = "DynamicModel",
) -> Type[BaseModel]:
    """
    Create a dynamic Pydantic model from a Python type hint.

    This function takes a Python type hint and creates a Pydantic model class
    that can validate data of that type. It supports basic types, generic types,
    Optional types, Union types, and existing Pydantic models.

    Args:
        type_hint: The Python type hint to create a model for
        field_name: The name of the field in the generated model (default: "data")
        model_name: The name of the generated model class (default: "DynamicModel")

    Returns:
        A Pydantic model class that validates the specified type

    Examples:
        >>> IntModel = create_dynamic_model(int)
        >>> instance = IntModel(data=42)
        >>> instance.data
        42

        >>> ListModel = create_dynamic_model(List[str], field_name="items")
        >>> instance = ListModel(items=["a", "b", "c"])
        >>> instance.items
        ['a', 'b', 'c']
    """
    # Create the model with a single field of the specified type
    field_definition = (type_hint, ...)

    # Use Pydantic's create_model to dynamically create the model class
    return create_model(model_name, **{field_name: field_definition})
