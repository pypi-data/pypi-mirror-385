import logging
from pathlib import Path

import pytest

from markitdown_pro.common.utils import ensure_minimum_content
from markitdown_pro.conversion_pipeline import ConversionPipeline

from ..fixtures import data_path, pretty_id
from ..utils import list_files

log = logging.getLogger(__name__)

EXCLUDE_EXTENSIONS = {".heic", ".doc", ".odt", ".ppt", ".zip"}

TEST_FILES_PATH = data_path()
ALL_FILES = list_files(TEST_FILES_PATH, exclude_ext=EXCLUDE_EXTENSIONS, recursive=True)
log.info(f"ConversionPipeline: Found {len(ALL_FILES)} test files in {TEST_FILES_PATH}.")


@pytest.mark.asyncio
@pytest.mark.parametrize("file_path", ALL_FILES, ids=[pretty_id(p) for p in ALL_FILES])
async def test_files(file_path: Path, pipeline: ConversionPipeline):
    log.info(f"ConversionPipeline: Testing file: {file_path}")

    markdown_text = await pipeline.convert_document_to_md(str(file_path))
    assert markdown_text is not None, f"Conversion returned None for {file_path.name}"
    assert isinstance(markdown_text, str), f"Output type is not str for {file_path.name}"
    assert ensure_minimum_content(
        markdown_text
    ), f"Output does not meet minimum content requirements for {file_path.name}"
