<script setup>
import 'vfonts/FiraSans.css'
import 'vfonts/FiraCode.css'
import { NButton, NSpace, NIcon, NAlert} from 'naive-ui'
import { FistRaised } from '@vicons/fa'
import { PlayCard } from '@vicons/tabler'
</script>

<template>
  <div class="container">
    <div class="canvas">
      <canvas ref="canvas" width="2000" height="550"></canvas>
    </div>
    <div class="form">
      <n-alert v-if="(this.num_players < 4)" title="Game Not Ready" type="warning">
        Waiting for {{4 - this.num_players}} to join...
      </n-alert>
      <n-space v-else align="center">
        <n-button strong secondary type="warning" size="large">
          <template #icon>
            <n-icon>
              <play-card />
            </n-icon>
          </template>
          Throw
        </n-button>
        <n-button strong secondary type="success" size="large">
          <template #icon>
            <n-icon>
              <fist-raised />
            </n-icon>
          </template>
          Pass
        </n-button>
      </n-space>
    </div>
  </div>
</template>

<script>
const card_width = 202.5
const card_height = 315
const draw_width = 64
const draw_height = 96
const draw_x_bias = 48
const draw_y_bias = 120
const deck_x_offset = 320
const deck_y_offset = 320
const comp_y_offset = 170

const turn_pos = [
  {x: 630, y: 300},
  {x: 1000, y: 250},
  {x: 630, y: 140},
  {x: 270, y: 250}
]

let color_map = {
  'Club': 0,
  'Diamond': 1,
  'Heart': 2,
  'Spade': 3
}

function get_location(color, number) {
  let x, y
  if (number >= 1 && number <= 13) {
    x = (number - 1) * card_width
    y = color_map[color] * card_height
  } else {
    // 15, 16, 17, 18 black joker, red joker, cover, blank
    x = (number - 15) * card_width
    y = 4 * card_height
  }
  return [x, y]
}

