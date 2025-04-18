import uuid
from Card import Card, CombinationFinder
from random import choices
from uuid import uuid4
from copy import deepcopy
from functools import cmp_to_key


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
            "fold": False,  # True if the player folded yet
            "showed_cards": False,  # True if the player showed the cards
            "all-in": False,  # True if the player played all-in
            "current_round_bet": 0,  # Amount of money already bet in the current round
            "bet": 0  # Total amount of money that was bet during all rounds in one game
        }
        return d

    @staticmethod
    def _reset_player_profile(player_profile: dict):
        """Resets the players profile after the game has finished"""
        if player_profile["money"] == 0:
            player_profile["out_of_money"] = True

        player_profile["showed_cards"] = False
        player_profile["all-in"] = False
        player_profile["bet"] = 0
        player_profile["current_round_bet"] = 0
        player_profile["fold"] = False

    @staticmethod
    def _players_profile_comparator(player_profile1: dict, player_profile2: dict):
        """
        Compares two players profiles. The priority of comparing: \n
        1) Folded or out_of_money (negative if player1 is not in game and positive if player2 isn't)\n
        2) combination strength (positive if player1 has stronger hand)\n
        3) amount of bet (positive if the player_profile1 has higher bet) \n
        """
        if player_profile1["fold"] or player_profile1["out_of_money"]:
            return -1
        if player_profile2["fold"] or player_profile2["out_of_money"]:
            return 1

        dif = CombinationFinder.combination_comparator(player_profile1["cards"], player_profile2["cards"])
        if dif != 0:
            return dif

        return player_profile1["bet"] - player_profile2["bet"]

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
        self.players_profiles = {
            self.players_ids[i]: Game._create_player_profile(start_value, self.players_ids[i])
            for i in range(num_players)
        }
        self.players = [PlayerBase(deepcopy(self.players_profiles[self.players_ids[i]])) for i in range(num_players)]

        self.pots = [0]
        self.players_in_pots = [player_id for player_id in self.players_ids]
        self.pots_bet = [0]  # bet to participate in the pot

        self.community_cards = []
        self.shown_community_cards = []
        self.current_round_bet = 0

    def provide_game_info(self):
        """
        Provides information about the game to the players
        """
        game_info = {
            "num_players": self.num_players,
            "small_blind": self.small_blind,
            "dealer_idx": self.dealer_idx,
            "players_profiles": self.players_profiles,
            "pots": self.pots,
            "shown_community_cards": self.shown_community_cards,
            "current_bet": self.current_round_bet,
        }

        for i in range(self.num_players):
            player = self.players[i]
            player_id = self.players_ids[i]
            game_info_copy = deepcopy(game_info)
            if not game_info_copy["players_profiles"][player_id]["showed_cards"]:
                game_info_copy["players_profiles"][player_id]["cards"] = []

            player.update_game_info(game_info_copy)

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
            player_profile.cards = drawn_cards[5 + 2 * i: 5 + 2 * (i + 1)]

    def _get_next_player_idx(self, i: int):
        j = (i + 1) % self.num_players

        player_profile_j = self.players_profiles[self.players_ids[j]]
        while player_profile_j["fold"] or player_profile_j["out_of_money"]:
            j = (j + 1) % self.num_players
            player_profile_j = self.players_profiles[self.players_ids[j]]

        return j

    def _action_processing(self, action_bet: int, player_id: uuid):
        """
        Processes the action (bet) that was made by the player
        :returns: True if the bet was raised, False otherwise
        """
        player_profile = self.players_profiles[player_id]
        action_bet = min(action_bet, player_profile["money"])

        if player_profile["current_round_bet"] + action_bet < self.current_round_bet:

            if action_bet == player_profile["money"]:
                player_profile["all-in"] = True
                player_profile["money"] = 0
                player_profile["current_round_bet"] += action_bet
                player_profile["bet"] += action_bet

            else:
                player_profile["fold"] = True

            return False

        else:
            player_profile["bet"] += action_bet
            player_profile["current_round_bet"] += action_bet
            player_profile["money"] -= action_bet

            if player_profile["money"] == 0:
                player_profile["all-in"] = True

            if player_profile["current_round_bet"] == self.current_round_bet:
                return False

            self.current_round_bet = player_profile["current_round_bet"]
            return True

    def count_active_players(self):
        num_active_players = self.num_players
        for player_profile in self.players_profiles.values():
            if player_profile["out_of_money"] or player_profile["fold"]:
                num_active_players -= 1

        return num_active_players

    def play_round(self, bet_start_idx: int, is_first_round: bool = False):
        """
        Plays betting round
        :param bet_start_idx: the index of the first player to bet
        :param is_first_round: True if it is the first round, False otherwise
        :return: True if the game is still going, False otherwise
        """

        last_index_raised = bet_start_idx
        current_player_index = bet_start_idx
        first_flag = True

        while first_flag or last_index_raised != current_player_index:
            self.provide_game_info()
            player_uuid = self.players_ids[current_player_index]
            player = self.players[current_player_index]
            player_profile = self.players_profiles[player_uuid]

            if not (player_profile["fold"] or player_profile["out_of_money"] or player_profile["all-in"]):
                action_bet = player.action()
                if self._action_processing(action_bet, player_uuid):
                    last_index_raised = current_player_index

            first_flag = False
            current_player_index = self._get_next_player_idx(current_player_index)

            if self.count_active_players() == 1:
                self.provide_game_info()
                return False

        self.provide_game_info()
        return self.count_active_players() != 1


    def _update_players_profiles(self):
        """Updates the players profiles"""
        for player_profile in self.players_profiles.values():
            Game._reset_player_profile(player_profile)

    # TODO
    def play_game(self):
        """
        Plays a game. Firstly runs rounds and updates money value in players_profiles
        :return:
        """
        self.give_cards()
        self._update_players_profiles()

        active_players = self.count_active_players()

        if active_players == 1:
            return

        self.current_round_bet = self.small_blind
        small_blind_player_idx = self.dealer_idx if active_players == 2 else self._get_next_player_idx(self.dealer_idx)
        small_blind_player_id = self.players_ids[small_blind_player_idx]
        self._action_processing(self.small_blind, small_blind_player_id)

        self.current_round_bet = self.small_blind * 2
        big_blind_player_idx = self._get_next_player_idx(small_blind_player_idx)
        big_blind_player_id = self.players_ids[big_blind_player_idx]
        self._action_processing(self.small_blind * 2, big_blind_player_id)

        start_bet_idx = self._get_next_player_idx(big_blind_player_idx)
        if not self.play_round(start_bet_idx):
            self.game_end()
            return

        self.shown_community_cards = self.community_cards[:3]
        start_bet_idx = self._get_next_player_idx(self.dealer_idx)
        if not self.play_round(start_bet_idx):
            self.game_end()
            return

        self.shown_community_cards.append(self.community_cards[3])
        start_bet_idx = self._get_next_player_idx(self.dealer_idx)
        if not self.play_round(start_bet_idx):
            self.game_end()
            return

        self.shown_community_cards.append(self.community_cards[4])
        start_bet_idx = self._get_next_player_idx(self.dealer_idx)
        if not self.play_round(start_bet_idx):
            self.game_end()
            return

        start_player_idx = cur_player_idx = self._get_next_player_idx(self.dealer_idx)
        flag = True
        while flag or cur_player_idx != start_player_idx:
            self.players_profiles[self.players_ids[cur_player_idx]]["showed_cards"] = True
            cur_player_idx = self._get_next_player_idx(cur_player_idx)
            flag = False

        self.provide_game_info()
        self.game_end()


    def game_end(self):
        players_profiles = deepcopy(list(self.players_profiles.values()))

        for player_profile in players_profiles:
            player_profile["cards"] = player_profile["cards"] + self.community_cards

        players_profiles.sort(key=cmp_to_key(Game._players_profile_comparator), reverse=True)

        i = 0
        while i < len(players_profiles):
            if players_profiles[i]["out_of_money"] or players_profiles[i]["fold"]:
                break
            j = i
            while j < len(players_profiles) and CombinationFinder.combination_comparator(
                players_profiles[i]["cards"], players_profiles[j]["cards"]
            ) == 0:
                j += 1

            # smallest bet among equally strong hand players
            j -= 1
            get_bet = players_profiles[j]["bet"]
            total_gain = 0
            m = j - i + 1
            for k in range(j + 1, len(players_profiles)):
                total_gain += min(players_profiles[k]["bet"], get_bet)
                players_profiles[k]["bet"] = max(0, players_profiles[k]["bet"] - get_bet)


            for k in range(i, j + 1):
                players_profiles[k]["money"] += total_gain // m

            for k in range(i, i + total_gain % m):
                players_profiles[k]["money"] += 1

            for k in range(i, j + 1):
                players_profiles[k]["bet"] -= get_bet
                players_profiles[k]["money"] += players_profiles[k]["bet"]

        for player_profile in players_profiles:
            player_id = player_profile["id"]
            self.players_profiles[player_id]["money"] = player_profile["money"]

        self._update_players_profiles()