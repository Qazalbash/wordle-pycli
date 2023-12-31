# MIT License

# Copyright (c) 2023 Meesum Qazalbash

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
import os
import random
import time

try:
    from .allowed_words import WORDS
except ImportError:
    from allowed_words import WORDS


def print_centered(text: str, width: int = 80) -> None:
    """Prints the given text centered within the given width.

    Parameters
    ----------
    text : str
        The text to be printed.
    width : int, optional
        Width of the text, by default 80
    """
    print(text.center(width))


def display_title_bar(title: str, width: int = 80) -> None:
    """Displays a title bar with the given title centered within it.

    Parameters
    ----------
    title : str
        The title to be displayed in the title bar.
    width : int, optional
        Width of the title bar, by default 80
    """

    horizontal_border = "─"
    vertical_border = "│"
    corner_top_left = "┌"
    corner_top_right = "┐"
    corner_bottom_left = "└"
    corner_bottom_right = "┘"
    reset_style = "\033[0m"

    title_text = f"{title}".center(width + 89)
    github_link = "https://github.com/Qazalbash/wordle-pycli".center(width - 5)

    inner_width = width - 5

    print(corner_top_left + (horizontal_border * inner_width) + corner_top_right)
    print(vertical_border + title_text + vertical_border)
    print(vertical_border + github_link + vertical_border)
    print(corner_bottom_left + (horizontal_border * inner_width) + corner_bottom_right + reset_style)


def display_game_board(guesses: str, width: int = 80) -> None:
    """Displays the game board with the given guesses.

    Parameters
    ----------
    guesses : str
        The guesses to be displayed on the game board.
    width : int, optional
        Width of the game board, by default 80
    """

    horizontal_border = "\033[100m─\033[0m"
    vertical_border = "\033[100m│\033[0m"
    corner_top_left = "\033[100m┌\033[0m"
    corner_top_right = "\033[100m┐\033[0m"
    corner_bottom_left = "\033[100m└\033[0m"
    corner_bottom_right = "\033[100m┘\033[0m"

    inner_width = width - 5
    padding = 35

    print_centered(corner_top_left + (horizontal_border * inner_width) + corner_top_right, width)

    for guess in guesses:
        guess_line = vertical_border + ' ' * padding + guess + ' ' * padding + vertical_border
        print_centered(guess_line, width)

    print_centered(corner_bottom_left + (horizontal_border * inner_width) + corner_bottom_right, width)


def update_keyboard_state(keyboard_state: dict, guess_word: str, target_word: str) -> dict:
    """Updates the keyboard state based on the given guess and target word.

    If a letter is present in the target word but not in the guess word, it is marked yellow.
    If a letter is present in the target word and in the guess word, it is marked green.
    If a letter is not present in the target word, it is marked black (dark grey).
    

    Parameters
    ----------
    keyboard_state : dict
        The current state of the keyboard.
    guess_word : str
        Guess word.
    target_word : str
        Target word.

    Returns
    -------
    dict
        Updated keyboard state.
    """

    for letter in set(guess_word):
        if letter not in keyboard_state:
            keyboard_state[letter] = "\033[100m" + letter + "\033[0m"

    for i, letter in enumerate(guess_word):
        if letter == target_word[i]:
            keyboard_state[letter] = "\033[42m" + letter + "\033[0m"

    for i, letter in enumerate(guess_word):
        if letter in target_word and keyboard_state.get(letter) != "\033[42m" + letter + "\033[0m":

            if guess_word.count(letter) > sum(
                    1 for j in range(len(target_word)) if guess_word[j] == letter and target_word[j] == letter):
                keyboard_state[letter] = "\033[43m" + letter + "\033[0m"

    return keyboard_state


def display_keyboard(keyboard_state: dict, width: int = 80) -> None:
    """Displays the keyboard with the given keyboard state.

    Parameters
    ----------
    keyboard_state : dict
        The current state of the keyboard.
    width : int, optional
        Width of the game board, by default 80
    """

    horizontal_border = "─"
    vertical_border = "│"
    corner_top_left = "┌"
    corner_top_right = "┐"
    corner_bottom_left = "└"
    corner_bottom_right = "┘"
    reset_style = "\033[0m"

    keyboard_rows = [' q w e r t y u i o p ', '  a s d f g h j k l  ', '   z x c v b n m   ']

    inner_width = max(len(row) for row in keyboard_rows)

    padding_left = (width - inner_width) // 2
    padding_right = width - inner_width - padding_left

    print(' ' * padding_left + corner_top_left + (horizontal_border * inner_width) + corner_top_right +
          ' ' * padding_right)

    for i, row in enumerate(keyboard_rows):

        padded_row = vertical_border

        for key in row:
            if key.isalpha():
                colored_key = keyboard_state.get(key, key)
                padded_row += colored_key
            else:
                padded_row += key

        if i == 2:
            padded_row += '  '
        padded_row += vertical_border

        print(' ' * padding_left + padded_row + ' ' * padding_right)

    print(' ' * padding_left + corner_bottom_left + (horizontal_border * inner_width) + corner_bottom_right +
          ' ' * padding_right + reset_style)


