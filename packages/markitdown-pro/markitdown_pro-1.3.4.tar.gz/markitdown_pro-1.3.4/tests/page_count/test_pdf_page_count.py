import logging
import os
from pathlib import Path

import pytest

from markitdown_pro.handlers.pdf_handler import PDFHandler
from tests.fixtures import data_path

log = logging.getLogger(__name__)

PAGE_COUNT = 96


@pytest.mark.asyncio
async def test_files(pdf_handler: PDFHandler):
    path = os.path.join(
        data_path(),
        "pdf",
        "netl-trs-9-2018-ct-of-the-tuscarora-sandstone-from-the-preston-119-well-final-20180509.pdf",
    )
    file_path = Path(path)
    log.info(f"DocumentIntelligenceHandler: Testing file: {file_path}")

    pages = await pdf_handler.get_page_count(file_path)
    assert pages is not None, f"Page count returned None for {file_path.name}"
    assert isinstance(pages, int), f"Output type is not int for {file_path.name}"
    assert (
        pages == PAGE_COUNT
    ), f"Output is not {PAGE_COUNT} for {file_path.name}. Returned {pages} instead."
