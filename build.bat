@echo off
title Compilador Ferragil
setlocal

echo =======================================================
echo  Ferragil Backup
echo =======================================================
echo.
echo  REQUISITOS:
echo  - Python 2.7.18 32bits em C:\Python27
echo  - pip instalado (get-pip.py com Python 2.7)
echo.
echo =======================================================
echo.

set PYTHON=C:\Python27\python.exe
set PIP=C:\Python27\python.exe -m pip
set PATH=C:\Python27;C:\Python27\Scripts;%PATH%

if not exist "%PYTHON%" (
    echo [ERRO] Python 2.7 nao encontrado em C:\Python27
    pause
    exit /b 1
)
echo Python encontrado:
%PYTHON% --version
echo.

echo Instalando dependencias...
%PIP% install --user "pyinstaller==3.6"
%PIP% install --user "pywin32==228"
echo.

if not exist "FerragilBackup.pyw" (
    echo [ERRO] FerragilBackup.pyw nao encontrado.
    pause
    exit /b 1
)

if exist "FerragilBackup.ico" (
    echo Icone localizado: FerragilBackup.ico
    set ICON_FLAG=--icon "FerragilBackup.ico"
    set ADD_DATA_FLAG=--add-data "FerragilBackup.ico;."
) else (
    echo [AVISO] FerragilBackup.ico nao encontrado; EXE usara icone padrao.
    set ICON_FLAG=
    set ADD_DATA_FLAG=
)

echo Compilando...
%PYTHON% -m PyInstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --noupx ^
    %ICON_FLAG% ^
    %ADD_DATA_FLAG% ^
    --hidden-import=Tkinter ^
    --hidden-import=ttk ^
    --hidden-import=tkFileDialog ^
    --hidden-import=tkMessageBox ^
    --hidden-import=_winreg ^
    --hidden-import=json ^
    --hidden-import=ctypes ^
    --hidden-import=threading ^
    --hidden-import=collections ^
    --name FerragilBackup ^
    FerragilBackup.pyw

if exist "_tmp_logo.ico" del "_tmp_logo.ico"

echo.
if exist "dist\FerragilBackup.exe" (
    echo =======================================================
    echo  SUCESSO! dist\FerragilBackup.exe
    echo =======================================================
) else (
    echo =======================================================
    echo  FALHA - verifique o log do PyInstaller acima.
    echo =======================================================
)
pause