def wordle_guess(target_word: str, guess_word: str, keyboard_state: dict, current_progress: str) -> tuple[str, str]:
    """Creates a guess result and updates the keyboard state and current progress.
    
    Parameters
    ----------
    target_word : str
        The target word.
    guess_word : str
        The guess word.
    keyboard_state : dict
        The current state of the keyboard.
    current_progress : str
        The current progress of the game.

    Returns
    -------
    tuple[str, str]
        A tuple of the guess result and the current progress.
    """
    result = ""
    for i, letter in enumerate(guess_word):

        if letter == target_word[i]:
            result += f"\033[42m{letter}\033[0m"
            current_progress[i] = f"\033[42m{letter}\033[0m"
        elif letter in target_word:
            result += f"\033[43m{letter}\033[0m"
        else:
            result += f"\033[40m{letter}\033[0m"
    update_keyboard_state(keyboard_state, guess_word, target_word)

    progress_display = "".join(current_progress)
    return result, progress_display


def clear_screen() -> None:
    """Clears the screen.

    This function is taken from https://stackoverflow.com/a/684344
    """
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')


def display_score(stats: dict, max_bar_length=50, animation_speed=0.05, style='█', width=80) -> None:
    """Print an animated histogram with a trophy symbol next to the highest score.

    _extended_summary_

    Parameters
    ----------
    stats : dict
        Stats dictionary
    max_bar_length : int, optional
        Maximum length of the bar, by default 50
    animation_speed : float, optional
        Animation speed, by default 0.05
    style : str, optional
        Bar style, by default '█'
    width : int, optional
        Width of the histogram, by default 80
    """
    if not stats:
        print("No data to display.")
        return

    horizontal_border = "─"
    vertical_border = "│"
    corner_top_left = "┌"
    corner_top_right = "┐"
    corner_bottom_left = "└"
    corner_bottom_right = "┘"
    reset_style = "\033[0m"

    title_text = f"Score".center(width - 5)

    inner_width = width - 5

    print(corner_top_left + (horizontal_border * inner_width) + corner_top_right)
    print(vertical_border + title_text + vertical_border)
    print(corner_bottom_left + (horizontal_border * inner_width) + corner_bottom_right + reset_style)

    max_count = max(stats.values())

    scaling_factor = max_bar_length / max_count if max_count > max_bar_length else 1

    highest_attempts = [attempt for attempt, count in stats.items() if count == max_count]

    paading_left = (width - max_bar_length) // 2

    length = max_bar_length
    for attempt, count in stats.items():
        if count == 0:
            bar_length = 0
        else:
            final_bar_length = int(count * scaling_factor)
            bar_length = min(length, final_bar_length)

        score_display = f' {count}' if length >= bar_length and count != 0 else ''
        trophy_display = ' 🏆' if attempt in highest_attempts and length >= final_bar_length else ''
        print(' ' * paading_left + f'{attempt} {style * bar_length}{score_display}{trophy_display}')

    time.sleep(animation_speed)
    if length < max_bar_length:
        print(f"\033[{len(stats)}A", end='')


def update_stats(filename: str, attempt: int) -> None:
    """Update the stats file with the new attempt

    Parameters
    ----------
    filename : str
        filename of the stats file
    attempt : int
        attempt number
    """
    with open(filename, 'r') as f:
        stats = json.load(f)

    if attempt < 7:
        stats[str(attempt)] += 1

    display_score(stats, max_bar_length=30, animation_speed=0.05, style='.')

    with open(filename, 'w') as f:
        json.dump(stats, f)


def play_wordle() -> None:
    """Plays the Wordle game.

    The game is played in the terminal. The player has 6 attempts to guess a 5-letter word.
    """
    target_word = random.choice(WORDS)
    attempts = 6
    guesses = []
    keyboard_state = {}
    current_progress = ["*"] * len(target_word)

    clear_screen()
    colored_title = "\033[100mW\033[0m\033[42mO\033[0m\033[43mR\033[0m\033[100mD\033[0m\033[42mL\033[0m\033[43mE\033[0m \033[100mG\033[0m\033[42mA\033[0m\033[43mM\033[0m\033[100mE\033[0m"
    display_title_bar(colored_title, width=80)
    print_centered("Welcome to Wordle! You have 6 attempts to guess a 5-letter word.", width=80)

    while attempts > 0:
        guess_word = input("Enter your guess: ").lower().strip()

        if len(guess_word) != len(target_word) or guess_word not in WORDS:
            print(f"Please enter a valid {len(target_word)}-letter word from the word list.")
            continue

        guess_result, progress_display = wordle_guess(target_word, guess_word, keyboard_state, current_progress)
        guesses.append(guess_result)
        clear_screen()
        display_title_bar(colored_title, width=80)
        display_game_board(guesses, width=80)
        print(f"\nProgress: {progress_display}")
        print(f"Attempt: {7-attempts}")
        keyboard_state = update_keyboard_state(keyboard_state, guess_word, target_word)
        display_keyboard(keyboard_state, width=80)

        if guess_word == target_word:
            break

        attempts -= 1

    if guess_word == target_word:
        print("\nCongratulations, you've guessed the word!\n")
    else:
        print(f"\nSorry, you've run out of attempts. The word was '{target_word}'.\n")

    if not os.path.exists('stats.json'):
        with open('stats.json', 'w') as f:
            json.dump({str(i): 0 for i in range(1, 7)}, f)

    update_stats('stats.json', 7 - attempts)
