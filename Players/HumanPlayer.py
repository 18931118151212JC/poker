from .PlayerBase import PlayerBase
from poker.environment.Game import GameInfo

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



    def action(self):
        if self.verbose:
            # UNCOMMENT THIS LINE TO SEE THE GAME STATE AS THE PLAYER
            print(f"Game:\n {str(self.game_info)}")
            print(f"Player:\n {str(self.player_profile)}")
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


    def update_game_info(self, game_info: GameInfo):
        super().update_game_info(game_info)
        # print(self.game_info)
