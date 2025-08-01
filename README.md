# Poker agents (Texas Hold'em)

## About

This is a research project aimed at trying to implement a poker (Texas Hold'em) game as well as poker agents. The purpose of the project is to create an adequate AI agent to win the game.

## Project composition

### Environment

The environment is implemented in the `poker/environment` folder. It holds the `Card`, `CombinationFinder`, `GameInfo`, and `Game` classes.

`Card` is simply a wrapper class, since every card can be implemented via an index from 0 to 51. However, it is necessary for the execution of the code and has many useful methods.

`CombinationFinder` finds poker combinations and ranks them. It is used by the `Game` class to find the winner.

The `Game` class runs the game. It holds the array of players, updates the information for them after every action (this way it is protected against possible leaks of private information to the other players, since players don't have any reference to the `Game` object and can only get a `GameInfo` instance), and makes sure that the game is run according to Texas Hold'em rules.

### Agents/Players

There are several *Player* classes implemented. All of them inherit the `PlayerBase` class (which has standard methods for interactions with the game) and use the `PlayerProfile` container class (which holds the data about the player and is also used by the `Game` class). It is important to note that `PlayerBase` has `winning_prob(self, iter_num)`, which estimates the winning probability by simulating `iter_num` games and getting the ratio of the number of winning games to `iter_num`.

`HumanPlayer` has no agent and simply allows a user to play poker via the terminal.

`RLPlayer` is the Reinforcement Learning agent. It implements two linear models: one to select the type of action (fold, raise, or call/check), while the second is used when the action type is "raise," allowing it to choose the raising value. It can be weighted or unweighted based on the `weighted` attribute. If the agent is weighted, then the softmax function is applied and the action is selected based on probabilities; otherwise, if `weighted` is `False`, it simply selects the action with the highest reward of the Q function. Tests show that the `weighted` attribute set to `False` tends to show better results (see [Agent Comparison](#agent-training-and-comparison)). It uses the epsilon-greedy algorithm. Income at the end of the game is used for reward estimates, where losing all money gives a huge "negative reward."

`MCCFRPlayer` is a Monte Carlo Counterfactual Regret Minimization algorithm. The idea for its implementation is influenced by [andyliu42's implementation of MCCFR for Khun poker](https://github.com/andyliu42/Counterfactual_Regret_Minimization_Python). It tries to find a Nash Equilibrium strategy. Since the number of states is so huge, it simply stores the round index, quantized probability of winning, and quantized current bet in the information set. All the reached nodes, and hence policies, are shared by all instances of the `MCCFRPlayer` class, since the set of nodes is static.

`TFRLPlayer` is a subclass of `RLPlayer` with the only difference being that it uses the `tensorflow` library to implement the agent with a `tf.keras.layers.Dense` model. By default, it simply adds one hidden layer, which is equal in size to the input layer. Also, it doesn't use the `weighted` attribute.

## Agent Training and comparison

Two `MCCFRPlayer` agents were trained against each other (1 vs 1) with a total of 200,000 games simulated. `RLPlayer` agents were originally trained by allowing only one agent to learn, while others remained the same. 27,000 games were simulated for each of the weighted and unweighted agents to train them.

To compare the agents, 1,000 games were simulated, each lasting 50 games or until one player gets the whole bank (whichever happens first). The results clearly show that the MCCFR agent is superior in a 1 vs 1 setup (which was very predictable, since it exploits Nash Equilibrium, so nobody can mathematically outperform this agent). Additionally, it shows that the weighted RL agent seems to perform worse than the unweighted one, though the difference is not very clear. At the same time, MCCFR against itself has a lower maximum gain compared with its setup against other agents, as well as switches in the winner over a long period, supporting the fact that Nash Equilibrium cannot be overplayed and can only result in a stalemate over a long time (though only when there are two players).

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
  Image 4. MCCFRPlayer against itself
  <br>
</div>

Another comparison was also made after a simulation of 1,000 games, but this time there were six players in total with two players of each class. (In every game, the seats at the table were shuffled to avoid getting any benefit from location.) This time, the RL unweighted agent clearly outperformed the weighted and MCCFR agents, whereas the weighted agent's performance was the worst. MCCFR didn't win because it is most effective when there are only two players and loses its effectiveness with three or more players.

<div align="center">
  <img width="975" height="647" alt="image" src="https://github.com/user-attachments/assets/5ed6d1d2-c0ea-4ee9-a270-09ac1da53647" />
  Image 5. Comparison of MCCFR, RL weighted and RL unweighted agents (2 of each)
</div>


Finally, `RLPlayer` (unweighted) and `TFRLPlayer` were trained on a simulation of 30,000 games with four players at the table. After setting up a table with two players of each class (giving four players in total) and running 10,000 games, the custom RL player agent had superior performance over the TFRLPlayer.

<div align="center">
  <img width="633" height="473" alt="TFRLPlayer vs RLPlayer poker copy" src="https://github.com/user-attachments/assets/64e87495-580b-49c1-8861-966bf1cd859c" />
  <br>
  Image 6. Comparison of RL unweighted and Tensor Flow RL agent
</div>


## Result
On average, `RLPlayer` unweighted has the best performance (which is a simple linear model). It is recommended to use `MCCFRPlayer`, however, in case there are only two players.

It is important to note that these agents' performances were only compared with other agents and not with real people. It is possible that some agents can simply find an exploit in another agent's policy, which won't work for humans.
