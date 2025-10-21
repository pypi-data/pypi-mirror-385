import json
from typing import Any, Dict

def json_diff(a: Any, b: Any) -> Dict[str, Any]:
    """Compare two JSON-like Python objects and return a structured diff."""
    if a == b:
        return {"changed": False, "diff": {}}

    diff = {"added": {}, "removed": {}, "modified": {}}

    if isinstance(a, dict) and isinstance(b, dict):
        a_keys, b_keys = set(a.keys()), set(b.keys())
        for key in sorted(a_keys - b_keys):
            diff["removed"][key] = a[key]
        for key in sorted(b_keys - a_keys):
            diff["added"][key] = b[key]
        for key in sorted(a_keys & b_keys):
            if a[key] != b[key]:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    nested = json_diff(a[key], b[key])
                    if nested["changed"]:
                        diff["modified"][key] = nested["diff"]
                else:
                    diff["modified"][key] = {"from": a[key], "to": b[key]}
    elif isinstance(a, list) and isinstance(b, list):
        diff["added"] = [x for x in b if x not in a]
        diff["removed"] = [x for x in a if x not in b]
    else:
        diff["modified"] = {"from": a, "to": b}

    changed = any(bool(diff[k]) for k in diff)
    return {"changed": changed, "diff": diff}

def to_pretty_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)
