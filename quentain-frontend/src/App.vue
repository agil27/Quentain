<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'
import 'vfonts/FiraSans.css'
import 'vfonts/FiraCode.css'
</script>

<template>
  <nav>
    <div class="logo">
      <img class="logoimg" src="@/assets/logo.svg" alt="Logo" height="50">
      <p class="name"> QUENTAIN</p>
    </div>
    <ul>
      <li>
        <RouterLink class="navlink" to="/">Join a game</RouterLink>
        <RouterLink class="navlink" to="/game">Game Room</RouterLink>
      </li>
    </ul>
  </nav>
  <RouterView />
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  data() {
    return {
    }
  },
})
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

nav a.router-link-exact-active:hover {
  color: #6b2d92;
  background-color: #f8f8f8;
}

nav a.router-link-exact-active {
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

