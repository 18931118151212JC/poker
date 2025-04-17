def player_profile_string(player_profile: dict):
    s = ""
    for key in player_profile:
        s += f"\t{key}: {player_profile[key]}\n"

    return s


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


class HumanPlayer(PlayerBase):
    """
    Class for human player
    """

    def __init__(self, testing=False, actions=None, verbose=False, *args):
        """
        If testing is true, then the action will not ask the console for actions, but will just
        implement already determined actions
        """
        super().__init__(*args)
        self.testing = testing
        self.actions = actions
        self.verbose = verbose
        self.i = 0
        self.j = 0

    def _get_action(self):
        """
        Gets the next action in the actions list
        :return: the action to take in string format
        """
        if self.i >= len(self.actions):
            return "fold"

        s = self.actions[self.i][self.j]

        if self.j == len(self.actions[self.i]) - 1:
            self.i += 1
            self.j = 0
        else:
            self.j += 1

        return s

    def _game_string(self):
        s = ""
        for key in self.game_info:
            if key != "players_profiles":
                s += f"{key}: {self.game_info[key]}\n"

        s += "players_profiles:\n"

        for player_id in self.game_info["players_profiles"]:
            player_profile = self.game_info["players_profiles"][player_id]
            s += f"{player_id}:\n {player_profile_string(player_profile)}\n"

        return s

    def action(self):
        if self.verbose:
            # UNCOMMENT THIS LINE TO SEE THE GAME STATE AS THE PLAYER
            # print(f"Game:\n {self._game_string()}")
            print(f"Player:\n {player_profile_string(self.player_profile)}")
            print("=" * 100)

            print("""Choose action:
            call: call the current bet
            raise x: raise the bet by x (if the value is negative, it will fold)
            fold: fold cards
            """)

        if not self.testing:
            s = input()
        else:
            s = self._get_action()
            if self.verbose:
                print(s)

        s = s.split(" ")

        if s[0] == "call":
            return self._call()

        if s[0] == "raise":
            try:
                return self._raise(int(s[1]))
            except Exception as e:
                print(e)
                return -1

        return -1

    def _call(self):
        current_bet = self.game_info["current_bet"]
        return current_bet - self.player_profile["current_round_bet"]

    def _fold(self):
        return -1

    def _raise(self, x: int):
        current_bet = self.game_info["current_bet"]
        return current_bet - self.player_profile["current_round_bet"] + x

    def update_game_info(self, game_info: dict):
        super().update_game_info(game_info)
        # print(self.game_info)
