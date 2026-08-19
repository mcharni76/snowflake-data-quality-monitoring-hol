#!/usr/bin/env python3
"""Validate all HOL notebooks are valid JSON with expected structure."""
import json
import sys
from pathlib import Path

def validate_notebook(path: Path) -> list[str]:
    errors = []
    try:
        with open(path) as f:
            nb = json.load(f)
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"]

    if nb.get("nbformat") != 4:
        errors.append(f"Unexpected nbformat: {nb.get('nbformat')}")

    cells = nb.get("cells", [])
    if not cells:
        errors.append("No cells found")

    for i, cell in enumerate(cells):
        if cell.get("cell_type") not in ("code", "markdown", "raw"):
            errors.append(f"Cell {i}: invalid cell_type '{cell.get('cell_type')}'")
        if "source" not in cell:
            errors.append(f"Cell {i}: missing 'source' field")

    return errors

def main():
    notebook_dir = Path(__file__).parent.parent / "notebooks"
    notebooks = sorted(notebook_dir.glob("*.ipynb"))

    if not notebooks:
        print("ERROR: No notebooks found in notebooks/")
        sys.exit(1)

    total_errors = 0
    for nb_path in notebooks:
        errors = validate_notebook(nb_path)
        if errors:
            print(f"FAIL: {nb_path.name}")
            for err in errors:
                print(f"  - {err}")
            total_errors += len(errors)
        else:
            print(f"OK:   {nb_path.name}")

    print(f"\n{'='*50}")
    print(f"Notebooks: {len(notebooks)} | Errors: {total_errors}")

    if total_errors > 0:
        sys.exit(1)
    print("All notebooks valid.")

if __name__ == "__main__":
    main()
