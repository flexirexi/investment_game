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
        print_into_menu("MENU", True, True, True, False, False)
        print_throughout("-", True)
        
        print_into_menu("Welcome to the investment game!", True, False, False, False, False)
        print_throughout(" ", True)
        print_into_menu(f"You have a portfolio of 3 securities and one cash account. You have to allocate {self.ptf_amount:.2f}€ to them, at the beginning of the game. You will play 5 rounds. Each round you can re-allocate your money and see how it gains profits! But be careful there are costs - Please read the rules! At the end, your final portfolio value will be ranked amongst other players. Are you be the best investor?", 
            True, False, False, False, False)
        print_throughout("-", True)
        print_into_menu("Enter a number:", True, False, True, False, False)
        print_throughout(" ", True)
        print_into_menu("1. start", True, False, True, False, False)
        print_into_menu("2. rules", True, False, False, False, False)
        print_into_menu("3. rankings", True, False, False, False, False)
        print_into_menu("4. exit game", True, False, False, False, False)
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
        previous_round_data = None
        for i in range(self.ROUNDS):
            current_round = Round(i+1, previous_round_data)
            current_round_data = current_round.play()
            self.rounds_data[f"round {i+1}"] = current_round_data
            previous_round_data = current_round_data
            print_game_history(i+1, self.rounds_data)
            input("Hit any key to continue: ")
        # end ########################################
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
                diff_input = int(input("Enter a number (1 to 3):"))
                if not isinstance(diff_input, int) or diff_input > 3 or diff_input < 1:
                    raise ValueError
                break
            except ValueError:
                delete_last_line()
                print("Not valid. Please enter a number between 1 and 3")
                time.sleep(1)
                delete_last_line()
        
        return diff_input


class Round():
    """
    A class for a round that creates a dictionary that will be a component of the InvestmentGame's dictionary
    """
    def __init__(self, round, difficulty, previous_round_data=None):
        self.round = round
        self.previous_round_data = previous_round_data
        self.difficulty = difficulty
        
        #dictionary content: they all consist of 4 numbers
        self.before_start_reallocate    = []    #when player changes start values: this is the delta between last round's end value and the new start value, BEFORE COSTS
        self.before_start_paytax        = []    #when player changes start values: taxes to be paid might occur when selling
        self.before_start_trnsx_costs   = []    #when player changes start values: transaction costs might occur when buying
        self.booking_value              = []    #all summed up pay-ins in history: not below 0; when higher than end value, then taxes might occur on the sale
        self.start_value                = []    #the values that the player can choose at the beginning of each round and might cause costs
        
        self.performance                = []    #the return of the securities (and cash)
        self.dividends                  = []    #sometimes, dividends occur, the player can decide to re-invest for free
        self.end_value                  = []    #the value at the end of the round, after return and dividend
        self.delta_start_end            = []    #the monetary delta between start value and end value

    
    def play(self):
        print_game_header()

        if self.previous_round_data == None: 
            #play the first round:
            print("Please \033[1mallocate 100 000€ to the above 3 securities and 1 cash\033[0m.")
            print("")
            while True:
                try:
                    alloc_input = [float(x) for x in input("4 two-digits numbers which sum up to 100 000€:").split(",")]
                    if not round(sum(alloc_input),2) == 100000.0:
                        raise SumUpError(f"\033[31mThe numbers don't sum up to 100 000€ (your total: {format(sum(alloc_input), ",.2f").replace(",", " ")})\033[0m")
                    if not len(alloc_input) == 4 or not isinstance(alloc_input, list):
                        raise ValueError
                    print(alloc_input)
                    break
                except ValueError:
                    print("\033[31mNot valid. Please enter 4 two-digits numbers, separated by commas\033[0m")
                    print("")
                except SumUpError as e:
                    print(e)
                    print("")
            
                time.sleep(1)
                delete_last_line()
            
            
            #the entered data will be handled as delta, since the previous rounds data dont exist in the first round
            self.pre_round(alloc_input)
            self.main_round()

        else:
            y=5

        return {}
    
    def pre_round(self, alloc_input):
        """
        Reallocation process: This method handles everything to determine the start value, including costs and taxes 
        """
        before_start_reallocate     = 0
        before_start_paytax         = 0
        before_start_trnsx_costs    = 0
        booking_value               = 0
        start_value                 = 0 

        before_start_reallocate = self.pre_round_get_reallocation(alloc_input) 
        #get hypothetical delta (gross amount), no extra inputs here

        before_start_paytax     = self.pre_round_get_tax_paid(before_start_reallocate) 
        #get hypothetical taxes to be paid on negative reallocation numbers; 
        #for the time being, it will be 0 -> taxes reduce the total amount to be allocated, but where? 
        #the player must decide -> add extra input: -> where to reduce the reallocation values (only positive numbers)

        before_start_trnsx_costs = self.pre_round_get_transaction_costs(before_start_reallocate, before_start_paytax) 
        #get hypothetical transaction costs on positive reallocation numbers

        start_value = self.pre_round_get_start_value(before_start_reallocate, before_start_paytax, before_start_trnsx_costs)
        #adjust the initial start value by all costs
        #previous end value + reallocate + tax on negative numbers (from reallocate) - trnsx costs on positive numbers (from reallocate)

        booking_value = self.pre_round_get_booking_value(start_value) 
        #will be used to calculate taxes when selling in the next round..
        #when sales: minimum prev booking value, current start value
        #when purchase: previous booking value + reallocate + tax - trnsx costs

        confirmation = False
        confirmation = self.pre_round_confirmation(
            alloc_input, 
            before_start_trnsx_costs, 
            before_start_paytax,
            start_value,
            booking_value)

        if confirmation:
            self.before_start_reallocate    = before_start_reallocate
            self.before_start_paytax        = before_start_paytax
            self.before_start_trnsx_costs   = before_start_trnsx_costs
            self.start_value                = start_value
            self.booking_value              = booking_value

            self.main_round()
        else:
            self.play()
            

        if self.difficulty == 1:
            #mode easy:
            if self.round == 1:
                before_start_reallocate = alloc_input
            else:
                before_start_reallocate = alloc_input - self.previous_round_data[f"round {self.round-1}"]["end_value"]
        else:
            #both modes medium and hard:
            before_start_reallocate     = get_reallocation(alloc_input) #alloc_input - endvalue
            before_start_trnsx_costs    = get_transaction_costs(before_start_reallocate) #on each positive number flat 5%, mind 50
            if self.difficulty == 3:
                #mode hard only:
                before_start_paytax = get_tax_paid(before_start_reallocate) #on each negative number amount of sales - previous booking value

        #previous end value + reallocate + tax on negative numbers (from reallocate) - trnsx costs on positive numbers (from reallocate)
        start_value = get_start_value(before_start_reallocate, before_start_paytax, before_start_trnsx_costs)
        
        #when sales: minimum prev booking value, current start value
        #when purchase: previous booking value + reallocate + tax - trnsx costs
        booking_value = get_booking_value(start_value)


    def main_round(self):
        performance     = []
        dividends       = []
        end_value       = []
        delta_start_end = []

        performance, dividends = self.main_round_get_perf(self.round)



    def get_tax_paid(self, before_start_reallocate):
        return 0

