# Poker agents (Texas Hold'em)

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
Tests show that `weighted` attribute set to `False` tend to show better results (see [Agent Comparison](#agent-training-and-comparison)).
Uses epsilon-greedy algorithm. Income in the end of the game are used for the rewards estimates, where losing all money
gives a huge "negative reward".

`MCCFRPlayer` is Monte Carlo Counterfactual Regret Minimization algorithm. Idea how to implement it is influenced by
[andyliu42 implementation of MCCFR for Khun poker](https://github.com/andyliu42/Counterfactual_Regret_Minimization_Python).
Tries to find Nash Equilibrium strategy. Since the number of states is so huge, it simply stores round index, quantized 
probability of winning and quantized current bet in the information set. All the reached nodes, and hence policies, are 
shared by all instances of `MCCFRPlayer` class, since the set of nodes is static.

`TFRLPlayer` is subclass of `RLPlayer` with the only difference it uses `tensorflow` library to implement the agent with 
`tf.keras.layers.Dense` model. By default, it simply adds one hidden layer, which is equal in size to the input layer. 
Also, it doesn't use `weighted` attribute. 


## Agent Training and comparison

2 `MCCFRPlayer` agents were trained against each other (1 vs 1) with total number of 200000 games simulated. 
`RLPLayer` agents were originally trained by allowing only one agent to learn, while others remained the same.
27000 games were simulated for weighted and not weighted agents each to train. 

To compare the agents, 1000 games were simulated lasting 50 games each or until one player gets the whole bank
(whichever happens first). The results clearly show that the MCCFR agent is superior in 1 vs 1 setup (which was
very predictable, since it exploits Nash Equilibrium so nobody can mathematically outperform this agent). Additionally,
it shows that the weighted RL agents seems to perform worse than unweighted one, though the difference is not very clear.
In the same time, MCCFR against itself has a lower maximum gain comparing with its setup agains other agents as well as 
switches of winner throughout large time, supporting the fact that Nash Equilibrium cannot be overplayed and only can give
stalemate over the large time (though only when there are only 2 players).


<div align="center"> 
  <img width="975" height="731" alt="image" src="https://github.com/user-attachments/assets/78b620d6-3cc9-4575-9263-62b05d49a5f6" />
  Image 1. MCCFRPlayer against unweighted RLPlayer
  <br>
  
  <img width="975" height="731" alt="image" src="https://github.com/user-attachments/assets/ded340e9-7bde-4bb0-96f1-a6d6cb255e92" />
  Image 2. MCCFRPlayer against weighted RLPlayer
  <br>
  
  <img width="975" height="731" alt="image" src="https://github.com/user-attachments/assets/cc8669ce-0058-4cea-812b-b813dbebb0f7" />
  Image 3. Unweighted RLPlayer vs weighted RLPlayer
  <br>
  
  <img width="975" height="731" alt="image" src="https://github.com/user-attachments/assets/505e51c7-866c-451b-9a37-311c3be9e754" />
  Image 4. MCCFRPlayer aginst itself
  <br>
</div>

Another comparison is also after simulation of 1000 games, but this time there were 6 players in total with 2 players of
each class (every game the seats on the table were shuffled to avoid getting any benefit from location). This time, RL 
unweighted agent clearly outperformed weighted and MCCFR agents, whereas weighted agent performance was the worst. 
MCCFR didn't win because it is most effective when there are only 2 players and loses its effectiveness with 3+ players.
<div align="center">
  <img width="975" height="647" alt="image" src="https://github.com/user-attachments/assets/5ed6d1d2-c0ea-4ee9-a270-09ac1da53647" />
  Image 5. Comparison of MCCFR, RL weighted and RL unweighted agents (2 of each)
</div>


Finally, `RLPlayer` (unweighted) and `TFRLPlayer` were trained on simulation of 30000 games with 4 players on the table.
After settign a table with 2 players of each class (giving 4 players in total) and running 10000 games, custom RL player
agent has a superior performance over TFRLPlayer.
<div align="center">
  <img width="633" height="473" alt="TFRLPlayer vs RLPlayer poker copy" src="https://github.com/user-attachments/assets/64e87495-580b-49c1-8861-966bf1cd859c" />
  Image 6. Comparison of RL unweighted and Tensor Flow RL agent
</div>


## Result
On average `RLPlayer` unweighted has the best performance (which is a simply a linear model). It is recommended to use 
`MCCFRPlayer` though in case there are only 2 players. 

However, it is important to note that these agents performances were only compared with other agents and not the
real people. It is possible that some agents can simply find an exploit in other agent policy, which won't work for
humans.
