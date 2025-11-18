"""Generate Pydantic v2 models from JSON Schema using datamodel-code-generator.

Usage:
    python -m scripts.generate_models
"""
from pathlib import Path
import sys

def main() -> int:
    try:
        from datamodel_code_generator import InputFileType
        from datamodel_code_generator import generate
    except Exception:
        print(
            "datamodel-code-generator is not installed. "
            "Run: pip install datamodel-code-generator",
            file=sys.stderr,
        )
        return 1

    project_root = Path(__file__).resolve().parents[1]
    schema_path = (
        project_root
        / "src"
        / "stock_ticker_api"
        / "models"
        / "schemas"
        / "stock_schema.json"
    )
    out_path = (
        project_root / "src" / "stock_ticker_api" / "models" / "stock_model.py"
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)

    generate(
        input_=str(schema_path),
        input_file_type=InputFileType.JsonSchema,
        output=str(out_path),
        target_python_version="3.13",
        use_pydantic_v2=True,
    )

    print(f"Generated: {out_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