export default {
  name: 'MyCanvas',
  data() {
    return {
      num_players: 4,
      items: [
        { color: 'Heart', number: 11, selected: false},
        { color: 'Spade', number: 1, selected: false},
        { color: 'Club', number: 2, selected: false},
        { color: 'Diamond', number: 13, selected: false},
        { color: 'Club', number: 2, selected: false},
        { color: 'Diamond', number: 12, selected: false},
        { color: 'Heart', number: 11, selected: false},
        { color: 'Spade', number: 7, selected: false},
        { color: 'Joker', number: 15, selected: false},
        { color: 'Joker', number: 16, selected: false},
        { color: 'Joker', number: 16, selected: false},
        { color: 'Heart', number: 11, selected: false},
        { color: 'Spade', number: 1, selected: false},
        { color: 'Club', number: 2, selected: false},
        { color: 'Diamond', number: 13, selected: false},
        { color: 'Club', number: 2, selected: false},
        { color: 'Diamond', number: 12, selected: false},
        { color: 'Heart', number: 11, selected: false},
        { color: 'Spade', number: 7, selected: false},
        { color: 'Joker', number: 15, selected: false},
        { color: 'Joker', number: 16, selected: false},
        { color: 'Diamond', number: 10, selected: false},
        { color: 'Diamond', number: 13, selected: false},
        { color: 'Club', number: 2, selected: false},
        { color: 'Diamond', number: 12, selected: false},
        { color: 'Heart', number: 13, selected: false},
        { color: 'Spade', number: 7, selected: false},
        { color: 'Joker', number: 15, selected: false}
      ],
      comp: [
        { color: 'Heart', number: 1, selected: false},
        { color: 'Spade', number: 7, selected: false},
        { color: 'Joker', number: 15, selected: false},
        { color: 'Joker', number: 16, selected: false},
      ],
      player_index: 0,
      turn: 3,
      text: "pass"
    }
  },
  computed: {
    margin() {
      return this.num_players < 4 ? "20%" : "28%"
    }
  },
  mounted() {
    const canvas = this.$refs.canvas
    const ctx = canvas.getContext('2d')
    const image = new Image()
    image.src = 'src/assets/deck.svg'

    function draw_deck() {
      // Clear the canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      let deck_offsetX = deck_x_offset
      let deck_offsetY = deck_y_offset
      if (this.items.length < 14) {
        deck_offsetX += (14 - this.items.length) / 2 * draw_x_bias
        deck_offsetY += 20
      }

      let comp_offsetX = deck_x_offset + (14 - this.comp.length) / 2 * draw_x_bias
      let comp_offsetY = comp_y_offset

      // draw deck for user
      this.items.forEach((region, index) => {
        // Draw the image
        draw_card(region, index, deck_offsetX, deck_offsetY)
      })

      // draw the card covers for other users
      draw_cover(580, 10)
      draw_cover(80, 200)
      draw_cover(1100, 200)

      // draw the thrown comp in the middle
      this.comp.forEach((region, index) => {
        draw_card(region, index, comp_offsetX, comp_offsetY)
      })

      // draw turn sign
      let visual_idx = (this.turn + this.player_index) % 4
      if (this.text === "pass") {
        ctx.fillStyle = '#4db6ac'
      } else {
        ctx.fillStyle = '#ff69b4'
      }

      // draw the rectangle
      ctx.fillRect(turn_pos[visual_idx].x - 4, turn_pos[visual_idx].y - 22, 65, 28)

      // draw the turn text
      ctx.fillStyle = "#f8f8f8"
      ctx.shadowBlur = 0
      ctx.shadowColor = 'rgba(0, 0, 0, 0)'
      ctx.shadowOffsetX = 0
      ctx.shadowOffsetY = 0
      ctx.font = "bold 24px v-mono"
      ctx.fillText(this.text, turn_pos[visual_idx].x, turn_pos[visual_idx].y)
    }

    function draw_cover(x, y) {
      ctx.shadowColor = 'rgba(0, 0, 0, 0.5)'
      ctx.shadowBlur = 4
      ctx.shadowOffsetX = -4
      ctx.shadowOffsetY = 2
      ctx.class = 'deck'
      let coord = get_location('Cover', 17)
      for (let i = 0; i < 7; i++) {
        ctx.drawImage(
          image, coord[0], coord[1], card_width, card_height,
          x + i * draw_x_bias / 3, y, draw_width, draw_height
        )
      }
    }

    function draw_card(region, index, offsetX, offsetY) {
      ctx.shadowColor = 'rgba(0, 0, 0, 0.5)'
      ctx.shadowBlur = 8
      ctx.shadowOffsetX = -8
      ctx.shadowOffsetY = 4
      ctx.class = 'deck'
      let coord = get_location(region.color, region.number)
      region.x = coord[0]
      region.y = coord[1]

      let row = parseInt(index / 14)
      let col = index % 14

      region.draw_x = offsetX + col * draw_x_bias
      region.draw_y = offsetY + row * draw_y_bias
      if (region.selected) {
        region.draw_y -= 20
      }

      ctx.drawImage(image,
        // Source x and y
        region.x, region.y,
        // Source width and height
        card_width, card_height,
        // Destination x and y
        region.draw_x, region.draw_y,
        // Destination width and height
        draw_width, draw_height
      )
    }

    draw_deck = draw_deck.bind(this)
    image.onload = () => {
      draw_deck()
    }

    // add click events
    function onClick(event, region, index) {
      const rect = canvas.getBoundingClientRect()
      const x = event.clientX - rect.left
      const y = event.clientY - rect.top
      // Check if the mouse is over the image
      if (x >= region.draw_x && x <= region.draw_x + draw_x_bias && y >= region.draw_y && y <= region.draw_y + draw_height) {
        region.selected = ! region.selected
        draw_deck()
      }
    }
    const boundOnClick = onClick.bind(this)
    this.items.forEach((region, index) => {
      canvas.addEventListener('click', event => boundOnClick(event, region, index))
    })
  }
}
</script>

<style>
@media (min-width: 1024px) {
  .canvas {
    margin-left: 0;
    margin-top: 0;
    margin-bottom: 1%;
    display: flex;
    align-items: center;
  }

  .form {
    display: flex;
    margin-top: 0;
    margin-left: 28%;
    margin-bottom: 3%;
    align-items: center;
  }
  
  .container {
    margin-top: 2%;
  }
}
</style>
