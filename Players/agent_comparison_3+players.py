import matplotlib.pyplot as plt
import numpy as np
from MCCFRPlayer import MCCFPlayer
from RLPlayer import RLPlayer
from pickle import load
from poker.environment.Game import Game
import logging
from logging import WARNING, DEBUG
import sys
from agent_comparison_1vs1 import calculate_gain

def shuffled_gain(players, shuffles=100):
    """Shuffles the players. Returns the gain history over time"""

    n = len(players)
    players_gain_history = []
    for shuffle_idx in range(shuffles):
        # permutation of players
        perm = np.linspace(0, n - 1, n, dtype=int)
        perm = np.random.permutation(perm)
        permuted_players = [None] * n
        for j in range(n):
            permuted_players[perm[j]] = players[j]

        permuted_gain_history = calculate_gain(permuted_players, num_games=10)
        for t in range(len(permuted_gain_history)):
            normalized_gain = [0] * n
            for j in range(n):
                normalized_gain[j] = permuted_gain_history[t][perm[j]]

            permuted_gain_history[t] = normalized_gain

        players_gain_history += permuted_gain_history

        print(f"{shuffle_idx + 1} passed")

    return players_gain_history

if __name__ == "__main__":

    # Setting up logging
    Game.logger.setLevel(WARNING)

    logging.basicConfig(
        format='%(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    # ====================================
    # 2 MCCFRPlayers vs 2 RLPlayers (unweighted) vs 2 RLPlayers (weighted)
    MCCFR_nodes_file_name = "MCCFRPlayer_nodes_prob10_sample400.pkl"
    with open(MCCFR_nodes_file_name, "rb") as f:
        MCCFPlayer.nodes = load(f)
    player1 = MCCFPlayer(is_learning=False)
    player2 = MCCFPlayer(is_learning=False)

    unweighted_agent_file_name = "RLPlayer_agent_sw900_p3_unweighted.pkl"
    with open(unweighted_agent_file_name, "rb") as f:
        player3 = load(f)
    unweighted_agent_file_name = "RLPlayer_agent_sw900_p2_unweighted.pkl"
    with open(unweighted_agent_file_name, "rb") as f:
        player4 = load(f)

    weighted_agent_file_name = "RLPlayer_agent_sw900_p3_weighted.pkl"
    with open(weighted_agent_file_name, "rb") as f:
        player5 = load(f)
    weighted_agent_file_name = "RLPlayer_agent_sw900_p3_weighted.pkl"
    with open(weighted_agent_file_name, "rb") as f:
        player6 = load(f)

    players = [player1, player2, player3, player4, player5, player6]

    players_gain_history = np.array(shuffled_gain(players, 100))
    players_cum_gain_history = np.cumsum(players_gain_history, axis=0)

    MCCFR_cum_gain_history = (players_cum_gain_history[:, 0] + players_cum_gain_history[:, 1]) / 2
    RL_unweighted_cum_gain_history = (players_cum_gain_history[:, 2] + players_cum_gain_history[:, 3]) / 2
    RL_weighted_cum_gain_history = (players_cum_gain_history[:, 4] + players_cum_gain_history[:, 5]) / 2

    time = np.linspace(0, players_cum_gain_history.shape[0] - 1, players_cum_gain_history.shape[0])

    fig, ax = plt.subplots()

    ax.plot(time, MCCFR_cum_gain_history, label="MCCFR agent")
    ax.plot(time, RL_unweighted_cum_gain_history, label="RL (unweighted) agent")
    ax.plot(time, RL_weighted_cum_gain_history, label="RL (weighted) agent")

    ax.set_title("6 players (2 each type avg) MCCFRPlayer, RLPlayer unweighted, and RLPlayer weighted")
    ax.set_xlabel("game")
    ax.set_ylabel("gain")
    ax.legend()

    plt.show()