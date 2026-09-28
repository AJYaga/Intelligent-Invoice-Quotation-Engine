import sys
from pathlib import Path
from app.pipeline.document_pipeline import DocumentPipeline
from app.api.serializers import serialize_pipeline_result

def main():
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python -m scripts.analyze_file <file>"
        )

    path = Path(sys.argv[1])

    if not path.exists():
        raise FileNotFoundError(path)

    pipeline = DocumentPipeline()

    result = pipeline.analyze(
        file_bytes=path.read_bytes(),
        filename=path.name,
    )

    response = serialize_pipeline_result(result)

    print(response.model_dump_json(indent=2))

    print("\n=== OCR BOXES ===")

    for page in result.ocr.pages:
        for line in page.lines:
            print(
                f"{line.text!r:30} "
                f"conf={line.confidence:.3f} "
                f"box={line.box.points}"
            )

if __name__ == "__main__":
    main()