"""Tests for the helpers module."""

from pathlib import Path
from typing import Annotated, Dict, List, Optional, Union

import pytest
from madsci.common.types.action_types import (
    ActionFiles,
    ActionJSON,
    FileActionResultDefinition,
    JSONActionResultDefinition,
)
from madsci.node_module.helpers import create_dynamic_model, parse_result, parse_results
from pydantic import BaseModel, ValidationError


class ExampleJSONData(ActionJSON):
    """Example JSON data for testing."""

    value1: str
    value2: int


class ExampleFileData(ActionFiles):
    """Example file data for testing."""

    file1: Path
    file2: Path


class CustomPydanticModel(BaseModel):
    """Example custom pydantic model for testing."""

    name: str
    value: int
    metadata: dict[str, str] = {}


class ComplexPydanticModel(BaseModel):
    """Complex custom pydantic model for testing."""

    id: str
    data: list[float]
    config: dict[str, Union[str, int]]
    nested: Optional[CustomPydanticModel] = None


def test_parse_result_basic_types():
    """Test parse_result with basic types."""
    # Test int
    result = parse_result(int)
    assert len(result) == 1
    assert isinstance(result[0], JSONActionResultDefinition)
    assert result[0].result_label == "json_result"
    assert result[0].json_schema is not None
    assert "properties" in result[0].json_schema

    # Test str
    result = parse_result(str)
    assert len(result) == 1
    assert isinstance(result[0], JSONActionResultDefinition)
    assert result[0].result_label == "json_result"
    assert result[0].json_schema is not None

    # Test dict
    result = parse_result(dict)
    assert len(result) == 1
    assert isinstance(result[0], JSONActionResultDefinition)
    assert result[0].result_label == "json_result"
    assert result[0].json_schema is not None


def test_parse_result_path():
    """Test parse_result with Path type."""
    result = parse_result(Path)
    assert len(result) == 1
    assert isinstance(result[0], FileActionResultDefinition)
    assert result[0].result_label == "file"


def test_parse_result_action_json():
    """Test parse_result with ActionJSON subclass."""
    result = parse_result(ExampleJSONData)
    assert len(result) == 1

    # Check that we get a single json_result with schema
    assert result[0].result_label == "json_result"
    assert isinstance(result[0], JSONActionResultDefinition)
    assert result[0].json_schema is not None

    # Check that the schema includes the fields from the ActionJSON subclass
    schema = result[0].json_schema
    assert "properties" in schema
    assert "data" in schema["properties"]


def test_parse_result_action_files():
    """Test parse_result with ActionFiles subclass."""
    result = parse_result(ExampleFileData)
    assert len(result) == 2

    # Check that both fields are present
    labels = [r.result_label for r in result]
    assert "file1" in labels
    assert "file2" in labels

    # Check that they're all file result definitions
    for r in result:
        assert isinstance(r, FileActionResultDefinition)


def test_parse_result_tuple_basic_types():
    """Test parse_result with tuple of basic types."""
    result = parse_result(tuple[int, str])
    assert len(result) == 2

    # Should get two JSON result definitions with schemas
    assert all(isinstance(r, JSONActionResultDefinition) for r in result)
    assert all(r.result_label == "json_result" for r in result)
    assert all(r.json_schema is not None for r in result)


def test_parse_result_tuple_mixed_types():
    """Test parse_result with tuple of mixed types including Path."""
    result = parse_result(tuple[int, Path])
    assert len(result) == 2

    # Should get one JSON and one file result definition
    result_types = [type(r) for r in result]
    assert JSONActionResultDefinition in result_types
    assert FileActionResultDefinition in result_types


def test_parse_result_tuple_action_types():
    """Test parse_result with tuple of ActionJSON and ActionFiles."""
    result = parse_result(tuple[ExampleJSONData, ExampleFileData])
    assert len(result) == 3  # 1 JSON result + 2 file fields

    # Check that we get the right mix of result types
    json_results = [r for r in result if isinstance(r, JSONActionResultDefinition)]
    file_results = [r for r in result if isinstance(r, FileActionResultDefinition)]

    assert len(json_results) == 1  # Single json_result with schema
    assert len(file_results) == 2  # file1 and file2


# Test functions for Annotated return types


