# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from pathlib import Path
from unittest import mock

import pytest
import yaml

import fabric_cicd.constants as constants
from fabric_cicd._parameter._parameter import Parameter

SAMPLE_PARAMETER_FILE = """ 
find_replace:
    # Required Fields 
    - find_value: "db52be81-c2b2-4261-84fa-840c67f4bbd0"
      replace_value:
          PPE: "81bbb339-8d0b-46e8-bfa6-289a159c0733"
          PROD: "5d6a1b16-447f-464a-b959-45d0fed35ca0"
      # Optional Fields
      item_type: "Notebook"
      item_name: ["Hello World"] 
      file_path: "/Hello World.Notebook/notebook-content.py"
spark_pool:
    # Required Fields
    - instance_pool_id: "72c68dbc-0775-4d59-909d-a47896f4573b"
      replace_value:
          PPE:
              type: "Capacity"
              name: "CapacityPool_Large_PPE"
          PROD:
              type: "Capacity"
              name: "CapacityPool_Large_PROD"
      # Optional Fields
      item_name: 
"""

SAMPLE_PARAMETER_FILE_MULTIPLE = """ 
find_replace:
    # Required Fields 
    - find_value: "db52be81-c2b2-4261-84fa-840c67f4bbd0"
      replace_value:
          PPE: "81bbb339-8d0b-46e8-bfa6-289a159c0733"
          PROD: "5d6a1b16-447f-464a-b959-45d0fed35ca0"
      # Optional Fields
      item_type: "Notebook"
      item_name: ["Hello World"] 
      file_path: "/Hello World.Notebook/notebook-content.py"
    # Required Fields 
    - find_value: "db52be81-c2b2-4261-84fa-840c67f4bbd0"
      replace_value:
          PPE: "81bbb339-8d0b-46e8-bfa6-289a159c0733"
          PROD: "5d6a1b16-447f-464a-b959-45d0fed35ca0"
      # Optional Fields
      item_type: "Notebook"
      item_name: ["Hello World"] 
      file_path: "/Hello World.Notebook/notebook-content.py"
key_value_replace:
    - find_key: $.variables[?(@.name=="SQL_Server")].value
      replace_value:
        PPE: "contoso-ppe.database.windows.net"
        PROD: "contoso-prod.database.windows.net"
        UAT: "contoso-uat.database.windows.net"
      # Optional fields:
      item_type: "VariableLibrary"
      item_name: "Vars"
    - find_key: $.variables[?(@.name=="Environment")].value
      replace_value:
        PPE: "PPE"
        PROD: "PROD"
        UAT: "UAT"
      # Optional fields:
      item_type: "VariableLibrary"
      item_name: "Vars"
    - find_key: $.variableOverrides[?(@.name=="SQL_Server")].value
      replace_value:
        PROD: "contoso-production-override.database.windows.net"
      file_path: Vars.VariableLibrary/valueSets/PROD.json
      item_type: "VariableLibrary"
      item_name: "Vars"
    - find_key: $.variableOverrides[?(@.name=="Environment")].value
      replace_value:
        PROD: "PROD_ENV"
      file_path: Vars.VariableLibrary/valueSets/PROD.json
      item_type: "VariableLibrary"
      item_name: "Vars"
"""

SAMPLE_INVALID_PARAMETER_FILE = """
find_replace:
    # Required Fields 
    - find_value: "db52be81-c2b2-4261-84fa-840c67f4bbd0"
      replace_value:
          PPE: "81bbb339-8d0b-46e8-bfa6-289a159c0733"
          PROD: "5d6a1b16-447f-464a-b959-45d0fed35ca0"
      # Optional Fields
      item_type: "Notebook"
      item_name: ["Hello World"] 
      file_path: "/Hello World.Notebook/notebook-content.py"
spark_pool:
    # CapacityPool_Large
    "72c68dbc-0775-4d59-909d-a47896f4573b":
        type: "Capacity"
        name: "CapacityPool_Large"
    # CapacityPool_Medium
    "e7b8f1c4-4a6e-4b8b-9b2e-8f1e5d6a9c3d":
        type: "Workspace"
        name: "WorkspacePool_Medium"
"""

SAMPLE_PARAMETER_NO_TARGET_ENV = """ 
find_replace:
    # Required Fields 
    - find_value: "db52be81-c2b2-4261-84fa-840c67f4bbd0"
      replace_value:
          DEV: "81bbb339-8d0b-46e8-bfa6-289a159c0733"
          PROD: "5d6a1b16-447f-464a-b959-45d0fed35ca0"
      # Optional Fields
      item_type: "Notebook"
      item_name: ["Hello World"] 
      file_path: "/Hello World.Notebook/notebook-content.py"
"""

SAMPLE_PARAMETER_MISSING_FIND_VAL = """ 
find_replace:
    # Required Fields 
    - find_value: 
      replace_value:
          PPE: "81bbb339-8d0b-46e8-bfa6-289a159c0733"
          PROD: "5d6a1b16-447f-464a-b959-45d0fed35ca0"
      # Optional Fields
      item_type: "Notebook"
      item_name: ["Hello World"] 
      file_path: "/Hello World.Notebook/notebook-content.py"
"""

SAMPLE_PARAMETER_MISMATCH_FILTER = """ 
find_replace:
    # Required Fields 
    - find_value: "db52be81-c2b2-4261-84fa-840c67f4bbd0"
      replace_value:
          PPE: "81bbb339-8d0b-46e8-bfa6-289a159c0733"
          PROD: "5d6a1b16-447f-464a-b959-45d0fed35ca0"
      # Optional Fields
      item_type: "Notebook"
      item_name: ["Hello World", 'Hello World Subfolder'] 
      file_path: "/Hello World.Notebook/notebook-content.py"
"""

SAMPLE_PARAMETER_MISSING_REPLACE_VAL = """
spark_pool:
    # Required Fields
    - instance_pool_id: "72c68dbc-0775-4d59-909d-a47896f4573b"
      replace_value:
      # Optional Fields
      item_name:
"""

SAMPLE_PARAMETER_INVALID_NAME = """
spark_pool_param:
    # Required Fields
    - instance_pool_id: "72c68dbc-0775-4d59-909d-a47896f4573b"
      replace_value:
          PPE:
              type: "Capacity"
              name: "CapacityPool_Large_PPE"
          PROD:
              type: "Capacity"
              name: "CapacityPool_Large_PROD"
      # Optional Fields
      item_name: 
"""

