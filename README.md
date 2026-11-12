# Nomina

**Nomina** is a batch file renamer with a clean Tkinter interface. Instead of one big "rename" dialog, you stack small, ordered **layers** (find & replace, remove digits, trim characters, add prefix/suffix, change case, change extension). A **live preview** shows exactly what every file will become before anything is touched, and every rename can be **undone**, even after restarting the program.

- Single Python file, standard library only (Tkinter)
- Runs on Linux (primary target); written to be cross-platform
- Interface in **English, Romanian and Italian**
- Drag & drop of files and folders (optional)

## Features

### Layers
Layers are applied from top to bottom. You can enable/disable each one, move it up or down, and delete it. The preview updates on every keystroke.

| Layer | What it does |
|---|---|
| **Find and replace** | Plain text or regular expression, with an optional case-sensitive match. Invalid regexes are reported inline. |
| **Remove digits / numbers** | Removes all digits, only leading digits, or only trailing digits. Optionally cleans leftover spaces and separators at the edges. |
| **Remove first / last characters** | Cuts *N* characters from the start and/or the end of the name. |
| **Remove brackets and their content** | Round `( )`, square `[ ]`, curly `{ }` and angle `< >` (tags), nested ones included; optionally keeps the content and removes only the symbols. |
| **Remove special characters** | Characters forbidden in file names, all symbols (keeps letters, digits, space and `_ - .`), everything that is not ASCII, or a custom set of characters, optionally replaced with a character of your choice. |
| **Remove diacritics** | `ă â î ș ț → a a i s t`, and the same for every accented letter (`é ü ñ ç`) plus `ß æ œ ø đ ł`. |
| **Add at start / end** | Adds a prefix and/or a suffix. The suffix goes before the extension. |
| **Insert text at a position** | Inserts text at the start, at the end, after the first *N* characters, or before the last *N* characters. |
| **Numbering** | Sequential numbers with a chosen number of digits (`1`, `01`, `001`), start value and step, text before/after the number (`SE01`, `01SE`), the same position options as above, and an option to restart the count in every folder. |
| **Date and time** | Inserts the file's creation date (or last-modified date, or the current date and time) with any `strftime` format, text before/after, and the same position options. |
| **Parent folder name** | Adds the name of the folder (or of a folder some levels up) as a prefix/suffix, with a format such as `Folder - `, `[Folder]`, `(FOLDER)`, `_Folder`, in original, lowercase or uppercase letters. |
| **Upper / lower case** | lowercase, UPPERCASE, Title Case, or Sentence case. |
| **Naming style** | `snake_case`, `UPPER_SNAKE_CASE`, `kebab-case`, `camelCase` or `PascalCase`. Words are split at spaces, `_ - .` and at lower→upper case changes. |
| **Extension** | Change to a given extension, lowercase it, uppercase it, or remove it. |

All layers except **Extension** work on the file name only and never touch the extension. The **Extension** layer touches only the extension.

