# Python Reimplementation (Work in Progress)

This directory provides an initial Python 3 reimplementation of selected
utilities from the original Open Electribe Editor.  The goal is to gradually
replace the Java code with Python equivalents.

Currently implemented modules:

- `extended_byte_buffer.py` &ndash; a minimal drop-in replacement for the Java
  `ExtendedByteBuffer` class supporting unsigned reads and writes.
- `esx_constants.py` &ndash; constants describing the ESX file layout.
- `esx_util.py` &ndash; small helpers for byte conversions and validating an ESX
  file.
- `esx_file.py` &ndash; provides the `ESXFile` class for loading and saving ESX
  data.
- `esx_structs.py` &ndash; simple dataclasses for storing parsed ESX sections
  such as global parameters, patterns, songs and sample headers.

These modules are **not** feature complete but serve as a starting point for a
full Python translation.