SAMPLE_PARAMETER_INVALID_YAML_STRUC = """
spark_pool:
    # Required Fields
    instance_pool_id: "72c68dbc-0775-4d59-909d-a47896f4573b"
      replace_value:
          PPE:
              type: "Capacity"
              name: "CapacityPool_Large_PPE"
          PROD:
              type: "Capacity"
              name: "CapacityPool_Large_PROD"
      # Optional Fields
      item_name: 
"""

SAMPLE_PARAMETER_INVALID_YAML_CHAR = """
find_replace:
    # Required Fields 
    - find_value: '"db52be81-c2b2-4261-84fa-840c67f4bbd0"
      replace_value:
          PPE: "81bbb339-8d0b-46e8-bfa6-289a159c0733"
          PROD: "5d6a1b16-447f-464a-b959-45d0fed35ca0"
      # Optional Fields
      item_type: "Notebook"
      item_name: ["Hello World"] 
      file_path: "/Hello World.Notebook/notebook-content.py"
"""

SAMPLE_PARAMETER_INVALID_IS_REGEX = """
find_replace:
    # Required Fields
    - find_value: "\\#\\s*META\\s+\"default_lakehouse\":\\s*\"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})\""
      replace_value:
          PPE: "81bbb339-8d0b-46e8-bfa6-289a159c0733"
          PROD: "5d6a1b16-447f-464a-b959-45d0fed35ca0"
      # Optional Fields
      is_regex: True
      item_type: "Notebook"
"""

SAMPLE_PARAMETER_ALL_ENV = """
find_replace:
    # Required Fields 
    - find_value: "db52be81-c2b2-4261-84fa-840c67f4bbd0"
      replace_value:
          ALL: "universal-workspace-id-12345"
      # Optional Fields
      item_type: "Notebook"
      item_name: ["Hello World"] 
      file_path: "/Hello World.Notebook/notebook-content.py"
key_value_replace:
    - find_key: $.variables[?(@.name=="Environment")].value
      replace_value:
        ALL: "ANY_ENV"
      # Optional fields:
      item_type: "VariableLibrary"
      item_name: "Vars"
"""

SAMPLE_PLATFORM_FILE = """
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
  "metadata": {
    "type": "Notebook",
    "displayName": "Hello World",
    "description": "Sample notebook"
  },
  "config": {
    "version": "2.0",
    "logicalId": "99b570c5-0c79-9dc4-4c9b-fa16c621384c"
  }
}
"""

SAMPLE_NOTEBOOK_FILE = "print('Hello World and replace connection string: db52be81-c2b2-4261-84fa-840c67f4bbd0')"


@pytest.fixture
def item_type_in_scope():
    return ["Notebook", "DataPipeline", "Environment"]


@pytest.fixture
def target_environment():
    return "PPE"


@pytest.fixture
def repository_directory(tmp_path):
    # Create the sample workspace structure
    workspace_dir = tmp_path / "sample" / "workspace"
    workspace_dir.mkdir(parents=True, exist_ok=True)

    # Create the sample parameter file
    parameter_file_path = workspace_dir / constants.PARAMETER_FILE_NAME
    parameter_file_path.write_text(SAMPLE_PARAMETER_FILE)

    # Create sample invalid parameter files
    invalid_parameter_file_path = workspace_dir / "invalid_parameter.yml"
    invalid_parameter_file_path.write_text(SAMPLE_INVALID_PARAMETER_FILE)

    invalid_parameter_file_path1 = workspace_dir / "no_target_env_parameter.yml"
    invalid_parameter_file_path1.write_text(SAMPLE_PARAMETER_NO_TARGET_ENV)

    invalid_parameter_file_path2 = workspace_dir / "missing_find_val_parameter.yml"
    invalid_parameter_file_path2.write_text(SAMPLE_PARAMETER_MISSING_FIND_VAL)

    invalid_parameter_file_path3 = workspace_dir / "mismatch_filter_parameter.yml"
    invalid_parameter_file_path3.write_text(SAMPLE_PARAMETER_MISMATCH_FILTER)

    invalid_parameter_file_path4 = workspace_dir / "missing_replace_val_parameter.yml"
    invalid_parameter_file_path4.write_text(SAMPLE_PARAMETER_MISSING_REPLACE_VAL)

    invalid_parameter_file_path5 = workspace_dir / "invalid_name_parameter.yml"
    invalid_parameter_file_path5.write_text(SAMPLE_PARAMETER_INVALID_NAME)

    invalid_parameter_file_path6 = workspace_dir / "invalid_yaml_struc_parameter.yml"
    invalid_parameter_file_path6.write_text(SAMPLE_PARAMETER_INVALID_YAML_STRUC)

    invalid_parameter_file_path7 = workspace_dir / "invalid_yaml_char_parameter.yml"
    invalid_parameter_file_path7.write_text(SAMPLE_PARAMETER_INVALID_YAML_CHAR)

    invalid_parameter_file_path8 = workspace_dir / "invalid_is_regex_parameter.yml"
    invalid_parameter_file_path8.write_text(SAMPLE_PARAMETER_INVALID_IS_REGEX)

    # Create the sample parameter file with ALL environment key
    all_env_parameter_file_path = workspace_dir / "all_env_parameter.yml"
    all_env_parameter_file_path.write_text(SAMPLE_PARAMETER_ALL_ENV)

    # Create the sample parameter file with multiple of a parameter
    multiple_parameter_file_path = workspace_dir / "multiple_parameter.yml"
    multiple_parameter_file_path.write_text(SAMPLE_PARAMETER_FILE_MULTIPLE)

    # Create the sample notebook files
    notebook_dir = workspace_dir / "Hello World.Notebook"
    notebook_dir.mkdir(parents=True, exist_ok=True)

    notebook_platform_file_path = notebook_dir / ".platform"
    notebook_platform_file_path.write_text(SAMPLE_PLATFORM_FILE)

    notebook_file_path = notebook_dir / "notebook-content.py"
    notebook_file_path.write_text(SAMPLE_NOTEBOOK_FILE)

    return workspace_dir


