# Repository Guidelines

## Project Structure & Module Organization

This is a Python/Pygame UNO project. `main.py` is the application entry point and initializes Pygame, audio, the card atlas, and the active screen loop. Core code lives in `scripts/`: `game_manager.py` owns UNO rules and state, `screens.py` handles screen flow, `ui.py` renders UI, `multiplayer.py` contains lobby/host/client networking, and smaller modules cover cards, deck creation, AI, sprites, assets, and animation. Runtime assets are under `assets/`, including sprites, music, sound effects, fonts, and enhanced UI packs. `task.md` tracks project tasks, and `uno_spec.pdf` is the game reference.

## Build, Test, and Development Commands

- `py -m venv .venv` creates a local virtual environment.
- `.\.venv\Scripts\Activate.ps1` activates it on PowerShell.
- `pip install -r requirements.txt` installs the pinned dependency, currently `pygame==2.6.1`.
- `python main.py` runs the game locally.
- `python -m compileall main.py scripts` performs a quick syntax/import-path sanity check without launching the UI.

There is no separate build step for this repository.

## Coding Style & Naming Conventions

Use 4-space indentation and keep Python code type-annotated where practical, matching the existing `-> None`, `Optional[...]`, and `tuple[...]` style. Use `snake_case` for functions, variables, and module-level helpers; use `PascalCase` for classes such as `UnoGameManager` and `MultiplayerHost`. Keep asset lookups centralized through `scripts.assets.asset_path()` rather than hard-coded relative paths. Prefer small rule/state helpers in `game_manager.py` and keep drawing-only logic in `ui.py`.

## Testing Guidelines

No automated test suite is currently present. For logic changes, add focused `pytest` tests under a new `tests/` directory, using names like `test_game_manager.py` and `test_multiplayer_serialization.py`. Prioritize deterministic tests for card rules, draw/skip/reverse behavior, 0/7 custom rules, serialization, and host-side action validation. Always run `python -m compileall main.py scripts`; for UI or asset changes, also run `python main.py` and manually smoke-test title, settings, gameplay, and multiplayer screens.

## Commit & Pull Request Guidelines

Recent history uses short imperative messages and occasional prefixes such as `feat:`, `fix:`, and `task:`. Prefer `feat: add lobby refresh`, `fix: validate wild color`, or another concise imperative subject. Pull requests should include a short summary, testing notes, linked tasks/issues when available, and screenshots or short clips for UI-visible changes.

## Security & Configuration Tips

Treat multiplayer input as untrusted. Keep the host authoritative, validate all client actions server-side, sanitize serialized payloads, and avoid exposing room passwords or local network details in logs. Do not commit secrets, generated caches, `.venv/`, `__pycache__/`, or unlicensed replacement assets.
