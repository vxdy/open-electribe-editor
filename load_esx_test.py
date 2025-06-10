from open_electribe_editor_py import ESXFile
from pathlib import Path


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


if __name__ == "__main__":
    main()
