from copy import deepcopy

import matplotlib.pyplot as plt
import numpy as np
from poker.Players.TFRLPlayer import TFRLPlayer
from poker.Players.RLPlayer import RLPlayer
from pickle import load
from poker.environment.Game import Game
import logging
from logging import WARNING, DEBUG
import sys
from agent_comparison_1vs1 import calculate_gain
from agent_comparison_3to6players import shuffled_gain


if __name__ == "__main__":

    # Setting up logging
    Game.logger.setLevel(WARNING)

    logging.basicConfig(
        format='%(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    # ====================================
    # 2 TFRLPLayers vs 2 RLPlayers (unweighted)
    tfrlplayer_agent_file_name = "../training/TFRLPlayer_agent.pkl"
    with open(tfrlplayer_agent_file_name, "rb") as f:
        player1 = load(f)
        player2 = deepcopy(player1)

    unweighted_agent_file_name = "../training/RLPlayer_agent.pkl"
    with open(unweighted_agent_file_name, "rb") as f:
        player3 = load(f)
        player4 = deepcopy(player3)


    players = [player1, player2, player3, player4]

    # getting gain history
    players_gain_history = np.array(shuffled_gain(players, 20))
    players_cum_gain_history = np.cumsum(players_gain_history, axis=0)

    TFRL_cum_gain_history = (players_cum_gain_history[:, 0] + players_cum_gain_history[:, 1]) / 2
    RL_unweighted_cum_gain_history = (players_cum_gain_history[:, 2] + players_cum_gain_history[:, 3]) / 2

    time = np.linspace(0, players_cum_gain_history.shape[0] - 1, players_cum_gain_history.shape[0])

    fig, ax = plt.subplots()

    ax.plot(time, TFRL_cum_gain_history, label="Tensorflow RL agent")
    ax.plot(time, RL_unweighted_cum_gain_history, label="Custom RL (unweighted) agent")

    ax.set_title("2 TFRL agents vs 2 RL (unweighted) agents")
    ax.set_xlabel("game")
    ax.set_ylabel("gain")
    ax.legend()

    plt.show()