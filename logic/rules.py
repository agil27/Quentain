colors = ['Spade', 'Club', 'Heart', 'Diamond']
name_map = {
    11: 'Jack',
    12: 'Queen',
    13: 'King',
    14: 'Ace',
    15: 'Red Joker',
    16: 'Black Joker'
}

class Card:
    def __init__(self, number, color, level):
        # Jack, Queen, King, Ace, Black Joker, Red Joker <==> 11, 12, 13, 14, 15, 16
        assert isinstance(number, int) and 1 <= number <= 16
        if number == 1:
            # ace
            number = 14
        if 2 <= number <= 14:
            assert color in colors
        else:
            assert color == 'Joker'
        self.number = number
        self.color = color
        self.level = level
        if 2 <= number <= 10:
            self.name = str(number)
        else:
            self.name = name_map[self.number]

    def clone(self):
        return Card(self.number, self.color, self.level)

    def is_wildcard(self):
        return self.number == self.level and self.color == 'Heart'

    def greater_than(self, card):
        # level card: this level's special number, as the greatest number other than the jokers
        assert isinstance(card, Card)
        assert isinstance(self.level, int)
        if card.number == self.level:
            if self.number >= 15:
                return True
            else:
                return False
        else:
            if self.number == self.level:
                if card.number <= 14:
                    return True
                else:
                    return False
            else:
                return self.number > card.number

    def __lt__(self, card):
        if card.greater_than(self):
            return True
        elif self.equals(card) and card.color == 'Heart' and self.color != 'Heart':
            return True
        return False

    def __gt__(self, card):
        if self.greater_than(card):
            return True
        elif self.equals(card) and self.color == 'Heart' and card.color != 'Heart':
            return True
        return False

    def equals(self, card):
        return self.number == card.number

    def __str__(self):
        if self.color != 'Joker':
            return self.name + ' of ' + self.color
        else:
            return self.name

    def __repr__(self):
        return str(self)


class CardComp:
    '''
    A composition of playing cards that is legal
    '''
    def __init__(self, cards):
        assert isinstance(cards, list)

    def greater_than(self, card_comp):
        pass

    @staticmethod
    def satisfy(cards):
        # return two values
        # (whether_satisfy, the re-organized card comp)
        pass

    @staticmethod
    def is_bomb():
        pass

    @staticmethod
    def from_card_list(cards):
        try:
            if len(cards) == 1:
                return Single(cards)
            if len(cards) == 2:
                return Pair(cards)
            if len(cards) == 3:
                return Triple(cards)
            if len(cards) == 5:
                return FullHouse(cards)
            if len(cards) == 6:
                return Plate(cards)
        except Exception as e:
            return IllegalComp(cards)


class IllegalComp(CardComp):
    pass


class Single(CardComp):
    def __init__(self, cards):
        super().__init__(cards)
        whether, sorted_cards = self.satisfy(cards)
        assert whether
        self.card = sorted_cards[0]

    def greater_than(self, card_comp):
        if not isinstance(card_comp, Single):
            return False
        return self.card.greater_than(card_comp.card)

    @staticmethod
    def satisfy(cards):
        return len(cards) == 1, cards

    @staticmethod
    def is_bomb():
        return False


class Pair(CardComp):
    def __init__(self, cards):
        super().__init__(cards)
        whether, sorted_cards = self.satisfy(cards)
        assert whether
        self.cards = sorted_cards

    def greater_than(self, card_comp):
        if not isinstance(card_comp, Pair):
            return False
        return self.cards[0].greater_than(card_comp.cards[0])

    @staticmethod
    def satisfy(cards):
        if len(cards) != 2:
            return False, None
        level_cond0 = cards[0].is_wildcard() and cards[1].color != 'Joker'
        level_cond1 = cards[1].is_wildcard() and cards[0].color != 'Joker'
        whether = (cards[0].equals(cards[1]) or level_cond0 or level_cond1)
        if not whether:
            return False, None
        if level_cond1 and not level_cond0:
            cards[1].number = cards[0].number
        elif level_cond0 and not level_cond1:
            cards[0].number = cards[1].number
        return True, cards

    @staticmethod
    def is_bomb():
        return False


class Triple(CardComp):
    def __init__(self, cards):
        super().__init__(cards)
        whether, sorted_cards = self.satisfy(cards)
        assert whether
        self.cards = sorted_cards
        self.cards[1].number = self.cards[0].number
        self.cards[2].number = self.cards[0].number

    def greater_than(self, card_comp):
        if not isinstance(card_comp, Triple):
            return False
        return self.cards[0].greater_than(card_comp.cards[0])

    @staticmethod
    def satisfy(cards):
        if len(cards) != 3:
            return False, None

        # sorted with ascending order
        # using the __lt__ function defined in Card class
        sorted_cards = sorted(cards)

        # if there are joker(s) in this comp, it is definitely illegal
        if sorted_cards[-1].color == 'Joker':
            return False, None

        # there are at most two wild cards in one card composition
        # so the smallest card must be the value for this triple
        if not sorted_cards[1].equals(sorted_cards[0]) and sorted_cards[1].is_wildcard():
            return False, None
        if not sorted_cards[2].equals(sorted_cards[0]) and sorted_cards[2].is_wildcard():
            return False, None

        sorted_cards[1].number = sorted_cards[0].number
        sorted_cards[2].number = sorted_cards[0].number
        return True, sorted_cards


    @staticmethod
    def is_bomb():
        return False


