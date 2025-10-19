@echo off

echo [=] Installation...

:: Create a virtual environment if it doesn't exist
if not exist venv (
    echo [-] Creating virtual environment...
    python -m venv .venv
    echo [+] Virtual environment created
)

:: Activate virtual environment
echo [-] Activating virtual environment...
call .venv/Scripts/activate
echo [+] Virtual environment activated

:: Install dependencies
echo [-] Updating pip...
python -m pip install --upgrade pip
echo [+] Updated pip

echo [-] Installing requirements...
pip install -r requirements.txt
echo [+] Installed requirements

:: Ask user to install wauxio from PyPI, locally specified path, or default ../..
echo [=] Select where to install from wauxio library:
echo To install from local source enter path (or leave empty: default ../..)
echo ? to install from PyPI
echo * to skip installation
set /p option="<path>/<>/<?>/<*>: "

if /i "%option%" == "*" (
    echo [+] wauxio installation skipped
) else if /i "%option%"=="?" (
    echo [-] Installing wauxio from PyPI...
    pip install wauxio
    echo [+] Installed wauxio
) else if /i "%option%"=="" (
    echo [-] Installing wauxio from ../..
    pip install -e ../..
    echo [+] Installed wauxio
) else (
    echo [-] Installing wauxio from %option%
    pip install -e %option%
    echo [+] Installed wauxio
)

echo [=] Installation finished
