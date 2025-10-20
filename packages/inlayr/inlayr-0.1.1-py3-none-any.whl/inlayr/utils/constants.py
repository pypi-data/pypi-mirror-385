"""
Library-wide default endpoints and configurations.
Override any of them via environment variables.
"""

import os
import yaml

from importlib.resources import files

data_yaml = files(__package__).joinpath("defaults.yaml").read_bytes()
defaults: dict[str, str] = yaml.load(data_yaml, Loader=getattr(yaml, "CSafeLoader", yaml.SafeLoader))

ConstDict = {
	k : os.getenv(k, v) for k, v in defaults.items()
}
