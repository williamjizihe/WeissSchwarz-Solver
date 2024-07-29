# README

This project utilizes a search approach aimed at calculating the potential damage and its probability under various scenarios. The main functionalities implemented so far include:

- **Calculating Expected Damage**: Given a specific situation and a sequence of actions, it calculates all possible damages and their probabilities, providing the expected value and variance.

- **Calculating Kill Probability Curve**: Given a deck and the number of cards in the Waiting Room and Climax cards, along with a sequence of actions, it calculates the probability of reducing health from 3-6 to 0-0. (We assume there are no Climax cards in the Level and Clock areas under any health conditions).

- **Finding the Optimal Strategy**: Given a situation and a set of action combinations, it identifies the optimal strategy. This aims to answer questions like whether the attack order of the other two characters should be changed after the first damage is cancelled. The presentation of this feature still needs improvement.

## Running the Application

To run the application, follow these steps:

1. Navigate to the [Releases](https://github.com/williamjizihe/WeissSchwarz-Solver/releases) section of this repository.
2. Find the latest release and download the `.zip` file attached to it.
3. Locate the downloaded `.zip` file on your computer and extract it.
4. Open the extracted folder and double-click the `.exe` file to execute the application.

## Usage

After running the program, a console and a program window will open. The left side is for input, and the right side displays images.

### Setting the Scene

You can set the total number of cards and the number of climax cards in the Deck, Waiting Room, Level, and Clock at the top left area. In the Atk column, set the number of cards in your deck and the soul amount (assuming all triggers are 1 soul).

### Operator List

Below the setting area is the Operator List, where you can enter a series of operations, separated by spaces or a plus sign '+'. Effects connected by a plus sign are considered effects of the same card and are indivisible. The difference between a space and a plus sign only affects the functionality of finding the optimal strategy.

The following table lists the operators that can be used in the input box. The operators are case-insensitive.

| Operator  | Explanation            | Format       | Example       |
|---------------------------|-------------------------|------------|------------|
| Beat N damage                 | Beat N damage. (Damage can be cancelled)   | N          | 3          |
| Beat N damage with trigger | Check Trigger, if succeed, beat N+1 damage, else N damage. (Damage can be cancelled)       | Nt         | 3t         |
| Moka N cards              | Look at up to N cards from your opponent's top Deck, place the climax into Waiting Room, place the remaining cards on top Deck    | moka(N)    | moka(3)    |
| Michiru N cards           | Place N cards from your opponent's bottom Deck into Waiting Room, deal X Damage to your opponent. X is equal to the number of Climax among those cards. (Damage can be cancelled) | michiru(N) | michiru(3) |
| Woody N cards             | Your opponent reveals the top N cards of their deck, shuffles their deck, then send the top X cards of their deck to Clock. X equals the number of Climaxes revealed              | woody(N)   | woody(3)   |

For example, if you want to simulate the card "icy tail, Michiru" (SHS/W56-E081) attacks when "icy tail" in your climax area, you can input `3t michiru(4)` in the input box. If there are three Michiru attacks, you can input `3t+michiru(4) 3t+michiru(4) 3t+michiru(4)` in the input box.

### Buttons

Below the Operator List are five buttons:

- **Calculate**: Calculates damage expectation, and draws a bar graph on the right side, with each damage probability displayed in the text area below on the left.

- **Kill Probability Curve**: Calculates the damage curve, and draws a line graph on the right side, with the kill probabilities for different remaining health levels displayed in the text area below on the left.

- **Add Curve**: After calculating the damage curve, click this button to save the most recently calculated damage curve, and draws all saved line graphs on the right.

- **Delete Last Curve**: Click to delete the last saved damage curve.

- **Find Best Strategy**: Finds the best strategy, and draws a bar graph on the right side, with each damage probability displayed in the text area below on the left. A strategy_graph.png image will be generated in the exe directory, depicting the optimal actions and possible scene states in a tree diagram. This function may take a longer time.

**Decimal/Fraction**: When selected, click the above buttons, then all probabilities displayed in the text areas will be shown in decimal/fraction form.

### Timing

Tested on CPU: Intel(R) Core(TM) i7-9750H CPU @ 2.60GHz

1. **Calculating Damage Expectation**: Deck: 7/37, Waiting Room: 0/0, Level: 0/2, Clock: 0/0, Atk: 15/50, Operator list: 3t+michiru(4)+michiru(4) 3t+michiru(4)+michiru(4) 3t+michiru(4)+michiru(4)
   Time spent: 0.68s

2. **Calculating Kill Probability Curve**: Deck: 7/37, Waiting Room: 0/0, Atk: 15/50, Operator list: 3t+michiru(4)+michiru(4) 3t+michiru(4)+michiru(4) 3t+michiru(4)+michiru(4)
   Time spent: 12s

3. **Finding the Best Strategy**: This function is time-consuming. It is recommended not to use overly complex combinations of operations. The calculation time is within 0.1 seconds, but drawing the image takes about tens of seconds.