def dummy_function_annotated_str() -> Annotated[str, "A string result"]:
    """Dummy function for testing parse_results with Annotated str."""
    return "test"


def dummy_function_annotated_int() -> Annotated[int, "An integer result"]:
    """Dummy function for testing parse_results with Annotated int."""
    return 42


def dummy_function_annotated_dict() -> Annotated[dict[str, int], "A dictionary result"]:
    """Dummy function for testing parse_results with Annotated dict."""
    return {"key": 1}


def dummy_function_annotated_path() -> Annotated[Path, "A file path result"]:
    """Dummy function for testing parse_results with Annotated Path."""
    return Path("/test")


def dummy_function_annotated_tuple() -> Annotated[tuple[str, int], "A tuple result"]:
    """Dummy function for testing parse_results with Annotated tuple."""
    return ("test", 42)


def dummy_function_annotated_pydantic() -> Annotated[
    CustomPydanticModel, "A custom model result"
]:
    """Dummy function for testing parse_results with Annotated custom Pydantic model."""
    return CustomPydanticModel(name="test", value=42)


def test_parse_results_with_annotated_str():
    """Test parse_results function with Annotated str return annotation."""
    result = parse_results(dummy_function_annotated_str)
    assert len(result) == 1
    assert isinstance(result[0], JSONActionResultDefinition)
    assert result[0].result_label == "json_result"
    assert result[0].json_schema is not None


def test_parse_results_with_annotated_int():
    """Test parse_results function with Annotated int return annotation."""
    result = parse_results(dummy_function_annotated_int)
    assert len(result) == 1
    assert isinstance(result[0], JSONActionResultDefinition)
    assert result[0].result_label == "json_result"
    assert result[0].json_schema is not None


def test_parse_results_with_annotated_dict():
    """Test parse_results function with Annotated dict return annotation."""
    result = parse_results(dummy_function_annotated_dict)
    assert len(result) == 1
    assert isinstance(result[0], JSONActionResultDefinition)
    assert result[0].result_label == "json_result"
    assert result[0].json_schema is not None


def test_parse_results_with_annotated_path():
    """Test parse_results function with Annotated Path return annotation."""
    result = parse_results(dummy_function_annotated_path)
    assert len(result) == 1
    assert isinstance(result[0], FileActionResultDefinition)
    assert result[0].result_label == "file"


def test_parse_results_with_annotated_tuple():
    """Test parse_results function with Annotated tuple return annotation."""
    result = parse_results(dummy_function_annotated_tuple)
    assert len(result) == 2  # str + int

    json_results = [r for r in result if isinstance(r, JSONActionResultDefinition)]
    assert len(json_results) == 2


def test_parse_results_with_annotated_pydantic():
    """Test parse_results function with Annotated custom Pydantic model return annotation."""
    result = parse_results(dummy_function_annotated_pydantic)
    assert len(result) == 1
    assert isinstance(result[0], JSONActionResultDefinition)
    assert result[0].result_label == "json_result"
    assert result[0].json_schema is not None


def test_parse_result_annotated_basic_types():
    """Test parse_result with Annotated basic types."""
    # Test Annotated[int, "description"]
    result = parse_result(Annotated[int, "An integer"])
    assert len(result) == 1
    assert isinstance(result[0], JSONActionResultDefinition)

    # Test Annotated[str, "description"]
    result = parse_result(Annotated[str, "A string"])
    assert len(result) == 1
    assert isinstance(result[0], JSONActionResultDefinition)

    # Test Annotated[Path, "description"]
    result = parse_result(Annotated[Path, "A file path"])
    assert len(result) == 1
    assert isinstance(result[0], FileActionResultDefinition)


def test_parse_result_nested_tuple():
    """Test parse_result with nested tuple types."""
    # This should work since we recursively handle tuples
    result = parse_result(tuple[tuple[int, str], Path])
    assert len(result) == 3  # int + str + Path

    json_results = [r for r in result if isinstance(r, JSONActionResultDefinition)]
    file_results = [r for r in result if isinstance(r, FileActionResultDefinition)]

    assert len(json_results) == 2  # int and str
    assert len(file_results) == 1  # Path


def test_parse_result_invalid_type():
    """Test parse_result with invalid type."""
    with pytest.raises(ValueError, match="Action return type must be"):
        parse_result(object)


