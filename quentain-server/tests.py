import unittest
from quentain import *
import pickle
import json


class CompTest(unittest.TestCase):
    def test_comp(self):
        pass
        with open('tests/comp.json', 'r') as f:
            test_file = json.load(f)
            level, comp_list = test_file['level'], test_file['comp_list']
            for comp in comp_list:
                cards = comp['cards']
                cards = [Card(c[0], c[1], level) for c in cards]
                inferred_card = CardComp.from_card_list(cards)
                inferred_type = type(inferred_card).__name__
                type_name = comp['type']
                print(inferred_card.cards, 'groundtruth:', type_name, 'inferred:', inferred_type)
                self.assertEqual(inferred_type, type_name)


if __name__ == '__main__':
    unittest.main()