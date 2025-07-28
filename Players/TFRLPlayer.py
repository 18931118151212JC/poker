# Same functionality as the RLPlayer, but is implemented via TensorFlow
import random

from poker.Players.RLPlayer import RLPlayer
import tensorflow as tf
import numpy as np


class TFRLPlayer(RLPlayer):
    """
    RL player, that uses tensorflow keras sequential model. Child class of the
    RLPlayer class.
    """
    # These are enum values used in the _update() function
    RAISE_WEIGHT = "rw"
    TYPE_WEIGHT = "tw"

    def __init__(self, type_units=None, raise_units=None, *args, **kwargs):
        """
        Initialize the RL player
        :param type_units: Creates keras sequential model with number of units in each layer
         specified in the parameter for the type_agent
         :param raise_units: Creates keras sequential model with number of units in each layer
         specified in the parameter for the raise_agent
        """
        super().__init__(*args, **kwargs)

        # These will be stored directly in the model
        # Assigning type_weights and raise weights with dummy values to
        # understand which model to update in the
        self.type_weights = TFRLPlayer.TYPE_WEIGHT
        self.type_bias = None
        self.raise_weights = TFRLPlayer.RAISE_WEIGHT
        self.raise_bias = None

        # The tf keras sequential models agents
        if type_units is None:
            type_units = [self.actions_type_num]
        if raise_units is None:
            raise_units = [self.actions_raise_num]

        self.type_units = type_units
        self.raise_units = raise_units

        # initializing agents
        self.init_agents()

    def init_agents(self):
        """
        Initialize the agents
        :return:
        """
        self.type_agent = tf.keras.Sequential(
            (
                [tf.keras.layers.Dense(x, activation='relu') for x in self.type_units]
                .append(tf.keras.layers.Dense(self.actions_type_num, activation='linear'))
            )
        )
        self.raise_agent = tf.keras.Sequential(
            (
                [tf.keras.layers.Dense(x, activation='relu') for x in self.raise_units]
                .append(tf.keras.layers.Dense(self.actions_type_num, activation='linear'))
            )
        )

        # compiling the models
        self.type_agent.compile(optimizer='adam', loss="mse")
        self.raise_agent.compile(optimizer='adam', loss="mse")

    def _update(self, features, weights, bias, action):
        """
        Update the weights and bias. Note that weights and bias are not used
        in calculations and are only mentioned to implement methods in super class
        :return:
        """
        if not self.is_learning:
            return

        # Getting reward and q value
        r = self._reward_est()
        q_val = self._q(
            features,
            weights,
            bias,
            action
        )

        cur_features = self.get_features()

        # getting different length based on the action
        # using the dummy array to fit it into the keras model
        q_target = q_val
        if not self.is_terminal():
            # what action gives the most q value
            a_max_idx = np.argmax(q_val)
            delta = r + self.gamma * q_val[a_max_idx] - q_val[a_max_idx]
            q_target[a_max_idx] += delta

        else:
            delta = r - q_val
            self.epsilon *= self.decay

        # updating the weights
        agent = self._get_agent(weights)
        agent.fit(features, q_target, epochs=1, verbose=0)

    def learn(self, reset_params=True, *args, **kwargs):
        """
        Starts learning
        :param reset_params: True if wants to reset the weights in the model
        :return:
        """
        self.is_learning = True

        # reinitialize agents
        if reset_params:
            self.init_agents()

    def action(self):
        """
        Return the action taken
        """

        # update the models
        if self.last_action_type is not None:
            self._update(self.last_action_features, self.type_weights, self.type_bias, self.last_action_type)
            # if last action was raise
            if self.last_action_type == 2:
                self._update(self.last_action_features, self.raise_weights, self.raise_bias, self.last_action_raise)

        features = self.get_features()

        if random.random() < self.epsilon:
            action_type = random.randint(0, self.actions_type_num - 1)
        else:
            # choosing the maximal version
            action_type = np.argmax(self._q(features, self.type_weights, self.type_bias, None))

        self.last_action_type = action_type

        # if raise
        action_raise = 0
        if action_type == 2:
            if random < self.epsilon:
                action_raise = random.randint(0, self.actions_raise_num - 1)
            else:
                action_raise = np.argmax(self._q(features, self.raise_weights, self.raise_bias, None))

            self.last_action_raise = action_raise

        self.last_action_features = features

        if action_type == 0:
            return super()._fold()

        if action_type == 1:
            return super()._call()

        diff = self.player_profile.money / (self.actions_raise_num - 1)
        rand_val = random.uniform(-diff / 2, diff / 2)
        raise_val = max(0, round(diff * action_raise + rand_val))
        return super()._raise(raise_val)

    def _q(self, features, weights, bias, action):
        """
        q function. Returns the action distribution. Note that weights and bias are not used
        in calculations and are only mentioned to implement methods in super class
        :return: A tensor of q_values depending on the action
        """
        agent = self._get_agent(weights)

        # getting the q values array
        q_val = agent(features)

        return q_val

    def _get_agent(self, weights):
        """
        Get the agent based on the weights provided
        :param weights:
        :return:
        """
        # Choosing the agent based on the weights parameter
        # which must be equal to one of the enum variables
        if weights == TFRLPlayer.RAISE_WEIGHT:
            agent = self.raise_agent
        else:
            agent = self.type_agent

        return agent
