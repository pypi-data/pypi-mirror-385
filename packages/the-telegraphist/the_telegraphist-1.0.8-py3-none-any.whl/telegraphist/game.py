import threading
import time
from pathlib import Path

from playsound3 import playsound
from rich.console import Console
from rich.control import Control

# from rich.live import Live
from rich.panel import Panel

from .input import start_listening
from .levels import levels

# from .levels import levels
from .morse_code import MORSE_CODE_DICT

# Get the directory where this module is located
_MODULE_DIR = Path(__file__).parent
_SFX_DIR = _MODULE_DIR / "sfx"

current_input = ""
input_lock = threading.Lock()

feedback_message: str = ""

current_level_index = 0
current_letter_index = 0
player_input_for_letter = ""

# These state variables will handle all the timer logic
word_start_time: float = time.time()
word_time_limit: float = 15.0
game_over: bool = False

listener_stop_event: threading.Event | None = None


def display_title_screen() -> None:
    console = Console()
    console.clear()

    title_art = r"""
  ▗▄▄▄▖▗▄▄▄▖▗▖   ▗▄▄▄▖ ▗▄▄▖▗▄▄▖  ▗▄▖ ▗▄▄▖ ▗▖ ▗▖▗▄▄▄▖ ▗▄▄▖▗▄▄▄▖
  █  ▐▌   ▐▌   ▐▌   ▐▌   ▐▌ ▐▌▐▌ ▐▌▐▌ ▐▌▐▌ ▐▌  █  ▐▌     █
  █  ▐▛▀▀▘▐▌   ▐▛▀▀▘▐▌▝▜▌▐▛▀▚▖▐▛▀▜▌▐▛▀▘ ▐▛▀▜▌  █   ▝▀▚▖  █
  █  ▐▙▄▄▖▐▙▄▄▖▐▙▄▄▖▝▚▄▞▘▐▌ ▐▌▐▌ ▐▌▐▌   ▐▌ ▐▌▗▄█▄▖▗▄▄▞▘  █

- . .-.. . --. .-. .- .--. .... .. ... -
"""

    console.print(f"[bold cyan]{title_art}[/bold cyan]", justify="center")

    input("\n \n" + " " * 35 + "Press Enter to Start Transmission...")


def handle_new_char(char: str) -> None:
    """Handles space key press to morse code

    Adds . or - to current input box according to user's duration to hold a space bar

    Args:
        char (str): The symbol translated from user input, either . or -
    """
    global current_input
    with input_lock:
        current_input += char


def reset_game_state() -> None:
    """Resets all game state variables to their initial values for a new game."""
    global current_input, player_input_for_letter, current_level_index, current_letter_index
    global feedback_message, word_start_time, word_time_limit, game_over

    current_input = ""
    player_input_for_letter = ""
    current_level_index = 0
    current_letter_index = 0
    feedback_message = ""
    word_start_time = time.time()
    word_time_limit = 15.0
    game_over = False


