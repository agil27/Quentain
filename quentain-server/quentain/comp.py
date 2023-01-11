from .card import Card, colors, name_map


class CardComp:
    '''
    A composition of playing cards that is legal
    '''

    def __init__(self, cards):
        assert isinstance(cards, list)

    def greater_than(self, card_comp):
        pass

    @staticmethod
    def sort_no_level(cards):
        sorted_cards = sorted(cards)
        num_wildcards = sum([card.is_wildcard() for card in sorted_cards])
        if num_wildcards == 0:
            if sorted_cards[-1].level != sorted_cards[-1].number:
                return sorted_cards
            else:
                wildcards = []
        if num_wildcards == 1:
            if sorted_cards[-2].level != sorted_cards[-2].number:
                return sorted_cards
            else:
                wildcards = [sorted_cards[-1]]
                sorted_cards = sorted_cards[0:-1]
        if num_wildcards == 2:
            if sorted_cards[-3].level != sorted_cards[-3].number:
                return sorted_cards
            else:
                wildcards = [sorted_cards[-2], sorted_cards[-1]]
                sorted_cards = sorted_cards[0:-2]
        card_numbers = [(card.number, i) for i, card in enumerate(sorted_cards)]
        card_numbers = sorted(card_numbers, key=lambda tup: tup[0])
        return [sorted_cards[card[1]] for card in card_numbers] + wildcards

    def __str__(self):
        return type(self).__name__ + ': ' + str(self.cards)

    def __repr__(self):
        return str(self)

    @staticmethod
    def satisfy(cards):
        # return two values
        # (whether_satisfy, the re-organized card comp)
        pass

    @staticmethod
    def is_bomb():
        pass

    @staticmethod
    def from_card_list(cards, prev=None):
        '''
        Generating card compostition from card list
        follow the same form as the previous composition
        except it's the first one to throw cards
        :param cards: list of Cards
        :param prev: previous CardComp
        :return: CardComp object
        '''
        if len(cards) == 0:
            return Fold(cards)
        elif len(cards) == 1:
            single = Single(cards)
            if single.valid:
                return single
            else:
                return IllegalComp(cards)
        elif len(cards) == 2:
            pair = Pair(cards)
            if pair.valid:
                return pair
            else:
                return IllegalComp(cards)
        elif len(cards) == 3:
            triple = Triple(cards)
            if triple.valid:
                return triple
            else:
                return IllegalComp(cards)
        elif len(cards) == 4:
            joker_bomb = JokerBomb(cards)
            if joker_bomb.valid:
                return joker_bomb
            else:
                bomb = NaiveBomb(cards)
                if bomb.valid:
                    return bomb
                else:
                    return IllegalComp(cards)
        elif len(cards) == 5:
            straight_flush = StraightFlush(cards)
            if straight_flush.valid:
                return straight_flush
            else:
                bomb = NaiveBomb(cards)
                if bomb.valid:
                    return bomb
                else:
                    fullhouse = FullHouse(cards)
                    if fullhouse.valid:
                        return fullhouse
                    else:
                        straight = Straight(cards)
                        if straight.valid:
                            return straight
                        else:
                            return IllegalComp(cards)
        elif len(cards) == 6:
            bomb = NaiveBomb(cards)
            if bomb.valid:
                return bomb
            else:
                # tube and plate are the only
                # possible conflicted types of composition

                # if the previous comp is not plate
                # prioritize the tube
                if not isinstance(prev, Plate):
                    tube = Tube(cards)
                    if tube.valid:
                        return tube
                plate = Plate(cards)
                if plate.valid:
                    return plate
                else:
                    return IllegalComp(cards)
        else:
            bomb = NaiveBomb(cards)
            if bomb.valid:
                return bomb
            else:
                return IllegalComp(cards)


class Fold(CardComp):
    def __init__(self, cards):
        super().__init__(cards)
        self.cards = sorted(cards)

    def greater_than(self, card_comp):
        return False

    @staticmethod
    def satisfy(cards):
        if len(cards) == 0:
            return True, cards
        else:
            return False, cards

    @staticmethod
    def is_bomb():
        return False


class IllegalComp(CardComp):
    def __init__(self, cards):
        super().__init__(cards)
        self.cards = sorted(cards)

    @staticmethod
    def is_bomb():
        return False


