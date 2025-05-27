import sys

from poker.environment.Game import Game
from MCCFRPlayer import MCCFPlayer
from random import seed
from logging import WARNING, DEBUG
import logging

from pickle import dump, load

if __name__ == '__main__':
    # seed(0)

    # SET LEVEL TO DEBUG IF YOU WANT TO SEE THE GAME INFORMATION AFTER EVERY ROUND, SET TO WARNING NOT TO
    Game.logger.setLevel(WARNING)

    logging.basicConfig(
        format='%(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    player1 = MCCFPlayer(is_learning=True)
    player2 = MCCFPlayer(is_learning=True)
    players = [player1, player2]

    num_iter = 1000000
    num_games = 3

    # name of the pickle saved agent to use
    file_name = "MCCFRPlayer_nodes_prob10_sample400.pkl"

    with open(file_name, "rb") as f:
        MCCFPlayer.nodes = load(f)

    for i in range(num_iter):
        game = Game(players, 1000, 10)
        for j in range(num_games):
            game.play_game()
        if (i + 1) % 50 == 0:
            print(f"Completed {i + 1} games out of {num_iter}")
            # print(MCCFPlayer.nodes)

        # Saving progress
        if (i + 1) % 50 == 0:
            with open(file_name, 'wb') as f:
                dump(MCCFPlayer.nodes, f)
            print("===SAVED===")

    with open(file_name, 'wb') as f:
        dump(MCCFPlayer.nodes, f)

    Game.logger.setLevel(DEBUG)

    player1.is_learning = False
    player2.is_learning = False

    for gameidx in range(3):

        game = Game(players, 1000, 10)

        for i in range(1):
            game.play_game()

    # for node in MCCFPlayer.nodes.values():
    #     if round(node.get_average_strategy()[0], 5) != round(1 / 12, 5):
    #         print(node.info_set)
    #         print(node.get_average_strategy())

    # For some reason, agent is really prone to betting all-in. Much more inadequate than RL
