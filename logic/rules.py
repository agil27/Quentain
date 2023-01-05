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

        # for special case of Ace
        # A, 2, 3, 4, 5 and 10, J, Q, K, A is both acceptable
        self.raw_number = number
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
                try:
                    return FullHouse(cards)
                except Exception as e:
                    return Straight(cards)

                # TODO: one unique number: bomb
                # TODO: two unique numbers and two wildcards as a pair: bomb
                # TODO: three unique numbers with one wildcard: fullhouse
                # TODO: two unique numbers and no wildcard: fullhouse
                # TODO: five consecutive numbers and no wildcard: straight
                # TODO: four unique numbers and one wildcard: straight
            if len(cards) == 6:
                return Plate(cards)
        except Exception as e:
            return IllegalComp(cards)


class IllegalComp(CardComp):
    def __init__(self, cards):
        super().__init__(cards)
        self.cards = sorted(cards)


class Single(CardComp):
    def __init__(self, cards):
        super().__init__(cards)
        whether, sorted_cards = self.satisfy(cards)
        assert whether
        self.cards = sorted_cards

    def greater_than(self, card_comp):
        if not isinstance(card_comp, Single):
            return False
        return self.cards[0].greater_than(card_comp.cards[0])

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
        return True, sorted(cards)

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
        if not sorted_cards[1].equals(sorted_cards[0]) and not sorted_cards[1].is_wildcard():
            return False, None
        if not sorted_cards[2].equals(sorted_cards[0]) and not sorted_cards[2].is_wildcard():
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
            # check 1 + 2 to prioritize the larger fullhouse
            whether, pair_cards = Pair.satisfy(sorted_cards[1:3])
            if whether and not sorted_cards[0].equals(pair_cards[0]):
                return_cards = [sorted_cards[0]] + sorted_cards[3:] + pair_cards
                return True, return_cards
            # check 2 + 1
            whether, pair_cards = Pair.satisfy(sorted_cards[:2])
            if whether and not sorted_cards[2].equals(pair_cards[0]):
                return_cards = [sorted_cards[2]] + sorted_cards[3:] + pair_cards
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
            # check 2 + 3 first to prioritize the larger fullhouse
            whether_triple, triple_cards = Triple.satisfy(sorted_cards[2:])
            whether_pair, pair_cards = Pair.satisfy(sorted_cards[:2])
            if whether_triple and whether_pair and not triple_cards[0].equals(pair_cards[0]):
                return True, triple_cards + pair_cards
            # check 3 + 2
            whether_triple, triple_cards = Triple.satisfy(sorted_cards[:3])
            whether_pair, pair_cards = Pair.satisfy(sorted_cards[3:])
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
        if whether_pair1 and whether_pair2 and not pair_cards1[0].equals(pair_cards2[0]):
            return True, pair_cards2 + [sorted_cards[-1]] + pair_cards1
        # check 1 + 3 first to prioritize larger fullhouse
        whether, triple_cards = Triple.satisfy(sorted_cards[1:4])
        if whether and not triple_cards[0].equals(sorted_cards[0]):
            return True, triple_cards + [sorted_cards[0], sorted_cards[-1]]
        # check 3 + 1
        whether, triple_cards = Triple.satisfy(sorted_cards[:3])
        if whether and not triple_cards[0].equals(sorted_cards[3]):
            return True, triple_cards + [sorted_cards[3], sorted_cards[-1]]
        # otherwise
        return False, None

    @staticmethod
    def is_bomb():
        return False


