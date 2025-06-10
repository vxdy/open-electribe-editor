import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import struct

from open_electribe_editor_py import ESXFile, esx_constants as C


def parse_sample_header(raw: bytes) -> dict:
    """Return a dictionary of parameters from a sample header."""
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
    """Return new raw bytes for a sample header from info."""
    out = bytearray(raw)
    name_bytes = info.get("name", "").encode("ascii", errors="ignore")[:8]
    out[0:8] = name_bytes.ljust(8, b"\x00")
    if info.get("stereo"):
        struct.pack_into(">I", out, 8, info["offset_channel1_start"])
        struct.pack_into(">I", out, 12, info["offset_channel1_end"])
        struct.pack_into(">I", out, 16, info["offset_channel2_start"])
        struct.pack_into(">I", out, 20, info["offset_channel2_end"])
        struct.pack_into(">I", out, 24, info["start"])
        struct.pack_into(">I", out, 28, info["end"])
        struct.pack_into(">I", out, 32, info["sample_rate"])
        struct.pack_into(">h", out, 36, info["sample_tune"])
        out[38] = info["play_level"] & 0xFF
        struct.pack_into(">b", out, 39, info["unknown_stereo1"])
        out[40] = info["stretch_step"] & 0xFF
        struct.pack_into(">b", out, 41, info["unknown_stereo2"])
        struct.pack_into(">b", out, 42, info["unknown_stereo3"])
        struct.pack_into(">b", out, 43, info["unknown_stereo4"])
    else:
        struct.pack_into(">I", out, 8, info["offset_channel1_start"])
        struct.pack_into(">I", out, 12, info["offset_channel1_end"])
        struct.pack_into(">I", out, 16, info["start"])
        struct.pack_into(">I", out, 20, info["end"])
        struct.pack_into(">I", out, 24, info["loop_start"])
        struct.pack_into(">I", out, 28, info["sample_rate"])
        struct.pack_into(">h", out, 32, info["sample_tune"])
        out[34] = info["play_level"] & 0xFF
        struct.pack_into(">b", out, 35, info["unknown_mono1"])
        out[36] = info["stretch_step"] & 0xFF
        struct.pack_into(">b", out, 37, info["unknown_mono2"])
        struct.pack_into(">b", out, 38, info["unknown_mono3"])
        struct.pack_into(">b", out, 39, info["unknown_mono4"])
    return bytes(out)

def header_offset(index: int) -> tuple[int, int, bool]:
    """Return (offset, size, stereo) for sample header at index."""
    if index < C.NUM_SAMPLES_MONO:
        off = C.ADDR_SAMPLE_HEADER_MONO + index * C.CHUNKSIZE_SAMPLE_HEADER_MONO
        return off, C.CHUNKSIZE_SAMPLE_HEADER_MONO, False
    idx = index - C.NUM_SAMPLES_MONO
    off = C.ADDR_SAMPLE_HEADER_STEREO + idx * C.CHUNKSIZE_SAMPLE_HEADER_STEREO
    return off, C.CHUNKSIZE_SAMPLE_HEADER_STEREO, True


class ESXGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ESX Sample Editor")
        self.geometry("800x400")

        self.esx: ESXFile | None = None
        self.sample_info = []

        top = tk.Frame(self)
        top.pack(fill=tk.X)

        tk.Button(top, text="Open ESX", command=self.load_file).pack(side=tk.LEFT)
        tk.Button(top, text="Save ESX", command=self.save_file).pack(side=tk.LEFT)

        body = tk.Frame(self)
        body.pack(fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(body, width=30)
        self.listbox.pack(side=tk.LEFT, fill=tk.Y)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        edit_frame = tk.Frame(body)
        edit_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.entries = {}
        for i, field in enumerate(["name", "start", "end", "sample_rate", "sample_tune", "play_level"]):
            tk.Label(edit_frame, text=field).grid(row=i, column=0, sticky=tk.W)
            ent = tk.Entry(edit_frame)
            ent.grid(row=i, column=1, sticky=tk.EW)
            self.entries[field] = ent
        edit_frame.columnconfigure(1, weight=1)
        tk.Button(edit_frame, text="Apply", command=self.apply_changes).grid(row=6, column=0, columnspan=2)

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("ESX Files", "*.esx")])
        if not path:
            return
        try:
            self.esx = ESXFile.from_file(Path(path))
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to load file: {exc}")
            return
        self.sample_info = [parse_sample_header(s.raw) for s in self.esx.data.samples.entries]
        self.listbox.delete(0, tk.END)
        for idx, info in enumerate(self.sample_info):
            name = info.get("name", f"Sample {idx}")
            self.listbox.insert(tk.END, f"{idx:03d}: {name}")

    def on_select(self, event=None):
        if not self.listbox.curselection():
            return
        idx = self.listbox.curselection()[0]
        info = self.sample_info[idx]
        for field, ent in self.entries.items():
            ent.delete(0, tk.END)
            val = info.get(field, "")
            ent.insert(0, str(val))

    def apply_changes(self):
        if self.esx is None or not self.listbox.curselection():
            return
        idx = self.listbox.curselection()[0]
        info = self.sample_info[idx]
        for field, ent in self.entries.items():
            text = ent.get()
            if field == "name":
                info[field] = text
            else:
                try:
                    info[field] = int(text)
                except ValueError:
                    messagebox.showwarning("Warning", f"Invalid value for {field}")
                    return
        off, size, stereo = header_offset(idx)
        info["stereo"] = stereo
        raw = self.esx.buffer.as_bytearray()[off:off+size]
        new_raw = pack_sample_header(info, raw)
        self.esx.buffer.as_bytearray()[off:off+size] = new_raw
        self.esx.data.samples.entries[idx].raw = bytes(new_raw)
        self.listbox.delete(idx)
        self.listbox.insert(idx, f"{idx:03d}: {info.get('name','')}" )

    def save_file(self):
        if self.esx is None:
            return
        path = filedialog.asksaveasfilename(defaultextension=".esx", filetypes=[("ESX Files", "*.esx")])
        if not path:
            return
        try:
            self.esx.save(Path(path))
            messagebox.showinfo("Saved", "File saved successfully")
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to save file: {exc}")


if __name__ == "__main__":
    app = ESXGUI()
    app.mainloop()
