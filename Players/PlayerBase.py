from copy import deepcopy
from poker.environment.Game import GameInfo
from poker.Players.PlayerProfile import PlayerProfile
from poker.environment.Card import Card
from random import sample
from poker.environment.Card import CombinationFinder


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

    def total_bank(self):
        """Calculates the total amount of money in the game based on the game_info. Used to normalize features"""
        total_bank = 0
        for player_profile in self.game_info.players_profiles.values():
            total_bank += player_profile.money + player_profile.bet

        return total_bank

    def game_over(self, earned: int):
        """Passing earned value in the end of the game"""
        pass

    def winning_prob(self, iter_num=200) -> float:
        """
        Calculate probability of winning, knowing the cards. \n
        NOTE: Instead of using mathematical formulas, it simply iterates iter_num times.
        :return: Probability of winning the game up to 3 digits
        """
        cards = Card.all_possible_cards()

        for player_profile in self.game_info.players_profiles.values():
            if player_profile.showed_cards:
                for card in player_profile.cards:
                    cards.remove(card)

        for card in self.game_info.shown_community_cards:
            cards.remove(card)

        if not self.player_profile.showed_cards:
            for card in self.player_profile.cards:
                cards.remove(card)

        final_community_cards = deepcopy(self.game_info.shown_community_cards)

        # the first element of the players_cards is always this player cards
        players_cards = [deepcopy(self.player_profile.cards)]

        num_unknown_pairs = 0
        for player_profile in self.game_info.players_profiles.values():
            if not (player_profile.out_of_money or player_profile.fold) \
                    and player_profile.id != self.player_profile.id:
                if player_profile.showed_cards:
                    players_cards.append(deepcopy(player_profile.cards))
                else:
                    players_cards.append([])
                    num_unknown_pairs += 1

        # finding out number of cards to draw
        community_cards_num_to_draw = 5 - len(final_community_cards)

        # number of winning iterations
        num_won = 0

        for it in range(iter_num):
            it_players_cards = deepcopy(players_cards)
            it_community_cards = deepcopy(final_community_cards)

            drawn_cards = sample(cards, k=community_cards_num_to_draw + 2 * num_unknown_pairs)
            it_community_cards.extend(drawn_cards[:community_cards_num_to_draw])

            cnt = 0
            for i in range(len(it_players_cards)):
                if not it_players_cards[i]:
                    it_players_cards[i] = drawn_cards[
                                          community_cards_num_to_draw + 2 * cnt: community_cards_num_to_draw + 2 * cnt + 2]
                    cnt += 1
                it_players_cards[i].extend(it_community_cards)

            won = True
            for i in range(1, len(it_players_cards)):
                if CombinationFinder.combination_comparator(it_players_cards[0], it_players_cards[i]) < 0:
                    won = False
                    break

            if won:
                num_won += 1

        # print(self.player_profile.cards, self.game_info.shown_community_cards, num_won / iter_num)

        return round(num_won / iter_num, 3)



