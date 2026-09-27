from app.models.extraction import ExtractionResult, ExtractedField
from app.models.ocr import OCRResult
from app.services.extraction.fields import FieldExtractor
from app.services.extraction.line_items import LineItemExtractor
from app.services.extraction.parties import PartyExtractor

class ExtractionService:
    def __init__(self) -> None:
        self.field_extractor = FieldExtractor()
        self.line_item_extractor = LineItemExtractor()
        self.party_extractor = PartyExtractor()

    def extract(
        self,
        ocr_result: OCRResult,
    ) -> ExtractionResult:
        fields = self.field_extractor.extract(
            ocr_result
        )

        customer = self.party_extractor.extract_customer(
            ocr_result
        )

        fields["customer_name"] = ExtractedField(
            value=customer.name,
            confidence=customer.confidence,
        )

        fields["address"] = ExtractedField(
            value=customer.address,
            confidence=customer.confidence,
        )

        return ExtractionResult(
            fields=fields,
            line_items=self.line_item_extractor.extract(
                ocr_result
            ),
        )