def start_game() -> None:
    """Event to render the game UI

    Handles positioning of cursor, it's visibility and ensures clearing terminal before and after the game.
    """
    global current_input, player_input_for_letter, current_level_index, current_letter_index, feedback_message
    global word_time_limit, word_start_time, listener_stop_event

    while True:
        display_title_screen()
        display_tutorial()

        reset_game_state()

        word_start_time = time.time()

        listener_stop_event = threading.Event()

        listener_thread = threading.Thread(target=start_listening, args=(handle_new_char, listener_stop_event))
        listener_thread.daemon = True
        listener_thread.start()

        console = Console()
        should_retry = False

        try:
            console.control(Control.show_cursor(False))
            console.clear()

            while not game_over:
                current_level_data = levels[current_level_index]
                target_word = current_level_data["word"]

                if current_letter_index >= len(target_word):
                    console.clear()
                    playsound(str(_SFX_DIR / "level_up.wav"), block=False)

                    current_level_index += 1

                    if current_level_index >= len(levels):
                        msg = "[bold green]Congratulations! You completed all levels![/bold green]"
                        console.print(Panel(msg, border_style="green"))
                        input("\n" + " " * 40 + "Press Enter to Continue...")
                        break
                    else:
                        completed_msg = f"[bold green]Level {current_level_data['level']} Complete! Transmitted: {current_level_data['word']}[/bold green]"  # noqa: E501
                        console.print(Panel(completed_msg, border_style="green"))
                        next_level = levels[current_level_index]["level"]
                        next_msg = f"[cyan]Get ready for Level {next_level}...[/cyan]"
                        console.print(Panel(next_msg, border_style="cyan"))
                        time.sleep(2)

                    current_letter_index = 0
                    word_start_time = time.time()

                game_loop()

                console.control(Control.home())

                if current_letter_index < len(target_word):
                    current_char = target_word[current_letter_index]
                    correct_morse = MORSE_CODE_DICT[current_char]
                    complexity = analyse_word(current_char)
                    word_time_limit = (complexity["dots"] * 0.5) + (complexity["dashes"] * 1.0) + 2.0

                    time_remaining = word_time_limit - (time.time() - word_start_time)
                    time_remaining = max(0, time_remaining)

                    cheat_sheet = f"Transmit '{current_char}': [bold cyan]{correct_morse}[/bold cyan]"
                    transmission_panel = Panel(
                        f"[bold red]Time Remaining: {time_remaining:.1f}s[/bold red]\n\n"
                        f"{cheat_sheet}\n\nYour Input: {player_input_for_letter}",
                        title="Telegraph Console",
                        border_style="cyan",
                    )

                    console.print(transmission_panel)

                    if feedback_message:
                        console.print(Panel(feedback_message, border_style="yellow"))
                        feedback_message = ""

                time.sleep(0.05)

            if game_over:
                console.clear()
                current_level_data = levels[current_level_index]
                target_word = current_level_data["word"]

                game_over_art = r"""
 ▗▄▄▖ ▗▄▖ ▗▖  ▗▖▗▄▄▄▖     ▗▄▖ ▗▖  ▗▖▗▄▄▄▖▗▄▄▖
▐▌   ▐▌ ▐▌▐▛▚▞▜▌▐▌       ▐▌ ▐▌▐▌  ▐▌▐▌   ▐▌ ▐▌
▐▌▝▜▌▐▛▀▜▌▐▌  ▐▌▐▛▀▀▘    ▐▌ ▐▌▐▌  ▐▌▐▛▀▀▘▐▛▀▚▖
▝▚▄▞▘▐▌ ▐▌▐▌  ▐▌▐▙▄▄▖    ▝▚▄▞▘ ▝▚▞▘ ▐▙▄▄▖▐▌ ▐▌
"""
                console.print(f"[bold red]{game_over_art}[/bold red]", justify="center")
                console.print("\n")

                stats_msg = "[yellow]You ran out of time![/yellow]\n\n"
                stats_msg += f"[cyan]Level Reached:[/cyan] {current_level_data['level']}\n"
                stats_msg += f"[cyan]Word:[/cyan] {target_word}\n"
                stats_msg += f"[cyan]Letters Transmitted:[/cyan] {current_letter_index}/{len(target_word)}"

                console.print(Panel(stats_msg, title="Transmission Failed", border_style="red"))

                console.print("\n[bold cyan]Would you like to try again?[/bold cyan]")
                console.print("[green]1.[/green] Replay Game")
                console.print("[red]2.[/red] Exit")

                choice = input("\n" + " " * 40 + "Enter your choice (1 or 2): ").strip()

                if choice == "1":
                    should_retry = True
                    console.clear()

        except KeyboardInterrupt:
            pass

        finally:
            # Stop the listener thread
            if listener_stop_event:
                listener_stop_event.set()
                time.sleep(0.1)  # Give the thread time to stop

            console.control(Control.show_cursor(True))

        # If not retrying, break out of the main loop
        if not should_retry:
            break

    # Print final message only once, after the main loop
    console = Console()
    console.print("[bold blue]Thank You for playing![/bold blue]")


