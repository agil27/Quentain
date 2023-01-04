colors = ['Spade', 'Club', 'Heart', 'Diamond']

class Card:
    def __init__(self, number, color):
        # Jack, Queen, King, Black Joker, Red Joker <==> 11, 12, 13, 14, 15
        assert isinstance(number, int) and 1 <= number <= 15
        if 1 <= number <= 13:
            assert color in colors
        else:
            assert color == 'Joker'
        self.number = number
        self.color = color

    def is_wildcard(self, level):
        return self.number == level and self.color == 'Heart'

    def greater_than(self, card, level):
        # level card: this level's special number, as the greatest number other than the jokers
        assert isinstance(card, Card)
        assert isinstance(level, int)
        if card.number == level:
            if self.number >= 14:
                return True
            else:
                return False
        else:
            if self.number == level:
                if card.number <= 13:
                    return True
                else:
                    return False
            else:
                return self.number > card.number


class CardComp:
    '''
    A composition of playing cards that is legal
    '''
    def __init__(self, cards, level):
        assert isinstance(cards, list)
        pass

    def greater_than(self, card_comp, level):
        pass


class Single(CardComp):
    def __init__(self, cards, level):
        super().__init__(cards, level)
        assert len(cards) == 1
        self.card = cards[0]

    def greater_than(self, card_comp, level):
        if not isinstance(card_comp, Single):
            return False
        return self.card.greater_than(card_comp.card, level)


class Pair(CardComp):
    def __init__(self, cards, level):
        super().__init__(cards, level)
        assert len(cards) == 2
        level_cond0 = cards[0].is_wildcard() and cards[1].color != 'Joker'
        level_cond1 = cards[1].is_wildcard() and cards[0].color != 'Joker'
        assert cards[0].number == cards[1].number or level_cond0 or level_cond1
        self.cards = cards
        if level_cond1 and not level_cond0:
            self.cards[1].number = self.cards[0].number
        elif level_cond0 and not level_cond1:
            self.cards[0].number = self.cards[1].number

    def greater_than(self, card_comp, level):
        if not isinstance(card_comp, Pair):
            return False
        return self.cards[0].greater_than(card_comp.cards[0], level)


class Triple(CardComp):
    def __init__(self, cards, level):
        super().__init__(cards, level)
        assert len(cards) == 3
        # TODO: judge whether it's legal
        self.cards = cards

    def greater_than(self, card_comp, level):
        if not isinstance(card_comp, Triple):
            return False
        return self.cards[0].greater_than(card_comp.cards[0], level)



