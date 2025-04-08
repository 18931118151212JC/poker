class Card:
    _char_to_string = {
        "H": "hearts",
        "D": "diamonds",
        "C": "clubs",
        "S": "spades",
        "1": "ace",
        "2": "2",
        "3": "3",
        "4": "4",
        "5": "5",
        "6": "6",
        "7": "7",
        "8": "8",
        "9": "9",
        "a": "10",
        "b": "jack",
        "c": "queen",
        "d": "king"
    }

    _suit_to_value = {
        "H": 1,
        "D": 2,
        "C": 3,
        "S": 4
    }

    _pips_to_value = {
        "1": 13,
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "6": 6,
        "7": 7,
        "8": 8,
        "9": 9,
        "a": 10,
        "b": 11,
        "c": 12,
        "d": 13
    }

    """
    clubs, diamonds, hearts and spades \n
    Card is the wrapper around the string of length 2, where the first character is the suite and the second is pip # in hex \n
    Examples: C1 (clubs Ace), HB (hearts jack) S5 (5 of spades)
    The Card is immutable
    """

    def __init__(self, val):
        """
        Initialize card
        :param val: the value in the form of 2 char string
        """
        if len(val) != 2 or val[0] not in Card._char_to_string or val[1] not in Card._char_to_string:
            raise ValueError("Impossible value passed")

        self.val = val

    def less_than_by_one(self, card: "Card") -> bool:
        """
        :param card: the card to compare this card with
        :return: if the next card is less than the current card returns True, otherwise returns False
        """

        if card.val[1] == "d" and self.val[1] == "1":
            return True
        if card.val[1] == "9" and self.val[1] == "a":
            return True
        if ord(self.val[1]) - ord(card.val[1]) == 1:
            return True
        return False

    def greater_than_by_one(self, card: "Card") -> bool:
        """
        :param card: the card to compare this card with
        :return: if the card is less than this card returns True, otherwise returns False
        """
        return card.less_than_by_one(self)

    def same_suit(self, card: "Card") -> bool:
        return self.val[0] == card.val[0]

    def get_pips(self) -> int:
        """
        :return: pips value
        """
        return Card._pips_to_value[self.val[1]]

    def same_pips(self, card: "Card") -> bool:
        """
        :param card:
        :return: True if has same pips, False otherwise
        """
        return self.val[1] == card.val[1]

    @staticmethod
    def all_possible_cards() -> list:
        ans = []

        for suit in Card._suit_to_value:
            for pips in Card._pips_to_value:
                card = Card(suit + pips)
                ans.append(card)

        return ans


