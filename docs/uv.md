# UV - Package & Project Manager

## Installation

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Basic Usage

### Install dependencies
```bash
uv sync # will create .venv as well
```

### Run commands
```bash
uv run python main.py
uv run pytest
uv run scripts/some_script.py
uv run jupyter lab
```

### Add new packages
```bash
uv add requests
uv add --dev pytest
```

## Common Commands

| Command | What it does |
|---------|--------------|
| `uv sync` | Install all dependencies from pyproject.toml |
| `uv run` | Run a command in the project environment |
| `uv add <package>` | Add a new dependency |
| `uv remove <package>` | Remove a dependency |
| `uv pip list` | Show installed packages |
