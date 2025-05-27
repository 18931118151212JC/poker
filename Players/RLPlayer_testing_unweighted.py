import sys

from poker.environment.Game import Game
from RLPlayer import RLPlayer
from random import seed
from logging import WARNING, DEBUG
from pickle import dump, load
from os.path import exists
import logging

if __name__ == '__main__':
    # ALL COMMENTS ABOUT THE CASES WHEN THE SEED IS SET TO 0.
    # seed(0)

    # SET LEVEL TO DEBUG IF YOU WANT TO SEE THE GAME INFORMATION AFTER EVERY ROUND, SET TO WARNING NOT TO
    Game.logger.setLevel(WARNING)

    logging.basicConfig(
        format='%(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    # Letting players learn by switching learning rates
    player1 = RLPlayer(weighted=False)
    player2 = RLPlayer(weighted=False)
    player3 = RLPlayer(weighted=False)

    players = [player1, player2, player3]

    saved_agent1_file_name = "RLPlayer_agent_sw900_p1_unweighted.pkl"
    saved_agent2_file_name = "RLPlayer_agent_sw900_p2_unweighted.pkl"
    saved_agent3_file_name = "RLPlayer_agent_sw900_p3_unweighted.pkl"

    if not (exists(saved_agent1_file_name) and exists(saved_agent2_file_name) and exists(saved_agent3_file_name)):
        # agents don't exist, train them
        for i in range(len(players)):
            players[i].stop_learn()

        num_switches = 900
        num_big_games = 10
        num_games = 3

        for i in range(num_switches):
            players[i % len(players)].stop_learn()
            players[(i + 1) % len(players)].learn(reset_params=False)
            for j in range(num_big_games):
                game = Game(players, 1000, 10)
                for k in range(num_games):
                    game.play_game()
            if (i + 1) % 20 == 0:
                print(f"Completed {i + 1} switches out of {num_switches}")

                with open(saved_agent1_file_name, "wb") as f:
                    dump(player1, f)
                with open(saved_agent2_file_name, "wb") as f:
                    dump(player2, f)
                with open(saved_agent3_file_name, "wb") as f:
                    dump(player3, f)

                print(f"player1.epsilon: {player1.epsilon}")
                print("===Saved===")

    else:
        # trained agents exist:
        with open(saved_agent1_file_name, "rb") as f:
            player1 = load(f)
        with open(saved_agent2_file_name, "rb") as f:
            player2 = load(f)
        with open(saved_agent3_file_name, "rb") as f:
            player3 = load(f)
        print("===Agents are successfully loaded===")
    #
    Game.logger.setLevel(DEBUG)

    print(f"player1.epsilon: {player1.epsilon}\n"
          f"player1.weights: {player1.type_weights}\n\t {player1.raise_weights}\n"
          f"player1.bias: {player1.type_bias}\n\t {player1.raise_bias}\n")

    for player in players:
        player.stop_learn()

    for gameidx in range(10):

        game = Game(players, 1000, 10)

        for i in range(3):
            game.play_game()

    # GOOD SIDES: Players don't fold without reason, players raise when they have relatively strong hands
    # WEAK SIDES: Players prone to bet all-in even if there are no clear reasons to do something like that


