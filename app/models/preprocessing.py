from dataclasses import dataclass
import numpy as np

@dataclass
class ProcessedPage:
    page_number: int
    image: np.ndarray
    width: int
    height: int

@dataclass
class PreprocessingResult:
    pages: list[ProcessedPage]
    source_type: str
    page_count: int