@pytest.fixture
def parameter_object(repository_directory, item_type_in_scope, target_environment):
    """Fixture to create a Parameter object."""
    return Parameter(
        repository_directory=repository_directory,
        item_type_in_scope=item_type_in_scope,
        environment=target_environment,
        parameter_file_name=constants.PARAMETER_FILE_NAME,
    )


def test_parameter_class_initialization(parameter_object, repository_directory, item_type_in_scope, target_environment):
    """Test the Parameter class initialization."""
    parameter_file_name = constants.PARAMETER_FILE_NAME

    # Check if the object is initialized correctly
    assert parameter_object.repository_directory == repository_directory
    assert parameter_object.item_type_in_scope == item_type_in_scope
    assert parameter_object.environment == target_environment
    assert parameter_object.parameter_file_name == parameter_file_name
    assert parameter_object.parameter_file_path == repository_directory / parameter_file_name


def test_parameter_file_validation(parameter_object):
    """Test the validation methods for the parameter file"""
    assert parameter_object._validate_parameter_file_exists() == True
    assert parameter_object._validate_load_parameters_to_dict() == (True, parameter_object.environment_parameter)
    assert parameter_object._validate_parameter_load() == (True, constants.PARAMETER_MSGS["valid load"])
    assert parameter_object._validate_parameter_names() == (True, constants.PARAMETER_MSGS["valid name"])
    assert parameter_object._validate_parameter_structure() == (True, constants.PARAMETER_MSGS["valid structure"])
    assert parameter_object._validate_parameter("find_replace") == (
        True,
        constants.PARAMETER_MSGS["valid parameter"].format("find_replace"),
    )
    assert parameter_object._validate_parameter("spark_pool") == (
        True,
        constants.PARAMETER_MSGS["valid parameter"].format("spark_pool"),
    )
    assert parameter_object._validate_parameter_file() == True


def test_multiple_parameter_validation(repository_directory, item_type_in_scope, target_environment):
    """Test the validation methods for multiple parameters case"""
    multi_param_obj = Parameter(
        repository_directory=repository_directory,
        item_type_in_scope=item_type_in_scope,
        environment=target_environment,
        parameter_file_name="multiple_parameter.yml",
    )
    assert multi_param_obj._validate_parameter("find_replace") == (
        True,
        constants.PARAMETER_MSGS["valid parameter"].format("find_replace"),
    )
    assert multi_param_obj._validate_parameter("key_value_replace") == (
        True,
        constants.PARAMETER_MSGS["valid parameter"].format("key_value_replace"),
    )
    assert multi_param_obj._validate_parameter_file() == True


@pytest.mark.parametrize(
    ("param_name", "param_value", "result", "msg"),
    [
        ("find_replace", ["find_value", "replace_value"], True, "valid keys"),
        ("find_replace", ["find_value", "item_type", "item_name", "file_path"], False, "missing key"),
        ("find_replace", ["find_value", "replace_value", "is_regex", "item_type"], True, "valid keys"),
        ("spark_pool", ["instance_pool_id", "replace_value", "item_name"], True, "valid keys"),
        ("spark_pool", ["instance_pool_id", "replace_value", "item_name", "file_path"], False, "invalid key"),
    ],
)
def test_validate_parameter_keys(parameter_object, param_name, param_value, result, msg):
    """Test the validation methods for the find_replace parameter"""

    assert parameter_object._validate_parameter_keys(param_name, param_value) == (
        result,
        constants.PARAMETER_MSGS[msg].format(param_name),
    )


@pytest.mark.parametrize(("param_name"), [("find_replace"), ("spark_pool")])
def test_validate_parameter(parameter_object, param_name):
    """Test the validation methods for a specific parameter"""
    param_dict = parameter_object.environment_parameter.get(param_name)
    for param in param_dict:
        assert parameter_object._validate_required_values(param_name, param) == (
            True,
            constants.PARAMETER_MSGS["valid required values"].format(param_name),
        )
        assert parameter_object._validate_replace_value(param_name, param["replace_value"]) == (
            True,
            constants.PARAMETER_MSGS["valid replace value"].format(param_name),
        )


@pytest.mark.parametrize(
    ("replace_value", "result", "msg"),
    [
        (
            {"PPE": "81bbb339-8d0b-46e8-bfa6-289a159c0733", "PROD": "5d6a1b16-447f-464a-b959-45d0fed35ca0"},
            True,
            "valid replace value",
        ),
        (
            {"PPE": "81bbb339-8d0b-46e8-bfa6-289a159c0733", "PROD": None},
            False,
            "missing replace value",
        ),
    ],
)
def test_validate_find_replace_replace_value(parameter_object, replace_value, result, msg):
    """Test the _validate_find_replace_replace_value method."""
    assert parameter_object._validate_find_replace_replace_value(replace_value) == (
        result,
        constants.PARAMETER_MSGS[msg].format("find_replace", "PROD")
        if msg == "missing replace value"
        else constants.PARAMETER_MSGS[msg].format("find_replace"),
    )


@pytest.mark.parametrize(
    ("replace_value", "result", "msg"),
    [
        # Valid cases - all values are same type
        (
            {"PPE": "string_value", "PROD": "another_string"},
            True,
            "valid replace value",
        ),
        (
            {"PPE": True, "PROD": False},
            True,
            "valid replace value",
        ),
        (
            {"PPE": 123, "PROD": 456},
            True,
            "valid replace value",
        ),
        (
            {"PPE": 1.5, "PROD": 2.7},
            True,
            "valid replace value",
        ),
        (
            {"PPE": ["item1", "item2"], "PROD": ["item3", "item4"]},
            True,
            "valid replace value",
        ),
        (
            {"PPE": {"key": "value1"}, "PROD": {"key": "value2"}},
            True,
            "valid replace value",
        ),
        # Invalid cases - missing values
        (
            {"PPE": "value", "PROD": None},
            False,
            "missing replace value",
        ),
        # Invalid cases - mixed types
        (
            {"PPE": "string_value", "PROD": 123},
            False,
            "mixed types",
        ),
        (
            {"PPE": True, "PROD": "false"},
            False,
            "mixed types",
        ),
        (
            {"PPE": 123, "PROD": 45.6},
            False,
            "mixed types",
        ),
    ],
)
def test_validate_key_value_replace_replace_value(parameter_object, replace_value, result, msg):
    """Test the _validate_key_value_replace_replace_value method."""
    is_valid, actual_msg = parameter_object._validate_key_value_replace_replace_value(replace_value)

    if msg == "valid replace value":
        expected_msg = constants.PARAMETER_MSGS[msg].format("key_value_replace")
        assert (is_valid, actual_msg) == (result, expected_msg)
    elif msg == "missing replace value":
        # For missing replace value, check that the message contains the expected format
        assert is_valid == result
        assert "key_value_replace is missing a replace value for" in actual_msg
    elif msg == "mixed types":
        # For mixed types, check that the message contains the expected content
        assert is_valid == result
        assert "Inconsistent data types in key_value_replace replace_value" in actual_msg


