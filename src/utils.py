"""Utility functions."""

import os

import yaml


def get_config() -> dict:
    """Read the configuration for the app."""
    config = {}
    try:
        with open("config.yaml", encoding="utf-8") as f:
            config = yaml.safe_load(os.path.expandvars(f.read()))
    except Exception as e:
        print(f"Exception occurred when reading configuration: {e}")
    return config
