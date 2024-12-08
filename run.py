import gspread
from google.oauth2.service_account import Credentials
import time

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

CREDS = Credentials.from_service_account_file("creds.json")
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open("investment_game")

secs = SHEET.worksheet("securities")
data = secs.get_all_values()

class investment_game():
    """
    the class of the game to be played
    """
    def __init__(self):
        self.rounds = 5
        self.ptf_amount = 1000.00
        self.difficulty = ""
        self.rounds_data = {}

    def set_difficulty(self):
        """
        The player choses either 'easy', 'medium' or 'hard' mode as a game difficulty
        """
        diff = input("")

    def start(self):
        """
        Method that welcomes the player, starts the game and fills the dictionary with data each round
        """
        print("")
        self.difficulty = self.set_difficulty()

def print_with_attention(str):
    """
    function that prints a text slowly to gather attention - I like it 
    """
    for i in str:
        print(i, end=" ")
        time.sleep(0.3)
        
    time.sleep(1)
    print()

print_with_attention("\033[1mTHE INVESTMENT GAME\033[0m\n")
