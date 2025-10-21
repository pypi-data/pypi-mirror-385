#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2025 Thomas@chriesibaum.com

if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "Virtual environment not found. Let's create it first."
    python -m venv .venv

    source .venv/bin/activate

    pip install --upgrade pip

    if [ -f "requirements.txt" ]; then
        echo "Installing requirements from requirements.txt..."
        pip install -r requirements.txt
    else
        echo "No requirements.txt found, skipping dependency installation."
    fi

    echo "Virtual environment setup complete and ready to use."
fi


