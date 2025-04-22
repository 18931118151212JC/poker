import sys

from poker.environment.Game import Game
from RLPlayer import RLPlayer
from random import seed
from logging import WARNING, DEBUG
import logging

if __name__ == '__main__':
    # ALL COMMENTS ABOUT THE CASES WHEN THE SEED IS SET TO 0.
    seed(0)

    # SET LEVEL TO DEBUG IF YOU WANT TO SEE THE GAME INFORMATION AFTER EVERY ROUND, SET TO WARNING NOT TO
    Game.logger.setLevel(WARNING)

    logging.basicConfig(
        format='%(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    # Letting players learn by switching learning rates
    player1 = RLPlayer()
    player2 = RLPlayer()

    players = [player1, player2]

    for i in range(len(players)):
        players[i].stop_learn()


    num_switches = 100
    num_big_games = 10
    num_games = 5

    for i in range(num_switches):
        players[i % len(players)].stop_learn()
        players[(i + 1) % len(players)].learn(reset_params=False)
        for j in range(num_big_games):
            game = Game(players, 1000, 10)
            for k in range(num_games):
                game.play_game()
        print(f"Completed {i + 1} switches out of {num_switches}")

    Game.logger.setLevel(DEBUG)

    for player in players:
        player.stop_learn()

    game = Game(players, 1000, 10)

    for i in range(5):
        game.play_game()

    # GOOD SIDES: Players don't fold without reason, players raise when they have relatively strong hands
    # WEAK SIDES: Players prone to bet all-in even if there are no clear reasons to do something like that




