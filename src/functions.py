from typing import Generator
import requests, lichess.api, math, re
from datetime import datetime, timedelta

def send_simple_message(mail_api_url:str, key:str, sender:str, to:str, subject:str, text:str):
    """Send a text email.

    Args:
        mail_api_url (str): mail api.
        key (str): Key for the mail api.
        to (str): Receiving email adress.
        subject (str): Email subject.
        text (str): Email text.

    Returns:
        No returns.
    """
    requests.post(
        mail_api_url,
        auth=("api", key),
        data={"from": sender,
            "to": to,
            "subject": subject,
            "text": text})


def am_winner(game:dict, username:str) -> bool:
    """Determines who is the winner of a game.

    Args:
        game (dict): The game that was played.
        username (str): Username on Lichess.

    Returns:
        bool: Whether the user won or not.
    """
    if "winner" in game.keys():
        winner = game['winner']
        if game['players'][winner]['user']['name'] == username:
            return True
        else:
            return False


def am_white(game:dict, username:str) -> bool:
    """Determines if the user was white or black.

    Args:
        game (dict): The game that was played.
        username (str): Username on Lichess.

    Returns:
        bool: Whether the user was white or not.
    """
    if game['players']['white']['user']['name'] == username:
        return True
    else:
        return False


def game_move_list(game:dict) -> list:
    """Creates a list of game moves.

    Args:
        game (dict): The game that was played.

    Returns:
        list: List of played moves.
    """
    move_list = game['moves'].split(' ')
    moves = []
    for i in range(math.ceil((len(move_list) / 2))):
        moves.append(move_list[2*i:2*i+2])
    return moves


def progress_message(user:dict) -> str:
    """Creates a progress message.

    Args:
        user (dict): The user on Lichess.

    Returns:
        str: The massage about the progress of the user.
    """
    rating = user['perfs']['blitz']['rating']
    progress = user['perfs']['blitz']['prog']
    return f"Current rating: {rating}({progress})."


def yesterday_message(games:Generator[dict, None, None], username:str) -> str:
    """Creates a message about games played yesterday.

    Args:
        games (Generator): Object from Lichess API.

    Returns:
        str: The message about the games played yesterday.
    """
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_dmj = (yesterday.day, yesterday.month, yesterday.year)

    outcomes_yesterday = []
    openings = []
    for game in games:
        result_str = ''
        time = game["createdAt"]
        time = datetime.fromtimestamp(time/1000)
        if (time.day, time.month, time.year) == yesterday_dmj:
            if am_winner(game, username):
                outcomes_yesterday.append(1)
                result_str = '(W), '
            if not am_winner(game, username):
                outcomes_yesterday.append(0)
                result_str = '(L), '
            if 'opening' in game.keys():
                made_mistake, move_nr = opening_mistake(game, username)
                if made_mistake:
                    analysis_string = f"opening mistake in move {move_nr}"
                else:
                    analysis_string = f"no opening mistake"
                openings.append(f"{game['opening']['name']}{result_str}{analysis_string}")

    yesterday_played_string = f"Played {len(outcomes_yesterday)} games yesterday, won {outcomes_yesterday.count(1)}, lost {outcomes_yesterday.count(0)}."
    nl = '\n'
    nlk = ',\n\n'
    mistakes = [opening for opening in openings if "move" in opening]
    no_mistakes = [opening for opening in openings if not "move" in opening]
    mistakes.sort(key=lambda test_string : list(map(int, re.findall(r'\d+', test_string)))[0])
    openings = mistakes + no_mistakes  # sort openings
    openings_string = f"Openings played:{nl}{nlk.join(openings)}"
    return f"{yesterday_played_string}\n\n{openings_string}"

def opening_mistake(game:dict, username:str) -> tuple[bool, int]:
    """Determines whether an opening mistake was made and in which move.

    Args:
        game (dict): Game dictionary from the Lichess API>

    Returns:
        tuple[bool, int]: Whether a mistake was made and in which move.
    """
    boolean = False
    for move_nr, eval in enumerate(game['analysis']):
        if move_nr == 16:  # threshold for openining theory.
            break
        elif move_nr % 2 == 0:  # Moves by white
            if am_white(game, username):
                if 'judgment' in eval.keys():
                    if eval['judgment']['name'] in ['Mistake', 'Blunder']:
                        boolean = True
                        break
        else:  # Moves by black
            if not am_white(game, username):
                if 'judgment' in eval.keys():
                    if eval['judgment']['name'] in ['Mistake', 'Blunder']:
                        boolean = True
                        break
    return boolean, int(math.ceil((move_nr / 2)) + 1) 