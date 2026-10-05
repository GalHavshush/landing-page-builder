"""Migrations must build the same schema as the models (so autogenerate finds no drift)."""

from pathlib import Path

from alembic import command
from alembic.config import Config

API_DIR = Path(__file__).resolve().parent.parent


def alembic_config(url: str) -> Config:
    cfg = Config(str(API_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(API_DIR / "migrations"))
    cfg.cmd_opts = type("Opts", (), {"x": [f"url={url}"]})()
    return cfg


def test_upgrade_head_matches_models(tmp_path):
    cfg = alembic_config(f"sqlite:///{tmp_path / 'm.db'}")
    command.upgrade(cfg, "head")
    command.check(cfg)  # raises if models and migrations disagree
    command.downgrade(cfg, "base")
