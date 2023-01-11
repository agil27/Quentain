colors = ['Spade', 'Club', 'Heart', 'Diamond']
name_map = {
    11: 'Jack',
    12: 'Queen',
    13: 'King',
    14: 'Ace',
    15: 'Black Joker',
    16: 'Red Joker'
}


class Card:
    def __init__(self, number, color, level):
        # Jack, Queen, King, Ace, Black Joker, Red Joker <==> 11, 12, 13, 14, 15, 16
        assert isinstance(number, int) and 1 <= number <= 16

        # for special case of Ace
        # A, 2, 3, 4, 5 and 10, J, Q, K, A is both acceptable
        self.raw_number = number if number != 14 else 1
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

    def consecutive_greater_than(self, card):
        return self.raw_number > card.raw_number

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

    def json_encode(self):
        return {
            'color': self.color,
            'number': self.raw_number,
            'selected': False
        }