class SumUpError(Exception):
    pass
        


# printing functions ############################
def print_table_into_menu(val1="", val2="", val3="", val4="", val5="", val6="", color=False):
    c = ""
    if color:
        c = "\033[34m"
    
    print(f"| {c}{val1:<12}{val2:>12}{val3:>12}{val4:>12}{val5:>12}\033[1m{val6:>15}\033[0m |")

def print_game_header():
    print_throughout("_", False)
    print_into_menu("YOUR PORTFOLIO", True, True, True, False, False)
    print_throughout("-",True)
    print_table_into_menu("", "SAP", "TESLA", "ALIBABA", "CASH", "TOTAL", True)
    print_throughout(" ", True)
    print_into_menu("  ROUND 1  ", True, True, True, True, False)
    print("")

def print_game_history(round, rounds_data):
    print("print game history here")
    input("hit any key to continue: ")

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

def print_into_menu(str, with_border, centralized, bold, background, underlined):
    """
    This function prints a string that fits into the menu width and format 
    """
    total = TERMINAL_WIDTH
    str_start = ""
    str_bold_in = ""
    str_bold_out = ""
    str_background_in = ""
    str_underlined_in = ""
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
    
    if background:
        str_background_in = "\033[43m"
        str_bold_out = "\033[0m"
    
    if underlined:
        str_underlined_in = "\033[4m"
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
        print(str_start + str_centr_in + str_bold_in + str_underlined_in + str_background_in + sub_str + str_bold_out + str_centr_out + str_end)
    
def delete_last_line():
    "Deletes the last line in the STDOUT"
    # cursor up one line
    sys.stdout.write('\x1b[1A')
    # delete last line
    sys.stdout.write('\x1b[2K')
    


game = InvestmentGame()
game.menu()