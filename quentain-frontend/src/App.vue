<script setup>
import LoginView from './views/LoginView.vue'
import StartView from './views/StartView.vue'
import GameView from './views/GameView.vue'
import 'vfonts/FiraSans.css'
import 'vfonts/FiraCode.css'
import { NButton} from 'naive-ui'
import config from '../config'
</script>

<template>
<div class="main">
  <nav>
    <div class="logo">
      <img class="logoimg" src="@/assets/logo.svg" alt="Logo" height="50">
      <p class="name"> QUENTAIN</p>
    </div>
    <ul>
      <li>
        <a :class="{selected: !inGame}" to="/">Join a game</a>
        <a :class="{selected: inGame}" to="/game">Game Room</a>
        <n-button v-if="loggedIn" @click="log_out">Log out</n-button >
      </li>
    </ul>
  </nav>
  <LoginView v-if="!loggedIn" @loggedIn="log_in" @loggedOut="log_out"/>
  <StartView v-else-if="!inGame" @joinGame="join_game" :username="username"/>
  <GameView v-else :player_id="player_id" :token="token" :server="gameServer" :username="username" @endGame="end_game" @returnIndex="return_index" ref="gameview"/>
</div>
</template>

<script>
export default {
  components: {
    LoginView, StartView, GameView
  },
  data() {
    return {
      loggedIn: false,
      username: '',
      inGame: false,
      player_id: -1,
      token: '',
      gameServer: config.serverPath
    }
  },
  methods: {
    join_game(player_id, token, returnServer) {
      this.player_id = player_id
      this.token = token
      this.inGame = true
      this.gameServer = returnServer
    },
    return_index() {
      this.inGame = false
      this.token = ''
      this.player_id = -1
    },
    end_game() {
      this.inGame = false
      this.token = ''
      this.player_id = -1
    },
    log_in(username){
      this.loggedIn = true
      this.username = username
    },
    log_out(){
      this.loggedIn = false
      this.username = ''
      clearInterval(this$refs.gameview.intervalId)
    }
  }
}
</script>

<style scoped>
nav {
  background-color: #fafafa;
  border-bottom: 1px solid #d3d3d3;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 45px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1;
}

nav ul {
  display: flex;
  list-style-type: none;
  margin: 0;
  padding: 0;
}

nav li {
  display: flex;
}

nav a {
  font-family: v-sans;
  color: #333;
  display: block;
  font-size: 12px;
  padding: 0 12px;
  text-decoration: none;
  line-height: 32px;
}

nav a.selected {
  color: #6b2d92;
  background-color: #eee;
}

nav .logo {
  margin: 0 2rem 0;
  display: flex;
  align-items: center;
  text-decoration: none;
}

nav .logoimg {
  color: #6b2d92;
}

nav .name {
  font-family: v-mono;
  margin: 0 3rem 0;
}
</style>

