# poker

## About

This is a research project aimed on trying to implement poker (Texas Hold'em) game as well as poker agents. The purpose of the project is to create an adequate AI agent to win game.

## Project composition

### Environment

Environment is implemented in `poker/environment` folder. It holds the `Card`, `CombinationFinder`, `GameInfo` and `Game` classes.

`Card` is a simply a wrapper class, since every card can be simply implemented via index from 0 to 51.
However, it is necessary for execution of the code and has a lot of useful methods. 

`CombinationFinder` finds poker combinations and ranks them. Used to find the winner by the `Game` class

`Game` class runs the game. It holds the array of the players, updates the information for them after every action
(this way it is proved against possible leaks of private information to the other players since players don't have
any reference to the `Game` object and can only get `GameInfo` instance) and makes sure that the game is run according
to Texas Hold'em rules.

### Agents/Players

There are several *Player* classes implemented. All of them inherit `PlayerBase` (has standard methods for interactions 
with the game) class and use `PlayerProfile` container class (holds the data about the player, also used by the `Game` class).
Important to note that `PlayerBase` has `winning_prob(self, iter_num)`, which estimates winning probability by simulation 
`iter_num` of games and getting ratio of number of winning games and `iter_num`.

`HumanPlayer` has not agent and simply allows user to play poker via terminal.

`RLPlayer` is the Reinforcement Learning agent, implements 2 linear models, one to select type of the action (fold, raise, or call/check),
while second is used when action type is raise, allowing to choose the raising value. Can be weighted or unweighted based
on the `weighted` attribute. If the agent is weighted, then softmax function is applied and action is selected based on 
probabilities; otherwise, if `weighted` has value `False`, then it simply selects the action with the highest reward of Q function.
Tests show that `weighted` attribute set to `False` tend to show better results (see [Agent Comparison](#agent-comparison)).
Uses epsilon-greedy algorithm. Income in the end of the game are used for the rewards estimates, where losing all money
gives a huge "negative reward".

`MCCFRPlayer` is Monte Carlo Counterfactual Regret Minimization algorithm. Idea how to implement it is influenced by
[andyliu42 implementation of MCCFR for Khun poker](https://github.com/andyliu42/Counterfactual_Regret_Minimization_Python).
Tries to find Nash Equilibrium strategy. Since the number of states is so huge, it simply stores round index, quantized 
probability of winning and quantized current bet in the information set. All the reached nodes, and hence policies, are 
shared by all instances of `MCCFRPlayer` class, since the set of nodes is static.

`TFRLPlayer` is subclass of `RLPlayer` with the only difference it uses `tensorflow` library to implement the agent with 
`tf.keras``.



## Agent Comparison
