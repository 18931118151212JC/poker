from PlayerBase import PlayerBase
from random import choices

"""
This CFR implementation is inspired by the code of github user andyliu42

CFR for KHUN Poker code: https://github.com/andyliu42/Counterfactual_Regret_Minimization_Python/blob/master/Kuhn_poker/Kuhn_poker_CFR.py
Profile: https://github.com/andyliu42


"""


class Node():
    def __init__(self, num_of_actions):
        self.info_set = ()
        self.regret_sum = [0.0] * num_of_actions
        self.strategy = [0.0] * num_of_actions
        self.strategy_sum = [0.0] * num_of_actions
        self.num_of_actions = num_of_actions
        self.actions = [i for i in range(self.num_of_actions)]
        self.util = [0] * self.num_of_actions
        self.node_util = 0

    # Realization weight is probability of reaching this node by the current player
    def update_strategy(self, realization_weight):
        normalizing_sum = 0.0
        for a in range(self.num_of_actions):
            self.strategy[a] = self.regret_sum[a] if self.regret_sum[a] > 0 else 0
            normalizing_sum += self.strategy[a]
        for a in range(self.num_of_actions):
            if normalizing_sum > 0:
                self.strategy[a] /= normalizing_sum
            else:
                self.strategy[a] = 1.0 / self.num_of_actions
            self.strategy_sum[a] += realization_weight * self.strategy[a]

    def get_average_strategy(self):
        avg_strategy = [0.0] * self.num_of_actions
        normalizing_sum = 0.0
        for a in range(self.num_of_actions):
            normalizing_sum += self.strategy_sum[a]
        for a in range(self.num_of_actions):
            if normalizing_sum > 0:
                avg_strategy[a] = self.strategy_sum[a] / normalizing_sum
            else:
                avg_strategy[a] = 1.0 / self.num_of_actions
        return avg_strategy

    def get_action(self):
        return choices(self.actions, self.get_average_strategy(), k=1)[0]

    def update_util(self, action, cfr):
        self.node_util += cfr * self.strategy[action] - self.util[action]
        self.util[action] = cfr

    def update_regrets(self, p):
        for a in range(self.num_of_actions):
            regret = self.util[a] - self.node_util
            self.regret_sum[a] += p * regret


class MCCFPlayer(PlayerBase):
    action_taken = []
    prob = []
    node_order = []
    player_id_order = []
    nodes = {}

    def __init__(self, is_learning=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # last game information taken
        self.last_game_info = None

        self.actions_raise_num = 10

        self.is_learning = is_learning

        # amount of money gained
        self.gained = 0

    def update_game_info(self, *args, **kwargs):
        """Update game info. Calculates all cfr in the end of the game"""

        super().update_game_info(*args, **kwargs)

    def game_over(self, gained):
        """
        Game is over. Do CFR calculations
        :param gained: amount of money earned in this game
        :return:
        """
        self.cfr(0, 1, 1)
        MCCFPlayer.action_taken = []
        MCCFPlayer.prob = []
        MCCFPlayer.node_order = []
        MCCFPlayer.player_id_order = []
        self.gained = gained

    def _quantize_player_money(self, money: int):
        """Quantize the money to a certain action number relatively to player's money"""
        return round(money / self.player_profile.money * (self.actions_raise_num - 1))

    def _quantize_total_money(self, money: int):
        """Quantize the money to a certain action number relatively to total money"""
        return round(money / self.total_bank() * (self.actions_raise_num - 1))

    def _quantize_probability(self, prob, num=10):
        """Quantize the probability of winning based on the num value"""
        return round(prob * (num - 1))

    def _quantized_player_to_money(self, val):
        """Quantized val (action) to the money to bet relatively to player's money"""
        return round(val / (self.actions_raise_num - 1) * self.player_profile.money)

    def _quantized_total_to_money(self, val):
        """Quantized val (action) to the money to bet relatively to total bank"""
        return round(val / (self.actions_raise_num - 1) * self.total_bank())
    def _get_info_set(self):
        """Return a tuple of the information set"""
        if self.game_info is None:
            return ()

        # shown_cards = []
        # if self.game_info is not None:
        #     shown_cards = [self.game_info.shown_community_cards].sort(key=lambda c: c.get_card_id())

        return (
            self.game_info.round_idx,
            self._quantize_total_money(self.game_info.current_bet),
            # self._quantize_money(self.player_profile.money),
            self._quantize_probability(self.winning_prob(400))
        )

    def action(self):
        info_set = self._get_info_set()

        node = MCCFPlayer.nodes.get(info_set)
        if node is None:
            node = Node(self.actions_raise_num + 2)
            node.info_set = info_set
            MCCFPlayer.nodes[info_set] = node

        act = node.get_action()

        if self.is_learning:
            MCCFPlayer.action_taken.append(act)
            MCCFPlayer.prob.append(node.strategy[act])
            MCCFPlayer.node_order.append(node)
            MCCFPlayer.player_id_order.append(self.player_profile.id)

        if act == 0:
            return self._fold()

        if act == 1:
            return self._call()

        act -= 2
        return self._raise(self._quantized_player_to_money(act))

    def cfr(self, idx, p_player, p_opponent):
        """Does all cfr stuff for i element
            Basically, returns approximate utility of the player's action
        """

        # If the action is the last one
        is_last_flag = True
        for i in range(idx + 1, len(MCCFPlayer.player_id_order)):
            player_id = MCCFPlayer.player_id_order[i]
            if player_id == self.player_profile.id:
                is_last_flag = False
                break

        # terminal state analogue
        if is_last_flag:
            return self.gained

        node = self.node_order[idx]
        is_player = self.player_profile.id == self.player_id_order[idx]

        if is_player:
            node.update_strategy(p_player)
        else:
            node.update_strategy(p_opponent)

        action = MCCFPlayer.action_taken[idx]
        if is_player:
            next_util = self.cfr(idx + 1, p_player * node.strategy[action], p_opponent)
        else:
            next_util = self.cfr(idx + 1, p_player, p_opponent * node.strategy[action])

        next_util = next_util if self.player_id_order[idx] == self.player_id_order[idx + 1] else -next_util
        node.update_util(MCCFPlayer.action_taken[idx], next_util)

        if is_player:
            node.update_regrets(p_opponent)
        else:
            node.update_regrets(p_player)

        return node.node_util
