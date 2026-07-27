from collections.abc import AsyncIterable
from datetime import datetime
from typing import Protocol


class StoredObject(Protocol):
    content_type: str
    file_size: int


class StorageAdapter(Protocol):
    async def write_upload(self, stored_filename: str, content_type: str, content: AsyncIterable[bytes], maximum_size: int) -> StoredObject: ...
    def inspect(self, stored_filename: str) -> StoredObject | None: ...
    def release_quarantined(self, stored_filename: str) -> bool: ...
    def delete(self, stored_filename: str) -> None: ...
