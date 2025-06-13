# run_analyzer.ps1
Set-Location -Path "$PSScriptRoot\.."
.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "$PWD\src"
.venv\Scripts\python.exe scripts\main_analyzer.py