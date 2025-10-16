#!/usr/bin/env python3
"""
insert_docstrings.py
--------------------
Automatically inserts or replaces docstrings in functions and class methods
based on mappings defined in meta_data.json.

🧩 How It Works
---------------
- Looks for 'meta_data.json' in the current directory.
- Each key is a full file path (absolute or relative).
- Each file maps function names to docstrings.
- Class methods can be addressed as "ClassName.method".
- Existing docstrings are removed before new ones are inserted.
- Uses LibCST for format-preserving transformation.

📁 Example meta_data.json
-------------------------
{
  "src/example.py": {
    "add": "Add two numbers.\\n:param a: first number\\n:param b: second number",
    "Math.divide": "Divide a by b safely."
  },
  "tests/test_math.py": {
    "TestMath.test_add": "Unit test for addition."
  }
}

🖥️ Usage
---------
python insert_docstrings.py
"""

import json
import sys
import libcst as cst
from pathlib import Path


class DocInserter(cst.CSTTransformer):
    """
    Removes existing docstrings and inserts new ones
    based on mappings for both top-level functions and class methods.
    """

    def __init__(self, doc_map: dict[str, str]):
        self.doc_map = doc_map
        self.current_class = None  # track nested class context

    def visit_ClassDef(self, node):
        # Enter class context
        self.current_class = node.name.value

    def leave_ClassDef(self, original_node, updated_node):
        # Leave class context
        self.current_class = None
        return updated_node

    def leave_FunctionDef(self, original_node, updated_node):
        func_name = original_node.name.value
        key = func_name
        if self.current_class:
            key = f"{self.current_class}.{func_name}"

        if key not in self.doc_map:
            return updated_node

        new_docstring = self.doc_map[key]
        new_doc_node = cst.SimpleStatementLine(
            [cst.Expr(cst.SimpleString(f'"""{new_docstring}"""'))]
        )

        body = list(updated_node.body.body)

        # Remove old docstring if present
        if (
            len(body) > 0
            and isinstance(body[0], cst.SimpleStatementLine)
            and isinstance(body[0].body[0], cst.Expr)
            and isinstance(body[0].body[0].value, cst.SimpleString)
        ):
            del body[0]

        # Insert new docstring at top
        body.insert(0, new_doc_node)

        return updated_node.with_changes(body=cst.IndentedBlock(body=body))


def update_file(source_path: Path, doc_map: dict[str, str]):
    """Update one Python file based on docstring mapping."""
    if not source_path.exists():
        print(f"⚠️  File not found: {source_path}")
        return

    try:
        with open(source_path, encoding="utf-8") as f:
            module = cst.parse_module(f.read())

        new_module = module.visit(DocInserter(doc_map))

        with open(source_path, "w", encoding="utf-8") as f:
            f.write(new_module.code)

        print(f"✅ Updated {len(doc_map)} docstrings in {source_path.resolve()}")
    except Exception as e:
        print(f"❌ Failed to update {source_path}: {e}")


def main():
    meta_path = Path("meta_data.json")
    if not meta_path.exists():
        sys.exit("❌ meta_data.json not found in current directory.")

    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)

    if not isinstance(meta, dict):
        sys.exit("❌ meta_data.json must be a dict mapping file paths → functions.")

    for file_path, funcs in meta.items():
        update_file(Path(file_path), funcs)


if __name__ == "__main__":
    main()