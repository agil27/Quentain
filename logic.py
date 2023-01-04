colors = ['Spade', 'Club', 'Heart', 'Diamond']

class Card:
    def __init__(self, number, color, level):
        # Jack, Queen, King, Black Joker, Red Joker <==> 11, 12, 13, 14, 15
        assert isinstance(number, int) and 1 <= number <= 15
        if 1 <= number <= 13:
            assert color in colors
        else:
            assert color == 'Joker'
        self.number = number
        self.color = color
        self.level = level

    def clone(self):
        return Card(self.number, self.color, self.level)

    def is_wildcard(self):
        return self.number == self.level and self.color == 'Heart'

    def greater_than(self, card):
        # level card: this level's special number, as the greatest number other than the jokers
        assert isinstance(card, Card)
        assert isinstance(self.level, int)
        if card.number == self.level:
            if self.number >= 14:
                return True
            else:
                return False
        else:
            if self.number == self.level:
                if card.number <= 13:
                    return True
                else:
                    return False
            else:
                return self.number > card.number

    def __lt__(self, card):
        return card.greater_than(self)


class CardComp:
    '''
    A composition of playing cards that is legal
    '''
    def __init__(self, cards):
        assert isinstance(cards, list)
        pass

    def greater_than(self, card_comp):
        pass


class Single(CardComp):
    def __init__(self, cards):
        super().__init__(cards)
        assert len(cards) == 1
        self.card = cards[0]

    def greater_than(self, card_comp):
        if not isinstance(card_comp, Single):
            return False
        return self.card.greater_than(card_comp.card)


class Pair(CardComp):
    def __init__(self, cards):
        super().__init__(cards)
        assert len(cards) == 2
        level_cond0 = cards[0].is_wildcard() and cards[1].color != 'Joker'
        level_cond1 = cards[1].is_wildcard() and cards[0].color != 'Joker'
        assert cards[0].number == cards[1].number or level_cond0 or level_cond1
        self.cards = cards
        if level_cond1 and not level_cond0:
            self.cards[1].number = self.cards[0].number
        elif level_cond0 and not level_cond1:
            self.cards[0].number = self.cards[1].number

    def greater_than(self, card_comp):
        if not isinstance(card_comp, Pair):
            return False
        return self.cards[0].greater_than(card_comp.cards[0])


class Triple(CardComp):
    def __init__(self, cards):
        super().__init__(cards)
        assert len(cards) == 3

        # sorted with ascending order
        # using the __lt__ function defined in Card class
        sorted_cards = sorted(cards)

        # if there are joker(s) in this comp, it is definitely illegal
        assert sorted_cards[-1].color != 'Joker'

        # there are at most two wild cards in one card composition
        # so the smallest card must be the value for this triple
        assert sorted_cards[1].number == sorted_cards[0].number or sorted_cards[1].is_wildcard()
        assert sorted_cards[2].number == sorted_cards[0].number or sorted_cards[2].is_wildcard()
        self.cards = sorted_cards
        self.cards[1].number = self.cards[0].number
        self.cards[2].number = self.cards[0].number

    def greater_than(self, card_comp):
        if not isinstance(card_comp, Triple):
            return False
        return self.cards[0].greater_than(card_comp.cards[0])



