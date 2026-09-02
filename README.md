# Assistive Window Switcher

An always-on-top, translucent desktop assistive widget that instantly switches focus between the current active window/application and the last active window/application on click. 

## Features
- **translucent & Stays-on-top**: Idle at 50% opacity, fading smoothly to 90% opacity on hover with a snappy `120ms` animation.
- **State-Preserving Switch (Windows)**: Instantly switches active windows without altering their window size/maximization state.
- **Smooth Window Fades (Windows)**: Active windows smoothly fade into each other over a snappy `120ms` transition.
- **Cross-Platform (Windows & macOS)**: Tracks active application and handles switching natively on both Windows (via Win32 `ctypes`) and macOS (via `AppKit` / AppleScript).
- **Single Stand-Alone File**: Embedded base64 minimal icon ensures no external file dependencies at runtime.

---

## 🛠️ Setup & Running Locally

Ensure you have Python 3 and PyQt5 installed:

```bash
pip install PyQt5
```

For optimal performance on macOS, install `pyobjc`:

```bash
pip install pyobjc-core pyobjc-framework-Cocoa
```
*(If `pyobjc` is not installed, the widget automatically falls back to system AppleScript `osascript` calls).*

### Start the Widget:
```bash
python switcher.py
```

---

## 📦 Packaging Standalone Executables

Use PyInstaller to compile the python script into a single standalone executable.

### 🪟 Windows Compilation (Standalone EXE):
Install PyInstaller:
```bash
pip install pyinstaller
```

Compile:
```bash
pyinstaller --onefile --noconsole --icon="icon.ico" --name="AssistiveWindowSwitcher" switcher.py
```
This produces `dist/AssistiveWindowSwitcher.exe`.

### 🍎 macOS Compilation (Standalone APP Bundle):
Install PyInstaller:
```bash
pip install pyinstaller
```

Compile:
```bash
pyinstaller --onefile --noconsole --windowed --name="AssistiveWindowSwitcher" switcher.py
```
This produces `dist/AssistiveWindowSwitcher.app` (a native double-clickable Mac app bundle).

---

## 🕹️ Widget Controls
- **Left-Click & Drag**: Drag the floating button anywhere on the screen.
- **Left-Click (Release)**: Toggle/switch focus back to the last active window or application.
