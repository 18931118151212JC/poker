from poker.Players.HumanPlayer import HumanPlayer
from poker.Players.RLPlayer import RLPlayer
from poker.Players.PlayerBase import PlayerBase
from pickle import load
from typing import TypeAlias
from poker.environment.Game import Game
from logging import WARNING, DEBUG
import logging
import sys
import types



if __name__ == '__main__':
    # Patch sys.modules to map 'RLPlayer' to your actual module
    import poker.Players.RLPlayer as actual_module

    sys.modules['RLPlayer'] = actual_module

    # logging.basicConfig(
    #     format='%(message)s',
    #     handlers=[logging.StreamHandler(sys.stdout)]
    # )
    #
    # Game.logger.setLevel(DEBUG)

    player1 = HumanPlayer(verbose=True)
    player2 = None
    with open('../Players/RLPlayer_agent_sw900_p2_weighted.pkl', 'rb') as f:
        player2 = load(f)

    game = Game(players=[player1, player2], start_value=1000, small_blind=10)
    for i in range(10):
        game.play_game()