def dummy_function_with_tuple() -> tuple[int, Path]:
    """Dummy function for testing parse_results with tuple."""
    return 42, Path("/test")


def dummy_function_with_action_tuple() -> tuple[ExampleJSONData, ExampleFileData]:
    """Dummy function for testing parse_results with action types in tuple."""
    return (
        ExampleJSONData(value1="test", value2=42),
        ExampleFileData(file1=Path("/test1"), file2=Path("/test2")),
    )


def test_parse_results_with_tuple():
    """Test parse_results function with tuple return annotation."""
    result = parse_results(dummy_function_with_tuple)
    assert len(result) == 2

    # Should get one JSON and one file result definition
    result_types = [type(r) for r in result]
    assert JSONActionResultDefinition in result_types
    assert FileActionResultDefinition in result_types


def test_parse_results_with_action_tuple():
    """Test parse_results function with tuple of action types."""
    result = parse_results(dummy_function_with_action_tuple)
    assert len(result) == 3  # 1 JSON result + 2 file fields

    # Check that we get the right mix of result types
    json_results = [r for r in result if isinstance(r, JSONActionResultDefinition)]
    file_results = [r for r in result if isinstance(r, FileActionResultDefinition)]

    assert len(json_results) == 1  # Single json_result with schema
    assert len(file_results) == 2  # file1 and file2


def test_create_dynamic_model_basic_types():
    """Test create_dynamic_model with basic types."""
    # Test int
    model = create_dynamic_model(int, field_name="value", model_name="IntModel")
    instance = model(value=42)
    assert instance.value == 42

    # Test str
    model = create_dynamic_model(str, field_name="text", model_name="StrModel")
    instance = model(text="hello")
    assert instance.text == "hello"

    # Test dict
    model = create_dynamic_model(dict, field_name="data", model_name="DictModel")
    instance = model(data={"key": "value"})
    assert instance.data == {"key": "value"}


def test_create_dynamic_model_optional_types():
    """Test create_dynamic_model with Optional types."""
    model = create_dynamic_model(
        Optional[int], field_name="value", model_name="OptionalIntModel"
    )

    # Test with value
    instance = model(value=42)
    assert instance.value == 42

    # Test with None
    instance = model(value=None)
    assert instance.value is None


def test_create_dynamic_model_list_types():
    """Test create_dynamic_model with List types."""
    model = create_dynamic_model(List[str], field_name="items", model_name="ListModel")
    instance = model(items=["a", "b", "c"])
    assert instance.items == ["a", "b", "c"]


def test_create_dynamic_model_dict_types():
    """Test create_dynamic_model with Dict types."""
    model = create_dynamic_model(
        Dict[str, int], field_name="mapping", model_name="DictModel"
    )
    instance = model(mapping={"a": 1, "b": 2})
    assert instance.mapping == {"a": 1, "b": 2}


def test_create_dynamic_model_union_types():
    """Test create_dynamic_model with Union types."""

    model = create_dynamic_model(
        Union[str, int], field_name="value", model_name="UnionModel"
    )

    # Test with string
    instance = model(value="hello")
    assert instance.value == "hello"

    # Test with int
    instance = model(value=42)
    assert instance.value == 42


def test_create_dynamic_model_tuple_types():
    """Test create_dynamic_model with tuple types."""
    model = create_dynamic_model(
        tuple[str, int], field_name="pair", model_name="TupleModel"
    )
    instance = model(pair=("hello", 42))
    assert instance.pair == ("hello", 42)


def test_create_dynamic_model_nested_types():
    """Test create_dynamic_model with nested complex types."""
    model = create_dynamic_model(
        Dict[str, List[int]], field_name="nested", model_name="NestedModel"
    )
    instance = model(nested={"a": [1, 2, 3], "b": [4, 5, 6]})
    assert instance.nested == {"a": [1, 2, 3], "b": [4, 5, 6]}


def test_create_dynamic_model_custom_pydantic_model():
    """Test create_dynamic_model with existing pydantic model."""
    model = create_dynamic_model(
        CustomPydanticModel, field_name="model", model_name="WrapperModel"
    )

    custom_instance = CustomPydanticModel(name="test", value=42)
    instance = model(model=custom_instance)
    assert instance.model.name == "test"
    assert instance.model.value == 42


