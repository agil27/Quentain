import quentain

series = quentain.Series()

series.add_player('A')
assert series.start() == None
series.add_player('B')
series.add_player('C')
series.add_player('D')

game = series.start()
game.finished_players = [0,1,2,3]

game = series.next_game()
assert game.level == 4
assert series.current_turn == 0
game.finished_players = [0,2,1,3]

game = series.next_game()
assert game.level == 7
assert series.current_turn == 0
game.finished_players = [1,2,0,3]

game = series.next_game()
assert game.level == 3
assert series.current_turn == 1
game.finished_players = [0,2,1,3]

game = series.next_game()
assert game.level == 10
assert series.current_turn == 0
game.finished_players = [0,1,2,3]

game = series.next_game()
assert game.level == 12
assert series.current_turn == 0
game.finished_players = [0,2,1,3]

game = series.next_game()
assert game.level == 13
assert series.current_turn == 0
game.finished_players = [0,1,3,2]

game = series.next_game()
assert game.level == 13
assert series.current_turn == 0
game.finished_players = [0,1,2,3]

game = series.next_game()
assert game == None
assert series.finished
assert series.winning_turn == 0