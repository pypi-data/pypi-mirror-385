#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2025 Thomas@chriesibaum.dev

if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "Virtual environment not found. Let's create it first."
    python -m venv .venv

    source .venv/bin/activate

    pip install --upgrade pip

    if [ -f "pyproject.toml" ]; then
        echo "Installing requirements from pyproject.toml..."
        pip install .

        echo ""
        read -p "Do you want to install the development environment with additional tools (autopep8, etc.)? [y/N]: " install_dev
        if [[ $install_dev =~ ^[Yy]$ ]]; then
            echo "Installing development dependencies..."
            pip install -e ".[dev]"
            echo "Development environment installed successfully!"
        else
            echo "Skipping development dependencies installation."
        fi
    else
        echo "No pyproject.toml found, skipping dependency installation."
    fi

    echo "Virtual environment setup complete and ready to use."
fi