class FullHouse(CardComp):
    '''
    Triple + Pair
    '''
    def __init__(self, cards):
        super().__init__(cards)
        whether, sorted_cards = self.satisfy(cards)
        assert whether
        self.cards = sorted_cards

    def greater_than(self, card_comp):
        if not isinstance(card_comp, FullHouse):
            return False
        return self.cards[0].greater_than(card_comp.cards[0])

    @staticmethod
    def satisfy(cards):
        if len(cards) != 5:
            return False, None

        # similar, sort first
        sorted_cards = sorted(cards)

        # if the largest card is Joker, it must be a pair of Joker
        if sorted_cards[4].color == 'Joker':
            if not sorted_cards[3].equals(sorted_cards[4]):
                return False, None
            else:
                # check if the rest is a triple
                whether, triple_cards = Triple.satisfy(sorted_cards[:3])
                if not whether:
                    return False, None
                else:
                    return True, triple_cards + sorted_cards[3:]

        # there are no jokers in this composition
        # if there are wild cards, it must be the largest
        # since we sort by setting Heart wild card to be the largest

        # if there are two wild cards
        if sorted_cards[3].is_wildcard() and sorted_cards[4].is_wildcard():
            # the rest 3 cards can be 2 + 1, 1 + 2, or 3
            # check 1 + 2
            whether, pair_cards = Pair.satisfy(sorted_cards[1:3])
            if whether and not sorted_cards[0].equals(pair_cards[0]):
                return_cards = [sorted_cards[0]] * 3 + pair_cards
                return True, return_cards
            # check 2 + 1
            whether, pair_cards = Pair.satisfy(sorted_cards[:2])
            if whether and not sorted_cards[2].equals(pair_cards[0]):
                return_cards = [sorted_cards[2]] * 3 + pair_cards
                return True, return_cards
            # check 3
            whether, triple_cards = Triple.satisfy(sorted_cards[:3])
            if whether:
                return True, triple_cards + sorted_cards[3:]
            # otherwise
            return False, None

        # if no wildcards
        if not sorted_cards[3].is_wildcard() and not sorted_cards[4].is_wildcard():
            # it can either be 3 + 2 or 2 + 3
            # check 3 + 2
            whether_triple, triple_cards = Triple.satisfy(sorted_cards[:3])
            whether_pair, pair_cards = Pair.satisfy(sorted_cards[3:])
            if whether_triple and whether_pair and not triple_cards[0].equals(pair_cards[0]):
                return True, triple_cards + pair_cards
            # check 2 + 3
            whether_triple, triple_cards = Triple.satisfy(sorted_cards[2:])
            whether_pair, pair_cards = Pair.satisfy(sorted_cards[:2])
            if whether_triple and whether_pair and not triple_cards[0].equals(pair_cards[0]):
                return True, triple_cards + pair_cards
            # otherwise
            return False, None

        # if there is only one wild card
        # it must be the greatest one
        # the rest can be 2 + 2, 3 + 1, 1 + 3
        # check 2 + 2
        whether_pair1, pair_cards1 = Pair.satisfy(sorted_cards[:2])
        whether_pair2, pair_cards2 = Pair.satisfy(sorted_cards[2:4])
        if whether_pair1 and whether_pair2 and not pair_cards1[0].equals(pair_cards2):
            if pair_cards1[0].greater_than(pair_cards2[0]):
                return True, pair_cards1 + [pair_cards1[0].clone()] + pair_cards2
            else:
                return True, pair_cards2 + [pair_cards2[0].clone()] + pair_cards1
        # check 3 + 1
        whether, triple_cards = Triple.satisfy(sorted_cards[:3])
        if whether and not triple_cards[0].equals(sorted_cards[3]):
            return True, triple_cards + [sorted_cards[3], sorted_cards[3].clone()]
        # check 1 + 3
        whether, triple_cards = Triple.satisfy(sorted_cards[1:4])
        if whether and not triple_cards[0].equals(sorted_cards[0]):
            return True, triple_cards + [sorted_cards[0] + sorted_cards[0].clone()]

        # otherwise
        return False, None

    @staticmethod
    def is_bomb():
        return False


class Plate(CardComp):
    '''
    Two consecutive Triples
    '''
    def __init__(self, cards):
        super().__init__(cards)
        whether, sorted_cards = self.satisfy(cards)
        assert whether
        self.cards = sorted_cards

    def greater_than(self, card_comp):
        if not isinstance(card_comp, Plate):
            return False
        return self.cards[0].greater_than(card_comp.cards[0])

    @staticmethod
    def satisfy(cards):
        if len(cards) != 6:
            return False, None

        # same logic as Triple, we first sort the card comp
        sorted_cards = sorted(cards)

        # no joker in a plate
        if sorted_cards[-1].color == 'Joker':
            return False, None

        # if no wildcards
        if not sorted_cards[4].is_wildcard() and not sorted_cards[5].is_wildcard():
            # check 3 + 3
            whether_triple1, triple_cards1 = Triple.satisfy(sorted_cards[:3])
            whether_triple2, triple_cards2 = Triple.satisfy(sorted_cards[3:])
            if whether_triple1 and whether_triple2 and triple_cards1[0].number + 1 == triple_cards2[0].number:
                return True, triple_cards1 + triple_cards2
            # otherwise
            return False, None

        # at least 1 wild card
        # check fullhouse first
        whether, fullhouse = FullHouse.satisfy(sorted_cards)

        # there will be at most 1 wildcard in this fullhouse
        # so we can always check the first number in the triple
        # and the the first in the pair
        if whether:
            triple, pair = fullhouse[:3], fullhouse[3:]
            if triple[0].number + 1 == pair[0].number:
                return True, triple + pair + [pair[0].clone()]
            if triple[0].number - 1 == pair[0].number:
                return True, pair + [pair[0].clone()] + triple
        # otherwise
        return False, None

    @staticmethod
    def is_bomb():
        return False







