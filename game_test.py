import requests
import os
import json
import time
import ast
import quentain

# # Initiate new game
# url = 'http://localhost:5000/new_game'
# headers = {'Content-Type': 'application/json'}
# data = '{"level": 2}'

# r_start_new = requests.post(url, headers=headers, data=data)
# token = json.loads(r_start_new.text)["token"]

token = input("Please enter token: ")

# Member Join
url = 'http://localhost:5000/join_game/' + token
r_join = requests.post(url)
print(r_join.text)
player = current_player = json.loads(r_join.text)["player_number"]

# start game when the last player enter
if int(player)== 3:
    url = 'http://localhost:5000/start_game/' + token
    r_start_game = requests.post(url)


prev_state = requests.get('http://localhost:5000/get_game_state/' + token)
headers = {'Content-Type': 'application/json'}
url = 'http://localhost:5000/throw_cards/' + token

# query server every one second
while True:
    # Query the server
    state = requests.get('http://localhost:5000/get_game_state/' + token)
    if prev_state.text != state.text:
        current_player = json.loads(state.text)["current_player"]
        print("Current player", current_player)

        # hint user to user to throw cards
        if int(current_player) == int(player):
            cards = json.loads(state.text)["game_state"]
            print("Your Cards: ", cards)
            succeed = False
            explanation = None
            while not succeed:
                if explanation is not None:
                    print('Illegal Operation:', explanation)
                choices = input('Input your choices, splitting with comma: ')
                choices = '[' + choices.replace(" ","") + ']'
                data = '{"player_number": '+ str(current_player) + ', "choices": '+ choices + '}'
                r_throw = requests.post(url, headers=headers, data=data)
                succeed = (r_throw.status_code == 200)
        
                if not succeed:
                    explanation = json.loads(r_throw.text)["error"]
           
            if "folded" in json.loads(r_throw.text):
                print('You folded!\n')
            else:
                print('You throw ', json.loads(r_throw.text)["thrown_cards"])

    prev_state = state
    # Sleep for 1 second
    time.sleep(1)

