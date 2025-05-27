import matplotlib.pyplot as plt
import numpy as np
from MCCFRPlayer import MCCFPlayer
from RLPlayer import RLPlayer
from pickle import load
from poker.environment.Game import Game
import logging
from logging import WARNING, DEBUG
import sys


def calculate_gain(players, init_val=1000, small_blind=10, num_games=50, cnt_limit=50):
    """
    Simulate games between given players agents and return the gains of these players
    :param players: player agents
    :param init_val: initial amount of money provided in the game
    :param small_blind: small blind at the game
    :param num_games: number of games that are simulated (games with all players starting from init_val)
    :param cnt_limit: limit of games simulated for the one particular starting configuration
    :return:
    """

    # tracks amount of money gained over time
    players_gain_history = []
    for game_idx in range(num_games):
        game = Game(players=players, small_blind=small_blind, start_value=init_val)
        cnt = 0

        # money in the previous game
        prev_game_money = [init_val] * len(players)
        while game.count_active_players() > 1 and cnt < cnt_limit:
            game.play_game()
            cnt += 1

            players_gain_history.append([0] * len(players))

            # calculate the gain
            for i in range(len(players)):
                player_profile = game.players_profiles[game.players_ids[i]]
                now_money = player_profile.money + player_profile.bet
                gain = now_money - prev_game_money[i]
                players_gain_history[-1][i] = gain
                prev_game_money[i] = now_money

    return players_gain_history

def get_cul(players_gain_history):
    """
    :param players_gain_history: Gain history over time
    :return: the cumulative gain
    """
    n = len(players_gain_history[0])
    cumulative_gain = [[0] * n]
    for i in range(len(players_gain_history)):
        cumulative_gain.append([0] * n)
        for j in range(n):
            cumulative_gain[-1][j] = players_gain_history[i][j] + cumulative_gain[i][j]

    return cumulative_gain

def get_col(mat, col_idx):
    col = []
    for i in range(len(mat)):
        col.append(mat[i][col_idx])
    return col

if __name__ == '__main__':

    # Setting up logging
    Game.logger.setLevel(WARNING)

    logging.basicConfig(
        format='%(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    # ====================================
    # MCCFRPlayer vs RLPlayer(unweighted)
    MCCFR_nodes_file_name = "MCCFRPlayer_nodes_prob10_sample400.pkl"
    with open(MCCFR_nodes_file_name, "rb") as f:
        MCCFPlayer.nodes = load(f)
    player1 = MCCFPlayer(is_learning=False)

    unweighted_agent_file_name = "RLPlayer_agent_sw900_p3_unweighted.pkl"
    with open(unweighted_agent_file_name, "rb") as f:
        player2 = load(f)

    players = [player1, player2]

    players_gain_history = np.array(calculate_gain(players, num_games=1000))
    players_cum_gain_history = np.cumsum(players_gain_history, axis=0)

    # print(players_gain_history[:5])
    # print(players_cum_gain_history[:5])

    time = np.linspace(0, players_cum_gain_history.shape[0] - 1, players_cum_gain_history.shape[0])

    # print(time)
    # print(players_cum_gain_history[:, 0])

    fig, ax = plt.subplots()

    ax.plot(time, players_cum_gain_history[:, 0], label="MCCFR agent")
    ax.plot(time, players_cum_gain_history[:, 1], label="RL (unweighted) agent")

    ax.set_title("MCCFRPlayer against unweighted RLPlayer")
    ax.set_xlabel("game")
    ax.set_ylabel("gain")
    ax.legend()


    # ====================================
    # MCCFRPlayer vs RLPlayer(weighted)
    MCCFR_nodes_file_name = "MCCFRPlayer_nodes_prob10_sample400.pkl"
    with open(MCCFR_nodes_file_name, "rb") as f:
        MCCFPlayer.nodes = load(f)
    player1 = MCCFPlayer(is_learning=False)

    weighted_agent_file_name = "RLPlayer_agent_sw900_p3_weighted.pkl"
    with open(weighted_agent_file_name, "rb") as f:
        player2 = load(f)

    players = [player2, player1]

    players_gain_history = np.array(calculate_gain(players, num_games=1000))
    players_cum_gain_history = np.cumsum(players_gain_history, axis=0)

    time = np.linspace(0, players_cum_gain_history.shape[0] - 1, players_cum_gain_history.shape[0])


    fig, ax = plt.subplots()

    ax.plot(time, players_cum_gain_history[:, 1], label="MCCFR agent")
    ax.plot(time, players_cum_gain_history[:, 0], label="RL (weighted) agent")

    ax.set_title("MCCFRPlayer against weighted RLPlayer")
    ax.set_xlabel("game")
    ax.set_ylabel("gain")
    ax.legend()


    # ====================================
    # RLPlayer(weighted) vs RLPlayer(weighted)
    unweighted_agent_file_name = "RLPlayer_agent_sw900_p3_unweighted.pkl"
    with open(unweighted_agent_file_name, "rb") as f:
        player1 = load(f)

    weighted_agent_file_name = "RLPlayer_agent_sw900_p3_weighted.pkl"
    with open(unweighted_agent_file_name, "rb") as f:
        player2 = load(f)



    players = [player1, player2]

    players_gain_history = np.array(calculate_gain(players, num_games=1000))
    players_cum_gain_history = np.cumsum(players_gain_history, axis=0)

    time = np.linspace(0, players_cum_gain_history.shape[0] - 1, players_cum_gain_history.shape[0])

    fig, ax = plt.subplots()

    ax.plot(time, players_cum_gain_history[:, 0], label="RL (unweighted) agent")
    ax.plot(time, players_cum_gain_history[:, 1], label="RL (weighted) agent")

    ax.set_title("RLPlayer unweighted against weighted RLPlayer")
    ax.set_xlabel("game")
    ax.set_ylabel("gain")
    ax.legend()



    # ====================================
    # MCCFRPlayer vs RLPlayer(weighted)
    MCCFR_nodes_file_name = "MCCFRPlayer_nodes_prob10_sample400.pkl"
    with open(MCCFR_nodes_file_name, "rb") as f:
        MCCFPlayer.nodes = load(f)
    player1 = MCCFPlayer(is_learning=False)
    player2 = MCCFPlayer(is_learning=False)

    players = [player1, player2]

    players_gain_history = np.array(calculate_gain(players, num_games=1000))
    players_cum_gain_history = np.cumsum(players_gain_history, axis=0)

    time = np.linspace(0, players_cum_gain_history.shape[0] - 1, players_cum_gain_history.shape[0])


    fig, ax = plt.subplots()

    ax.plot(time, players_cum_gain_history[:, 1], label="MCCFR agent 1")
    ax.plot(time, players_cum_gain_history[:, 0], label="MCCFR agent 2")

    ax.set_title("MCCFRPlayer against itself")
    ax.set_xlabel("game")
    ax.set_ylabel("gain")
    ax.legend()


    plt.show()



