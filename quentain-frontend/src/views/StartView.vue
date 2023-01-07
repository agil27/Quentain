<script setup lang="ts">
import { NButton, NCard, NIcon, NSpace, NInput} from 'naive-ui'
import { GameControllerOutline, GameController } from '@vicons/ionicons5'
import { TokenFilled } from '@vicons/material'
</script>

<template>
  <n-card style="margin-left: 35%" size="huge" hoverable
    title="Join a game room"
    :segmented="{
      content: true,
      footer: 'soft'
    }"
  >
    <n-space vertical>
      <n-space>
        Please enter a token number to join a game room
        <n-icon size="25" color="#0e7a0d">
          <game-controller />
        </n-icon>
      </n-space>
      <n-input placeholder="Token">
        <template #prefix>
          <n-icon :component="TokenFilled" />
        </template>
      </n-input>
    </n-space>
    <template #action>
      <n-button type="primary">
        Join Now!
      </n-button>
    </template>
  </n-card>
</template>