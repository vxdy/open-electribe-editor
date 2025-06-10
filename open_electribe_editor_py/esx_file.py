"""High level ESX file wrapper."""
from __future__ import annotations

from pathlib import Path
from .extended_byte_buffer import ExtendedByteBuffer
from . import esx_util


class ESXFile:
    """Represents an ESX file and provides basic load/save operations."""

    def __init__(self, data: bytes):
        if not esx_util.is_valid_esx_file(data):
            raise ValueError("Invalid ESX file")
        # store mutable buffer for modifications
        self.buffer = ExtendedByteBuffer(bytearray(data))

    @classmethod
    def from_file(cls, path: str | Path) -> "ESXFile":
        with open(path, "rb") as f:
            data = f.read()
        return cls(data)

    def to_bytes(self) -> bytes:
        """Return the current contents as bytes."""
        return self.buffer.array()

    def save(self, path: str | Path) -> None:
        """Write current contents to a file."""
        with open(path, "wb") as f:
            f.write(self.to_bytes())

