import os

from mtcli.conf import config

SYMBOL = os.getenv("SYMBOL", config["DEFAULT"].get("symbol", fallback="WIN$N"))
DIGITOS = int(os.getenv("DIGITOS", config["DEFAULT"].getint("digitos", fallback=0)))
PERIOD = os.getenv("PERIOD", config["DEFAULT"].get("period", fallback="M1"))
BARS = int(os.getenv("BARS", config["DEFAULT"].getint("bars", fallback=566)))
STEP = float(os.getenv("STEP", config["DEFAULT"].getfloat("step", fallback=100)))
VOLUME = os.getenv("VOLUME", config["DEFAULT"].get("volume", fallback="tick"))
