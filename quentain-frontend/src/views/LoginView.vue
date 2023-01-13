<template>
  <form>
    <n-card style="margin-left: 35%" size="large" hoverable
      :title="title"
      :segmented="{
        content: true,
        footer: 'soft'
      }"
    >
      <template #header-extra>
        <n-button v-if="whetherlogin" @click="toggle" text>
          Register
        </n-button>
        <n-button v-else @click="toggle" text>
          Log in
        </n-button>
      </template>
      <n-space vertical>
          <n-space>
            {{ whetherlogin ? 'Please Log in' : 'Please Register' }}
            <n-icon size="25" color="#0e7a0d" :component="GameController"/>
          </n-space>
        <n-input v-model:value="username" placeholder="Username">
          <template #prefix>
            <n-icon :component="Server24Filled" />
          </template>
        </n-input>
        <n-input v-if='whetherlogin' v-model:value="password" placeholder="Password">
          <template #prefix>
              <n-icon :component="TokenFilled" />
          </template>
        </n-input>
        <n-input v-else v-model:value="password" placeholder='Password'>
          <template #prefix>
            <n-icon :component="DocumentPageNumber24Filled" />
          </template>
        </n-input>
        <n-input v-if='!whetherlogin' v-model:value="confirmation" placeholder='Confirm Password'>
          <template #prefix>
            <n-icon :component="DocumentPageNumber24Filled" />
          </template>
        </n-input>
        <n-alert v-if="faillogin && whetherlogin" title="Error" type="error">
          Fail to Log in: {{ failError }}
        </n-alert>
        <n-alert v-if="faillogin && !whetherlogin" title="Error" type="error">
          Fail to Register: {{ failError }}
        </n-alert>
      </n-space>
      <template #action>
        <n-button v-if="whetherlogin" type="primary" @click="login">
          Log in
        </n-button>
        <n-button v-else type="primary" @click="register">
          Register
        </n-button>
      </template>
    </n-card>
  </form>
    <!-- <div>
      <div v-if="!loggedIn">
        <h2>Login</h2>
        <form @submit.prevent="login">
          <label>
            Username:
            <input type="username" v-model="username" />
          </label>
          <br />
          <label>
            Password:
            <input type="password" v-model="password" />
          </label>
          <br />
          <button type="submit">Login</button>
        </form>
        <br />
        <h2>Register</h2>
        <form @submit.prevent="register">
          <label>
            Username:
            <input type="username" v-model="username" />
          </label>
          <br />
          <label>
            Password:
            <input type="password" v-model="password" />
          </label>
          <br />
          <button type="submit">Register</button>
        </form>
      </div>
      <div v-else>
        <p>You are logged in!</p>
        <button @click="logout">Logout</button>
      </div>
    </div> -->
  </template>

<script setup>
import { NButton, NCard, NIcon, NAlert, NSpace, NInput, NInputNumber, NSwitch} from 'naive-ui'
import { GameControllerOutline, GameController } from '@vicons/ionicons5'
import { TokenFilled } from '@vicons/material'
import { Server24Filled, DocumentPageNumber24Filled} from '@vicons/fluent'
import axios from 'axios'
</script>

  <!-- <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        username: '',
        password: '',
        loggedIn: false,
      };
    },
    methods: {
      async login() {
        try {
          await axios.post('/login', { username: this.username, password: this.password });
          this.loggedIn = true;
          this.$emit('loggedIn', this.username)
        } catch (error) {
          console.error(error);
        }
      },
      async register() {
        try {
          await axios.post('/register', { username: this.username, password: this.password });
          this.loggedIn = true;
          this.$emit('loggedIn', this.username)
        } catch (error) {
          console.error(error);
        }
      },
      logout() {
        this.loggedIn = false;
      },
    },
  };
  </script> -->


<script>
export default {
  data() {
    return {
      whetherlogin: true,
      username: '',
      password: '',
      confirmation: '',
      loggedIn: false,
      failError: '',
      // server: 'https://quentain-server.onrender.com'
      server: 'http://127.0.0.1:5050'
    }
  },
  methods: {
    toggle() {
      this.whetherlogin = !this.whetherlogin
    },
    async login() {
        try {
          await axios.post(this.server +'/login', 
                          {username: this.username, password: this.password });
          this.loggedIn = true;
          this.$emit('loggedIn', this.username)
        } catch (error) {
          console.error(error);
          this.failError = error.response.data
        }
      },
      async register() {
        try {
          await axios.post(this.server +'/register', 
                  {username: this.username, 
                   password: this.password, 
                   confirmation: this.confirmation});
          this.loggedIn = true;
          this.$emit('loggedIn', this.username)
        } catch (error) {
          console.error(error);
          this.failError = error.response.data
        }
      },
      logout() {
        this.loggedIn = false;
      },
  },
  computed: {
    title() {
      return (this.whetherlogin) ? 'Login' : 'Register'
    },
    faillogin() {
      return this.failError !== ""
    }
  }
}
</script>
