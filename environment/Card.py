from copy import deepcopy


class Card:
    _char_to_string = {
        "H": "♥️",
        "D": "♦️",
        "C": "♣️",
        "S": "♠️",
        "1": "A",
        "2": "2",
        "3": "3",
        "4": "4",
        "5": "5",
        "6": "6",
        "7": "7",
        "8": "8",
        "9": "9",
        "a": "10",
        "b": "J",
        "c": "Q",
        "d": "K"
    }

    _suit_to_value = {
        "H": 1,
        "D": 2,
        "C": 3,
        "S": 4
    }

    _pips_to_value = {
        "1": 14,
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
        :return: if the next card is greater than this card returns True, otherwise returns False
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

    def __str__(self):
        return Card._char_to_string[self.val[0]] + Card._char_to_string[self.val[1]]

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.val == other.val


class CombinationFinder:
    """
    Set of functions to find combinations
    """

    @staticmethod
    def _path_finder(cards: list, bitmask: int, current_card_idx: int, *args) -> int:
        """
        Finds the maximum length of the path between cards, that return true in the card methods \n
        Note that if initial current_card_idx is not 0, the path length returned is 1 less than the actual one.
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
    def has_royal_flush(cards: list) -> bool:
        for i in range(len(cards)):
            if cards[i].val[1] == "a" \
                    and CombinationFinder._path_finder(cards, ((1 << len(cards)) - 1) ^ (1 << i), i, Card.same_suit,
                                                       Card.greater_than_by_one) + 1 >= 5:
                return True
        return False

    @staticmethod
    def has_straight_flush(cards: list) -> bool:
        return CombinationFinder.has_flush(cards) and CombinationFinder.has_straight(cards)

    @staticmethod
    def has_four_of_a_kind(cards: list) -> bool:
        return CombinationFinder._path_finder(cards, (1 << len(cards)) - 1, -1, Card.same_pips) == 4

    @staticmethod
    def has_full_house(cards: list) -> bool:
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
    def has_flush(cards: list) -> bool:
        a = CombinationFinder._path_finder(cards, (1 << len(cards)) - 1, -1, Card.same_suit)
        return a >= 5

    @staticmethod
    def has_straight(cards: list) -> bool:
        for i in range(len(cards)):
            pips = cards[i].get_pips()
            if (pips <= 10 or pips == 14) and CombinationFinder._path_finder(cards, ((1 << len(cards)) - 1) ^ (1 << i), i, Card.greater_than_by_one) + 1 >= 5:
                return True
        return False

    @staticmethod
    def has_three_of_a_kind(cards: list) -> bool:
        return CombinationFinder._path_finder(cards, (1 << len(cards)) - 1, -1, Card.same_pips) == 3

    @staticmethod
    def has_two_pairs(cards: list) -> bool:
        a = 0
        for i in range(len(cards)):
            if CombinationFinder._path_finder(cards, ((1 << len(cards)) - 1) ^ (1 << i), i, Card.same_pips) + 1 >= 2:
                a += 1
        return a >= 4

    @staticmethod
    def has_pair(cards: list) -> bool:
        return CombinationFinder._path_finder(cards, (1 << len(cards)) - 1, -1, Card.same_pips) == 2

    @staticmethod
    def combination_determiner(cards: list) -> int:
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


    @staticmethod
    def combination_comparator(cards1: list, cards2: list):
        """
        Returns positive number if the first list of cards is stronger than the second list of cards,
        negative if weaker and 0 if they are equally strong.\n
        Lists of cards won't be modified
        :param cards1: first list of coards to compare
        :param cards2: second list of coards to compare
        :return: positive, negative or 0
        """

        strength1 = CombinationFinder.combination_determiner(cards1)
        strength2 = CombinationFinder.combination_determiner(cards2)
        dif = strength1 - strength2
        if dif != 0:
            return dif

        cards1 = deepcopy(cards1)
        cards2 = deepcopy(cards2)

        cards1.sort(key=lambda card: card.get_pips(), reverse=True)
        cards2.sort(key=lambda card: card.get_pips(), reverse=True)

        method = CombinationFinder.tiebreakers[strength1]

        return method(cards1, cards2)


    @staticmethod
    def _highest_card_finder_by_combination(cards: list, length: int, *args):
        """
        Finds the highest cards in the combination (path)
        :return: The pips value
        """

        for i in range(len(cards)):
            if CombinationFinder._path_finder(cards, ((1 << len(cards)) - 1) ^ (1 << i), i, *args) + 1 >= length:
                return cards[i].get_pips()

        return -1


    @staticmethod
    def royal_flush_tiebreaker(cards1: list, cards2: list):
        """
        Royal Flush has no tiebreaker, the values are equal
        :return: 0
        """
        return 0



    @staticmethod
    def straight_flush_tiebreaker(cards1: list, cards2: list):
        """
        Has no kicker. Straight with the highest card wins
        """
        a1 = CombinationFinder._highest_card_finder_by_combination(cards1, 5, Card.less_than_by_one, Card.same_suit)
        a2 = CombinationFinder._highest_card_finder_by_combination(cards2, 5, Card.less_than_by_one, Card.same_suit)

        return a1 - a2

    @staticmethod
    def four_of_kind_tiebreaker(cards1: list, cards2: list):
        """
        Determines by kicker if two four_of_kind are the same
        """
        a1 = CombinationFinder._highest_card_finder_by_combination(cards1, 4, Card.same_pips)
        a2 = CombinationFinder._highest_card_finder_by_combination(cards2, 4, Card.same_pips)

        if a1 != a2:
            return a1 - a2

        return CombinationFinder.highest_card_tiebreaker(cards1, cards2)

    @staticmethod
    def full_house_tiebreaker(cards1: list, cards2: list):
        """
        No kicker. Firstly compare trips, then compare pairs
        """
        a1 = {i: 0 for i in Card._pips_to_value.values()}
        a2 = {i: 0 for i in Card._pips_to_value.values()}

        for i in range(len(cards1)):
            a1[cards1[i].get_pips()] += 1
        for i in range(len(cards2)):
            a2[cards2[i].get_pips()] += 1

        pips = list(Card._pips_to_value.values())
        pips.sort(reverse=True)
        pip3 = -1

        for pip in pips:
            if a1[pip] == 3 and a2[pip] != 3:
                return 1

            if a2[pip] == 3 and a1[pip] != 3:
                return -1

            if a1[pip] == a2[pip] == 3:
                pip3 = pip
                break

        for pip in pips:
            if pip != pip3 and a1[pip] >= 2 > a2[pip]:
                return 1
            if pip != pip3 and a1[pip] < 2 <= a2[pip]:
                return -1
            if pip != pip3 and a1[pip] >= 2 and a2[pip] >= 2:
                return 0

        return 0

    @staticmethod
    def flush_tiebreaker(cards1: list, cards2: list):
        """
        Comparing cards in the flush. No use of kicker
        """
        suit1 = ""
        suit2 = ""

        for i in range(len(cards1)):
            if CombinationFinder._path_finder(cards1, ((1 << len(cards1)) - 1) ^ (1 << i), i, Card.same_suit) + 1 >= 5:
                suit1 = cards1[i].val[0]
                break

        for i in range(len(cards2)):
            if CombinationFinder._path_finder(cards2, ((1 << len(cards2)) - 1) ^ (1 << i), i, Card.same_suit) + 1 >= 5:
                suit2 = cards2[i].val[0]
                break

        suit_cards1 = []
        suit_cards2 = []

        for i in range(len(cards1)):
            if cards1[i].val[0] == suit1:
                suit_cards1.append(cards1[i])

        for i in range(len(cards2)):
            if cards2[i].val[0] == suit2:
                suit_cards1.append(cards2[i])

        for i in range(5):
            if suit_cards1[i].get_pips() != suit_cards2[i].get_pips():
                return suit_cards1[i].get_pips() - suit_cards2[i].get_pips()

        return 0

    @staticmethod
    def straight_tiebreaker(cards1: list, cards2: list):
        """
        Has no kicker. Straight with the highest card wins
        """
        a1 = CombinationFinder._highest_card_finder_by_combination(cards1, 5, Card.less_than_by_one)
        a2 = CombinationFinder._highest_card_finder_by_combination(cards2, 5, Card.less_than_by_one)

        return a1 - a2

    @staticmethod
    def three_of_kind_tiebreaker(cards1: list, cards2: list):
        """
        Highest 3 of kind. Has kicker
        """
        a1 = CombinationFinder._highest_card_finder_by_combination(cards1, 3, Card.same_pips)
        a2 = CombinationFinder._highest_card_finder_by_combination(cards2, 3, Card.same_pips)

        if a1 != a2:
            return a1 - a2

        return CombinationFinder.highest_card_tiebreaker(cards1, cards2)

    @staticmethod
    def two_pairs_tiebreaker(cards1: list, cards2: list):
        """
        Highest pair win. Has a kicker
        """
        a1 = {i: 0 for i in Card._pips_to_value.values()}
        a2 = {i: 0 for i in Card._pips_to_value.values()}

        for i in range(len(cards1)):
            a1[cards1[i].get_pips()] += 1
        for i in range(len(cards2)):
            a2[cards2[i].get_pips()] += 1

        pips = list(Card._pips_to_value.values())
        pips.sort(reverse=True)

        cnt = 0
        for pip in pips:
            if a1[pip] == 2 and a2[pip] != 2:
                return 1
            if a1[pip] != 2 and a2[pip] == 2:
                return -1
            if a1[pip] == 2 == a2[pip]:
                cnt += 1
                if cnt == 2:
                    break

        return CombinationFinder.highest_card_tiebreaker(cards1, cards2)

    @staticmethod
    def pair_tiebreaker(cards1: list, cards2: list):
        a1 = CombinationFinder._highest_card_finder_by_combination(cards1, 2, Card.same_pips)
        a2 = CombinationFinder._highest_card_finder_by_combination(cards2, 2, Card.same_pips)

        if a1 != a2:
            return a1 - a2

        return CombinationFinder.highest_card_tiebreaker(cards1, cards2)

    @staticmethod
    def highest_card_tiebreaker(cards1: list, cards2: list):
        """
        Kicker
        """
        for i in range(len(cards1)):
            if cards1[i].get_pips() != cards2[i].get_pips():
                return cards1[i].get_pips() - cards2[i].get_pips()

        return 0

    tiebreakers = {
        10: royal_flush_tiebreaker,
        9: straight_tiebreaker,
        8: four_of_kind_tiebreaker,
        7: full_house_tiebreaker,
        6: flush_tiebreaker,
        5: straight_tiebreaker,
        4: three_of_kind_tiebreaker,
        3: two_pairs_tiebreaker,
        2: pair_tiebreaker,
        1: highest_card_tiebreaker,

    }


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
        print(CombinationFinder.combination_determiner(test))
    print(tests)

    tests = [
        [["H2", "H1", "Hd", "Hc", "Hb", "Ha", "S4"], ["H2", "S1", "Sd", "Sc", "Sb", "Sa", "C4"]],   # print 0
        [["S1", "D2", "C2", "C1", "H1", "C3", "H2"], ["H3", "C3", "C2", "D2", "H2", "D1", "Dd"]],   # print 1
        [["Sa", "H2", "H3", "H4", "H5", "D7", "Ca"], ["Hb", "D4", "H7", "Sd", "C8", "D6", "C5"]],   # print negative number
    ]

    for i in range(len(tests)):
        for j in range(2):
            for k in range(len(tests[i][j])):
                tests[i][j][k] = Card(tests[i][j][k])

    for test in tests:
        print(CombinationFinder.combination_comparator(test[0], test[1]))




