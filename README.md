![investment_game logo](images/logo2.png)

(Developer: Felix Lehmann) <br>
**11/12/2024**

This project is a playful simulation of an investment into 3 securities with the help of a cash account. The player will allocate, rebalance his/her money over five rounds and needs to make tactical decision related to tax payments, dividend payments, transaction costs, risk free rates of the cash account etc.

**The challenge in this project** is that there are no interfaces allowed. This forces me as the developer to think of simple ways to make game options. As a result, I decided to use classical "legacy" concepts such as a start menu and choosing options by entering numbers. For the rankings and the game overviews, however, I tried to simulate tables which makes it easier to understand numbers. For that I created functions which aligns the content with the 80 characters width.

__Information on the data of financial instruments__
They are fictive, even if they are oriented on real data to make the data acquisition faster. Randomly, prices and dates were modified and anonymized.

# How to play
As one can assume, this game can become very complex. The complexity is addressed by creating 3 game modes: easy, medium, hard.

## Easy Mode
All beginners should start here. The player starts with 100 000€ which need to be invested into 3 securities (equities/shares) and, if s/he wants into the cash account. The player will play **5 rounds**. The goal is to maximize the portfolio value. 

At the beginning of a round (the pre-round phase) the player can reallocate (in the first round must) and has to deal with costs. Transaction costs of 3% will charged for each purchase. Once, the allocation is confirmed by the player, the actual investment phase starts. The portfolio will grow or decrease, based on the market. At the end of the round, the player will be informed about occured dividends. S/he is allowed to re-invest for free or to take it out to the cash. After that, the new market values will be revealed to the player. The cash account pays a riskfree rate for the money parked of 3% per round. All numbers will be shown to the player. It's time for analysis. Costs are listed, returns and deltas are transparent etc. based on that, the next round can be planned.

## Medium Mode
This is a more complex mode. In the pre-round phase, the player not only has to deal with transaction costs of 6% but also is obliged to pay a 30% flat-tax rate on all profits realized by sales. Rebalancing is now an increasing cost factor. Moreover, the cash account will only pay a 1% risk-free rate per round.

## Hard Mode
The hard mode is not more complex than Medium mode but more expensive. The transaction costs increased to 8%, the tax rate to 40% and the cash acount is now charging 3% per round from the player, when s/he deposits money there. Good luck with this mode!

# Features
- **menu board**
  - as you can see below, the game starts with a classical menu, offering options to increase the user experience 
  - the width is adjusted to this app's screen but can dynamically be changed as a constant is used for the fix width
    ![menu_board](images/menu_board.png)
- **rules board**
  - the same functions are used to reproduce the board over and over again -> you just need to hand over the text(s) to display and some formatting boolean (background, underlined, bold etc.)
  - the rules are explained in details - an example for the tax calculation is shown
  - this board exists to make the player understand their actions
  - finally, the player can navigate back to the start menu
  ![rules board 01](images/rules01.png)
  ![rules board 02](images/rules02.png)
- **rankings boards**
  - this feature shall make the game more interesting
  - it uses google spreadsheet API to retrieve data from the best players 
  - the player can orientate and compete by the total portfolio value and the paid costs and taxes resp. 
  - there are 3 different lists, one per each game mode

  ![ranking_easy]()

  ![ranking_medium]()

  ![ranking_hard]()


## Reminders

- Your code must be placed in the `run.py` file
- Your dependencies must be placed in the `requirements.txt` file
- Do not edit any of the other files or your code may not deploy properly

## Creating the Heroku app

When you create the app, you will need to add two buildpacks from the _Settings_ tab. The ordering is as follows:

1. `heroku/python`
2. `heroku/nodejs`

You must then create a _Config Var_ called `PORT`. Set this to `8000`

If you have credentials, such as in the Love Sandwiches project, you must create another _Config Var_ called `CREDS` and paste the JSON into the value field.

Connect your GitHub repository and deploy as normal.

## Constraints

The deployment terminal is set to 80 columns by 24 rows. That means that each line of text needs to be 80 characters or less otherwise it will be wrapped onto a second line.

---

Happy coding!
