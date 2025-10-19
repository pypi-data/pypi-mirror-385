"""
This module contains the level data for The Telegraphist.
Each level is defined by a word that the player must transmit.
"""

from typing import Any

levels: list[dict[str, Any]] = [
    {"level": 1, "word": "SOS"},
    {"level": 2, "word": "SIGNAL"},
    {"level": 3, "word": "VOYAGER"},
    {"level": 4, "word": "DANGER"},
    {"level": 5, "word": "AVOIDED"}
]
