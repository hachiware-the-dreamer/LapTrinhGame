from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = PROJECT_ROOT / "assets"


def asset_path(*parts: str) -> Path:
    return ASSETS_DIR.joinpath(*parts)
