@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Подготовка игры. Это нужно только при первом запуске...
    py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)"
    if errorlevel 1 (
        echo Установите Python 3.12 или новее с python.org.
        pause
        exit /b 1
    )
    py -3 -m venv .venv
    if errorlevel 1 (
        echo Не удалось подготовить среду. Пришлите текст ошибки.
        pause
        exit /b 1
    )
)
".venv\Scripts\python.exe" -c "import pygame" >nul 2>&1
if errorlevel 1 (
    echo Установка Pygame. Для этого сейчас нужен интернет...
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Установка не завершена. Пришлите текст ошибки.
        pause
        exit /b 1
    )
)
".venv\Scripts\python.exe" main.py
if errorlevel 1 pause
