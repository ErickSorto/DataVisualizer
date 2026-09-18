# Data Visualizer

A Python desktop application for loading CSV and Excel files and creating simple data visualizations.

## User Flow

1. Browse for one or more `.csv` or `.xlsx` files.
2. Select the files to use.
3. Choose a chart type: pie, histogram, box plot, line, or scatter.
4. Enter the row or column labels/indexes and chart settings.
5. Select **Generate** to open the chart in a separate window.

Use **Reset** to clear the current files and settings and start over. Reset does not delete files from your computer.

## Requirements

- Python 3.11 or newer
- macOS, Windows, or Linux

The application uses PySide6 for the GUI, pandas and NumPy for data processing, and Matplotlib for charts.

## Installation for Users

Download the installer for your operating system from the project's GitHub Releases page:

- Windows: download the Windows installer or ZIP.
- macOS: download the macOS application ZIP.
- Linux: download the Linux package.

Open the downloaded file and follow the instructions for your operating system. No Python installation is required when using an installer.

## Installation for Developers

Clone the repository from GitHub, then open the project folder:

```bash
git clone <todo-url>
cd DataVisualizer
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, activate it with:

```powershell
.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run from Source

With the virtual environment active:

```bash
python main.py
```


## Development Notes

- Keep data-processing code in `core/` and interface code in `ui/`.
- Test with small CSV or Excel files before using larger datasets.
- Save spreadsheet changes before generating a chart so the application reads the latest file contents.
