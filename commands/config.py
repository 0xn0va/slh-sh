from pathlib import Path
import yaml


def load_config():
    """Load the configuration values from the config.yaml file."""
    config_path = Path.cwd() / "config.yaml"
    with open(config_path, "r") as f:
        # use safe_load instead load
        config = yaml.safe_load(f)

    return config
