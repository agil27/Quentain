# Quentain
An implementation of the Poker Game Guandan popular among Jiangsu and Anhui in China

## Rule
According to https://en.wikipedia.org/wiki/Guandan

## Coverage Test

Make sure `coverage` is installed, then use
```bash
coverage run test.py
```

## CLI version

A experimental CLI version is playable right now.

Run 
```bash
python  cli.py <-e/--exp>
```

The argument `-e` or `--exp` is to turn on the experimental debug version, where each player gets 7 cards instead of 27.

<img src='img/cli.gif'>

## Frontend UI

Make sure you install the latest version of `node`, `npm`. Install `vue` and `naive-ui` as well.

Under `frontend/quentain-frontend`, run

```bash
npm install
npm run dev
```

The current demo looks like this. The implementation is based on `HTML5 canvas`.

<img src='img/ui.gif'>

## Local server version

* To start game engine locally:

```bash
cd quentian
flask run --port=8080
```

* To start a new game (with level 2):
```bash
curl -X POST -H "Content-Type: application/json" -d '{"level": 2}' http://localhost:8080/start_game
```

* To check the current game state:
```bash
curl http://localhost:8080/get_game_state
```

* To throw cards if it is your turn:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"choices": [<your choices, seperated by comma>]}' http://localhost:8080/throw_cards
```
