"""Configuracoes da aplicacao."""
from __future__ import annotations

import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = PROJECT_ROOT / "app"


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def appdata_dir(app_name: str) -> Path:
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
    if base:
        return Path(base) / app_name
    return Path.home() / app_name


if is_frozen():
    DATA_DIR = appdata_dir("FluxoCaixa")
    OUTPUT_DIR = DATA_DIR / "output"
    ASSETS_DIR = DATA_DIR / "assets"
else:
    DATA_DIR = PROJECT_ROOT / "data"
    OUTPUT_DIR = PROJECT_ROOT / "output"
    ASSETS_DIR = PROJECT_ROOT / "assets"

DATABASE_PATH = DATA_DIR / "fluxo_caixa.db"

for folder in (DATA_DIR, OUTPUT_DIR, ASSETS_DIR):
    folder.mkdir(parents=True, exist_ok=True)


class Settings:
    """Configuracoes centralizadas da aplicacao."""

    APP_NAME = "Fluxo de Caixa"
    APP_VERSION = "1.0"
    WINDOW_SIZE = "1400x800"
    THEME = "cosmo"

    DB_PATH = DATABASE_PATH
    DATA_DIR = DATA_DIR
    OUTPUT_DIR = OUTPUT_DIR
    ASSETS_DIR = ASSETS_DIR

    @classmethod
    def get_database_path(cls) -> str:
        """Retorna caminho do banco de dados."""
        return str(cls.DB_PATH)
