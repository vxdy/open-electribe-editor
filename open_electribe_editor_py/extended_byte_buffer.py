"""Minimal ExtendedByteBuffer implementation using Python bytearray."""
from typing import Optional, Union
import struct


class ExtendedByteBuffer:
    """A simple byte buffer supporting unsigned operations."""

    def __init__(self, data: Union[int, bytes, bytearray], endian: str = ">"):
        if isinstance(data, int):
            self._buf = bytearray(data)
        else:
            self._buf = bytearray(data)
        self._pos = 0
        self.endian = endian

    def remaining(self) -> int:
        return len(self._buf) - self._pos

    def position(self, pos: Optional[int] = None) -> int:
        if pos is None:
            return self._pos
        if pos < 0 or pos > len(self._buf):
            raise IndexError("position out of range")
        self._pos = pos
        return self._pos

    def get_unsigned_byte(self, index: Optional[int] = None) -> int:
        if index is None:
            index = self._pos
            self._pos += 1
        return self._buf[index]

    def put_unsigned_byte(self, value: int, index: Optional[int] = None) -> None:
        if index is None:
            index = self._pos
            self._pos += 1
        self._buf[index] = value & 0xFF

    def _unpack(self, fmt: str, index: int) -> int:
        return struct.unpack_from(self.endian + fmt, self._buf, index)[0]

    def _pack(self, fmt: str, index: int, value: int) -> None:
        struct.pack_into(self.endian + fmt, self._buf, index, value)

    def get_unsigned_short(self, index: Optional[int] = None) -> int:
        if index is None:
            index = self._pos
            self._pos += 2
        return self._unpack("H", index)

    def put_unsigned_short(self, value: int, index: Optional[int] = None) -> None:
        if index is None:
            index = self._pos
            self._pos += 2
        self._pack("H", index, value & 0xFFFF)

    def get_unsigned_int(self, index: Optional[int] = None) -> int:
        if index is None:
            index = self._pos
            self._pos += 4
        return self._unpack("I", index)

    def put_unsigned_int(self, value: int, index: Optional[int] = None) -> None:
        if index is None:
            index = self._pos
            self._pos += 4
        self._pack("I", index, value & 0xFFFFFFFF)

    def array(self) -> bytes:
        return bytes(self._buf)

    def as_bytearray(self) -> bytearray:
        return self._buf
