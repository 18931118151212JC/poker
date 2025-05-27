import sys

from poker.environment.Game import Game
from poker.Players.HumanPlayer import HumanPlayer
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

    player1_actions = [["fold"], ["call", "raise 2", "call", "raise 4"], ["raise 200"], ["call", "raise 10"]]
    player1 = HumanPlayer(True, player1_actions, True, {})

    player2_actions = [["call", "call", "call", "call"], ["fold"], ["raise 200"], ["call", "call", "fold"]]
    player2 = HumanPlayer(True, player2_actions, True, {})

    player3_actions = [["call", "call", "call", "call"], ["call", "call", "call", "call", "call", "call"], ["raise 200"]]
    player3 = HumanPlayer(True, player3_actions, True, {})

    # TEST 1 CORRECTLY FOUND THAT THE THIRD PLAYER WINS (FULL HOUSE)
    players = [player1, player2, player3]
    game = Game(players, 100, 2)
    game.play_game()
    print("Game ended")

    # TEST 2 CORRECTLY DETERMINED THE WINNER AS THE FIRST PLAYER HAS KING > QUEEN FOR THE THIRD PLAYER
    print("#" * 100 + "\n" * 20 + '#' * 100 + '\n')
    game.play_game()
    print(f"Game ended")

    # TEST 3 EVERYONE PLAYS ALL-IN
    # CORRECTLY ASSIGNS THE VALUES. THIRD PLAYER IS SUPPOSED TO BE OUT OF GAME
    print("#" * 100 + "\n" * 20 + '#' * 100 + '\n')
    game.play_game()
    print(f"Game ended")

    # TEST 4 TWO PLAYERS LEFT (FIRST AND THE SECOND ONE)
    # CORRECT, SECOND PLAYER FOLDED
    # CORRECTLY TAKEN SMALL BLIND FOR 2 PLAYERS ONLY
    print("#" * 100 + "\n" * 20 + '#' * 100 + '\n')
    game.play_game()
    print(f"Game ended")

    # ALL TESTS PASSED

