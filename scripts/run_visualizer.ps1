# run_visualizer.ps1
Set-Location -Path "$PSScriptRoot\.."
.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "$PWD\src"
.venv\Scripts\python.exe scripts\main_visualizer.py

#recomiendo en la pregunta, responder "todo", ya que el CSV de prueba no tiene tantos datos.