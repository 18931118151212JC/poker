from poker.environment.Card import Card
from poker.environment.Player import PlayerBase
from copy import deepcopy
from random import choices
from poker.environment.Card import CombinationFinder

class RLPlayer(PlayerBase):

    def __init__(self, is_learning=False, *args):
        super().__init__(*args)
        self.alpha = 0.05
        self.gamma = 0.99
        self.epsilon = 0.99
        self.decay = 0.999
        self.is_learning = is_learning
        # first one is responsible for 0, second one for 1, third one for 2, fourth one for 4, etc...
        self.actions_num = 30

        # States are current bet [0], money left [1] and probability of winning [2]
        self.weights = [[0]]



        if self.is_learning:
            self.learn()





    def learn(self, weights=None, alpha=0.05, gamma=0.99, epsilon=0.99, decay=0.999):
        """
        Starts learning. Updates the weights
        :param alpha:
        :param gamma:
        :param epsilon:
        :param decay:
        :param weights: if none, then weights will be set to 0
        :return:
        """
        self.is_learning = True
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.decay = decay

        if weights is None:
            self.weights = weights





    def winning_prob(self, iter_num=1000) -> float:
        """
        Calculate probability of winning, knowing the cards. \n
        NOTE: Instead of using mathematical formulas, it simply iterates iter_num times.
        :return: Probability of winning the game
        """
        cards = Card.all_possible_cards()

        for player_profile in self.game_info["players_profiles"].values():
            if player_profile["showed_cards"]:
                for card in player_profile["cards"]:
                    cards.remove(card)

        for card in self.game_info["community_cards"]:
            cards.remove(card)

        if not self.player_profile["showed_cards"]:
            for card in self.player_profile["cards"]:
                cards.remove(card)

        final_community_cards = deepcopy(self.game_info["community_cards"])

        # the first element of the players_cards is always this player cards
        players_cards = [deepcopy(self.player_profile["cards"])]

        num_unknown_pairs = 0
        for player_profile in self.game_info["players_profiles"].values():
            if not (player_profile["out_of_money"] or player_profile["fold"]) \
                    and player_profile["id"] != self.player_profile["id"]:
                if player_profile["showed_cards"]:
                    players_cards.append(deepcopy(player_profile["cards"]))
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

            drawn_cards = choices(cards, k=community_cards_num_to_draw + 2 * num_unknown_pairs)
            it_community_cards.extend(drawn_cards[:community_cards_num_to_draw])

            cnt = 0
            for i in range(len(it_players_cards)):
                if not it_players_cards[i]:
                   it_players_cards[i] = drawn_cards[community_cards_num_to_draw + 2 * cnt: community_cards_num_to_draw + 2 * cnt + 2]
                   cnt += 1
                it_players_cards[i].extend(it_community_cards)

            won = True
            for i in range(1, len(it_players_cards)):
                if CombinationFinder.combination_comparator(it_players_cards[0], it_players_cards[i]) < 0:
                    won = False
                    break

            if won:
                num_won += 1

        return num_won / iter_num





