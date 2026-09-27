from functools import lru_cache
from app.pipeline.document_pipeline import DocumentPipeline

@lru_cache(maxsize=1)
def get_document_pipeline() -> DocumentPipeline:
    return DocumentPipeline()