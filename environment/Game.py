import uuid
from .Card import Card, CombinationFinder
from random import sample
from uuid import uuid4
from copy import deepcopy
from functools import cmp_to_key
import logging
from poker.Players.PlayerProfile import PlayerProfile


class GameInfo:
    """
    Class of information about the game
    """
    def __init__(self):
        self.small_blind = None
        self.num_players = None
        self.dealer_idx = None
        self.players_profiles = None
        self.shown_community_cards = None
        self.current_bet = None
        self.players_ids = None
        self.game_idx = None
        self.round_idx = None

    def __str__(self):
        """
        Converts game information to convenient string representation for logging and printing
        """
        s = "GAME CURRENT STATE:\n\n"

        for key, val in vars(self).items():
            if key != "players_profiles":
                s += f"{key}: {val}\n"

        s += "players_profiles:\n"

        for player_id in self.players_profiles:
            player_profile = self.players_profiles[player_id]
            s += f"{player_id}:\n {str(player_profile)}\n"

        return s


class Game:
    logger = logging.getLogger("Game")
    logger.setLevel(logging.WARNING)


    def __init__(self, players: list, start_value: int, small_blind: int):
        self.num_players = len(players)
        # number of players that are still in the round
        self.num_active_players = self.num_players
        # number of players that are still in the game (still have money)
        self.num_players_in_game = self.num_players

        self.start_value = start_value
        self.small_blind = small_blind
        self.dealer_idx = 0

        self.game_idx = 0
        self.round_idx = 0

        # Leaving players empty for a while
        self.players_ids = [uuid4() for _ in range(self.num_players)]
        self.players_profiles = {
            self.players_ids[i]: PlayerProfile(start_value, self.players_ids[i])
            for i in range(self.num_players)
        }
        # self.players = [PlayerBase(deepcopy(self.players_profiles[self.players_ids[i]])) for i in range(num_players)]
        self.players = players
        for i in range(self.num_players):
            player_id = self.players_ids[i]
            self.players[i].update_player_profile(deepcopy(self.players_profiles[player_id]))

        self.community_cards = []
        self.shown_community_cards = []
        self.current_round_bet = 0

    def _create_game_info(self) -> GameInfo:
        """
        Creates GameInfo of the current game
        :return: game information class
        """

        game_info = GameInfo()
        game_info.num_players = self.num_players
        game_info.small_blind = self.small_blind
        game_info.dealer_idx = self.dealer_idx
        game_info.players_profiles = self.players_profiles
        game_info.shown_community_cards = self.shown_community_cards
        game_info.current_bet = self.current_round_bet
        game_info.players_ids = self.players_ids
        game_info.game_idx = self.game_idx
        game_info.round_idx = self.round_idx

        return deepcopy(game_info)




    def provide_game_info(self, verbose=False):
        """
        Provides information about the game to the players
        """

        game_info = self._create_game_info()
        for i in range(self.num_players):
            player = self.players[i]
            player_id = self.players_ids[i]

            if not game_info.players_profiles[player_id].showed_cards:
                game_info.players_profiles[player_id].cards = []

            player.update_player_profile(deepcopy(self.players_profiles[player_id]))

        for i in range(self.num_players):
            player = self.players[i]
            player.update_game_info(deepcopy(game_info))

        if verbose:
            return game_info

    def give_cards(self):
        """
        Randomly gives the cards away and selects community cards
        """
        deck = Card.all_possible_cards()
        num_drawn_cards = self.num_players * 2 + 5
        drawn_cards = sample(deck, k=num_drawn_cards)
        self.community_cards = drawn_cards[:5]
        self.shown_community_cards = []

        for i in range(len(self.players)):
            player_id = self.players_ids[i]
            player_profile = self.players_profiles[player_id]
            player_profile.cards = drawn_cards[5 + 2 * i: 5 + 2 * (i + 1)]

    def _get_next_player_idx(self, i: int):
        """Index of the next player still playing"""
        j = (i + 1) % self.num_players

        player_profile_j = self.players_profiles[self.players_ids[j]]
        while player_profile_j.fold or player_profile_j.out_of_money:
            j = (j + 1) % self.num_players
            player_profile_j = self.players_profiles[self.players_ids[j]]

        return j

    def _action_processing(self, action_bet: int, player_id: uuid):
        """
        Processes the action (bet) that was made by the player
        :returns: True if the bet was raised, False otherwise
        """
        player_profile = self.players_profiles[player_id]
        action_bet = min(action_bet, player_profile.money)

        if player_profile.current_round_bet + action_bet < self.current_round_bet:

            if action_bet == player_profile.money:
                player_profile.all_in = True
                player_profile.money = 0
                player_profile.current_round_bet += action_bet
                player_profile.bet += action_bet

            else:
                player_profile.fold = True

            return False

        else:
            player_profile.bet += action_bet
            player_profile.current_round_bet += action_bet
            player_profile.money -= action_bet

            if player_profile.money == 0:
                player_profile.all_in = True

            if player_profile.current_round_bet == self.current_round_bet:
                return False

            self.current_round_bet = player_profile.current_round_bet
            return True

    def count_active_players(self):
        """Return the number of players still in the game"""
        num_active_players = self.num_players
        for player_profile in self.players_profiles.values():
            if player_profile.out_of_money or player_profile.fold:
                num_active_players -= 1

        return num_active_players

    def play_round(self, bet_start_idx: int):
        """
        Plays betting round
        :param bet_start_idx: the index of the first player to bet
        :return: True if the game is still going, False otherwise
        """

        last_index_raised = bet_start_idx
        current_player_index = bet_start_idx
        first_flag = True

        while first_flag or last_index_raised != current_player_index:
            first_flag = False
            self.provide_game_info()
            player_uuid = self.players_ids[current_player_index]
            player = self.players[current_player_index]
            player_profile = self.players_profiles[player_uuid]

            if not (player_profile.fold or player_profile.out_of_money or player_profile.all_in):
                action_bet = player.action()
                if self._action_processing(action_bet, player_uuid):
                    last_index_raised = current_player_index
                elif last_index_raised == current_player_index and player_profile.fold:
                    # IF THE FIRST PLAYER BET IS FOLD, MAKE THE NEXT PERSON THE FIRST ONE TO BET
                    last_index_raised = self._get_next_player_idx(current_player_index)
                    first_flag = True

            current_player_index = self._get_next_player_idx(current_player_index)

            if self.count_active_players() == 1:
                self.provide_game_info()
                return False

        # Set current_round_bet back to 0
        for player_profile in self.players_profiles.values():
            player_profile.current_round_bet = 0

        self.provide_game_info()
        return self.count_active_players() != 1

    def _update_players_profiles(self):
        """Updates the players profiles"""
        for player_profile in self.players_profiles.values():
            player_profile.reset()

    def play_game(self):
        """
        Plays a game. Firstly runs rounds and updates money value in players_profiles
        :return:
        """
        self.give_cards()
        self._update_players_profiles()

        active_players = self.count_active_players()

        if active_players == 1:
            self.game_end()
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

        Game.logger.debug(str(self._create_game_info()))
        self.current_round_bet = 0
        self.shown_community_cards = self.community_cards[:3]
        start_bet_idx = self._get_next_player_idx(self.dealer_idx)
        if not self.play_round(start_bet_idx):
            self.game_end()
            return

        Game.logger.debug(str(self._create_game_info()))
        self.current_round_bet = 0
        self.shown_community_cards.append(self.community_cards[3])
        start_bet_idx = self._get_next_player_idx(self.dealer_idx)
        if not self.play_round(start_bet_idx):
            self.game_end()
            return

        Game.logger.debug(str(self._create_game_info()))
        self.current_round_bet = 0
        self.shown_community_cards.append(self.community_cards[4])
        start_bet_idx = self._get_next_player_idx(self.dealer_idx)
        if not self.play_round(start_bet_idx):
            self.game_end()
            return

        start_player_idx = cur_player_idx = self._get_next_player_idx(self.dealer_idx)
        flag = True
        while flag or cur_player_idx != start_player_idx:
            self.players_profiles[self.players_ids[cur_player_idx]].showed_cards = True
            cur_player_idx = self._get_next_player_idx(cur_player_idx)
            flag = False

        self.game_end()
        self.provide_game_info()

    def game_end(self):
        """Updates the information about the end of the game (determines the winner, gives the money back"""
        players_profiles = deepcopy(list(self.players_profiles.values()))

        for player_profile in players_profiles:
            player_profile.cards = player_profile.cards + self.community_cards

        players_profiles.sort(key=cmp_to_key(PlayerProfile.players_profile_comparator), reverse=True)

        i = 0
        while i < len(players_profiles):
            if players_profiles[i].out_of_money or players_profiles[i].fold:
                break
            j = i
            while j < len(players_profiles) and CombinationFinder.combination_comparator(
                    players_profiles[i].cards, players_profiles[j].cards
            ) == 0:
                j += 1

            # smallest bet among equally strong hand players
            j -= 1
            get_bet = players_profiles[j].bet
            total_gain = 0
            m = j - i + 1
            for k in range(j + 1, len(players_profiles)):
                total_gain += min(players_profiles[k].bet, get_bet)
                players_profiles[k].bet = max(0, players_profiles[k].bet - get_bet)

            for k in range(i, j + 1):
                players_profiles[k].money += total_gain // m

            for k in range(i, i + total_gain % m):
                players_profiles[k].money += 1

            for k in range(i, j + 1):
                players_profiles[k].money += players_profiles[k].bet

            i = j + 1

        for player_profile in players_profiles:
            player_id = player_profile.id
            self.players_profiles[player_id].money = player_profile.money

        self._update_players_profiles()
        self.dealer_idx = self._get_next_player_idx(self.dealer_idx)
        Game.logger.debug(str(self._create_game_info()))

        self.game_idx += 1
