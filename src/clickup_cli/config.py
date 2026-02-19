from pathlib import Path

import yaml

CONFIG_DIR = Path.home() / ".clickup-cli"
CONFIG_FILE = CONFIG_DIR / "config.yaml"


def load_config() -> dict:
    """Load config from ~/.clickup-cli/config.yaml."""
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Config not found at {CONFIG_FILE}. Run 'cl config init' to set up."
        )
    with open(CONFIG_FILE) as f:
        config = yaml.safe_load(f)
    if not config or "api_token" not in config:
        raise ValueError(
            "Config is missing 'api_token'. Run 'cl config init' to fix."
        )
    return config


def save_config(config: dict) -> None:
    """Save config to ~/.clickup-cli/config.yaml."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
