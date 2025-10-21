@echo off
REM SPDX-License-Identifier: Apache-2.0
REM SPDX-FileCopyrightText: 2025 Thomas@chriesibaum.com

if exist ".venv" (
    echo Activating virtual environment...
    call .venv\Scripts\activate
) else (
    echo Virtual environment not found. Let's create it first.
    python -m venv .venv

    call .venv\Scripts\activate

    python -m pip install --upgrade pip

    if exist "requirements.txt" (
        echo Installing requirements from requirements.txt...
        pip install -r requirements.txt
    ) else (
        echo No requirements.txt found, skipping dependency installation.
    )

    echo Virtual environment setup complete and ready to use.
)