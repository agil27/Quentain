<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import 'vfonts/FiraSans.css'
import 'vfonts/FiraCode.css'
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
      </li>
    </ul>
  </nav>
  <start-view v-if="!inGame" @joinGame="join_game" />
  <game-view v-else :player_id="player_id" :token="token" @returnIndex="return_index"/>
</div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import StartView from '@/views/StartView.vue'
import GameView from '@/views/GameView.vue'

export default {
  components: {
    StartView,
    GameView
  },
  data() {
    return {
      inGame: false,
      player_id: -1,
      token: ''
    }
  },
  methods: {
    join_game(player_id, token) {
      this.player_id = player_id
      this.token = token
      this.inGame = true
    },
    return_index() {
      this.inGame = false
      this.token = ''
      this.player_id = -1
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