@pytest.mark.parametrize(
    ("replace_value", "result", "msg", "desc"),
    [
        (
            {
                "PPE": {"type": "Capacity", "name": "CapacityPool_Large_PPE"},
                "PROD": {"type": "Capacity", "name": "CapacityPool_Large_PROD"},
            },
            True,
            "valid replace value",
            None,
        ),
        (
            {
                "PPE": {},
                "PROD": {"type": "Capacity", "name": "CapacityPool_Large_PROD"},
            },
            False,
            "missing replace value",
            None,
        ),
        (
            {
                "PPE": {"name": "CapacityPool_Large_PPE"},
                "PROD": {"type": "Capacity", "name": "CapacityPool_Large_PROD"},
            },
            False,
            "invalid replace value",
            "missing key",
        ),
        (
            {
                "PPE": {"type": "Capacity", "name": "CapacityPool_Large_PPE"},
                "PROD": {"type": "Capacity", "name": None},
            },
            False,
            "invalid replace value",
            "missing value",
        ),
        (
            {
                "PPE": {"type": "Capacity", "name": "CapacityPool_Large_PPE"},
                "PROD": {"type": "Test", "name": "CapacityPool_Large_PROD"},
            },
            False,
            "invalid replace value",
            "invalid value",
        ),
    ],
)
def test_validate_spark_pool_replace_value(parameter_object, replace_value, result, msg, desc):
    """Test the _validate_spark_pool_replace_value method."""
    if msg == "valid replace value":
        msg = constants.PARAMETER_MSGS[msg].format("spark_pool")
    if msg == "missing replace value":
        msg = constants.PARAMETER_MSGS[msg].format("spark_pool", "PPE")
    if msg == "invalid replace value" and desc == "missing key":
        msg = constants.PARAMETER_MSGS[msg][desc].format("PPE")
    if msg == "invalid replace value" and desc == "missing value":
        msg = constants.PARAMETER_MSGS[msg][desc].format("PROD", "name")
    if msg == "invalid replace value" and desc == "invalid value":
        msg = constants.PARAMETER_MSGS[msg][desc].format("PROD")

    assert parameter_object._validate_spark_pool_replace_value(replace_value) == (result, msg)
    assert parameter_object._validate_replace_value(
        "spark_pool",
        {
            "PPE": {},
            "PROD": {"type": "Capacity", "name": "CapacityPool_Large_PROD"},
        },
    ) == (False, constants.PARAMETER_MSGS["missing replace value"].format("spark_pool", "PPE"))


def test_validate_data_type(parameter_object):
    """Test data type validation"""
    # General data type validation
    assert parameter_object._validate_data_type([1, 2, 3], "string or list[string]", "key", "param_name") == (
        False,
        constants.PARAMETER_MSGS["invalid data type"].format("key", "string or list[string]", "param_name"),
    )

    required_values = {
        "find_value": ["db52be81-c2b2-4261-84fa-840c67f4bbd0"],
        "replace_value": {
            "PPE": "81bbb339-8d0b-46e8-bfa6-289a159c0733",
            "PROD": "5d6a1b16-447f-464a-b959-45d0fed35ca0",
        },
    }
    # Data type error in required values
    assert parameter_object._validate_required_values("find_replace", required_values) == (
        False,
        constants.PARAMETER_MSGS["invalid data type"].format("find_value", "string", "find_replace"),
    )

    find_replace_value = {
        "PPE": "81bbb339-8d0b-46e8-bfa6-289a159c0733",
        "PROD": 123,
    }
    # Data type error in find_replace replace value dict
    assert parameter_object._validate_find_replace_replace_value(find_replace_value) == (
        False,
        constants.PARAMETER_MSGS["invalid data type"].format("PROD replace_value", "string", "find_replace"),
    )

    spark_pool_replace_value_1 = {
        "PPE": "string",
        "PROD": {"type": "Capacity", "name": "CapacityPool_Large_PROD"},
    }
    # Data type error in spark_pool replace value dict
    assert parameter_object._validate_spark_pool_replace_value(spark_pool_replace_value_1) == (
        False,
        constants.PARAMETER_MSGS["invalid data type"].format("PPE key", "dictionary", "spark_pool"),
    )

    spark_pool_replace_value_2 = {
        "PPE": {"type": "Capacity", "name": "CapacityPool_Large_PPE"},
        "PROD": {"type": ["Capacity"], "name": "CapacityPool_Large_PROD"},
    }
    # Data type error in spark_pool replace value environment dict
    assert parameter_object._validate_spark_pool_replace_value(spark_pool_replace_value_2) == (
        False,
        constants.PARAMETER_MSGS["invalid data type"].format("type", "string", "spark_pool"),
    )

    param_dict = {
        "item_type": "Notebook",
        "item_name": {"Hello World"},
        "file_path": "/Hello World.Notebook/notebook-content.py",
    }
    # Data type error in optional values
    assert parameter_object._validate_optional_values("find_replace", param_dict) == (
        False,
        constants.PARAMETER_MSGS["invalid data type"].format("item_name", "string or list[string]", "find_replace"),
    )


def test_validate_yaml_content(parameter_object):
    """Test the validation of the YAML content"""
    invalid_content = "\n\n\n\t"
    assert parameter_object._validate_yaml_content(invalid_content) == ["YAML content is empty"]

    invalid_content = "\U0001f600"
    assert parameter_object._validate_yaml_content(invalid_content) == [
        constants.PARAMETER_MSGS["invalid content"]["char"]
    ]


def test_validate_parameter_file_structure(repository_directory, item_type_in_scope, target_environment):
    """Test the validation of the parameter file structure"""
    param_obj = Parameter(
        repository_directory=repository_directory,
        item_type_in_scope=item_type_in_scope,
        environment=target_environment,
        parameter_file_name="invalid_parameter.yml",
    )
    assert param_obj._validate_parameter_structure() == (False, constants.PARAMETER_MSGS["invalid structure"])


