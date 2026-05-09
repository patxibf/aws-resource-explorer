import json
import os
from pathlib import Path
import re

DEFAULT_CONFIG_PATH = Path.home() / ".aws-explorer-config.json"
AWS_REGION_PATTERN = re.compile(r"^[a-z]{2}-[a-z]+-\d+$")

def load_config() -> dict:
    if DEFAULT_CONFIG_PATH.exists():
        with open(DEFAULT_CONFIG_PATH) as f:
            return json.load(f)
    return {}

def save_config(config: dict) -> None:
    old_umask = os.umask(0o077)
    try:
        with open(DEFAULT_CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)
    finally:
        os.umask(old_umask)

def get_regions(config: dict) -> list:
    return config.get("regions", [])

def interactive_setup() -> list:
    print("AWS Explorer first-run setup")
    print("Enter regions to scan, comma-separated (e.g., us-east-1, eu-west-1):")
    while True:
        regions_input = input("Regions: ").strip()
        regions = [r.strip() for r in regions_input.split(",") if r.strip()]
        invalid = [r for r in regions if not AWS_REGION_PATTERN.match(r)]
        if invalid:
            print(f"Invalid region format: {invalid}. Expected format: us-east-1")
            continue
        if regions:
            break
        print("At least one region is required.")
    return regions

def ensure_config() -> dict:
    config = load_config()
    if not config or "regions" not in config or not config["regions"]:
        regions = interactive_setup()
        config = {"regions": regions}
        save_config(config)
        print(f"Config saved to {DEFAULT_CONFIG_PATH}")
    return config