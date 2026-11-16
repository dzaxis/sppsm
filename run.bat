@echo off
setlocal
cd /d "%~dp0"

echo =============================================
echo   SPPSM - Pengelolaan Penjemputan Sampah
echo =============================================
echo.

REM Gunakan uv jika terpasang.
where uv >nul 2>nul
if not errorlevel 1 goto run_uv

REM Jika uv tidak ada, gunakan Python.
where python >nul 2>nul
if errorlevel 1 goto no_python

python --version
python -c "import sys; exit(0 if sys.version_info >= (3, 13) else 1)"
if errorlevel 1 goto wrong_python

REM Pastikan dependency tersedia. Jika belum, coba pasang dari pyproject.toml.
python -c "import inquirer, prettytable, pwinput" >nul 2>nul
if errorlevel 1 (
    echo Dependency belum terpasang. Memasang aplikasi dan dependency...
    python -m pip install -e .
    if errorlevel 1 goto install_failed
)

REM Package berada di folder src dan perlu dimasukkan ke PYTHONPATH.
set "PYTHONPATH=%~dp0src;%PYTHONPATH%"
python -m sppsm.main
goto finish

:run_uv
uv run sppsm
goto finish

:no_python
echo [ERROR] Python tidak ditemukan. Instal Python 3.13 atau lebih baru.
goto failed

:wrong_python
echo [ERROR] Aplikasi memerlukan Python 3.13 atau lebih baru.
goto failed

:install_failed
echo [ERROR] Instalasi dependency gagal.
echo Pastikan koneksi internet tersedia dan pip sudah berfungsi.
goto failed

:failed
echo.
pause
exit /b 1

:finish
if errorlevel 1 (
    echo.
    echo [ERROR] Aplikasi berhenti dengan error.
    pause
    exit /b 1
)
endlocal
