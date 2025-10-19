from pathlib import Path
import sys
import os
import json


def load_config(config_path, cli_args):
    config = {
        "types": cli_args.types or ["pdf"],
        "depth": cli_args.depth,
        "output": cli_args.output,
    }

    if not config_path:
        config_path = get_config_dir("linkminer")

    config_path = set_config(
        config_file=set_config(os.path.join(config_path, "linkminer.json"))
    )

    if config_path:
        try:
            with open(config_path, "r") as f:
                file_config = json.load(f)
            config.update({k: file_config.get(k, config[k]) for k in config if k != ""})
        except Exception as e:
            print(f"[!] Failed to load config: {e}")
    return config


def get_config_dir(app_name="linkminer"):
    if sys.platform == "win32":
        base_dir = os.getenv("APPDATA")
        if not base_dir:
            base_dir = Path.home() / "AppData" / "Roaming"
    elif sys.platform == "darwin":
        base_dir = Path.home() / "Library" / "Application Support"
    else:  # Linux and other Unix
        base_dir = os.getenv("XDG_CONFIG_HOME", Path.home() / ".config")

    config_dir = Path(base_dir) / app_name
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def set_config(config_file):
    data = {
        "url": "",
        "types": ["pdf"],
        "depth": "",
        "output": "Downloads/linkminer_downloads/",
    }
    if not os.path.exists(config_file):
        with open(config_file, "w") as fp:
            json.dump(data, fp, indent=4)

    return config_file
