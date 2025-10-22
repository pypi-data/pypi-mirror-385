# merge_utils.py
from typing import Any, Dict, Tuple, Iterable

# ---------- your existing deep_merge (unchanged) ----------
def deep_merge(base: dict, updates: dict, delete_nulls: bool = True) -> dict:
    """
    Recursively merge two dictionaries.
    Args:
        base: original dict (must be a dict; caller should pass {} if None)
        updates: updates to apply
        delete_nulls: if True, keys with value None in updates are removed from result
    Returns:
        new dict with updates applied (shallow-copy semantics)
    """
    result = base.copy()
    for k, v in updates.items():
        if delete_nulls and v is None:
            result.pop(k, None)
        elif isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = deep_merge(result[k], v, delete_nulls)
        else:
            result[k] = v
    return result


# ---------- internal helpers (renamed with leading underscore) ----------
def _deep_get(obj: Dict[str, Any] | None, path: str) -> Tuple[Any, bool]:
    """
    Get a value by dot-path from a dict.
    Returns (value, found_flag). found_flag is True even when the found value is None.
    If path == "" returns (obj, True).
    """
    if obj is None:
        return None, False
    current = obj
    if path == "":
        return current, True
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None, False
        current = current[part]
    return current, True


def _compute_new_value_from_delta_or_data(data: Dict[str, Any] | None,
                                         delta: Dict[str, Any] | None,
                                         path: str,
                                         delete_nulls: bool = True) -> Tuple[Any, bool]:
    """
    Compute what the value at `path` will be after applying `delta` to `data`.
    - If `delta` contains the path:
        - if its value is None and delete_nulls==True -> treat as removed (return (None, False))
        - else -> return (value, True)
    - Else fall back to data's value if present.
    Returns (value, found_flag). If found_flag is False the path will be absent after merge.
    """
    # safe defaults
    delta = delta or {}
    data = data or {}

    val, found_in_delta = _deep_get(delta, path)
    if found_in_delta:
        if val is None and delete_nulls:
            return None, False
        return val, True

    val, found_in_data = _deep_get(data, path)
    if found_in_data:
        return val, True

    return None, False


def detect_field_changes(data: Dict[str, Any] | None,
                         delta: Dict[str, Any] | None,
                         fields: Iterable[str],
                         delete_nulls: bool = True) -> Dict[str, Dict[str, Any]]:
    """
    For each dot-path in fields returns:
      {
        "old": <old_value_or_None>,
        "old_found": True/False,
        "new": <new_value_or_None>,
        "new_found": True/False,
        "changed": True/False,
        "reason": "deleted"|"updated"|"added"|"unchanged"
      }
    Note: when new_found is False it means the field will be absent after merge (deleted).
    """
    data = data or {}
    delta = delta or {}
    out: Dict[str, Dict[str, Any]] = {}

    for path in fields:
        old_val, old_found = _deep_get(data, path)
        new_val, new_found = _compute_new_value_from_delta_or_data(data, delta, path, delete_nulls=delete_nulls)

        # Determine changed/ reason
        if not old_found and not new_found:
            changed = False
            reason = "unchanged"
        elif not old_found and new_found:
            changed = True
            reason = "added"
        elif old_found and not new_found:
            changed = True
            reason = "deleted"
        else:
            changed = old_val != new_val
            reason = "updated" if changed else "unchanged"

        out[path] = {
            "old": old_val,
            "old_found": old_found,
            "new": None if not new_found else new_val,
            "new_found": new_found,
            "changed": changed,
            "reason": reason,
        }

    return out
