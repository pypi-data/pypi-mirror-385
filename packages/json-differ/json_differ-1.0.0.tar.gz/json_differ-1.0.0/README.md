# 🧾 json-differ — Minimal JSON Difference Tool

[![PyPI version](https://img.shields.io/pypi/v/json-differ.svg?logo=python&label=PyPI)](https://pypi.org/project/json-differ/)
[![Python Version](https://img.shields.io/pypi/pyversions/json-differ.svg)](https://pypi.org/project/json-differ/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

A **lightweight JSON differ** that makes it easy to spot what changed — added, removed, or modified — between two JSON files or Python objects.

✨ Ideal for developers working with APIs, configurations, or data migrations.

---

## 🚀 Installation

```bash
pip install json-differ
```

Or, if using locally:
```bash
git clone git@github.com:syedrakesh/json-differ.git
cd json-differ
pip install .
```

---

## 💡 CLI Usage

```bash
json-differ examples/sample1.json examples/sample2.json
```

Output:
```json
{
  "changed": true,
  "diff": {
    "added": {"city": "Paris"},
    "removed": {},
    "modified": {"age": {"from": 25, "to": 26}}
  }
}
```

Optional flags:
```bash
--pretty   # formatted output (default)
--compact  # single-line JSON
```

---

## 🧠 Python API

```python
from json_differ import json_diff

a = {"name": "Alice", "age": 25}
b = {"name": "Alice", "age": 26, "city": "Paris"}

result = json_diff(a, b)
print(result)
```

---

## 🧩 Example JSON Files

```bash
json-differ examples/sample1.json examples/sample2.json
```

Sample input files are included in `examples/`.

---

## 🧰 Features

✅ No dependencies  
✅ Nested dict & list comparison  
✅ CLI + Python API both supported  
✅ Simple structured output  

---

## 🧾 License

MIT © 2025 Syed Rakesh Uddin

---

Built with ❤️ for developers who appreciate small, smart tools.
