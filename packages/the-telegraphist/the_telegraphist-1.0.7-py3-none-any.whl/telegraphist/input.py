import time
from collections.abc import Callable
from pathlib import Path

from playsound3 import playsound
from pynput import keyboard

DOT_DURATION: float = 0.2

press_time = None
key_down: bool = False

_MODULE_DIR = Path(__file__).parent
_SFX_DIR = _MODULE_DIR / "sfx"

def on_press(key: keyboard.Key | keyboard.KeyCode | None) -> None:
    """Handle spacebar press events for Morse code input.

    Tracks when the spacebar is pressed to measure hold duration.
    Prevents repeated key press events while the key is held down.

    Args:
        key: The keyboard key that was pressed.
    """
    global key_down, press_time

    if key == keyboard.Key.space and not key_down:
        key_down = True
        press_time = time.time()


def on_release(key: keyboard.Key | keyboard.KeyCode | None, on_char_received: Callable[[str], None]) -> None:
    """Handle spacebar release events and output Morse code symbols.

    Calculates the duration the spacebar was held and outputs either
    a dot (.) for short presses or a dash (-) for long presses.

    Args:
        key: The keyboard key that was released.
    """

    global key_down, press_time

    if key == keyboard.Key.space and press_time is not None:
        duration = time.time() - press_time

        if duration < DOT_DURATION:
            playsound(str(_SFX_DIR / "dot.wav"), block=False)
            on_char_received(".")
        else:
            playsound(str(_SFX_DIR / "dash.wav"), block=False)
            on_char_received("-")

        press_time = None
        key_down = False


def start_listening(on_char_received: Callable[[str], None]) -> None:
    """Start listening for keyboard input to capture Morse code.

    Creates a keyboard listener that monitors spacebar press and release
    events. This function blocks execution until the listener is stopped.
    """
    with keyboard.Listener(on_press=on_press, on_release=lambda key: on_release(key, on_char_received)) as listener:
        listener.join()