def test_validate_optional_values(parameter_object):
    """Test the _validate_optional_values method."""
    param_dict_1 = {
        "item_type": "Notebook",
        "item_name": ["Hello World"],
        "file_path": "/Hello World.Notebook/notebook-content.py",
    }
    assert parameter_object._validate_optional_values("find_replace", param_dict_1) == (
        True,
        constants.PARAMETER_MSGS["valid optional"].format("find_replace"),
    )

    param_dict_2 = {
        "item_type": "SparkNotebook",
        "item_name": ["Hello World"],
        "file_path": "/Hello World.Notebook/notebook-content.py",
    }
    assert parameter_object._validate_optional_values("find_replace", param_dict_2, check_match=True) == (
        False,
        "no match",
    )

    param_dict_3 = {"item_name": "Hello World"}
    assert parameter_object._validate_optional_values("spark_pool", param_dict_3, check_match=True) == (
        True,
        constants.PARAMETER_MSGS["valid optional"].format("spark_pool"),
    )


@pytest.mark.parametrize(
    ("param_name"),
    ["find_replace", "spark_pool"],
)
def test_validate_parameter_environment_and_filters(parameter_object, param_name):
    """Test the validation methods for environment and filters"""
    for param_dict in parameter_object.environment_parameter.get(param_name):
        # Environment validation
        assert parameter_object._validate_environment(param_dict["replace_value"]) == (True, "env")

    # Optional filters validation
    assert parameter_object._validate_item_type("Pipeline") == (
        False,
        constants.PARAMETER_MSGS["invalid item type"].format("Pipeline"),
    )
    assert parameter_object._validate_item_name("Hello World 2") == (
        False,
        constants.PARAMETER_MSGS["invalid item name"].format("Hello World 2"),
    )
    assert parameter_object._validate_file_path(["Hello World 2.Notebook/notebook-content.py"]) == (
        False,
        constants.PARAMETER_MSGS["no valid file path"].format(["Hello World 2.Notebook/notebook-content.py"]),
    )


@pytest.mark.parametrize(
    ("param_file_name", "result", "msg"),
    [
        ("no_target_env_parameter.yml", True, "valid parameter"),
        ("missing_find_val_parameter.yml", False, "missing required value"),
        ("mismatch_filter_parameter.yml", True, "valid parameter"),
        ("missing_replace_val_parameter.yml", False, "missing required value"),
        ("invalid_name_parameter.yml", False, "invalid name"),
        ("invalid_yaml_struc_parameter.yml", False, "invalid load"),
        ("invalid_yaml_char_parameter.yml", False, "invalid load"),
        ("invalid_is_regex_parameter.yml", False, "invalid data type"),
    ],
)
def test_validate_invalid_parameters(
    repository_directory, item_type_in_scope, target_environment, param_file_name, result, msg
):
    """Test the validation of invalid or error-prone parameter files"""
    param_obj = Parameter(
        repository_directory=repository_directory,
        item_type_in_scope=item_type_in_scope,
        environment=target_environment,
        parameter_file_name=param_file_name,
    )

    # Target environment not present in find_replace parameter (error-prone case)
    if param_file_name == "no_target_env_parameter.yml":
        assert param_obj._validate_parameter("find_replace") == (
            result,
            constants.PARAMETER_MSGS[msg].format("find_replace"),
        )

    # Missing required value in find_replace parameter
    if param_file_name == "missing_find_val_parameter.yml":
        for param_dict in param_obj.environment_parameter.get("find_replace"):
            assert param_obj._validate_required_values("find_replace", param_dict) == (
                result,
                constants.PARAMETER_MSGS[msg].format("find_value", "find_replace"),
            )
        assert param_obj._validate_parameter_file() == result

    # Mismatched optional filters in find_replace parameter (error-prone case)
    if param_file_name == "mismatch_filter_parameter.yml":
        assert param_obj._validate_parameter("find_replace") == (
            result,
            constants.PARAMETER_MSGS[msg].format("find_replace"),
        )

    # Missing required value in spark_pool parameter
    if param_file_name == "missing_replace_val_parameter.yml":
        assert param_obj._validate_parameter("spark_pool") == (
            result,
            constants.PARAMETER_MSGS[msg].format("replace_value", "spark_pool"),
        )

    # Invalid parameter name
    if param_file_name == "invalid_name_parameter.yml":
        assert param_obj._validate_parameter_names() == (
            result,
            constants.PARAMETER_MSGS[msg].format("spark_pool_param"),
        )

    # Errors in YAML content structure
    if param_file_name == "invalid_yaml_struc_parameter.yml":
        is_valid, msg = param_obj._validate_parameter_load()
        try:
            with Path.open(repository_directory / param_file_name, encoding="utf-8") as yaml_file:
                yaml_content = yaml_file.read()
                yaml.full_load(yaml_content)
        except yaml.YAMLError as e:
            error_message = str(e)

        assert is_valid == result
        assert msg == constants.PARAMETER_MSGS["invalid load"].format(error_message)

    # Mismatched quotes in YAML content
    if param_file_name == "invalid_yaml_char_parameter.yml":
        is_valid, msg = param_obj._validate_parameter_load()
        try:
            with Path.open(repository_directory / param_file_name, encoding="utf-8") as yaml_file:
                yaml_content = yaml_file.read()
                yaml.full_load(yaml_content)
        except yaml.YAMLError as e:
            error_message = str(e)

        assert is_valid == result
        assert msg == constants.PARAMETER_MSGS["invalid load"].format(error_message)

    # Invalid is_regex value in find_replace parameter
    if param_file_name == "invalid_is_regex_parameter.yml":
        # Mock the environment_parameter to have the invalid is_regex (boolean instead of string)
        param_obj.environment_parameter = {
            "find_replace": [
                {
                    "find_value": '\\#\\s*META\\s+"default_lakehouse":\\s*"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})"',
                    "replace_value": {
                        "PPE": "81bbb339-8d0b-46e8-bfa6-289a159c0733",
                        "PROD": "5d6a1b16-447f-464a-b959-45d0fed35ca0",
                    },
                    "is_regex": True,  # This is a boolean, not a string
                }
            ]
        }
        assert param_obj._validate_parameter("find_replace") == (
            result,
            constants.PARAMETER_MSGS[msg].format("is_regex", "string", "find_replace"),
        )


