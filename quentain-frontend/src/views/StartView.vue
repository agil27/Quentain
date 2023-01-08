<script setup lang="ts">
import { useNotification, useMessage, NButton, NCard, NIcon, NAlert, NSpace, NInput, NInputNumber} from 'naive-ui'
import { GameControllerOutline, GameController } from '@vicons/ionicons5'
import { TokenFilled } from '@vicons/material'
import axios from 'axios'
</script>

<script lang='ts'>

function notify(type, info) {
  notification[type]({
    content: info,
    meta: "error",
    duration: 2500,
    keepAliveOnHover: true
  })
}

export default {
  data() {
    return {
      joinGame: false,
      level: 2,
      token: '',
      player_id: -1,
      failError: ''
    }
  },
  methods: {
    toggle() {
      this.joinGame = !this.joinGame
    },
    async generate_token() {
      try {
        const response = await axios.post('http://localhost:5050/new_game', {
          level: parseInt(this.level)
        })
        this.joinGame = true;
        this.token = response.data.token
      } catch (error) {
        console.error(error)
      }
    },
    async join_game() {
      try {
        const response = await axios.post('http://localhost:5050/join_game/' + this.token, {})
        this.player_id = response.data.player_number
        console.log(this.player_id)
      } catch (error) {
        console.log(error)
        this.failError = error
      }
    }
  },
  computed: {
    title() {
      return this.joinGame ? 'Join a game' : 'Start a new game'
    },
    failJoin() {
      return this.failError !== ""
    }
  }
}
</script>

<template>

  <n-card style="margin-left: 35%" size="huge" hoverable
    :title="title"
    :segmented="{
      content: true,
      footer: 'soft'
    }"
  >
    <template #header-extra>
      <n-button v-if="joinGame" @click="toggle" text>
        Start a new game 
      </n-button>
      <n-button v-else @click="toggle" text>
        Join a game
      </n-button>
    </template>
    <n-space vertical>
      <n-space>
        {{ this.joinGame ? 'Please enter a token number to join a game room' : 'Please click the button to generate a game token' }}
        <n-icon size="25" color="#0e7a0d">
          <game-controller />
        </n-icon>
      </n-space>
      <n-input v-if='joinGame' v-model:value="token" placeholder="Please enter a token">
        <template #prefix>
          <n-icon :component="TokenFilled" />
        </template>
      </n-input>
      <n-input-number v-else v-model:value='level' placeholder='Input level number (1-13)'
      :min="1" :max="13">
        <template #prefix>
          <n-icon :component="TokenFilled" />
        </template>
      </n-input-number>
      <n-alert v-if="failJoin" title="Error" type="error">
        Fail to join game: {{ this.failError }}
      </n-alert>
    </n-space>
    <template #action>
      <n-button v-if="joinGame" type="primary" @click="join_game">
        Join Now!
      </n-button>
      <n-button v-else type="primary" @click="generate_token">
        Generate a token
      </n-button>
    </template>
  </n-card>
</template>