class Single(CardComp):
    def __init__(self, cards):
        super().__init__(cards)
        whether, sorted_cards = self.satisfy(cards)
        self.valid = whether
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
        self.valid = whether
        self.cards = sorted_cards

    def greater_than(self, card_comp):
        if not isinstance(card_comp, Pair):
            return False
        return self.cards[0].greater_than(card_comp.cards[0])

    @staticmethod
    def satisfy(cards):
        if len(cards) != 2:
            return False, sorted(cards)
        level_cond0 = cards[0].is_wildcard() and cards[1].color != 'Joker'
        level_cond1 = cards[1].is_wildcard() and cards[0].color != 'Joker'
        whether = (cards[0].equals(cards[1]) or level_cond0 or level_cond1)
        if not whether:
            return False, sorted(cards)
        return True, sorted(cards)

    @staticmethod
    def is_bomb():
        return False


class Triple(CardComp):
    def __init__(self, cards):
        super().__init__(cards)
        whether, sorted_cards = self.satisfy(cards)
        self.valid = whether
        self.cards = sorted_cards

    def greater_than(self, card_comp):
        if not isinstance(card_comp, Triple):
            return False
        return self.cards[0].greater_than(card_comp.cards[0])

    @staticmethod
    def satisfy(cards):
        if len(cards) != 3:
            return False, sorted(cards)

        # sorted with ascending order
        # using the __lt__ function defined in Card class
        sorted_cards = sorted(cards)

        # if there are joker(s) in this comp, it is definitely illegal
        if sorted_cards[-1].color == 'Joker':
            return False, sorted(cards)

        # there are at most two wild cards in one card composition
        # so the smallest card must be the value for this triple
        if not sorted_cards[1].equals(sorted_cards[0]) and not sorted_cards[1].is_wildcard():
            return False, sorted(cards)
        if not sorted_cards[2].equals(sorted_cards[0]) and not sorted_cards[2].is_wildcard():
            return False, sorted(cards)

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
        self.valid = whether
        self.cards = sorted_cards

    def greater_than(self, card_comp):
        if not isinstance(card_comp, FullHouse):
            return False
        return self.cards[0].greater_than(card_comp.cards[0])

    @staticmethod
    def satisfy(cards):
        if len(cards) != 5:
            return False, sorted(cards)

        # similar, sort first
        sorted_cards = sorted(cards)

        # if the largest card is Joker, it must be a pair of Joker
        if sorted_cards[4].color == 'Joker':
            if not sorted_cards[3].equals(sorted_cards[4]):
                return False, sorted(cards)
            else:
                # check if the rest is a triple
                whether, triple_cards = Triple.satisfy(sorted_cards[:3])
                if not whether:
                    return False, sorted(cards)
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
            return False, sorted(cards)

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
            return False, sorted(cards)

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
        return False, sorted(cards)

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
        self.valid = whether
        self.cards = sorted_cards

    def greater_than(self, card_comp):
        if not isinstance(card_comp, Straight):
            return False
        return self.cards[0].consecutive_greater_than(card_comp.cards[0])

    # @staticmethod
    # def sort_no_level(cards):
    #     return super(Straight, Straight).sort_no_level()

    @staticmethod
    def satisfy(cards):
        if len(cards) != 5:
            return False, sorted(cards)

        # sort the card and make level card at proper position
        sorted_cards = super(Straight, Straight).sort_no_level(cards)
        num_wildcards = sum([card.is_wildcard() for card in sorted_cards])
        # list of card numbers and colors
        card_numbers = [card.number for card in sorted_cards]

        # largest card can be no more than ace
        if max(card_numbers) > 14:
            return False, sorted(cards)
        # no wildcards
        if num_wildcards == 0:
            if card_numbers[0] + 4 == card_numbers[4] and len(set(card_numbers)) == 5:
                return True, sorted_cards
            else:
                return False, sorted(cards)
        # one wildcard
        elif num_wildcards == 1:
            first_four = [card_numbers[i] - card_numbers[0] for i in range(4)]
            # i, i+1, i+2, i+3 wild
            if first_four == [0, 1, 2, 3]:
                if card_numbers[3] <= 13:  # i+3 less than A
                    return True, sorted_cards
                if card_numbers[3] == 14:  # i+3 is A
                    return True, sorted_cards[4::] + sorted_cards[0:3]
            # i, i+1, i+2, i+4 wild
            elif first_four == [0, 1, 2, 4]:
                return True, sorted_cards[0:3] + sorted_cards[4::] + sorted_cards[3:4]
            # i, i+1, i+3, i+4 wild
            elif first_four == [0, 1, 3, 4]:
                return True, sorted_cards[0:2] + sorted_cards[4::] + sorted_cards[2:4]
            # i, i+2, i+3, i+4 wild
            elif first_four == [0, 2, 3, 4]:
                return True, sorted_cards[0:1] + sorted_cards[4::] + sorted_cards[1:4]
            else:
                return False, sorted(cards)

        # two wildcards
        elif num_wildcards == 2:
            first_three = [card_numbers[i] - card_numbers[0] for i in range(3)]
            # i, i+1, i+2, wild, wild
            if first_three == [0, 1, 2]:
                if card_numbers[2] <= 12:  # i+2 less than K
                    return True, sorted_cards
                if card_numbers[2] == 13:  # i+2 is K
                    return True, [sorted_cards[-1]] + sorted_cards[1:4] + [sorted_cards[-2]]
                if card_numbers[2] == 14:  # i+2 is A
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
                return True, sorted_cards[0:1] + [sorted_cards[-1]] + sorted_cards[1:2] + [
                    sorted_cards[-1]] + sorted_cards[2:3]
            # i, i+3, i+4, wild, wild
            elif first_three == [0, 3, 4]:
                return True, sorted_cards[0:1] + sorted_cards[-2:] + sorted_cards[1:3]
            elif first_three == [0, 1, 4]:
                return True, sorted_cards[:2] + sorted_cards[-2:] + sorted_cards[4:]
            else:
                return False, sorted(cards)

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
        self.valid = whether
        self.cards = sorted_cards

    def greater_than(self, card_comp):
        if not isinstance(card_comp, Plate):
            return False
        return self.cards[0].consecutive_greater_than(card_comp.cards[0])

    @staticmethod
    def satisfy(cards):
        if len(cards) != 6:
            return False, sorted(cards)

        # same logic as Triple, we first sort the card comp
        sorted_cards = sorted(cards)

        # no joker in a plate
        if sorted_cards[-1].color == 'Joker':
            return False, sorted(cards)

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
                    return True, triple_cards2 + triple_cards1
            # otherwise
            return False, sorted(cards)

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
                return True, triple + pair + [sorted_cards[-1]]
            if triple[0].number == 2 and pair[0].number == 14:
                return True, pair + [sorted_cards[-1]] + triple
        # otherwise
        return False, sorted(cards)

    @staticmethod
    def is_bomb():
        return False


