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
            print("play another round (not the first round)")

        return {
            "before_start_reallocate"   : self.before_start_reallocate,
            "before_start_paytax"       : self.before_start_paytax,
            "before_start_trnsx_costs"  : self.before_start_trnsx_costs,
            "booking_value"             : self.booking_value,
            "start_value"               : self.start_value,
            "performance"               : self.performance,
            "dividends"                 : self.dividends,
            "end_value"                 : self.end_value,
            "delta_start_end"           : self.delta_start_end
        }
    
    def pre_round(self, alloc_input):
        """
        Reallocation process: This method handles everything to determine the start value, including costs and taxes 
        """
        before_start_reallocate     = []
        before_start_paytax         = []
        before_start_trnsx_costs    = []
        booking_value               = []
        start_value                 = [] 
        alloc_input2                = [] #when selling, taxes might occur->it reduces the money to be allocated, but which purchase to reduce?? the player must decide again

        before_start_reallocate = self.pre_round_get_reallocation(alloc_input) 
        #get hypothetical delta (gross amount), no extra inputs here

        before_start_paytax = self.pre_round_get_tax_paid(before_start_reallocate) 
        #get hypothetical taxes to be paid on negative reallocation numbers; 
        #for the time being, it will be 0 -> taxes reduce the total amount to be allocated, but where? 
        #we determine taxes from negative numbers and charge them on positive numbers aka: the player
        #has less money to allocate after taxes
        if sum(before_start_paytax) > 0:
            before_start_reallocate = self.pre_round_adjust_reallocation(before_start_reallocate, before_start_paytax)

        before_start_trnsx_costs = self.pre_round_get_transaction_costs(before_start_reallocate) 
        #get hypothetical transaction costs on positive reallocation numbers (after taxes)
        #the positive numbers, now, will be charged by transaction costs
        #the only difference: you cant reallocate them, they are based on the amount of purchase

        start_value, booking_value = self.pre_round_get_start_value(before_start_reallocate, before_start_trnsx_costs)
        #adjust the initial start value by all costs
        #previous end value + reallocate - trnsx costs on positive numbers (from reallocate)

        #booking_value = self.pre_round_get_booking_value(start_value) 
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

            self.pre_round_print()
        else:
            print("\nNOT CONFIRMED!")
            time.sleep(2)
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
                before_start_paytax = self.pre_round_get_tax_paid(before_start_reallocate) #on each negative number amount of sales - previous booking value

        #previous end value + reallocate + tax on negative numbers (from reallocate) - trnsx costs on positive numbers (from reallocate)
        start_value, booking_value = get_start_value(before_start_reallocate, before_start_paytax, before_start_trnsx_costs)
        


    def main_round(self):
        performance     = []
        dividends       = []
        end_value       = []
        delta_start_end = []

        performance, dividends  = self.main_round_get_perf(self.round)
        end_value               = self.main_round_get_endvalue(performance, dividends) #add extra steps when dividends occur: free reinvestment or pay-out to cash
        delta_start_end         = self.main_round_get_delta(end_value, self.start_value)

        self.performance    = performance
        self.dividends      = dividends
        self.end_value      = end_value
        self.delta_start_end= delta_start_end

        self.main_round_print()

        if performance[3] > 0:
            print(f"Congrats! Your portfolio \033[32mgrew by {performance[3]}%\033[0m (excl. costs and taxes)")
        else:
            print(f"Meeehhh. Your portfolio \033[31mlost {performance[3]}%\033[0m (excl. costs and taxes)")


    def pre_round_get_reallocation(self, alloc_input):
        list = []
        if self.round == 1:
            alloc_input.append(sum(alloc_input))
            list = alloc_input
        else:
            end_value_previous = self.previous_round_data[f"round {self.round-1}"]["end_value"]
            alloc_input.append(sum(alloc_input))
            list = [a - b for a, b in zip(alloc_input, end_value_previous)]
        return list

    def pre_round_get_tax_paid(self, before_start_reallocate):
        list = [0]*5
        x = 0.25
        if self.difficulty == 2:
            x = 0.30
        elif self.difficulty == 3:
            x = 0.40
        tax = [x, x, x, x, 0]

        if self.round > 1:
            #as long as the sale amount is smaller than the previous round's book value - there are no taxes
            #everything above book value is profit 
            #assuming that your current market value is higher than the book value, if not, you have loss 
            book_value_prev = self.previous_round_data[f"round {self.round-1}"]["book_value"]
            taxable_amount = [(0 if -a-b < 0 else -a-b) for a,b in zip(before_start_reallocate, book_value_prev)] #only when book_value > sale; remember, we need positiv sales numbers thats why we make them positive with -a
            list = [a * b for a, b in zip(taxable_amount, tax)]
        return list


    def pre_round_adjust_reallocation(self, before_start_reallocate, before_start_paytax):
        sum_purchases = sum([0 if a < 0 else a for a in before_start_reallocate])
        sum_taxes     = sum(before_start_paytax)
        list          = []

        print("\033[31mATTENTION\n\nYou sell so much that you are in a profit zone. For that, my friend, you have to pay taxes\nThe Finanzamt is very quick - you have to pay:\n\033[0m")
        time.sleep(1)
        print(f"In detail: {before_start_paytax} ")
        print(f"In sum   : {sum(before_start_paytax)}€\n")
        time.sleep(1)
        print("This will reduce the money you can move to other securities (or bank account):")
        print(f"before taxes:\n {sum_purchases}€\n")
        print(f"What you actually can spend (after taxes):\n {sum_purchases-sum_taxes}\n")

        while True:
            available  = sum_purchases-sum_taxes
            a, b, c, d = 0
            try:
                if before_start_reallocate[0] > 0:
                    print(f"Enter a new purchase amount for the security \033[1;31mSAP:\033[0m")
                    a = input(f"Enter a value between 0 and {available}")
                    if not isinstance(a, (float, int)):
                        raise ValueError("\033[31mInvalid. Not a number. Reallocate again.\033[0m")
                    if a < 0 or a > available:
                        raise ValueError(f"\033[31mInvalid. Please enter a value between 0 and {available}. Reallocate again.\033[0m")
                    available -= a
                
                if before_start_reallocate[1] > 0:
                    print(f"Enter a new purchase amount for the security \033[1;31mTESLA:\033[0m")
                    b = input(f"Enter a value between 0 and {available}")
                    if not isinstance(b, (float, int)):
                        raise ValueError("\033[31mInvalid. Not a number. Reallocate again.\033[0m")
                    if b < 0 or b > available:
                        raise ValueError(f"\033[31mInvalid. Please enter a value between 0 and {available}. Reallocate again.\033[0m")
                    available -= b

                if before_start_reallocate[2] > 0:
                    print(f"Enter a new purchase amount for the security \033[1;31mALIBABA:\033[0m")
                    c = input(f"Enter a value between 0 and {available}")
                    if not isinstance(c, (float, int)):
                        raise ValueError("\033[31mInvalid. Not a number. Reallocate again.\033[0m")
                    if c < 0 or c > available:
                        raise ValueError(f"\033[31mInvalid. Please enter a value between 0 and {available}. Reallocate again.\033[0m")
                    available -= c

                if before_start_reallocate[3] > 0:
                    print(f"Enter a new transfer amount to \033[1;31myour cash account:\033[0m")
                    d = input(f"Enter a value between 0 and {available}")
                    if not isinstance(d, (float, int)):
                        raise ValueError("\033[31mInvalid. Not a number. Reallocate again.\033[0m")
                    if d < 0 or d > available:
                        raise ValueError(f"\033[31mInvalid. Please enter a value between 0 and {available}. Reallocate again.\033[0m")
                    available -= d

                if not round(available,2) == 0:
                    raise ValueError(f"\033[31mThe sum of your values doesn't equal {sum_purchases-sum_taxes} ({a+b+c+d}). Reallocate again.\033[0m")

            except ValueError as e:
                print(e)
                time.sleep(2)

        list = before_start_reallocate
        if before_start_reallocate[0] > 0:
            list[0] = a
        if before_start_reallocate[1] > 0:
            list[1] = b
        if before_start_reallocate[2] > 0:
            list[2] = c
        if before_start_reallocate[3] > 0:
            list[3] = d
        
        return list


    def pre_round_get_transaction_costs(self, before_start_reallocate):
        """
        Method that calculates 3% transaction costs on each new purchase 
        tip: the positive values include the tax reduction already, now we adjust them for transaction costs
        """
        x = 0
        if self.difficulty == 1:
            x = 0.03
        elif self.difficulty == 2:
            x = 0.04
        elif self.difficulty == 3:
            x = 0.05
        
        costs_rel = [x, x, x, 0, 0]
        costs_abs = [(0 if a < 0 else a) * b for a, b in zip(before_start_reallocate, costs_rel)]
        return costs_abs


    def pre_round_get_start_value(self, before_start_reallocate, before_start_trnsx_costs):
        end_value_prev      = self.previous_round_data[f"round {self.round-1}"]["end_value"]
        booking_value_prev  = self.previous_round_data[f"round {self.round-1}"]["booking_value"]

        list_start_value   = [a + b - c for a,b,c in zip(end_value_prev, before_start_reallocate, before_start_trnsx_costs)]
        list_booking_value = [a + b - c for a,b,c in zip(booking_value_prev, before_start_reallocate, before_start_trnsx_costs)]
        
        return (list_start_value, list_booking_value)


    def main_round_get_perf(self, round):
        
        

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