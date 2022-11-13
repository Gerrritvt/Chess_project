import lichess.api
from datetime import datetime
from functions import progress_message, yesterday_message, send_simple_message, grades_history
from credentials import username, mail_api_url, key, sender, to


if __name__ == "__main__":
    # API calls
    user = lichess.api.user(username)
    games = lichess.api.user_games(username, max=100, perfType='blitz', analysed=True, opening=True, evals=True)
    games_2 = lichess.api.user_games(username, max=200, perfType='blitz', analysed=True, opening=True, evals=True)

    # Progress text
    progress_string = progress_message(user)

    # Yesterday update
    yesterday_string = yesterday_message(games, username)
    
    # Recent games update
    recent_games_string = grades_history(games_2, username, min_played=5)
    print(recent_games_string)

    # Send email
    date = datetime.now().strftime("%d-%m-%Y")
    subject = f"Lichess update {date}"
    text = f"{progress_string}\n\n{yesterday_string}\n\n{recent_games_string}"
    send_simple_message(mail_api_url, key, sender, to, subject, text)
    print("Email succesful")