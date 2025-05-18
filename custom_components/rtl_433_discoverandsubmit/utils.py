import json
from importlib import resources


def load_device_mappings():
    """Load device mappings bundled with the integration."""
    path = resources.files(__package__).joinpath("device_mappings.json")
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)
