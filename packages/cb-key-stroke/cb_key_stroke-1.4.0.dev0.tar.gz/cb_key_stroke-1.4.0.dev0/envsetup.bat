@echo off
REM SPDX-License-Identifier: Apache-2.0
REM SPDX-FileCopyrightText: 2025 Thomas@chriesibaum.dev

if exist ".venv" (
    echo Activating virtual environment...
    call .venv\Scripts\activate
) else (
    echo Virtual environment not found. Let's create it first.
    python -m venv .venv

    call .venv\Scripts\activate

    python -m pip install --upgrade pip

    if exist "pyproject.toml" (
        echo Installing requirements from pyproject.toml...
        pip install .

        echo.
        set /p install_dev="Do you want to install the development environment with additional tools (autopep8, etc.)? [y/N]: "
        if /i "%install_dev%"=="y" (
            echo Installing development dependencies...
            pip install -e ".[dev]"
            echo Development environment installed successfully!
        ) else (
            echo Skipping development dependencies installation.
        )
    ) else (
        echo No pyproject.toml found, skipping dependency installation.
    )

    echo Virtual environment setup complete and ready to use.
)