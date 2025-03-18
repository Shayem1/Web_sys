@echo off
REM Ensure script runs from its directory
cd /d "%~dp0"

REM Install the required Python packages
python -m pip install --upgrade pip
python -m pip install customtkinter selenium tk

REM Start the Python script from the "python_stuff" folder and minimize the terminal window
start /min python "%~dp0python_stuff/WebComplex.py"

exit