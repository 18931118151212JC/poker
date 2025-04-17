from poker.environment.Game import Game
from poker.environment.Player import HumanPlayer
from random import seed

if __name__ == '__main__':
    seed(0)
    player1_actions = [["fold"], ["call", "raise 2", "call", "raise 4"]]
    player1 = HumanPlayer(True, player1_actions, True, {})

    player2_actions = [["call", "call", "call", "call"], ["fold"]]
    player2 = HumanPlayer(True, player2_actions, False, {})

    player3_actions = [["call", "call", "call", "call"], ["call", "call", "call", "call", "call"]]
    player3 = HumanPlayer(True, player3_actions, True, {})

    # TEST 1 CORRECTLY FOUND THAT BOTH PLAYERS HAVE FULL HOUSES AND BOTH PLAYERS DIVIDE THE POT
    players = [player1, player2, player3]
    game = Game(players, 100, 2)
    game.play_game()
    print(f"Game ended: {game.provide_game_info(verbose=True)}")

    print("#" * 100 + "\n" * 20 + '#' * 100 + '\n')
    game.play_game()
    print(f"Game ended: {game.provide_game_info(verbose=True)}")