# Snap OCR

Snap OCR is a cross-platform tray utility that grabs a screenshot in the background, runs Tesseract OCR, and saves both PNG and TXT outputs. The app stays out of the way: press the global hotkey, capture happens, and you keep working.

For a fully detailed reference (including troubleshooting matrices) see `src/snap_ocr/__main__.py`. The highlights below cover the essentials.

## Features

- Global hotkey capture using `pynput` (default `<ctrl>+<shift>+s`, configurable).
- Full screen, fixed region, Windows FancyZones, or macOS MacsyZones capture modes.
- Timestamped filenames with optional overwrite mode that keeps only the most recent capture.
- Background OCR via `pytesseract`, atomic writes, and user-configurable save locations.
- Smart pre-processing (grayscale + contrast boost) for sharper OCR results on dense exam layouts.
- Tray controls for quick actions (Take Screenshot, Toggle Overwrite, open folders, reload config, view logs, quit).
- Tray icon flashes a green check badge after verifying the PNG/TXT pair landed in your save folders.
- Zero network access; outputs and logs stay on your machine.

## Release Highlights

### v0.3.1

- Added a success badge overlay on the tray icon so you know the screenshot + OCR files are on disk without leaving your workflow.
- Updated the macOS build script with an `--install` flag that syncs the `.app` into `/Applications` (or falls back to `~/Applications`) automatically, keeping Spotlight pointed at the latest build.

### v0.3.0

- Fixed MacsyZones capture so repositioned layouts map 1:1 with on-screen zones.
- Improved OCR fidelity by pre-processing captures and normalizing multi-choice labels (no more duplicated letters).
- Added version metadata and refreshed install instructions for packaged and PyPI deployments.

## Prerequisites

- Python 3.10 or newer.
- Tesseract OCR installed and on your `PATH`, or set `tesseract_cmd` in the config file.
- macOS users must grant Screen Recording + Accessibility rights; Windows users just need Tesseract.

## Installation

### pipx (recommended)

1. Download or clone this repository.
2. In the project root run:
   ```bash
   pipx install .
   ```
3. Launch with `snap-ocr` (no terminal needs to remain open; the app continues from the tray).

`pipx` isolates the app in its own virtual environment and drops a `snap-ocr` command on your `PATH`. On Windows the shim is placed in `%USERPROFILE%\.local\bin`.

### From a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate            # or .venv\Scripts\activate on Windows
python -m pip install -r requirements.txt
python -m pip install -e .
python -m snap_ocr
```

To run a one-off capture without starting the tray: `snap-ocr --capture-once`.

## Usage Overview

- **Start the tray app:** `snap-ocr`
- **Global hotkey:** `<ctrl>+<shift>+s` (customize via `config.yaml`).
- **CLI helpers:**
  - `snap-ocr --capture-once` – Immediate capture then exit.
  - `snap-ocr --show-config-path` – Print the active config file path.
  - `snap-ocr --open-config` – Open the config in your default editor/finder.

The tray icon exposes menu items for the capture mode, overwrite toggle, reloading the config, opening output directories, viewing logs, and quitting.

## Configuration

The first launch writes `config.yaml` to the OS-specific config directory (`~/Library/Application Support/snap-ocr/config.yaml` on macOS, `%APPDATA%\snap-ocr\config.yaml` on Windows).

Key fields:

| Setting | Description |
| --- | --- |
| `hotkey` | `pynput` syntax string for the global hotkey (`"<option>+<shift>+s"`, etc.). |
| `save_dir_images`, `save_dir_text` | Output folders for PNG and text files. |
| `filename_pattern` | Naming template; supports `{base}` and `{timestamp}` placeholders. |
| `overwrite_mode` | If `true`, the previous capture files are deleted after each successful save. |
| `capture_mode` | One of `full`, `region`, `fancyzones`, or `macsyzones`. |
| `region` | Coordinates used when `capture_mode: region`. |
| `macsyzones_*` / `fancyzones_*` | Options for their respective zone integrations. |

Validation errors surface immediately with the file path and a suggested fix. After editing, choose **Reload Config** from the tray or restart the app.

## Platform Notes

### macOS

- Grant Screen Recording + Accessibility (and Input Monitoring if prompted) to the Python host or packaged app.
- Optional auto-start: place a `LaunchAgent` pointing to your `pipx` interpreter, then `launchctl load` it.
- **MacsyZones**: Snap OCR reads layouts from `~/Library/Application Support/MeowingCat.MacsyZones/UserLayouts.json`, honoring the zone numbers shown in the MacsyZones editor (1 = top-left, 2 = bottom-left, 3 = top-right, 4 = bottom-right). Captures are taken in raw pixels, so on Retina displays the saved PNG dimensions are 2× the values displayed in MacsyZones; the crop area is identical.

### Windows

- Installing Tesseract (UB Mannheim build recommended) is the only prerequisite; no special capture permissions are required.
- FancyZones mode reads Windows PowerToys configuration to align screenshots with zone layouts.
- You can pin `snap-ocr.exe` (from `%USERPROFILE%\.local\bin`) to the Start menu or drop a shortcut in `shell:startup` for launch-at-login.

## Packaging (macOS)

1. `pipx install pyinstaller` (or `python -m pip install pyinstaller`).
2. Run `scripts/build_mac_app.sh` to generate `dist/Snap OCR.app` (automatically converts the icon to `.icns`). Add `--install` to copy the bundle into `/Applications` (falls back to `~/Applications` if permissions are denied) so Spotlight sees the latest build without manual copying.
3. Update `scripts/sign_and_notarize.sh` with your Developer ID and notarytool profile, then execute it to sign/notarize/staple the bundle.
4. Launch the notarised app once to trigger the permission prompts.

## Troubleshooting Quick Hits

- **Hotkey doesn’t fire (macOS):** reopen System Settings → Privacy & Security to confirm Accessibility permission.
- **Black screenshots (macOS):** Screen Recording access missing or revoked.
- **No text output:** verify Tesseract path/language packs and that the captured region contains legible text.
- **Audible “bonk” sound on hotkey:** change `hotkey` to avoid combinations that the focused app doesn’t recognize.
- **Files not overwritten:** confirm `overwrite_mode: true`; the tool deletes the previous PNG/TXT pair immediately before writing the next capture.

---

If you plan to distribute Snap OCR, consider publishing to PyPI so others can install with `pip install snap-ocr`. Until then, installing from this repository via `pipx install .` remains the quickest path.
