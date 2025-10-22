# tests/test_utils.py
import pytest
import importlib
from opticedge_cloud_utils.merge import _deep_get, _compute_new_value_from_delta_or_data, detect_field_changes

MODULE_PATH = "opticedge_cloud_utils.merge"  # adjust if deep_merge is in another file/module


@pytest.fixture
def module():
    """Dynamically import and reload the target module before each test."""
    mod = importlib.import_module(MODULE_PATH)
    importlib.reload(mod)
    return mod


def test_merges_non_overlapping_keys(module):
    base = {"a": 1}
    updates = {"b": 2}
    result = module.deep_merge(base, updates)
    assert result == {"a": 1, "b": 2}


def test_overwrites_existing_value(module):
    base = {"a": 1, "b": 2}
    updates = {"b": 99}
    result = module.deep_merge(base, updates)
    assert result == {"a": 1, "b": 99}


def test_deep_merges_nested_dicts(module):
    base = {"a": {"x": 1, "y": 2}}
    updates = {"a": {"y": 99, "z": 3}}
    result = module.deep_merge(base, updates)
    assert result == {"a": {"x": 1, "y": 99, "z": 3}}


def test_removes_key_when_value_none_and_delete_nulls_true(module):
    base = {"a": 1, "b": 2}
    updates = {"b": None}
    result = module.deep_merge(base, updates, delete_nulls=True)
    assert result == {"a": 1}


def test_preserves_none_when_delete_nulls_false(module):
    base = {"a": 1, "b": 2}
    updates = {"b": None}
    result = module.deep_merge(base, updates, delete_nulls=False)
    assert result == {"a": 1, "b": None}


def test_handles_empty_updates(module):
    base = {"a": 1}
    updates = {}
    result = module.deep_merge(base, updates)
    assert result == {"a": 1}


def test_handles_empty_base(module):
    base = {}
    updates = {"x": 10}
    result = module.deep_merge(base, updates)
    assert result == {"x": 10}


def test_original_base_not_modified(module):
    base = {"a": {"b": 1}}
    updates = {"a": {"c": 2}}
    result = module.deep_merge(base, updates)
    assert result == {"a": {"b": 1, "c": 2}}
    assert base == {"a": {"b": 1}}
    assert id(result) != id(base)


def test_deep_get_found_and_not_found():
    obj = {"a": {"b": None}, "x": 1}
    # nested key exists and is None -> found True
    val, found = _deep_get(obj, "a.b")
    assert found is True
    assert val is None

    # top-level key
    val, found = _deep_get(obj, "x")
    assert found is True
    assert val == 1

    # missing key
    val, found = _deep_get(obj, "a.c")
    assert found is False
    assert val is None

    # empty path returns the object itself
    val, found = _deep_get(obj, "")
    assert found is True
    assert val == obj


def test_deep_get_obj_none_branches():
    # obj is None and non-empty path -> should be not found
    val, found = _deep_get(None, "a.b")
    assert found is False
    assert val is None

    # obj is None and empty path -> earlier code returns (None, False) because obj is None
    val, found = _deep_get(None, "")
    assert found is False
    assert val is None


@pytest.mark.parametrize(
    "data, delta, path, delete_nulls, expected_val, expected_found",
    [
        # delta contains non-None value -> use delta
        ({"k": "old"}, {"k": "new"}, "k", True, "new", True),
        # delta contains None and delete_nulls=True -> removed
        ({"k": "old"}, {"k": None}, "k", True, None, False),
        # delta contains None and delete_nulls=False -> explicit None
        ({"k": "old"}, {"k": None}, "k", False, None, True),
        # delta doesn't contain it -> fallback to data
        ({"a": {"b": 2}}, {"x": 1}, "a.b", True, 2, True),
        # neither contains it
        ({"a": {}}, {"x": {}}, "a.missing", True, None, False),
        # nested delta overrides nested data
        ({"profile": {"type": "student"}}, {"profile": {"type": "alumni"}}, "profile.type", True, "alumni", True),
    ]
)
def test_compute_new_value_from_delta_or_data(data, delta, path, delete_nulls, expected_val, expected_found):
    val, found = _compute_new_value_from_delta_or_data(data, delta, path, delete_nulls=delete_nulls)
    assert found is expected_found
    assert val == expected_val


def test_detect_field_changes_basic_scenario():
    data = {
        "email": "old@example.com",
        "profile": {"type": "student", "name": "Alice"},
        "extras": {"x": 1}
    }
    delta = {
        "email": None,               # deletion
        "profile": {"type": "alumni"}  # update nested field
    }
    fields = ["email", "profile.type", "profile.name", "extras.x", "missing.field"]

    changes = detect_field_changes(data, delta, fields, delete_nulls=True)

    # email -> deleted
    assert changes["email"]["old"] == "old@example.com"
    assert changes["email"]["new"] == None
    assert changes["email"]["old_found"] is True
    assert changes["email"]["new_found"] is False
    assert changes["email"]["changed"] is True
    assert changes["email"]["reason"] == "deleted"

    # profile.type -> updated
    assert changes["profile.type"]["old"] == "student"
    assert changes["profile.type"]["new"] == "alumni"
    assert changes["profile.type"]["old_found"] is True
    assert changes["profile.type"]["new_found"] is True
    assert changes["profile.type"]["changed"] is True
    assert changes["profile.type"]["reason"] == "updated"

    # profile.name -> unchanged (not present in delta)
    assert changes["profile.name"]["old"] == "Alice"
    assert changes["profile.name"]["new"] == "Alice"
    assert changes["profile.name"]["changed"] is False
    assert changes["profile.name"]["reason"] == "unchanged"

    # extras.x -> unchanged
    assert changes["extras.x"]["old"] == 1
    assert changes["extras.x"]["new"] == 1
    assert changes["extras.x"]["changed"] is False

    # missing.field -> remains missing
    assert changes["missing.field"]["old_found"] is False
    assert changes["missing.field"]["new_found"] is False
    assert changes["missing.field"]["changed"] is False


def test_detect_field_changes_delete_nulls_false_treats_null_as_value():
    data = {"k": "old"}
    delta = {"k": None}
    fields = ["k"]

    changes = detect_field_changes(data, delta, fields, delete_nulls=False)
    assert changes["k"]["old"] == "old"
    assert changes["k"]["old_found"] is True
    # new_found should be True because we treat None as explicit value
    assert changes["k"]["new_found"] is True
    assert changes["k"]["new"] is None
    assert changes["k"]["changed"] is True
    assert changes["k"]["reason"] == "updated"


def test_detect_field_changes_added_branch():
    # field does not exist in data but exists in delta -> 'added' branch should be hit
    data = {}
    delta = {"new_field": "value123"}
    fields = ["new_field"]

    changes = detect_field_changes(data, delta, fields, delete_nulls=True)

    assert changes["new_field"]["old_found"] is False
    assert changes["new_field"]["new_found"] is True
    assert changes["new_field"]["new"] == "value123"
    assert changes["new_field"]["changed"] is True
    assert changes["new_field"]["reason"] == "added"