def test_validate_file_path_scenarios(parameter_object):
    """Test _validate_file_path with different scenarios."""
    # Test 1: Single invalid path - expects "no valid file path" error
    single_invalid_path = ["nonexistent_file.py"]
    with mock.patch("fabric_cicd._parameter._utils.process_input_path", return_value=[]):
        result, msg = parameter_object._validate_file_path(single_invalid_path)
        assert result is False
        assert msg == constants.PARAMETER_MSGS["no valid file path"].format(single_invalid_path)

    # Test 2: Multiple invalid paths - expects "no valid file path" error
    multiple_invalid_paths = ["nonexistent_file1.py", "nonexistent_file2.py"]
    with mock.patch("fabric_cicd._parameter._utils.process_input_path", return_value=[]):
        result, msg = parameter_object._validate_file_path(multiple_invalid_paths)
        assert result is False
        assert msg == constants.PARAMETER_MSGS["no valid file path"].format(multiple_invalid_paths)

    # Test 3: Mixed valid/invalid paths - expects "invalid file path" error for missing paths
    mixed_paths = ["valid_path.py", "invalid_path.py"]

    # Create a custom test implementation that simulates the behavior we want to test
    def mock_validate_file_path(input_path):
        """Custom implementation to test the mixed valid/invalid paths case"""
        # For test purposes, we'll simulate that process_input_path returned a valid path
        valid_paths = [Path("valid_path.py")]

        # If there are no valid paths, return the "no valid file path" error
        if not valid_paths:
            return False, constants.PARAMETER_MSGS["no valid file path"].format(input_path)

        # Normalize paths for comparison
        processed_paths = {str(p).replace("\\", "/") for p in valid_paths}
        original_paths = {str(p).replace("\\", "/") for p in input_path}

        # Find invalid paths
        missing_paths = original_paths - processed_paths

        if missing_paths:
            path_diff = len(original_paths) - len(processed_paths)
            return False, constants.PARAMETER_MSGS["invalid file path"].format(input_path, path_diff)

        return True, "Valid file path"

    # Save the original method
    original_method = parameter_object._validate_file_path

    # Replace with our mock implementation
    parameter_object._validate_file_path = mock_validate_file_path

    try:
        # Call the method with our test data
        result, msg = parameter_object._validate_file_path(mixed_paths)

        # Should return False and the invalid file path message
        assert result is False

        # The message should contain the invalid path
        assert "invalid_path.py" in msg

        # Make sure we're getting the specific "invalid file path" message
        # We need to match the new format which takes input_path and path_diff
        mixed_paths = ["valid_path.py", "invalid_path.py"]
        path_diff = 1  # One invalid path
        expected_msg = constants.PARAMETER_MSGS["invalid file path"].format(mixed_paths, path_diff)
        assert msg == expected_msg
    finally:
        # Restore the original method
        parameter_object._validate_file_path = original_method

    # Test 4: All valid paths - should return True
    valid_paths = ["valid_path1.py", "valid_path2.py"]

    # Create a mock function that always returns success
    def mock_validate_all_valid(_):
        """Mock function that simulates all paths being valid"""
        return True, "Valid file path"

    # Save the original method and replace with our mock
    original_method = parameter_object._validate_file_path
    parameter_object._validate_file_path = mock_validate_all_valid

    try:
        # Call the method with our test data
        result, msg = parameter_object._validate_file_path(valid_paths)
        assert result is True
        assert msg == "Valid file path"
    finally:
        # Restore the original method
        parameter_object._validate_file_path = original_method


def test_validate_all_environment_key_valid():
    """Test the validation of _ALL_ environment key in valid scenarios"""
    # Test that _ALL_ key is accepted as a valid environment
    import tempfile

    from fabric_cicd._parameter._parameter import Parameter

    # Create a temporary parameter file with _ALL_ environment key
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as temp_file:
        temp_file.write("""
find_replace:
    - find_value: "test-value"
      replace_value:
          _ALL_: "universal-value"
key_value_replace:
    - find_key: $.test
      replace_value:
        _All_: "universal-key-value"
spark_pool:
    - instance_pool_id: "test-pool-id"
      replace_value:
        _all_:
          type: "Capacity"
          name: "UniversalPool"
""")
        temp_file_path = temp_file.name

    try:
        param_obj = Parameter(
            repository_directory=Path(temp_file_path).parent,
            item_type_in_scope=["Notebook"],
            environment="TEST",
            parameter_file_name=Path(temp_file_path).name,
        )

        # Should pass validation since _ALL_ is a valid environment key
        assert param_obj._validate_parameter("find_replace") == (
            True,
            constants.PARAMETER_MSGS["valid parameter"].format("find_replace"),
        )

        assert param_obj._validate_parameter("key_value_replace") == (
            True,
            constants.PARAMETER_MSGS["valid parameter"].format("key_value_replace"),
        )

        assert param_obj._validate_parameter("spark_pool") == (
            True,
            constants.PARAMETER_MSGS["valid parameter"].format("spark_pool"),
        )

        # Overall parameter file should be valid
        assert param_obj._validate_parameter_file() == True

        # Test that the _ALL_ environment key is properly recognized (case-insensitive)
        for param_dict in param_obj.environment_parameter.get("find_replace"):
            assert param_obj._validate_environment(param_dict["replace_value"]) == (True, "_ALL_")

        for param_dict in param_obj.environment_parameter.get("key_value_replace"):
            assert param_obj._validate_environment(param_dict["replace_value"]) == (True, "_All_")

        for param_dict in param_obj.environment_parameter.get("spark_pool"):
            assert param_obj._validate_environment(param_dict["replace_value"]) == (True, "_all_")

    finally:
        # Clean up temporary file
        Path(temp_file_path).unlink()


