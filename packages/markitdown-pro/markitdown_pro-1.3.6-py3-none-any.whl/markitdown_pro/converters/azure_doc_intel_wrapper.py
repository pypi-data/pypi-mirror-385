from pathlib import Path
from typing import Optional

from ..services.azure_doc_intelligence import DocumentIntelligenceHandler
from .base import ConverterWrapper


class DocIntelligenceWrapper(ConverterWrapper):

    SUPPORTED_EXTENSIONS = DocumentIntelligenceHandler.SUPPORTED_EXTENSIONS

    def __init__(self):
        super().__init__("Azure Document Intelligence")
        self.converter = DocumentIntelligenceHandler()

    async def convert(self, file_path: str) -> Optional[str]:
        markdown = await self.converter.convert_to_md(file_path)
        await self.converter.aclose()
        return markdown

    async def get_page_count(self, file_path: str | Path) -> Optional[int]:
        return await self.converter.get_page_count(file_path)
