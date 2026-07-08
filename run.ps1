$venv = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $venv) { . $venv }
python main.py
