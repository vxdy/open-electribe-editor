"""Sample management helpers for the Python ESX implementation."""
from __future__ import annotations

import struct
import wave
from pathlib import Path
from typing import Tuple

from . import esx_constants as C
from .esx_file import ESXFile


def parse_sample_header(raw: bytes) -> dict:
    """Parse a sample header and return a dict of parameters."""
    name = raw[0:8].decode("ascii", errors="ignore").rstrip("\x00")
    info = {"name": name}
    if len(raw) == C.CHUNKSIZE_SAMPLE_HEADER_MONO:
        info.update(
            {
                "offset_channel1_start": struct.unpack_from(">I", raw, 8)[0],
                "offset_channel1_end": struct.unpack_from(">I", raw, 12)[0],
                "start": struct.unpack_from(">I", raw, 16)[0],
                "end": struct.unpack_from(">I", raw, 20)[0],
                "loop_start": struct.unpack_from(">I", raw, 24)[0],
                "sample_rate": struct.unpack_from(">I", raw, 28)[0],
                "sample_tune": struct.unpack_from(">h", raw, 32)[0],
                "play_level": raw[34],
                "unknown_mono1": struct.unpack_from(">b", raw, 35)[0],
                "stretch_step": raw[36],
                "unknown_mono2": struct.unpack_from(">b", raw, 37)[0],
                "unknown_mono3": struct.unpack_from(">b", raw, 38)[0],
                "unknown_mono4": struct.unpack_from(">b", raw, 39)[0],
                "stereo": False,
            }
        )
    elif len(raw) == C.CHUNKSIZE_SAMPLE_HEADER_STEREO:
        info.update(
            {
                "offset_channel1_start": struct.unpack_from(">I", raw, 8)[0],
                "offset_channel1_end": struct.unpack_from(">I", raw, 12)[0],
                "offset_channel2_start": struct.unpack_from(">I", raw, 16)[0],
                "offset_channel2_end": struct.unpack_from(">I", raw, 20)[0],
                "start": struct.unpack_from(">I", raw, 24)[0],
                "end": struct.unpack_from(">I", raw, 28)[0],
                "sample_rate": struct.unpack_from(">I", raw, 32)[0],
                "sample_tune": struct.unpack_from(">h", raw, 36)[0],
                "play_level": raw[38],
                "unknown_stereo1": struct.unpack_from(">b", raw, 39)[0],
                "stretch_step": raw[40],
                "unknown_stereo2": struct.unpack_from(">b", raw, 41)[0],
                "unknown_stereo3": struct.unpack_from(">b", raw, 42)[0],
                "unknown_stereo4": struct.unpack_from(">b", raw, 43)[0],
                "stereo": True,
            }
        )
    else:
        info["raw_len"] = len(raw)
    return info


def pack_sample_header(info: dict, raw: bytes) -> bytes:
    """Create raw bytes for a sample header from the given info."""
    out = bytearray(raw)
    name_bytes = info.get("name", "").encode("ascii", errors="ignore")[:8]
    out[0:8] = name_bytes.ljust(8, b"\x00")
    if info.get("stereo"):
        struct.pack_into(">I", out, 8, info["offset_channel1_start"])
        struct.pack_into(">I", out, 12, info["offset_channel1_end"])
        struct.pack_into(">I", out, 16, info.get("offset_channel2_start", info["offset_channel1_start"]))
        struct.pack_into(">I", out, 20, info.get("offset_channel2_end", info["offset_channel1_end"]))
        struct.pack_into(">I", out, 24, info["start"])
        struct.pack_into(">I", out, 28, info["end"])
        struct.pack_into(">I", out, 32, info["sample_rate"])
        struct.pack_into(">h", out, 36, info.get("sample_tune", 0))
        out[38] = info.get("play_level", 100) & 0xFF
        struct.pack_into(">b", out, 39, info.get("unknown_stereo1", 0))
        out[40] = info.get("stretch_step", 0) & 0xFF
        struct.pack_into(">b", out, 41, info.get("unknown_stereo2", 0))
        struct.pack_into(">b", out, 42, info.get("unknown_stereo3", 0))
        struct.pack_into(">b", out, 43, info.get("unknown_stereo4", 0))
    else:
        struct.pack_into(">I", out, 8, info["offset_channel1_start"])
        struct.pack_into(">I", out, 12, info["offset_channel1_end"])
        struct.pack_into(">I", out, 16, info["start"])
        struct.pack_into(">I", out, 20, info["end"])
        struct.pack_into(">I", out, 24, info.get("loop_start", info["start"]))
        struct.pack_into(">I", out, 28, info["sample_rate"])
        struct.pack_into(">h", out, 32, info.get("sample_tune", 0))
        out[34] = info.get("play_level", 100) & 0xFF
        struct.pack_into(">b", out, 35, info.get("unknown_mono1", 0))
        out[36] = info.get("stretch_step", 0) & 0xFF
        struct.pack_into(">b", out, 37, info.get("unknown_mono2", 0))
        struct.pack_into(">b", out, 38, info.get("unknown_mono3", 0))
        struct.pack_into(">b", out, 39, info.get("unknown_mono4", 0))
    return bytes(out)


