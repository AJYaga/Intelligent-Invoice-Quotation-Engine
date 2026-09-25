import numpy as np
from app.models.ocr import OCRBox, OCRLine, OCRPage
from app.models.preprocessing import PreprocessingResult, ProcessedPage
from app.services.ocr.base import OCRProvider
from app.services.ocr.service import OCRService

class FakeOCRProvider(OCRProvider):
    def extract_page(self, image: np.ndarray, page_number: int) -> OCRPage:
        return OCRPage(
            page_number=page_number,
            lines=[
                OCRLine(
                    text="INVOICE",
                    confidence=0.95,
                    box=OCRBox(
                        points=[
                            [0, 0],
                            [100, 0],
                            [100, 20],
                            [0, 20],
                        ]
                    ),
                ),
                OCRLine(
                    text="INV-1001",
                    confidence=0.90,
                    box=OCRBox(
                        points=[
                            [0, 30],
                            [100, 30],
                            [100, 50],
                            [0, 50],
                        ]
                    ),
                ),
            ],
            mean_confidence=0.925,
        )

class EmptyOCRProvider(OCRProvider):
    def extract_page(self, image: np.ndarray, page_number: int) -> OCRPage:
        return OCRPage(
            page_number=page_number,
            lines=[],
            mean_confidence=0.0,
        )

def make_page(page_number: int) -> ProcessedPage:
    image = np.zeros((100, 200), dtype=np.uint8)

    return ProcessedPage(
        page_number=page_number,
        image=image,
        width=200,
        height=100,
    )

def test_extract_document_text():
    preprocessing_result = PreprocessingResult(
        pages=[make_page(1)],
        source_type="image",
        page_count=1,
    )

    service = OCRService(FakeOCRProvider())
    result = service.extract_document(preprocessing_result)

    assert result.full_text == "INVOICE\nINV-1001"
    assert result.mean_confidence == 0.925
    assert len(result.pages) == 1

def test_multi_page_ocr():
    preprocessing_result = PreprocessingResult(
        pages=[
            make_page(1),
            make_page(2),
        ],
        source_type="pdf",
        page_count=2,
    )

    service = OCRService(FakeOCRProvider())
    result = service.extract_document(preprocessing_result)

    assert len(result.pages) == 2
    assert result.full_text.count("INVOICE") == 2

def test_empty_ocr_result():
    preprocessing_result = PreprocessingResult(
        pages=[make_page(1)],
        source_type="image",
        page_count=1,
    )

    service = OCRService(EmptyOCRProvider())
    result = service.extract_document(preprocessing_result)

    assert result.full_text == ""
    assert result.mean_confidence == 0.0