import gspread
from google.oauth2.service_account import Credentials
import time, os, sys

TERMINAL_WIDTH = 78

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

class InvestmentGame():
    """
    the class of the game to be played
    """
    def __init__(self):
        self.ROUNDS = 5
        self.ptf_amount = 1000.00
        self.difficulty = ""
        self.rounds_data = {}

    def menu(self):
        """
        Method that welcomes the player and shows the start menu
        """
        self.ptf_amount = 1000.00
        self.difficulty = ""
        self.rounds_data = {}

        print("                    ", end="")
        print_with_attention("THE INVESTMENT GAME")
        
        print_throughout("_", False)
        print_into_menu("MENU", True, True, True)
        print_throughout("-", True)
        
        print_into_menu("Welcome to the investment game!", True, False, False)
        print_throughout(" ", True)
        print_into_menu(f"You have a portfolio of 3 securities and one cash account. You have to allocate {self.ptf_amount:.2f}€ to them, at the beginning of the game. You will play 5 rounds. Each round you can re-allocate your money and see how it gains profits! But be careful there are costs - Please read the rules! At the end, your final portfolio value will be ranked amongst other players. Are you be the best investor?", 
            True, False, False)
        print_throughout("-", True)
        print_into_menu("Enter a number:", True, False, True)
        print_throughout(" ", True)
        print_into_menu("1. start", True, False, True)
        print_into_menu("2. rules", True, False, False)
        print_into_menu("3. rankings", True, False, False)
        print_into_menu("4. exit game", True, False, False)
        print_throughout("_", True)

        while True:
            try:
                menu_input = int(input("Enter a number (1 to 4):"))

                if not isinstance(menu_input, int) or menu_input > 4 or menu_input < 1:
                    raise ValueError
                if menu_input == 1:
                    self.start()
                elif menu_input == 2:
                    self.rules()
                elif menu_input == 3:
                    self.rankings()
                elif menu_input == 4:
                    exit()
                else:
                    self.menu()

                break
            except ValueError:
                delete_last_line()
                print("Please select a number between 1 and 4")
                time.sleep(1)
                delete_last_line()

        self.menu()


    def start(self):
        """
        Method that starts the game
        """
        self.difficulty = self.set_difficulty()
        self.see_results()


    def rules(self, difficulty=None):
        print("rules:(highlight the play mode if the user has already selected one)")
        input("hit any key to continue: ")

    
    def rankings(self):
        print("select the difficulty for which you want to see the ranking..")
        input("hit any key to continue: ")


    def see_results(self):
        print("see here your results")
        input("hit any key to continue: ")

    def set_difficulty(self):
        """
        The player choses either 'easy', 'medium' or 'hard' mode as a game difficulty
        """
        print("\033[1mSelect a game mode: \033[0m\n")
        print("1. easy")
        print("2. medium")
        print("3. hard")
        while True:
            try:
                diff_input = int(input("Enter a number (1 to 4):"))
                if not isinstance(diff_input, int) or diff_input > 3 or diff_input < 1:
                    raise ValueError
                break

            except ValueError:
                delete_last_line()
                print("Not valid. Please enter a number between 1 and 3")
                time.sleep(1)
                delete_last_line()
        
        return diff_input


def Round():
    """

    """


# printing functions ############################
def print_with_attention(str):
    """
    function that prints a text slowly to gather attention - I like it 
    """
    for i in str:
        print(f"\033[1;47;30m{i}\033[0m", end="\033[47;30m \033[0m")
        time.sleep(0.15)

    time.sleep(0.5)
    print("\n")

def print_throughout(char, with_border):
    """
    This function prints one character throughout the the line, fitting into the menu format
    suitable for borders 
    """
    total = TERMINAL_WIDTH
    if with_border:
        print("|", end="")
        total -= 1
    for i in range(total):
        print(char, end="")
    if with_border:
        print("|", end="")
    print("")

def print_into_menu(str, with_border, centralized, bold):
    """
    This function prints a string that fits into the menu width and format 
    """
    total = TERMINAL_WIDTH
    str_start = ""
    str_bold_in = ""
    str_bold_out = ""
    str_centr_in = ""
    str_centr_out = ""
    str_end = ""

    if with_border:
        str_start = "|"
        str_end = "|"
        total -= 1
    
    if bold:
        str_bold_in = "\033[1m"
        str_bold_out = "\033[0m"

    str = [str[i:i+total] for i in range(0, len(str), total)]

    for sub_str in str:
        if centralized:
            str_centr_in = (total - len(sub_str)) // 2
        else:
            str_centr_in = 1
        
        str_centr_out = total-str_centr_in-len(sub_str)
        if str_centr_out < 0:
            str_centr_in = 0

        str_centr_in *= " "
        str_centr_out *= " "
        print(str_start + str_centr_in + str_bold_in + sub_str + str_bold_out + str_centr_out + str_end)
    
def delete_last_line():
    "Deletes the last line in the STDOUT"
    # cursor up one line
    sys.stdout.write('\x1b[1A')
    # delete last line
    sys.stdout.write('\x1b[2K')
    

game = InvestmentGame()
game.menu()