from dataclasses import dataclass

@dataclass
class OCRBox:
    points: list[list[float]]

@dataclass
class OCRLine:
    text: str
    confidence: float
    box: OCRBox

@dataclass
class OCRPage:
    page_number: int
    lines: list[OCRLine]
    mean_confidence: float

@dataclass
class OCRResult:
    pages: list[OCRPage]
    full_text: str
    mean_confidence: float