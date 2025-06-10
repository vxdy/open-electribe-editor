"""Dataclasses representing major sections of an ESX file."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .extended_byte_buffer import ExtendedByteBuffer
from . import esx_constants as C


@dataclass
class GlobalParameters:
    """Container for global parameter bytes."""

    raw: bytes

    @classmethod
    def from_esx(cls, data: bytes) -> "GlobalParameters":
        start = C.ADDR_GLOBAL_PARAMETERS
        end = C.ADDR_UNKNOWN_SECTION_1
        return cls(data[start:end])


@dataclass
class Pattern:
    """Container for a single pattern's raw data."""

    raw: bytes


@dataclass
class Patterns:
    """All pattern data loaded from the ESX file."""

    entries: List[Pattern]

    @classmethod
    def from_esx(cls, data: bytes) -> "Patterns":
        start = C.ADDR_PATTERN_DATA
        end = C.ADDR_UNKNOWN_SECTION_2
        pattern_data = data[start:end]
        num_patterns = 256
        pattern_size = len(pattern_data) // num_patterns if num_patterns else len(pattern_data)
        entries = [Pattern(pattern_data[i : i + pattern_size]) for i in range(0, len(pattern_data), pattern_size)]
        return cls(entries)


@dataclass
class Song:
    """Container for a single song's raw data."""

    raw: bytes


@dataclass
class Songs:
    """All song data loaded from the ESX file."""

    entries: List[Song]

    @classmethod
    def from_esx(cls, data: bytes) -> "Songs":
        start = C.ADDR_SONG_DATA
        end = C.ADDR_SONG_EVENT_DATA
        song_data = data[start:end]
        num_songs = 64
        song_size = len(song_data) // num_songs if num_songs else len(song_data)
        entries = [Song(song_data[i : i + song_size]) for i in range(0, len(song_data), song_size)]
        return cls(entries)


@dataclass
class Sample:
    """Container for a single sample header's raw bytes."""

    raw: bytes


@dataclass
class Samples:
    """All sample headers loaded from the ESX file."""

    entries: List[Sample]

    @classmethod
    def from_esx(cls, data: bytes) -> "Samples":
        headers = []
        # Mono sample headers
        start = C.ADDR_SAMPLE_HEADER_MONO
        for i in range(C.NUM_SAMPLES_MONO):
            off = start + i * C.CHUNKSIZE_SAMPLE_HEADER_MONO
            headers.append(Sample(data[off : off + C.CHUNKSIZE_SAMPLE_HEADER_MONO]))
        # Stereo sample headers
        start = C.ADDR_SAMPLE_HEADER_STEREO
        for i in range(C.NUM_SAMPLES_STEREO):
            off = start + i * C.CHUNKSIZE_SAMPLE_HEADER_STEREO
            headers.append(Sample(data[off : off + C.CHUNKSIZE_SAMPLE_HEADER_STEREO]))
        return cls(headers)


@dataclass
class ESXData:
    """Parsed representation of an ESX file."""

    global_params: GlobalParameters
    patterns: Patterns
    songs: Songs
    samples: Samples

    @classmethod
    def from_bytes(cls, data: bytes) -> "ESXData":
        gp = GlobalParameters.from_esx(data)
        patterns = Patterns.from_esx(data)
        songs = Songs.from_esx(data)
        samples = Samples.from_esx(data)
        return cls(gp, patterns, songs, samples)