class Tube(CardComp):
    '''
    Three consecutive Pairs
    '''

    def __init__(self, cards):
        super().__init__(cards)
        whether, sorted_cards = self.satisfy(cards)
        self.valid = whether
        self.cards = sorted_cards

    def greater_than(self, card_comp):
        if not isinstance(card_comp, Tube):
            return False
        return self.cards[0].consecutive_greater_than(card_comp.cards[0])

    @staticmethod
    def satisfy(cards):
        if len(cards) != 6:
            return False, sorted(cards)

        # sort the card and make level card at proper position
        sorted_cards = super(Tube, Tube).sort_no_level(cards)
        num_wildcards = sum([card.is_wildcard() for card in sorted_cards])
        # list of card numbers and colors
        card_numbers = [card.number for card in sorted_cards]

        # largest card can be no more than ace
        if max(card_numbers) > 14:
            return False, sorted(cards)
        # no wildcards
        if num_wildcards == 0:
            # must be i, i, i+1, i+1, i+2, i+2
            if len(set(card_numbers)) == 3:
                temp = [card.number - sorted_cards[0].number for card in sorted_cards]
                if temp == [0, 0, 1, 1, 2, 2]:
                    return True, sorted_cards
                else:
                    return False, sorted(cards)
            else:
                return False, sorted(cards)

        # one wildcard
        elif num_wildcards == 1:
            first_five = [card_numbers[i] - card_numbers[0] for i in range(5)]

            if first_five == [0, 0, 1, 1, 2]:  # i, i, i+1, i+1, i+2 wild
                return True, sorted_cards
            elif first_five == [0, 0, 1, 2, 2]:  # i, i, i+1, i+2, i+2 wild
                return True, sorted_cards[0:3] + [sorted_cards[-1]] + sorted_cards[3:5]
            elif first_five == [0, 1, 1, 2, 2]:  # i, i+1, i+1, i+2, i+2 wild
                return True, sorted_cards[0:1] + [sorted_cards[-1]] + sorted_cards[1:5]
            else:
                return False, sorted(cards)

        # two wildcards
        elif num_wildcards == 2:
            first_four = [card_numbers[i] - card_numbers[0] for i in range(4)]
            # i, i, i+1, i+1, wild wild
            if first_four == [0, 0, 1, 1]:
                if sorted_cards[-3].number < 14:  # i+1 smaller than Ace
                    return True, sorted_cards
                else:
                    return True, sorted_cards[4:6] + sorted_cards[0:4]
            # i, i, i+2, i+2, wild, wild
            elif first_four == [0, 0, 2, 2]:
                return True, sorted_cards[0:2] + sorted_cards[4:6] + sorted_cards[2:4]
            # i i i+1 i+2 wild wild
            elif first_four == [0, 0, 1, 2]:
                return True, sorted_cards[0:2] + [sorted_cards[2], sorted_cards[-1]] + [sorted_cards[3],
                                                                                        sorted_cards[-2]]
            # i i+1 i+1 i+2 wild wild
            elif first_four == [0, 1, 1, 2]:
                return True, [sorted_cards[0], sorted_cards[-1]] + sorted_cards[1:3] + [sorted_cards[3],
                                                                                        sorted_cards[-2]]
            # i i+1 i+2 i+2 wild wild
            elif first_four == [0, 1, 2, 2]:
                return True, [sorted_cards[0], sorted_cards[-1]] + [sorted_cards[1], sorted_cards[-2]] + sorted_cards[
                                                                                                         2:4]
            else:
                return False, sorted(cards)

    @staticmethod
    def is_bomb():
        return False


