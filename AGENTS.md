# MDCx Agent Guide

## Setup

```bash
git clone https://github.com/sqzw-x/mdcx.git
cd mdcx
uv sync --all-extras --dev
uv run pre-commit install
uv pip install -e .
```

## Quick Commands

### Python (Backend)
```bash
# Lint & format (uses ruff)
uv run ruff check --fix
uv run ruff format

# Run tests
uv run pytest

# Run single test file
uv run pytest tests/test_utils.py
```

### TypeScript (UI Frontend)
```bash
cd ui
pnpm install
pnpm run ci          # biome check (CI mode)
pnpm run lint        # biome check --write
pnpm run build       # rsbuild build
```

## Project Structure

- `mdcx/` - Python backend (PyQt5 GUI + web server)
- `ui/` - TypeScript frontend (React + MUI, rsbuild)
- `tests/` - Python tests (pytest)
- `scripts/` - Build, bump, changelog utilities
- `resources/` - Static assets (images, etc.)
- `main.py` - Desktop app entry (PyQt5)
- `server.py` - Web server entry (FastAPI)

## Key Facts

- **Python 3.13.4+** required (`os.path.ALLOW_MISSING`)
- **Package manager**: `uv` (not pip)
- **Linter/formatter**: ruff (line-length=120)
- **Pre-commit**: runs `ruff check --fix` then `ruff format`
- **UI package manager**: pnpm
- **UI linter**: biome
- **UI build**: rsbuild
- **Build system**: PyInstaller (via `scripts/build.py`)

## Running the App

```bash
# Desktop (PyQt5 GUI)
uv run main.py

# Web server (FastAPI)
# First build UI: cd ui && pnpm i && pnpm build && cd ..
# Then:
uv run fastapi dev server.py
# or with env var for dev mode:
# Windows: $env:MDCX_DEV=1; fastapi dev server.py
# Linux/macOS: MDCX_DEV=1 fastapi dev server.py
```

**Note**: Web server serves built UI from `ui/dist/`. Build UI first with `pnpm build`.

## Version

Version is in `mdcx/consts.py` → `LOCAL_VERSION` (integer, e.g., 220250909).

## Testing

Tests use `pytest` with `pytest-asyncio`. Run full suite:
```bash
uvx pytest tests/ -v
```

## Code Style

- Ruff enforces: isort, pyupgrade, pycodestyle, pyflakes, flake8-bugbear
- Double quotes, 4-space indent
- `__init__.py` files have relaxed import rules

## Code Generation

- Qt UI → Python: `./scripts/pyuic.sh` (from `mdcx/views/*.ui` files)
- Enum generation: `uv run gen_enums`

## Qt UI

- Main window: `mdcx/views/MDCx.ui` (edit with Qt Designer)
- Event handlers: `mdcx/controllers/main_window/main_window.py` and `handlers.py`
- Signal init: `mdcx/controllers/main_window/init.Init_Singal`
