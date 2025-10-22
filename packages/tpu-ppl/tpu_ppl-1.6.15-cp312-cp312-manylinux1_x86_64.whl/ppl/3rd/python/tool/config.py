import json, os, hashlib
from itertools import chain

config_path = os.path.join(
  os.environ["PPL_RUNTIME_PATH"], "chip")
chip_map = {}

def load_chip_map(config_file=None):
  """
  Load chip_map from a config file (JSON format).
  If config_path is None, use default 'chip_map.json' in the same directory.
  """
  global chip_map
  if config_file is None:
    config_file = os.path.join(config_path, "chip_map_dev.json")
  if not os.path.exists(config_file):
    config_file = os.path.join(config_path, "chip_map.json")
  if os.path.exists(config_file):
    with open(config_file, "r", encoding="utf-8") as f:
      chip_map = json.load(f)
  else:
    raise FileNotFoundError(f"Chip map config file not found: {config_file}")

def get_chip_code(chip_name):
  """
  Get the chip code for a given chip name.
  """
  if chip_name not in list(chain.from_iterable(chip_map.items())):
      raise ValueError(f"Invalid chip name {chip_name}")
  if chip_name in chip_map:
    return chip_map[chip_name]
  return chip_name

def get_chip_name(chip_code):
  """
  Get the chip name for a given chip code.
  """
  if chip_code not in list(chain.from_iterable(chip_map.items())):
      raise ValueError(f"Invalid chip code {chip_code}")
  for k, v in chip_map.items():
      if v == chip_code:
          return k
  return chip_code