def test_create_dynamic_model_with_custom_field_name():
    """Test create_dynamic_model with custom field name."""
    model = create_dynamic_model(
        str, field_name="custom_field", model_name="CustomFieldModel"
    )
    instance = model(custom_field="test")
    assert instance.custom_field == "test"


def test_create_dynamic_model_with_custom_model_name():
    """Test create_dynamic_model with custom model name."""
    model = create_dynamic_model(int, field_name="data", model_name="MyCustomModel")
    assert model.__name__ == "MyCustomModel"


def test_create_dynamic_model_validation():
    """Test that create_dynamic_model properly validates data."""
    model = create_dynamic_model(int, field_name="number", model_name="ValidationModel")

    # Valid data
    instance = model(number=42)
    assert instance.number == 42

    # Invalid data should raise ValidationError
    with pytest.raises(ValidationError):
        model(number="not a number")


def test_create_dynamic_model_complex_example():
    """Test create_dynamic_model with a complex real-world example."""
    complex_type = Dict[str, List[tuple[str, int]]]
    model = create_dynamic_model(
        complex_type, field_name="complex_data", model_name="ComplexModel"
    )

    test_data = {
        "group1": [("item1", 10), ("item2", 20)],
        "group2": [("item3", 30), ("item4", 40)],
    }

    instance = model(complex_data=test_data)
    assert instance.complex_data == test_data


def test_parse_result_custom_pydantic_model():
    """Test parse_result with custom pydantic models."""
    result = parse_result(CustomPydanticModel)
    assert len(result) == 1
    assert isinstance(result[0], JSONActionResultDefinition)
    assert result[0].result_label == "json_result"
    assert result[0].json_schema is not None


def test_parse_result_complex_pydantic_model():
    """Test parse_result with complex pydantic models."""
    result = parse_result(ComplexPydanticModel)
    assert len(result) == 1
    assert isinstance(result[0], JSONActionResultDefinition)
    assert result[0].result_label == "json_result"
    assert result[0].json_schema is not None


def test_parse_result_tuple_with_custom_pydantic():
    """Test parse_result with tuple containing custom pydantic model."""
    result = parse_result(tuple[CustomPydanticModel, Path])
    assert len(result) == 2

    # Check that we get one JSON and one file result definition
    result_types = [type(r) for r in result]
    assert JSONActionResultDefinition in result_types
    assert FileActionResultDefinition in result_types


def test_parse_result_tuple_mixed_custom_pydantic():
    """Test parse_result with tuple of mixed custom types."""
    result = parse_result(tuple[CustomPydanticModel, ExampleFileData])
    assert len(result) == 3  # 1 JSON result + 2 file fields

    # Check that we get the right mix of result types
    json_results = [r for r in result if isinstance(r, JSONActionResultDefinition)]
    file_results = [r for r in result if isinstance(r, FileActionResultDefinition)]

    assert len(json_results) == 1  # Single json_result with schema
    assert len(file_results) == 2  # file1 and file2


def dummy_function_with_custom_pydantic() -> CustomPydanticModel:
    """Dummy function for testing parse_results with custom pydantic model."""
    return CustomPydanticModel(name="test", value=42)


def dummy_function_with_mixed_custom() -> tuple[CustomPydanticModel, ExampleFileData]:
    """Dummy function for testing parse_results with mixed custom types."""
    return (
        CustomPydanticModel(name="test", value=42),
        ExampleFileData(file1=Path("/test1"), file2=Path("/test2")),
    )


def test_parse_results_with_custom_pydantic():
    """Test parse_results function with custom pydantic model return annotation."""
    result = parse_results(dummy_function_with_custom_pydantic)
    assert len(result) == 1
    assert isinstance(result[0], JSONActionResultDefinition)
    assert result[0].result_label == "json_result"
    assert result[0].json_schema is not None


def test_parse_results_with_mixed_custom_types():
    """Test parse_results function with tuple of custom model and ActionFiles."""
    result = parse_results(dummy_function_with_mixed_custom)
    assert len(result) == 3  # 1 JSON result + 2 file fields

    # Check that we get the right mix of result types
    json_results = [r for r in result if isinstance(r, JSONActionResultDefinition)]
    file_results = [r for r in result if isinstance(r, FileActionResultDefinition)]

    assert len(json_results) == 1  # Single json_result with schema
    assert len(file_results) == 2  # file1 and file2
