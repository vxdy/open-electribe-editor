from open_electribe_editor_py import ESXFile, esx_constants as C
from pathlib import Path
import struct


def parse_sample_header(raw: bytes) -> dict:
    """Return a dictionary with parameters from a sample header."""
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


def main() -> None:
    path = Path("ESX-Factory-Data.esx")
    if not path.exists():
        print(f"File not found: {path}")
        return

    esx = ESXFile.from_file(path)
    print("Loaded ESX file:")
    print(f"- size: {len(esx.to_bytes())} bytes")
    print(f"- global params: {len(esx.data.global_params.raw)} bytes")
    print(f"- patterns: {len(esx.data.patterns.entries)}")
    print(f"- songs: {len(esx.data.songs.entries)}")
    print(f"- sample headers: {len(esx.data.samples.entries)}")

    parsed_samples = [parse_sample_header(s.raw) for s in esx.data.samples.entries]
    names = [s["name"] for s in parsed_samples]
    print("Sample names:")
    print(names)
    print("Sample parameters:")
    for idx, sample in enumerate(parsed_samples):
        print(idx, sample)


if __name__ == "__main__":
    main()
