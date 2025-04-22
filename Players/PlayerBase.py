from copy import deepcopy
from poker.environment.Game import GameInfo
from .PlayerProfile import PlayerProfile


class PlayerBase:
    """
    Base for different subclasses of players with its own agents and behaviors
    """

    def __init__(self, player_profile: PlayerProfile = None):
        self.game_info = GameInfo()
        self.player_profile = player_profile

    def update_game_info(self, game_info: GameInfo):
        self.game_info = game_info

    def update_player_profile(self, player_profile: PlayerProfile):
        self.player_profile = player_profile

    def action(self):
        """Returns the bet the player did"""
        pass

    def _fold(self):
        return -1

    def _call(self):
        current_bet = self.game_info.current_bet
        return current_bet - self.player_profile.current_round_bet

    def _raise(self, x: int):
        current_bet = self.game_info.current_bet
        return current_bet - self.player_profile.current_round_bet + x



