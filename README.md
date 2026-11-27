# autodaily

A lightweight, Windows-first pixel and template-matching macro starter built in Python.

## Setup (Windows)

1. **Create and activate a virtual environment:**
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Game display settings:**
   Set your target game to **Borderless** or **Windowed** mode (exclusive fullscreen can cause black screenshots).

> **Note:** If a game runs as Administrator, Windows blocks input from non-elevated scripts. Run your terminal as Administrator if clicks/keys aren't registering.

## Workflow

### 1. Pick coordinates & pixel colors
Edit `TARGET_WINDOW` in `picker.py` (e.g., `"Notepad"`, `"Genshin Impact"`, `"Honkai: Star Rail"`), then run:
```powershell
python picker.py
```
Hover over any UI element in the target window and press **F8** to print its normalized `(x, y)` coordinates and RGB color. Press **Esc** to exit.

Normalized coordinates (`0.0` to `1.0`) are relative to the window's size, so your macro still works if you move or resize the window.

### 2. Run the macro
Update `TARGET_WINDOW` and your pixel/template rules in `main.py`, then run:
```powershell
python main.py
```
Press **F12** at any time to stop the macro immediately.
