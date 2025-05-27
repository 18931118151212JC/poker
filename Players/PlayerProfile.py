from poker.environment.Card import CombinationFinder
from copy import deepcopy


class PlayerProfile:
    """
    Class of profile
    """
    def __init__(self, start_value, player_id):
        self.money = start_value
        self.cards = []
        self.id = player_id
        self.out_of_money = False  # True if is out of money (can't play anymore)
        self.fold = False  # True if the player folded yet
        self.showed_cards = False  # True if the player showed the cards
        self.all_in = False  # True if the player played all-in
        self.current_round_bet = 0  # Amount of money already bet in the current round
        self.bet = 0  # Total amount of money that was bet during all rounds in one game

    def get_cards(self):
        deepcopy(self.cards)

    def __str__(self):
        s = ""
        for key, val in vars(self).items():
            s += f"\t{key}: {val}\n"

        return s


    def reset(self):
        """Resets the players profile after the game has finished"""
        if self.money == 0:
            self.out_of_money = True

        self.showed_cards = False
        self.all_in = False
        self.bet = 0
        self.current_round_bet = 0
        self.fold = False


    @staticmethod
    def players_profile_comparator(player_profile1: "PlayerProfile", player_profile2: "PlayerProfile"):
        """
        Compares two players profiles. The priority of comparing: \n
        1) Folded or out_of_money (negative if player1 is not in game and positive if player2 isn't)\n
        2) combination strength (positive if player1 has stronger hand)\n
        3) amount of bet (positive if the player_profile1 has higher bet) \n
        """
        if player_profile1.fold or player_profile1.out_of_money:
            return -1
        if player_profile2.fold or player_profile2.out_of_money:
            return 1

        dif = CombinationFinder.combination_comparator(player_profile1.cards, player_profile2.cards)
        if dif != 0:
            return dif

        return player_profile1.bet - player_profile2.bet
