from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv


def load_env_file() -> None:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if env_path.exists():
        load_dotenv(env_path)