class CombinationFinder:
    """
    Set of functions to find combinations
    """

    @staticmethod
    def _path_finder(cards: tuple, bitmask: int, current_card_idx: int, *args) -> int:
        """
        Finds the maximum length of the path between cards, that return true in the card methods
        :param cards:
        :param bitmask: 1 if the card wasn't used, 0 if it was
        :param args: boolean methods of cards, that connect two cards if they return true
        :param current_card_idx: the index of the card that is currently a "node"
        :return: length of the maximum path possible
        """
        ans = 0
        for i in range(len(cards)):
            if current_card_idx == -1:
                ans = max(ans, CombinationFinder._path_finder(cards, bitmask ^ (1 << i), i, *args) + 1)

            # card wasn't selected before
            elif bitmask & (1 << i):
                cur_card = cards[current_card_idx]
                next_card = cards[i]
                flag = True

                # check that all conditions apply
                for arg in args:
                    flag = flag and arg(cur_card, next_card)

                if flag:
                    ans = max(ans, CombinationFinder._path_finder(cards, bitmask ^ (1 << i), i, *args) + 1)

        return ans

    """
    PRIORITY OF COMBINATIONS:
    Royal Flush
    Straight Flush
    Four of a Kind
    Full House
    Flush
    Straight
    Three of a kind
    Two pair
    Pair
    High Card
    """

    @staticmethod
    def has_royal_flush(cards: tuple) -> bool:
        for i in range(len(cards)):
            if cards[i].val[1] == "a" \
                    and CombinationFinder._path_finder(cards, ((1 << len(cards)) - 1) ^ (1 << i), i, Card.same_suit,
                                                       Card.greater_than_by_one) + 1 >= 5:
                return True
        return False

    @staticmethod
    def has_straight_flush(cards: tuple) -> bool:
        return CombinationFinder.has_flush(cards) and CombinationFinder.has_straight(cards)

    @staticmethod
    def has_four_of_a_kind(cards: tuple) -> bool:
        return CombinationFinder._path_finder(cards, (1 << len(cards)) - 1, -1, Card.same_pips)  == 4

    @staticmethod
    def has_full_house(cards: tuple) -> bool:
        a = 0
        b = 0
        for i in range(len(cards)):
            if CombinationFinder._path_finder(cards, ((1 << len(cards)) - 1) ^ (1 << i), i, Card.same_pips) + 1 >= 3:
                a += 1
                b += 1
            elif CombinationFinder._path_finder(cards, ((1 << len(cards)) - 1) ^ (1 << i), i, Card.same_pips) + 1 >= 2:
                b += 1
        if a > 3 or a == 3 and b >= 5:
            return True
        return False

    @staticmethod
    def has_flush(cards: tuple) -> bool:
        a = CombinationFinder._path_finder(cards, (1 << len(cards)) - 1, -1, Card.same_suit)
        return a >= 5

    @staticmethod
    def has_straight(cards: tuple) -> bool:
        a = CombinationFinder._path_finder(cards, (1 << len(cards)) - 1, -1, Card.greater_than_by_one)
        return a >= 5

    @staticmethod
    def has_three_of_a_kind(cards: tuple) -> bool:
        return CombinationFinder._path_finder(cards, (1 << len(cards)) - 1, -1, Card.same_pips) == 3

    @staticmethod
    def has_two_pairs(cards: tuple) -> bool:
        a = 0
        for i in range(len(cards)):
            if CombinationFinder._path_finder(cards, ((1 << len(cards)) - 1) ^ (1 << i), i, Card.same_pips) + 1 >= 2:
                a += 1
        return a >= 4

    @staticmethod
    def has_pair(cards: tuple) -> bool:
        return CombinationFinder._path_finder(cards, (1 << len(cards)) - 1, -1, Card.same_pips) == 2

    @staticmethod
    def combination_determiner(cards: tuple) -> int:
        if CombinationFinder.has_royal_flush(cards):
            return 10
        if CombinationFinder.has_straight_flush(cards):
            return 9
        if CombinationFinder.has_four_of_a_kind(cards):
            return 8
        if CombinationFinder.has_full_house(cards):
            return 7
        if CombinationFinder.has_flush(cards):
            return 6
        if CombinationFinder.has_straight(cards):
            return 5
        if CombinationFinder.has_three_of_a_kind(cards):
            return 4
        if CombinationFinder.has_two_pairs(cards):
            return 3
        if CombinationFinder.has_pair(cards):
            return 2
        return 1


if __name__ == "__main__":
    tests = [
        ["H2", "H1", "Hd", "Hc", "Hb", "Ha", "S4"],
        ["S6", "S8", "S7", "S9", "Sa", "Ha", "H3"],
        ["S1", "D1", "C2", "C1", "H1", "C3", "C4"],
        ["S1", "D2", "C2", "C1", "H1", "C3", "H2"],
        ["S1", "S3", "Hb", "Sd", "D4", "S2", "Sa"],
        ["Hb", "D4", "H7", "Sd", "C8", "D6", "C5"],
        ["D4", "H4", "C4", "H8", "Dd", "Cc", "H2"],
        ["D1", "C1", "H2", "S2", "S6", "D3", "D6"],
        ["Sa", "H2", "H3", "H4", "H5", "D7", "Ca"],
        ["S1", "H2", "D5", "H7", "Hd", "Dc", "C9"]

    ]
    for i in range(len(tests)):
        for j in range(len(tests[i])):
            tests[i][j] = Card(tests[i][j])

    # Should print all numbers from 10 to 1
    for test in tests:
        print(CombinationFinder.combination_determiner(tuple(test)))
    print(tests)