class JokerBomb(CardComp):
    '''
    Four jokers; the largest Comp possible
    '''

    def __init__(self, cards):
        super().__init__(cards)
        whether, sorted_cards = self.satisfy(cards)
        self.valid = whether
        self.cards = sorted_cards

    def greater_than(self, card_comp):
        # there can only be one joker bomb in one game
        return True

    @staticmethod
    def satisfy(cards):
        if len(cards) != 4:
            return False
        elif sorted([card.number for card in cards]) == [15, 15, 16, 16]:
            return True, sorted(cards)
        else:
            return False, sorted(cards)

    @staticmethod
    def is_bomb():
        return True


class NaiveBomb(CardComp):
    '''
    At least 4 cards with the same number
    '''

    def __init__(self, cards):
        super().__init__(cards)
        whether, sorted_cards = self.satisfy(cards)
        self.valid = whether
        self.cards = sorted_cards

    def greater_than(self, card_comp):
        # if the other is not bomb
        if not card_comp.is_bomb():
            return True

        # if the other is actually bomb
        # JokerBomb > everything
        if isinstance(card_comp, JokerBomb):
            return False
        # 6 Bomb > StraightFlush > 5 Bomb
        elif isinstance(card_comp, StraightFlush):
            if len(self.cards) >= 6:
                return True
            else:
                return False
        # Also NaiveBomb, compare number of cards first
        # then actual value
        else:
            if len(self.cards) > len(card_comp.cards):
                return True
            else:
                return self.cards[0].greater_than(card_comp.cards[0])

    @staticmethod
    def satisfy(cards):
        sorted_cards = sorted(cards)
        card_numbers = [card.number for card in sorted_cards]
        num_wildcards = sum([card.is_wildcard() for card in sorted_cards])
        if len(cards) < 4:
            return False, sorted(cards)
        elif num_wildcards == 0 and len(set(card_numbers)) == 1:
            return True, sorted_cards
        elif num_wildcards == 1 and len(set(card_numbers[0:-1])) == 1:
            return True, sorted_cards
        elif num_wildcards == 2 and len(set(card_numbers[0:-2])) == 1:
            return True, sorted_cards
        else:
            return False, sorted(cards)

    @staticmethod
    def is_bomb():
        return True


class StraightFlush(CardComp):
    def __init__(self, cards):
        super().__init__(cards)
        whether, sorted_cards = self.satisfy(cards)
        self.valid = whether
        self.cards = sorted_cards

    def greater_than(self, card_comp):
        if not card_comp.is_bomb():
            return True

        if isinstance(card_comp, JokerBomb):
            return False
        elif isinstance(card_comp, StraightFlush):
            return self.cards[0].greater_than(card_comp.cards[0])
        else:
            if len(card_comp.cards) <= 5:
                return True
            else:
                return False

    @staticmethod
    def satisfy(cards):
        sorted_cards = sorted(cards)
        card_colors = [card.color for card in sorted_cards]
        num_wildcards = sum([card.is_wildcard() for card in sorted_cards])

        if len(cards) != 5:
            return False, sorted(cards)
        else:
            is_Straight, sorted_cards = Straight.satisfy(cards)
            if is_Straight:
                if num_wildcards == 0 and len(set(card_colors)) == 1:
                    return True, sorted_cards
                elif num_wildcards == 1 and len(set(card_colors[0:-1])) == 1:
                    return True, sorted_cards
                elif num_wildcards == 2 and len(set(card_colors[0:-2])) == 1:
                    return True, sorted_cards
                else:
                    return False, sorted(cards)
            else:
                return False, sorted(cards)

    @staticmethod
    def is_bomb():
        return True