def header_offset(index: int) -> Tuple[int, int, bool]:
    """Return (offset, size, stereo) for the header at the given index."""
    if index < C.NUM_SAMPLES_MONO:
        off = C.ADDR_SAMPLE_HEADER_MONO + index * C.CHUNKSIZE_SAMPLE_HEADER_MONO
        return off, C.CHUNKSIZE_SAMPLE_HEADER_MONO, False
    idx = index - C.NUM_SAMPLES_MONO
    off = C.ADDR_SAMPLE_HEADER_STEREO + idx * C.CHUNKSIZE_SAMPLE_HEADER_STEREO
    return off, C.CHUNKSIZE_SAMPLE_HEADER_STEREO, True


def read_sample_data(esx: ESXFile, index: int) -> bytes:
    """Return raw PCM data for the given sample index."""
    info = parse_sample_header(esx.data.samples.entries[index].raw)
    start = info.get("start")
    end = info.get("end")
    if start is None or end is None or start >= end:
        return b""
    buf = esx.buffer.as_bytearray()
    return bytes(buf[C.ADDR_SAMPLE_DATA + start : C.ADDR_SAMPLE_DATA + end])


def delete_sample(esx: ESXFile, index: int) -> None:
    """Clear the header and data for a sample."""
    off, size, _ = header_offset(index)
    buf = esx.buffer.as_bytearray()
    buf[off:off + size] = b"\x00" * size
    esx.data.samples.entries[index].raw = bytes([0] * size)


def import_sample(esx: ESXFile, index: int, wav_path: str) -> None:
    """Import a WAV file into the given sample slot."""
    with wave.open(str(wav_path), "rb") as w:
        frames = w.readframes(w.getnframes())
        sample_rate = w.getframerate()
        num_channels = w.getnchannels()
        sampwidth = w.getsampwidth()
    if sampwidth != 2:
        raise ValueError("Only 16-bit WAV files supported")

    # find next available offset
    max_end = 0
    for s in esx.data.samples.entries:
        info = parse_sample_header(s.raw)
        end = info.get("end", 0)
        if end > max_end:
            max_end = end
    start_off = max_end
    end_off = start_off + len(frames)

    buf = esx.buffer.as_bytearray()
    required = C.ADDR_SAMPLE_DATA + end_off
    if required > len(buf):
        buf.extend(b"\x00" * (required - len(buf)))
    buf[C.ADDR_SAMPLE_DATA + start_off : C.ADDR_SAMPLE_DATA + end_off] = frames

    off, size, stereo = header_offset(index)
    raw_header = buf[off:off + size]
    info = {
        "name": Path(wav_path).stem[:8],
        "offset_channel1_start": start_off,
        "offset_channel1_end": end_off,
        "start": start_off,
        "end": end_off,
        "loop_start": start_off,
        "sample_rate": sample_rate,
        "sample_tune": 0,
        "play_level": 100,
        "stretch_step": 0,
        "stereo": num_channels == 2,
    }
    new_raw = pack_sample_header(info, raw_header)
    buf[off:off + size] = new_raw
    esx.data.samples.entries[index].raw = bytes(new_raw)


def play_audio(data: bytes, sample_rate: int, stereo: bool) -> None:
    """Play audio data using simpleaudio if available."""
    try:
        import simpleaudio as sa
    except Exception as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("simpleaudio module is required for preview") from exc

    channels = 2 if stereo else 1
    sa.play_buffer(data, channels, 2, sample_rate).wait_done()

