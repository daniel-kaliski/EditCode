# EditCode 

**EditCode** is a lightweight, fast, and modern Integrated Development Environment (IDE) built in Python using the PyQt6 library. The core of the code editor is the **Monaco Editor** engine (the exact same one that powers Visual Studio Code), ensuring smooth syntax highlighting and IntelliSense (smart code completion).

The project has been optimized for a modern Dark Mode interface and native integration with macOS, while maintaining full compatibility with Windows and Linux.

---

## Key Features

* **Modern, flat interface:** No bright system borders. A 100% customized Dark Mode theme.
* **Monaco Editor inside PyQt6:** Utilizes Chromium rendering (WebEngine) to support an advanced, feature-rich code editor.
* **Multi-tab support:** Conveniently work with multiple files at once, featuring a dynamic `+` button for opening new tabs and protection against losing unsaved changes.
* **Integrated Terminal:** Built-in system console at the bottom of the screen (supports Zsh, Bash, and PowerShell).
* **Instant code execution:** The `▶ Run` button automatically detects and executes `.py` (Python), `.js` (Node.js), and shell scripts (`.sh`, `.bat`), outputting the result directly to the integrated terminal.
* **Project Explorer:** Built-in file tree for easy folder navigation.
* **Auto-completion (Snippets):** Predefined, intelligent code blocks for Python (e.g., auto-generating `for` loops, `def` definitions, or the `if __name__ == "__main__":` block).
* **Bilingual:** The application automatically adjusts the language (English / Polish) based on the operating system settings.

---

## System Requirements

To run the source code, you need **Python 3.x** installed along with the `pip` package manager.

Install the required dependencies:

```bash
pip install PyQt6 PyQt6-WebEngine
```

---

## Running the App

To run the application directly from the script, open a terminal in the project folder and type:

```bash
python3 EditCode.py
```
*(On Windows systems, use the `python EditCode.py` command)*

---

## Compiling to a Native App (macOS)

EditCode is ready to be built as a full-fledged native application (`.app` file on macOS) using the PyInstaller tool. This process integrates special instructions that force a 100% dark title bar and a native system "About" window.

1. Make sure you have PyInstaller installed:
   ```bash
   pip install pyinstaller
   ```
2. Build the application using the dedicated configuration file:
   ```bash
   pyinstaller EditCode.spec
   ```
3. Once the process is complete, you will find the standalone **`EditCode.app`** application inside the `dist` folder.

---

## Keyboard Shortcuts

* `Ctrl + N` (or `Cmd + N`) - New file
* `Ctrl + O` (or `Cmd + O`) - Open file
* `Ctrl + S` (or `Cmd + S`) - Save current file

---

## License and Copyright

**EditCode** Copyright © 2026 Daniel Kaliski. All rights reserved.
