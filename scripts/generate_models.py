"""Generate Pydantic v2 models from JSON Schema using datamodel-code-generator.

Usage:
    python -m scripts.generate_models
"""
from pathlib import Path
import sys

def main() -> int:
    try:
        from datamodel_code_generator import InputFileType, generate, DataModelType
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
        project_root
        / "src"
        / "stock_ticker_api"
        / "models"
        / "stock_model.py"
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)

    generate(
        # Read the JSON schema from file
        schema_path.read_text(encoding="utf-8"),
        input_file_type=InputFileType.JsonSchema,
        input_filename=str(schema_path),
        output=out_path,  # Path object, not string
        # Request Pydantic v2 models explicitly
        output_model_type=DataModelType.PydanticV2BaseModel,
        # IMPORTANT: don't pass target_python_version="3.13" because
        # datamodel-code-generator/black don't know about 3.13 yet.
    )

    print(f"Generated: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