class Straight(CardComp):
    '''
    Five consecutive singles
    '''
    def __init__(self, cards):
        super().__init__(cards)
        whether, sorted_cards = self.satisfy(cards)
        assert whether
        self.cards = sorted_cards

    def greater_than(self, card_comp):
        if not isinstance(card_comp, Straight):
            return False
        return self.cards[0].greater_than(card_comp.cards[0])


    @staticmethod
    def satisfy(cards):
        if len(cards) != 5:
            return False, None

        # sort the card and make level card at proper position
        sorted_cards = sorted(cards)
        num_wildcards = sum([card.is_wildcard() for card in sorted_cards])
        if num_wildcards == 1:
            # a b c level wild -> a b level c wild
            if sorted_cards[3].number < sorted_cards[2].number and sorted_cards[3].number > sorted_cards[1].number:
                sorted_cards = sorted_cards[0:2] + sorted_cards[3:4] + sorted_cards[2:3] + sorted_cards[4::]
            # a b c level wild -> a level b c wild
            if sorted_cards[3].number < sorted_cards[1].number and sorted_cards[3].number > sorted_cards[0].number:
                sorted_cards = sorted_cards[0:1] + sorted_cards[3:4] + sorted_cards[1:3] + sorted_cards[4::]
            # a b c level wild -> level a b c wild
            if sorted_cards[3].number < sorted_cards[0].number:
                sorted_cards = sorted_cards[3:4] + sorted_cards[0:3] + sorted_cards[4::]

        if num_wildcards == 2:
            # a b level wild wild -> a level b wild wild
            if sorted_cards[-3].number > sorted_cards[-5].number and sorted_cards[-3].number < sorted_cards[-4].number:
                sorted_cards = sorted_cards[0:1] + sorted_cards[2:3] + sorted_cards[1:2] + sorted_cards[3::]
            # a b level wild wild -> level a b wild wild
            elif sorted_cards[-3].number < sorted_cards[-5].number:
                sorted_cards = sorted_cards[2:3] + sorted_cards[0:2] + sorted_cards[3::]

        # list of card numbers and colors
        card_numbers = [card.number for card in sorted_cards]

        # largest card can be no more than ace
        if sorted(card_numbers)[-1] > 14:
            return False, None
        # if there are five unique numbers
        if len(set(card_numbers)) == 5:
            # no wild card:
            if num_wildcards == 0:
                if card_numbers[0] + 4 == card_numbers[4]:
                    return True, sorted_cards
                else:
                    return False, None
            if num_wildcards == 1:
                first_four = [card_numbers[i]-card_numbers[0] for i in range(4)]

                # i, i+1, i+2, i+3 wild
                if first_four == [0, 1, 2, 3]:
                    if card_numbers[3] <= 13:  # i+3 less than A
                        return True, sorted_cards
                    if card_numbers[3] == 14: # i+3 is A
                        return True, sorted_cards[4::] + sorted_cards[0:3]
                # i, i+1, i+2, i+4 wild
                elif first_four == [0, 1, 2, 4]:
                    return True,  sorted_cards[0:3] + sorted_cards[4::] + sorted_cards[3:4]
                # i, i+1, i+3, i+4 wild
                elif first_four == [0, 1, 3, 4]:
                    return True, sorted_cards[0:2] + sorted_cards[4::] + sorted_cards[2:4]
                # i, i+2, i+3, i+4 wild
                elif first_four == [0, 2, 3, 4]:
                    return True, sorted_cards[0:1] + sorted_cards[4::] + sorted_cards[1:4]
                else:
                    return False, None


        # four or three unique card numbers
        elif len(set(card_numbers)) == 4 or len(set(card_numbers)) == 3:
            if num_wildcards == 2:
                first_three = [card_numbers[i] - card_numbers[0] for i in range(3)]
                # i, i+1, i+2, wild, wild
                if first_three == [0, 1, 2]:
                    if card_numbers[2] <= 12:  # i+2 less than K
                        return True, sorted_cards
                    if card_numbers[2] == 13:  # i+2 is K
                        return True, [sorted_cards[-1]] + sorted_cards[1:4] + [sorted_cards[-2]]
                    if card_numbers[2] == 14: # i+2 is A
                        return True, sorted_cards[3::] + sorted_cards[1:4]
                # i, i+2, i+3, wild, wild
                elif first_three == [0, 2, 3]:
                    if card_numbers[2] <= 13:  # i+3 less than A
                        return True, [sorted_cards[0], sorted_cards[-1]] + sorted_cards[1:3] + [sorted_cards[-1]]
                    if card_numbers[2] == 14:  # i+3 is A
                        return True, [sorted_cards[-1], sorted_cards[0], sorted_cards[-1]] + sorted_cards[1:3]
                # i, i+1, i+3, wild, wild
                elif first_three == [0, 1, 3]:
                    if card_numbers[2] <= 13:  # i+3 less than A
                        return True, sorted_cards[0:2] + [sorted_cards[-1], sorted_cards[2]] + [sorted_cards[-1]]
                    if card_numbers[2] == 14:  # i+3 is A
                        return True, [sorted_cards[-1]] + sorted_cards[0:2] + [sorted_cards[-1], sorted_cards[2]]
                # i, i+2, i+4, wild, wild
                elif first_three == [0, 2, 4]:
                    return True, sorted_cards[0:1] + [sorted_cards[-1]] + sorted_cards[1:2] + [sorted_cards[-1]] + sorted_cards[2:3]
                else:
                    return false, None
            else:
                return False

        # less than three unique card numbers
        else:
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
            if whether_triple1 and whether_triple2:
                if triple_cards1[0].number + 1 == triple_cards2[0].number:
                    return True, triple_cards1 + triple_cards2
                # special case of Ace
                if triple_cards1[0].number == 2 and triple_cards2[0].number == 14:
                    for i in range(3):
                        triple_cards2[i].number = 1
                    return True, triple_cards1 + triple_cards2
            # otherwise
            return False, None

        # at least 1 wild card
        # check fullhouse first
        whether, fullhouse = FullHouse.satisfy(sorted_cards[:-1])

        # there will be at most 1 wildcard in this fullhouse
        # so we can always check the first number in the triple
        # and the the first in the pair
        if whether:
            triple, pair = fullhouse[:3], fullhouse[3:]
            if triple[0].number + 1 == pair[0].number:
                return True, triple + pair + [sorted_cards[-1]]
            if triple[0].number - 1 == pair[0].number:
                return True, pair + [sorted_cards[-1]] + triple
            # treat special case of Ace
            if triple[0].number == 14 and pair[0].number == 2:
                triple[0].number = 1
                return True, triple + pair + [sorted_cards[-1]]
            if triple[0].number == 2 and pair[0].number == 14:
                pair[0].number = 1
                return True, pair + [sorted_cards[-1]] + triple
        # otherwise
        return False, None

    @staticmethod
    def is_bomb():
        return False