def game_loop() -> None:
    """Handles core logic of each level

    This function checks for the value of current level and forwards that data to UI
    It also plays sounds if a word is correct or wrong
    """

    global current_input, player_input_for_letter, current_letter_index, feedback_message
    global game_over, word_time_limit, word_start_time

    current_level_data = levels[current_level_index]
    target_word = current_level_data["word"]

    elapsed_time = time.time() - word_start_time

    if elapsed_time > word_time_limit:
        game_over = True
        return

    if current_letter_index >= len(target_word):
        return

    current_char = target_word[current_letter_index]
    correct_morse = MORSE_CODE_DICT[current_char]

    with input_lock:
        if current_input:
            player_input_for_letter += current_input
            current_input = ""

        if player_input_for_letter == correct_morse:
            playsound(str(_SFX_DIR / "success.wav"), block=False)
            current_letter_index += 1
            player_input_for_letter = ""
            feedback_message = f"Correct: '{current_char}'"
            word_start_time = time.time()

        elif not correct_morse.startswith(player_input_for_letter):
            playsound(str(_SFX_DIR / "error.wav"), block=False)
            feedback_message = "[bold red]Wrong Code![/bold red]"
            player_input_for_letter = ""


def analyse_word(word: str) -> dict[str, int]:
    """Counts dots and slashes in a word.

    Accepts a string word, loops through each character, and then through each
    symbol of its morse code to count if it is a dot or a dash.

    Args:
        word (str): A word from a level

    Returns:
        dict[str, int]: Returned from counting the symbols in word
    """
    return_data: dict[str, int] = {"dots": 0, "dashes": 0}
    for char in word:
        morse = MORSE_CODE_DICT[char]
        for symbol in morse:
            if symbol == ".":
                return_data["dots"] += 1
            elif symbol == "-":
                return_data["dashes"] += 1

    return return_data


def type_text(console: Console, text: str) -> None:
    """Displays text with a typing effect character by character.

    Args:
        console (Console): The Rich console instance
        text (str): The text to display with typing effect
    """
    for char in text:
        console.print(char, end="")
        time.sleep(0.02)


def display_tutorial() -> None:
    """Displays the mission briefing and tutorial before the game starts."""
    console = Console()
    console.clear()

    # Connection sequence
    type_text(console, "> CONNECTING TO FIELD OPERATOR TERMINAL...\n")
    time.sleep(0.5)
    type_text(console, "> CONNECTION ESTABLISHED.\n")
    time.sleep(0.5)
    console.print("> AUTHENTICATION: [bold green]VALID[/bold green]")
    time.sleep(2)

    type_text(console, "\n> INCOMING MESSAGE...\n")
    time.sleep(1)

    console.clear()

    mission_text = """Operator.

Your mission is critical. You are our last line of communication.

You will receive messages that must be transmitted immediately.
Time is of the essence. Each transmission is on a strict timer.

Failure is not an option."""

    mission_panel = Panel(mission_text, border_style="red", title="[bold red]CLASSIFIED[/bold red]")
    console.print(mission_panel)

    input("\n" + " " * 30 + "Press Enter to review transmission protocol...")

    console.clear()

    protocol_text = """[bold cyan]TRANSMISSION PROTOCOL:[/bold cyan]

1. A target word will be displayed.
2. A 'cheat sheet' will show the required Morse code for each letter.
3. Use your [bold yellow]SPACEBAR[/bold yellow] to transmit the signal.

   • A [bold cyan]short tap[/bold cyan] sends a DOT (.).
   • A [bold cyan]long press[/bold cyan] sends a DASH (-).

[bold red]Transmit with speed and precision. The world is listening.[/bold red]"""

    protocol_panel = Panel(protocol_text, border_style="cyan", title="[bold cyan]FIELD MANUAL[/bold cyan]")
    console.print(protocol_panel)

    input("\n" + " " * 30 + "Press Enter to begin your first transmission...")
