<script setup>
import { NButton, NCard, NIcon, NAlert, NSpace, NInput, NInputNumber, NSwitch} from 'naive-ui'
import { GameControllerOutline, GameController } from '@vicons/ionicons5'
import { TokenFilled } from '@vicons/material'
import { Server24Filled, DocumentPageNumber24Filled} from '@vicons/fluent'
import axios from 'axios'
import config from '../../config'
</script>

<script>
export default {
  data() {
    return {
      whetherJoin: false,
      level: 2,
      token: '',
      player_id: -1,
      failError: '',
      experimental: false,
      server: config.serverPath,
    }
  },
  props: {
    username: {
      type: String,
      default: ''
    }
  },
  methods: {
    toggle() {
      this.whetherJoin = !this.whetherJoin
    },
    async generate_token() {
      try {
        const response = await axios.post(this.server + '/new_game', {
          level: parseInt(this.level),
          experimental: this.experimental
        })
        this.whetherJoin = true;
        this.token = response.data.token
        this.failError = ''
      } catch (error) {
        console.error(error)
        this.failError = error.response.data
      }
    },
    async join_game() {
      try {
        const response = await axios.post(this.server + '/join_game/' + this.token, 
          {username: this.$props.username, token:this.token})
        this.player_id = response.data.player_number
        console.log(this.player_id)
        this.$emit('joinGame', this.player_id, this.token, this.server)
        this.failError = ''
      } catch (error) {
        console.log(error)
        this.failError = error.response.data
      }
    }
  },
  computed: {
    title() {
      return this.whetherJoin ? 'Join a game' : 'Start a new game'
    },
    failJoin() {
      return this.failError !== ""
    }
  },
}
</script>

<template>

  <n-card style="margin-left: 35%" size="large" hoverable
    :title="title"
    :segmented="{
      content: true,
      footer: 'soft'
    }"
  >
    <template #header-extra>
      <n-button v-if="whetherJoin" @click="toggle" text>
        Start a new game 
      </n-button>
      <n-button v-else @click="toggle" text>
        Join a game
      </n-button>
    </template>
    <n-space vertical>
        <n-space>
          {{ whetherJoin ? 'Please enter server address and a token number to join a game room' : 'Please enter server address and level number to generate a game token' }}
          <n-icon size="25" color="#0e7a0d" :component="GameController"/>
        </n-space>
      <n-input v-model:value="server" placeholder="server IP address">
        <template #prefix>
          <n-icon :component="Server24Filled" />
        </template>
      </n-input>
      <n-input v-if='whetherJoin' v-model:value="token" placeholder="Input room token">
        <template #prefix>
            <n-icon :component="TokenFilled" />
        </template>
      </n-input>
      <n-input-number v-else v-model:value='level' placeholder='Input level number (1-13)'
      :min="1" :max="13">
        <template #prefix>
          <n-icon :component="DocumentPageNumber24Filled" />
        </template>
      </n-input-number>
      <n-space v-if='!whetherJoin'>
        Experimental Mode (4 cards)
        <n-switch v-model:value="experimental" />
      </n-space>
      <n-alert v-if="failJoin" title="Error" type="error">
        Fail to join game: {{ failError }}
      </n-alert>
    </n-space>
    <template #action>
      <n-button v-if="whetherJoin" type="primary" @click="join_game">
        Join Now!
      </n-button>
      <n-button v-else type="primary" @click="generate_token">
        Generate a token
      </n-button>
    </template>
  </n-card>
</template>