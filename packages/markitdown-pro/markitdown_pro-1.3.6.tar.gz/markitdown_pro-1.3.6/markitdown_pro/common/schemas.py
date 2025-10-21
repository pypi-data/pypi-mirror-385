import enum
from io import BytesIO


class NamedBytesIO(BytesIO):
    def __init__(self, data: bytes, name: str):
        super().__init__(data)
        self.name = name


class ExtensionCategory(enum.Enum):
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    LIGHTWEIGHT_TEXT = "lightweight_text"
    FORMATTED_DOCS = "formatted_docs"
    OTHER = "other"
