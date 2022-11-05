import lichess.api
from datetime import datetime
from functions import progress_message, yesterday_message, send_simple_message
from credentials import username, mail_api_url, key, sender, to


if __name__ == "__main__":
    # API calls
    user = lichess.api.user(username)
    games = lichess.api.user_games(username, max=100, perfType='blitz', analysed=True, opening=True, evals=True)

    # Progress text
    progress_string = progress_message(user)

    # Yesterday update
    yesterday_string = yesterday_message(games, username)
    
    # Send email
    date = datetime.now().strftime("%d-%m-%Y")
    subject = f"Lichess update {date}"
    text = f"{progress_string}\n\n{yesterday_string}"
    send_simple_message(mail_api_url, key, sender, to, subject, text)
    print("Email succesful")


