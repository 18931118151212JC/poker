from poker.environment.Card import Card
from poker.Players.PlayerBase import PlayerBase
from copy import deepcopy
from random import sample
from poker.environment.Card import CombinationFinder
from random import random, randint, uniform


class RLPlayer(PlayerBase):
    """
    Reinforcement learning player class. If is_learning is True, then it will change the weights,
    otherwise it doesn't
    """

    def __init__(self, is_learning=False, *args):
        super().__init__(*args)
        self.alpha = 0.05
        self.gamma = 0.99
        self.epsilon = 0.99
        self.decay = 0.999
        self.is_learning = is_learning

        # zero is responsible for fold, first one is for call and second one is for the raise
        self.actions_type_num = 3
        # uniformly distributed over the total bank
        self.actions_raise_num = 20

        # last game information taken
        self.last_game_info = None

        # last game features
        self.last_action_features = None

        # last action taken. Form of integer
        self.last_action_type = None
        self.last_action_raise = None

        # Max length of features
        self.MAX_LEN = 20

        self.type_weights = [[0] * self.actions_type_num for _ in range(self.MAX_LEN)]
        self.type_bias = [0 for _ in range(self.actions_type_num)]

        self.raise_weights = [[0] * self.actions_raise_num for _ in range(self.MAX_LEN)]
        self.raise_bias = [0 for _ in range(self.actions_raise_num)]

        if self.is_learning:
            self.learn()

    def update_game_info(self, *args):
        """Update game info."""

        self.last_game_info = self.game_info
        super().update_game_info(*args)

        # Update the weights and bias in case out off money or won the game
        if self.last_action_type is not None and (self.player_profile.out_of_money or self.is_last_player()):
            self._update(self.last_action_features, self.type_weights, self.type_bias, self.last_action_type)
            # if last action was raise
            if self.last_action_type == 2:
                self._update(self.last_action_features, self.raise_weights, self.raise_bias, self.last_action_raise)

            self.last_action_type = None
            self.last_action_raise = None
            self.last_action_features = None



    def _update(self, features, weights, bias, action):
        """
        Update the weights and bias
        :return:
        """
        # if it is not learning, it won't update a thing
        if not self.is_learning:
            return

        r = self._reward_est()

        q_val = self._q(
            features,
            weights,
            bias,
            action
        )

        cur_features = self.get_features()

        if not self.is_terminal():
            q_max = max(range(len(weights[0])), key=lambda ap: self._q(
                cur_features,
                weights,
                bias,
                ap
            )
                        )
            delta = r + self.gamma * q_max - q_val
        else:
            delta = r - q_val
            self.epsilon *= self.decay

        l = min(self.MAX_LEN, len(features))
        for i in range(l):
            weights[i][action] += self.alpha * delta * features[i]
        bias[action] += self.alpha * delta

    def learn(self, weights=None, bias=None, reset_params=True, alpha=0.05, gamma=0.99, epsilon=0.99, decay=0.999):
        """
        Starts learning. Updates the weights
        :param bias:
        :param reset_params:
        :param alpha:
        :param gamma:
        :param epsilon:
        :param decay:
        :param weights: if None, then weights will be set to 0
        :return:
        """
        self.is_learning = True

        if reset_params:
            self.alpha = alpha
            self.gamma = gamma
            self.epsilon = epsilon
            self.decay = decay
            self.type_weights = [[0] * self.actions_type_num for _ in range(self.MAX_LEN)]
            self.type_bias = [[0] * self.actions_type_num for _ in range(self.MAX_LEN)]

        if weights is not None:
            self.type_weights = deepcopy(weights[0])
            self.raise_weights = deepcopy(weights[1])

        if bias is not None:
            self.type_bias = deepcopy(bias[0])
            self.raise_bias = deepcopy(bias[1])

    def get_features(self):
        """
        Features are current bet [0], amount of money left [1], probability of winning [2] and amount already bet [3]
        :return: a list of features
        """
        f = [
            self.player_profile.money / self.total_bank() * self.game_info.num_players,
            self.game_info.current_bet / self.total_bank(),
            self.winning_prob(),
            self.player_profile.bet / self.total_bank(),
        ]
        return f

    def total_bank(self):
        """Calculates the total amount of money in the game based on the game_info. Used to normalize features"""
        total_bank = 0
        for player_profile in self.game_info.players_profiles.values():
            total_bank += player_profile.money + player_profile.bet

        return total_bank

    def stop_learn(self):
        """
        Stops learning.
        :return:
        """
        self.is_learning = False

    def action(self):
        """
        Returns an action
        """

        # update the weights and biases
        if self.last_action_type is not None:
            self._update(self.last_action_features, self.type_weights, self.type_bias, self.last_action_type)
            # if last action was raise
            if self.last_action_type == 2:
                self._update(self.last_action_features, self.raise_weights, self.raise_bias, self.last_action_raise)

        features = self.get_features()

        if random() < self.epsilon:
            action_type = randint(0, 2)
        else:
            action_type = max(range(3), key=lambda a: self._q(features, self.type_weights, self.type_bias, a))

        self.last_action_type = action_type

        # if raise
        action_raise = 0
        if action_type == 2:
            if random() < self.epsilon:
                action_raise = randint(0, self.actions_raise_num - 1)
            else:
                action_type = max(range(self.actions_raise_num),
                                  key=lambda a: self._q(features, self.raise_weights, self.raise_bias, a))
            self.last_action_raise = action_raise


        self.last_action_features = features

        if action_type == 0:
            return super()._fold()

        if action_type == 1:
            return super()._call()

        diff = self.total_bank() / (self.actions_raise_num - 1)
        rand_val = uniform(-diff / 2, diff / 2)
        raise_val = max(0, round(diff * action_raise + rand_val))
        return super()._raise(raise_val)





    def winning_prob(self, iter_num=100) -> float:
        """
        Calculate probability of winning, knowing the cards. \n
        NOTE: Instead of using mathematical formulas, it simply iterates iter_num times.
        :return: Probability of winning the game
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

        return num_won / iter_num

    def is_terminal(self):
        """
        :return: True if the game is over, otherwise False.
        """
        if self.last_game_info is None:
            return False
        return self.last_game_info.game_idx != self.game_info.game_idx

    def is_last_player(self):
        """
        Returns True if this player is the only one who has money (game is over)
        """
        for player_profile in self.game_info.players_profiles.values():
            if player_profile.id != self.player_profile.id and not player_profile.out_of_money:
                return False

        return True


    def _reward_est(self):
        """Estimate the reward from the game"""
        # There is no previous information to compare with
        if self.last_game_info is None:
            return 0

        # After the end of the game, reward is simply the amount of
        if self.is_terminal():
            lost_in_game = 0
            last_standing = self.total_bank() / self.game_info.num_players

            # Lost the game. Additional punishment is initial amount of money
            if self.player_profile.out_of_money:
                lost_in_game = - self.total_bank() / self.game_info.num_players

            # If it is the last player in the game, the player won
            if lost_in_game == 0 and not self.is_last_player():
                last_standing = 0

            last_player_profile = self.game_info.players_profiles[self.player_profile.id]

            return ((self.player_profile.money + self.player_profile.bet)
                    - (last_player_profile.bet + last_player_profile.money)) \
                / self.total_bank() + lost_in_game + last_standing

        return 0

    def _q(self, features, weights, bias, action):
        """
        q function. Returns the action distribution
        :return:
        """
        q_val = 0
        l = min(self.MAX_LEN, len(features))
        for i in range(l):
            q_val += weights[i][action] * features[i]
        return q_val + bias[action]
