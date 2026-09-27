from pathlib import Path
from app.services.classification.classifier import DocumentClassifier
from app.services.extraction.service import ExtractionService
from app.services.ocr.paddle import PaddleOCRProvider
from app.services.ocr.service import OCRService
from app.services.preprocessing.processor import preprocess_document
from app.services.validation.service import ValidationService

DOCUMENT_PATH = Path("samples/invoices/sample_invoice.png")

def main():
    if not DOCUMENT_PATH.exists():
        raise FileNotFoundError(f"Document not found: {DOCUMENT_PATH}")

    file_bytes = DOCUMENT_PATH.read_bytes()

    preprocessing_result = preprocess_document(
        file_bytes=file_bytes,
        filename=DOCUMENT_PATH.name,
    )

    ocr_service = OCRService(
        provider=PaddleOCRProvider()
    )

    ocr_result = ocr_service.extract_document(
        preprocessing_result
    )

    classifier = DocumentClassifier()
    classification = classifier.classify(ocr_result)

    extraction_service = ExtractionService()
    extraction = extraction_service.extract(ocr_result)

    print("\n=== DOCUMENT ===")
    print(f"File: {DOCUMENT_PATH}")
    print(f"Pages: {preprocessing_result.page_count}")

    print("\n=== CLASSIFICATION ===")
    print(f"Type: {classification.document_type.value}")
    print(f"Confidence: {classification.confidence}")
    print(f"Invoice score: {classification.invoice_score}")
    print(f"Quotation score: {classification.quotation_score}")

    print("\n=== OCR ===")
    print(f"Mean confidence: {ocr_result.mean_confidence:.3f}")
    print(ocr_result.full_text)

    print("\n=== OCR BOXES ===")

    for page in ocr_result.pages:
        for line in page.lines:
            print(
                f"{line.text!r:35} "
                f"conf={line.confidence:.3f} "
                f"box={line.box.points}"
            )

    print("\n=== EXTRACTED FIELDS ===")

    for name, field in extraction.fields.items():
        print(
            f"{name}: value={field.value!r}, "
            f"confidence={field.confidence}, "
            f"page={field.page_number}"
        )

    print("\n=== LINE ITEMS ===")

    if not extraction.line_items:
        print("No line items extracted.")

    for index, item in enumerate(
        extraction.line_items,
        start=1,
    ):
        print(
            f"{index}. "
            f"description={item.description!r}, "
            f"quantity={item.quantity}, "
            f"unit_price={item.unit_price}, "
            f"line_total={item.line_total}, "
            f"confidence={item.confidence}"
        )

    validation = ValidationService().validate(
        ocr_result=ocr_result,
        classification=classification,
        extraction=extraction,
    )

    print("\n=== VALIDATION ===")
    print(f"Confidence: {validation.confidence}")
    print(f"Status: {validation.status.value}")

    if not validation.issues:
        print("No validation issues.")
    else:
        for issue in validation.issues:
            print(
                f"{issue.severity.value} | "
                f"{issue.code} | "
                f"{issue.message}"
            )

if __name__ == "__main__":
    main()