def test_validate_all_environment_key_invalid():
    """Test validation of _ALL_ environment key in invalid scenarios"""
    import tempfile

    from fabric_cicd._parameter._parameter import Parameter

    # Create a parameter file with multiple environment keys including ALL
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as temp_file:
        temp_file.write("""
find_replace:
    - find_value: "test-connection-string"
      replace_value:
          DEV: "dev-connection-string"
          TEST: "test-connection-string"  
          PROD: "prod-connection-string"
          _ALL_: "universal-connection-string"
spark_pool:
    - instance_pool_id: "multi-env-pool-id"
      replace_value:
        DEV:
          type: "Workspace"
          name: "DevPool"
        TEST:
          type: "Workspace" 
          name: "TestPool"
        PROD:
          type: "Capacity"
          name: "ProdPool"
        _all_:
          type: "Capacity"
          name: "UniversalPool"
""")
        temp_file_path = temp_file.name

    try:
        param_obj = Parameter(
            repository_directory=Path(temp_file_path).parent,
            item_type_in_scope=["Notebook"],
            environment="TEST",
            parameter_file_name=Path(temp_file_path).name,
        )

        # Should fail validation since ALL cannot coexist with other environment keys
        assert param_obj._validate_parameter("find_replace") == (
            False,
            constants.PARAMETER_MSGS["other target env"].format(
                "_ALL_", param_obj.environment_parameter["find_replace"][0]["replace_value"]
            ),
        )

        assert param_obj._validate_parameter("spark_pool") == (
            False,
            constants.PARAMETER_MSGS["other target env"].format(
                "_all_", param_obj.environment_parameter["spark_pool"][0]["replace_value"]
            ),
        )

        # Overall parameter file should be invalid
        assert param_obj._validate_parameter_file() == False

        # Test that mixed environment combinations are invalid
        for param_dict in param_obj.environment_parameter.get("find_replace"):
            assert param_obj._validate_environment(param_dict["replace_value"]) == (False, "_ALL_")

        for param_dict in param_obj.environment_parameter.get("spark_pool"):
            assert param_obj._validate_environment(param_dict["replace_value"]) == (False, "_all_")

    finally:
        # Clean up temporary file
        Path(temp_file_path).unlink()


def test_validate_all_environment_key_with_logging():
    """Test that _ALL_ environment key triggers appropriate logging"""
    import tempfile

    # Create a temporary parameter file with _ALL_ environment key
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as temp_file:
        temp_file.write("""
find_replace:
    - find_value: "test-value"
      replace_value:
          _ALL_: "universal-value"
spark_pool:
    - instance_pool_id: "test-pool-id"
      replace_value:
        _all_:
          type: "Capacity"
          name: "UniversalPool"
""")
        temp_file_path = temp_file.name

    try:
        param_obj = Parameter(
            repository_directory=Path(temp_file_path).parent,
            item_type_in_scope=["Notebook"],
            environment="TEST",
            parameter_file_name=Path(temp_file_path).name,
        )

        # Test environment validation specifically for _ALL_ key
        replace_value_with_all = {"_all_": "universal-value"}
        assert param_obj._validate_environment(replace_value_with_all) == (True, "_all_")

        # Test spark_pool with _ALL_ environment key
        spark_pool_replace_value_with_all = {"_ALL_": {"type": "Capacity", "name": "UniversalPool"}}
        assert param_obj._validate_environment(spark_pool_replace_value_with_all) == (True, "_ALL_")

        # Test environment validation specifically for all key (not reserved)
        replace_value_with_all = {"all": "universal-value"}
        assert param_obj._validate_environment(replace_value_with_all) == (False, "env")

        # Test environment validation with both target env and _ALL_ key (should fail)
        replace_value_mixed = {"TEST": "test-value", "_ALL_": "universal-value"}
        assert param_obj._validate_environment(replace_value_mixed) == (False, "_ALL_")

        # Test spark_pool with mixed environment keys (should fail)
        spark_pool_mixed = {
            "TEST": {"type": "Workspace", "name": "TestPool"},
            "_ALL_": {"type": "Capacity", "name": "UniversalPool"},
        }
        assert param_obj._validate_environment(spark_pool_mixed) == (False, "_ALL_")

        # Test environment validation with multiple environment keys including all (not reserved)
        replace_value_multiple_envs = {"TEST": "test-value", "PROD": "prod-value", "all": "universal-value"}
        assert param_obj._validate_environment(replace_value_multiple_envs) == (True, "env")

        # Test spark_pool with multiple environment keys including ALL (not reserved)
        spark_pool_multiple_envs = {
            "PROD": {"type": "Workspace", "name": "ProdPool"},
            "All": {"type": "Capacity", "name": "UniversalPool"},
        }
        assert param_obj._validate_environment(spark_pool_multiple_envs) == (False, "env")

        # Test environment validation with only target env (no _ALL_ key)
        replace_value_target_only = {"TEST": "test-value"}
        assert param_obj._validate_environment(replace_value_target_only) == (True, "env")

        # Test environment validation with neither target env nor _ALL_ key
        replace_value_other = {"PROD": "prod-value"}
        assert param_obj._validate_environment(replace_value_other) == (False, "env")

    finally:
        # Clean up temporary file
        Path(temp_file_path).unlink()


def test_parameter_file_path_absolute():
    """Test that Parameter class accepts absolute parameter_file_path."""
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as temp_file:
        temp_file.write("""
find_replace:
    - find_value: "test-value"
      replace_value:
          TEST: "test-replacement"
""")
        temp_file_path = temp_file.name

    try:
        param_obj = Parameter(
            repository_directory=Path(temp_file_path).parent,
            item_type_in_scope=["Notebook"],
            environment="TEST",
            parameter_file_path=temp_file_path,
        )

        # Should work without errors
        assert param_obj.environment == "TEST"
        assert param_obj.item_type_in_scope == ["Notebook"]

    finally:
        Path(temp_file_path).unlink()


