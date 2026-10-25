"""Gate F-A: read-only architecture inventory; no model, DB, or production writes."""
import argparse
import ast
import hashlib
import json
from pathlib import Path

TARGET = Path("experiments/car_v2_gate_f_h2r.py")
EXPECTED = {"route", "answer_question", "validate_manifest", "evaluate"}


def inspect_source(path=TARGET):
    data = Path(path).read_bytes()
    tree = ast.parse(data, filename=str(path))
    functions = {n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    patterns = sorted(n.targets[0].id for n in tree.body
                      if isinstance(n, ast.Assign) and len(n.targets) == 1
                      and isinstance(n.targets[0], ast.Name)
                      and isinstance(n.value, ast.Call)
                      and isinstance(n.value.func, ast.Attribute)
                      and n.value.func.attr == "compile")
    return {"target": str(path), "sha256": hashlib.sha256(data).hexdigest(),
            "required_functions_present": sorted(EXPECTED & functions),
            "missing_functions": sorted(EXPECTED - functions),
            "compiled_regex_constants": patterns,
            "note": "Static inventory only; does not establish safety or semantic generalization."}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=TARGET)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if not args.source.is_file() or args.output.exists() or args.output.resolve() == args.source.resolve():
        parser.error("Source must exist; output must be new and distinct")
    report = inspect_source(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as handle:
        json.dump(report, handle, indent=2)
    print(f"Recorded read-only architecture inventory: {args.output}")


if __name__ == "__main__":
    main()
