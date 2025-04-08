import uuid
from Card import Card
from random import choices
from uuid import uuid4
from copy import deepcopy


# class PlayerProfile:
#     """
#     Contains the information about the player. Used in the game class to
#     store information about each player.
#     """
#     def __init__(self, start_value: int, player_id: uuid):
#         self.money = start_value
#         self.cards = []
#         self.id = player_id
#
#         # If the player is out of money to continue playing
#         self.out_of_money = False
#
#         # If the player is still in game (False if folded)
#         self.is_in_game = True
#
#     def get_dict(self):
#         d = {}
#         d['player_id'] = self.id
#         d['money'] = self.money
#         d['cards'] = self.cards
#         d['out_of_money'] = self.out_of_money
#         d['is_in_game'] = self.is_in_game
#         return d




class PlayerBase:
    """
    Base for different subclasses of players with its own agents and behaviors
    """


    def __init__(self, player_profile: dict):
        self.game_info = {}
        self.player_profile = player_profile

    def update_game_info(self, game_info: dict):
        self.game_info = game_info

    def update_player_profile(self, player_profile: dict):
        self.player_profile = player_profile

    def action(self):
        """Returns the bet the player did"""
        pass



class Game:
    @staticmethod
    def _create_player_profile(start_value: int, player_id: uuid):
        d = {
            "money": start_value,
            "cards": [],
            "id": player_id,
            "out_of_money": False,  # True if is out of money (can't play anymore)
            "is_active": True,  # True if the player didn't fold yet
            "pod_num": 0
        }
        return d

    def __init__(self, num_players: int, start_value: int, small_blind: int):
        self.num_players = num_players
        # number of players that are still in the round
        self.num_active_players = num_players
        # number of players that are still in the game (still have money)
        self.num_players_in_game = num_players

        self.start_value = start_value
        self.small_blind = small_blind
        self.dealer_idx = 0

        # Leaving players empty for a while
        self.players_ids = [uuid4() for _ in range(num_players)]
        self.players_profiles = {self.players_ids[i]: Game._create_player_profile(start_value, self.players_ids[i]) for i in range(num_players)}
        self.players = [PlayerBase(deepcopy(self.players_profiles[self.players_ids[i]])) for i in range(num_players)]

        self.pods = [0]

        self.community_cards = []
        self.shown_community_cards = []

    def provide_game_info(self):
        """
        Provides information about the game to the players
        """
        game_info = {
            "num_players": self.num_players,
            "small_blind": self.small_blind,
            "dealer_idx": self.dealer_idx,
            "players_profiles": self.players_profiles,
            "pods": self.pods,
            "shown_community_cards": self.shown_community_cards
        }

        for player in self.players:
            player.update_game_info(deepcopy(game_info))


    def give_cards(self):
        """
        Randomly gives the cards away and selects community cards
        """
        deck = Card.all_possible_cards()
        num_drawn_cards = self.num_players * 2 + 5
        drawn_cards = choices(deck, k=num_drawn_cards)
        self.community_cards = drawn_cards[:5]

        for i in range(len(self.players)):
            player_id = self.players_ids[i]
            player_profile = self.players_profiles[player_id]
            player_profile.cards = drawn_cards[5 + 2 * i : 5 + 2 * (i + 1)]


    def play_round(self, bet_start_idx: int):




    def play_game(self):