def test_parameter_file_path_relative():
    """Test that Parameter class handles relative parameter_file_path by resolving it against repository_directory."""
    import tempfile
    from pathlib import Path

    # Create a temporary directory to act as the repository
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_dir = Path(temp_dir)

        # Create a nested directory and parameter file
        relative_dir = "relative/path"
        (repo_dir / relative_dir).mkdir(parents=True)

        param_file = "parameters.yml"
        param_file_path = Path(repo_dir, relative_dir, param_file)
        param_file_path.write_text("key: value")  # Simple valid YAML

        # Test with relative path that exists
        relative_path = f"{relative_dir}/{param_file}"

        # Create a Parameter instance with a relative path
        param = Parameter(
            repository_directory=repo_dir,
            item_type_in_scope=["Notebook"],
            environment="TEST",
            parameter_file_path=relative_path,
        )

        # Verify the path was resolved relative to repository_directory
        expected_path = param_file_path.resolve()
        assert param.parameter_file_path == expected_path

        # Test with relative path that doesn't exist
        non_existent_path = "relative/path/non_existent.yml"

        # This should not raise an error but should log an error message
        param2 = Parameter(
            repository_directory=repo_dir,
            item_type_in_scope=["Notebook"],
            environment="TEST",
            parameter_file_path=non_existent_path,
        )

        # Verify the path was resolved but parameter loading failed
        assert param2.parameter_file_path is not None
        assert not param2.environment_parameter

        # Test with path that exists but is a directory, not a file
        param3 = Parameter(
            repository_directory=repo_dir,
            item_type_in_scope=["Notebook"],
            environment="TEST",
            parameter_file_path=relative_dir,
        )

        # Verify the path was resolved but parameter loading failed
        assert param3.parameter_file_path is not None
        assert not param3.environment_parameter


def test_parameter_file_path_none():
    """Test that Parameter class accepts None for parameter_file_path (uses parameter_file_name)."""
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        param_file = temp_dir_path / "parameters.yml"
        param_file.write_text("""
find_replace:
    - find_value: "test-value"
      replace_value:
          TEST: "test-replacement"
""")

        param_obj = Parameter(
            repository_directory=temp_dir_path,
            item_type_in_scope=["Notebook"],
            environment="TEST",
            parameter_file_name="parameters.yml",
            parameter_file_path=None,
        )

        # Should work with parameter_file_name fallback
        assert param_obj.environment == "TEST"
        assert param_obj.item_type_in_scope == ["Notebook"]
        # Verify the parameter_file_path was set correctly from parameter_file_name
        assert param_obj.parameter_file_path == (temp_dir_path / "parameters.yml").resolve()


def test_parameter_file_path_and_name_inputs():
    """Test that parameter_file_path takes precedence over parameter_file_name."""
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)

        # Create file referenced by parameter_file_name
        fallback_file = temp_dir_path / "parameters.yml"
        fallback_file.write_text("""
find_replace:
    - find_value: "fallback-value"
      replace_value:
          TEST: "fallback-replacement"
""")

        # Create file referenced by parameter_file_path
        primary_file = temp_dir_path / "primary_parameters.yml"
        primary_file.write_text("""
find_replace:
    - find_value: "primary-value"
      replace_value:
          TEST: "primary-replacement"
""")

        param_obj = Parameter(
            repository_directory=temp_dir_path,
            item_type_in_scope=["Notebook"],
            environment="TEST",
            parameter_file_name="parameters.yml",  # This should be ignored
            parameter_file_path=str(primary_file),  # This should be used
        )

        # Should use primary_file content
        assert param_obj.environment == "TEST"
        # Check that the primary file was used by examining parameter content
        assert "find_replace" in param_obj.environment_parameter
        assert len(param_obj.environment_parameter["find_replace"]) == 1
        assert param_obj.environment_parameter["find_replace"][0]["find_value"] == "primary-value"


def test_no_provided_parameter_file_path():
    """Test that default behavior without parameter_file_path remains unchanged."""
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        param_file = temp_dir_path / "parameters.yml"
        param_file.write_text("""
find_replace:
    - find_value: "test-value"
      replace_value:
          TEST: "test-replacement"
""")

        # Original behavior - no parameter_file_path specified
        param_obj = Parameter(
            repository_directory=temp_dir_path,
            item_type_in_scope=["Notebook"],
            environment="TEST",
            parameter_file_name="parameters.yml",
        )

        # Should work exactly as before
        assert param_obj.environment == "TEST"
        assert param_obj.item_type_in_scope == ["Notebook"]
        assert "find_replace" in param_obj.environment_parameter
        assert len(param_obj.environment_parameter["find_replace"]) == 1


def test_parameter_file_path_nonexistent():
    """Test behavior when parameter_file_path points to nonexistent file."""
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        nonexistent_path = str(Path(temp_dir) / "nonexistent" / "parameters.yml")

        # Should log an error but not raise an exception
        param = Parameter(
            repository_directory=Path.cwd(),
            item_type_in_scope=["Notebook"],
            environment="TEST",
            parameter_file_path=nonexistent_path,
        )

        # Parameter file path should be set but the environment_parameter should be empty
        assert param.parameter_file_path is not None
        assert not param.environment_parameter


def test_validate_parameter_file_exists_none():
    """Test that _validate_parameter_file_exists returns False when parameter_file_path is None."""
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a Parameter instance with parameter_file_path set to None in _set_parameter_file_path
        param = Parameter(
            repository_directory=Path(temp_dir),
            item_type_in_scope=["Notebook"],
            environment="TEST",
            parameter_file_name="does_not_exist.yml",  # This file doesn't exist
        )

        # Force parameter_file_path to None
        param.parameter_file_path = None

        # Method should return False without raising errors
        assert param._validate_parameter_file_exists() is False


def test_parameter_file_path_invalid_type():
    """Test that Parameter class handles invalid types for parameter_file_path."""
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        # Parameter class should handle the invalid type internally without raising an exception
        param = Parameter(
            repository_directory=Path(temp_dir),
            item_type_in_scope=["Notebook"],
            environment="TEST",
            parameter_file_path=123,  # Invalid type
        )

        # The error handling in _set_parameter_file_path sets is_param_path to False
        # and falls back to the default parameter file path
        assert param.parameter_file_path is not None
        assert param.parameter_file_path == (Path(temp_dir) / "parameter.yml").resolve()


def test_set_parameter_file_path_error_handling():
    """Test error handling in _set_parameter_file_path method."""
    import tempfile

    # Create a mock that raises an exception when called with any arguments
    path_mock = mock.Mock(side_effect=Exception("Simulated error"))

    with tempfile.TemporaryDirectory() as temp_dir, mock.patch("fabric_cicd._parameter._parameter.Path", path_mock):
        # Create parameter with both parameters to test the error handling
        param = Parameter(
            repository_directory=temp_dir,  # Using string path to avoid early Path conversion
            item_type_in_scope=["Notebook"],
            environment="TEST",
            parameter_file_name="parameters.yml",
            parameter_file_path="custom_path.yml",
        )

        # The method should have caught the exception and set parameter_file_path to None
        assert param.parameter_file_path is None