On Linux the creation date is read with `stat` (Python's standard library does not expose it); if the file system does not record it, the modification date is used instead.

### Apply a layer only to some files

Every layer has an **Apply to** setting: all files, only some extensions (`jpg, png`), all but some extensions, only names that contain a text, or only names that do not. The check is made against the *original* file name, and numbering counts only the files the layer applies to.

### Presets

The **Presets** menu saves the current stack of layers under a name and loads it back later (or deletes it). Presets are stored on disk and survive restarts.

### Suggest

The **Suggest** button looks at the file names in the list and builds a stack of layers it considers appropriate: it removes website addresses, bracketed text such as `[1080p]`, problematic characters, repeated spaces and stray separators, turns ALL-CAPS titles into Title Case and lowercases uppercase extensions. If you already have layers, it asks whether to replace them or add the suggestions after them. It **never renames anything**: it only fills in the layers, so you can review the preview, tweak or remove layers, and press *Rename* yourself.

### Live preview

The main table shows **Source → Destination** for every file, plus its status:

- unchanged files are greyed out,
- files that will be renamed are shown in green,
- problems are highlighted in red: *invalid name*, *duplicate* (two files would get the same name), *already exists*, or *missing* (the source file disappeared).

The **Rename** button is only enabled when there is something to rename, and it refuses to run while there are errors.

### Safe renaming and undo/redo

- Renaming is done in two phases through temporary names, so swaps and chains (`a → b`, `b → a`) work correctly.
- If anything fails halfway, **everything is rolled back** and nothing is changed.
- **Undo / Redo** work on whole batches and the history is saved to disk (last 100 batches), so you can undo a rename even after closing and reopening Nomina.
- If some files were moved or deleted in the meantime, undo applies what it can, skips the rest and tells you how many were skipped.

### Adding files

- **Add files** and **Add folder** buttons (optionally including subfolders; hidden files starting with `.` are skipped when scanning folders).
- **Drag & drop** files or folders onto the window (see [Drag & drop](#drag--drop)).
- Click the **Source** column header to sort the list (natural order: `file2` before `file10`).

### Other

- Window position, size, language and the "include subfolders" option are remembered between runs.
- The window has a minimum size so buttons are never clipped, in any language.
- The language is detected from the system on first launch and can be changed from the selector at any time.
- Buttons have their own icons (embedded in the program, no extra image files needed).

### Keyboard shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+O` | Add files |
| `Ctrl+Z` / `Ctrl+Y` | Undo / Redo (disabled while typing in a text field) |
| `Del` | Remove selected files from the list |
| `Ctrl+A` | Select all files in the list |

## Requirements

- Python **3.7+**
- Tkinter (on Debian/Ubuntu: `sudo apt install python3-tk`)
- Optional, for drag & drop: the `tkdnd` Tcl extension **or** the `tkinterdnd2` Python package

## Running from source

```sh
python3 nomina.py
```

### Drag & drop

Drag & drop needs one of the following. Without them Nomina works normally, just without dropping files onto the window.

```sh
sudo apt install tkdnd          # native Tcl extension, works on any architecture
# or
pip install tkinterdnd2
```

Nomina tries `tkinterdnd2` first and falls back to the system `tkdnd`.

## Installing as a .deb package

### Architecture-independent (tiny, recommended)

```sh
sudo apt install ./nomina_1.0.0_all.deb
```

- `Architecture: all` – the same package works on any CPU architecture (about 40 KB).
- Depends on `python3 (>= 3.7)` and `python3-tk`; recommends `tkdnd` for drag & drop (`DND_DEP=Depends` makes it mandatory).
- Build requirement: only `dpkg-deb`. No internet, no pip.

### Standalone (bundles Python and Tk)

```sh
sudo apt install python3 python3-venv python3-tk binutils dpkg-dev   # build machine only
sudo apt install ./nomina_1.0.0_standalone_ubuntu_amd64.deb
# or
sudo apt install ./nomina_1.0.0_standalone_debian_amd64.deb
```

- Compiled with PyInstaller (`--onedir`, no UPX), so the target machine needs no Python or Tk.
- Only the native drag & drop library matching the build machine's architecture and Tk version (8.6 or 9.0) is included.
- `Depends:` is computed automatically from the system libraries the bundle actually uses.
- The result is architecture-specific and tied to the glibc of the machine it was built on; build on the oldest distribution you want to support.
- Build requirement: internet access (pip downloads `pyinstaller` and `tkinterdnd2`).

Both scripts accept `MAINTAINER="Name <mail@example.com>"` and `KEEP=1` (keep the build directory).

## Where settings are stored

| System | Location |
|---|---|
| Linux | `~/.config/Nomina/` |
| Windows | `%APPDATA%\Nomina\` |
| macOS | `~/Library/Application Support/Nomina/` |

It contains `config.json` (window geometry, language, options) and `history.json` (undo/redo history). Removing the package does not delete them.

## Limitations

- Only files are renamed, not folders.
- Files are renamed in place (the folder never changes).
- Extensions are split at the last dot, so `archive.tar.gz` has the extension `.gz`.
- Layers are not saved between sessions (only the undo history is).

## Repository layout

```
nomina.py            the whole program (icons embedded)
```

## 📄 License

This project is licensed under the GNU General Public License v3.0 (GPLv3). Anyone is free to modify and redistribute this software, provided that any derivative works are also open-sourced under the same license terms.
