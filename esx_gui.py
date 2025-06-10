import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from open_electribe_editor_py import ESXFile, esx_constants as C, sample_manager


def parse_sample_header(raw: bytes) -> dict:
    """Wrapper around :func:`sample_manager.parse_sample_header`."""
    return sample_manager.parse_sample_header(raw)

def pack_sample_header(info: dict, raw: bytes) -> bytes:
    """Wrapper around :func:`sample_manager.pack_sample_header`."""
    return sample_manager.pack_sample_header(info, raw)

def header_offset(index: int) -> tuple[int, int, bool]:
    """Wrapper around :func:`sample_manager.header_offset`."""
    return sample_manager.header_offset(index)


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
        tk.Button(top, text="Import Sample", command=self.import_sample).pack(side=tk.LEFT)
        tk.Button(top, text="Delete Sample", command=self.delete_sample).pack(side=tk.LEFT)
        tk.Button(top, text="Preview", command=self.preview_sample).pack(side=tk.LEFT)

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

    def import_sample(self):
        if self.esx is None or not self.listbox.curselection():
            return
        idx = self.listbox.curselection()[0]
        wav_path = filedialog.askopenfilename(filetypes=[("WAV Files", "*.wav")])
        if not wav_path:
            return
        try:
            sample_manager.import_sample(self.esx, idx, wav_path)
            self.sample_info[idx] = parse_sample_header(self.esx.data.samples.entries[idx].raw)
            self.listbox.delete(idx)
            self.listbox.insert(idx, f"{idx:03d}: {self.sample_info[idx].get('name','')}")
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to import sample: {exc}")

    def delete_sample(self):
        if self.esx is None or not self.listbox.curselection():
            return
        idx = self.listbox.curselection()[0]
        sample_manager.delete_sample(self.esx, idx)
        self.sample_info[idx] = parse_sample_header(self.esx.data.samples.entries[idx].raw)
        self.listbox.delete(idx)
        self.listbox.insert(idx, f"{idx:03d}: {self.sample_info[idx].get('name','')}")

    def preview_sample(self):
        if self.esx is None or not self.listbox.curselection():
            return
        idx = self.listbox.curselection()[0]
        data = sample_manager.read_sample_data(self.esx, idx)
        info = self.sample_info[idx]
        try:
            sample_manager.play_audio(data, info.get("sample_rate", 44100), info.get("stereo", False))
        except Exception as exc:
            messagebox.showerror("Error", f"Preview failed: {exc}")

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
