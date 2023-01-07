<script setup>
</script>

<template>
  <div class="canvas">
    <canvas ref="canvas" width="2000" height="400"></canvas>
  </div>
</template>

<script>
let card_width = 202.5
let card_height = 315
let draw_width = 80
let draw_height = 120
let draw_x_bias = 60
let draw_y_bias = 150

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
    // 15, 16, 17: black joker, red joker, cover
    x = (number - 15) * card_width
    y = 4 * card_height
  }
  return [x, y]
}

export default {
  name: 'MyCanvas',
  data() {
    return {
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
        { color: 'Cover', number: 17, selected: false},
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
        { color: 'Cover', number: 17, selected: false},
        { color: 'Diamond', number: 13, selected: false},
        { color: 'Club', number: 2, selected: false},
        { color: 'Diamond', number: 12, selected: false},
        { color: 'Heart', number: 11, selected: false},
        { color: 'Spade', number: 7, selected: false},
        { color: 'Joker', number: 15, selected: false}
      ]
    }
  },
  mounted() {
    const canvas = this.$refs.canvas
    const ctx = canvas.getContext('2d')
    const image = new Image()
    image.src = 'src/assets/deck.svg'
    ctx.shadowColor = 'rgba(0, 0, 0, 0.5)'
    ctx.shadowBlur = 8
    ctx.shadowOffsetX = -8
    ctx.shadowOffsetY = 4
    ctx.class = 'deck'

    function draw_deck() {
      // Clear the canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      this.items.forEach((region, index) => {
        // Draw the image
        draw_card(region, index)
      })
    }
    
    function draw_card(region, index) {
      let coord = get_location(region.color, region.number)
      region.x = coord[0]
      region.y = coord[1]

      let row = parseInt(index / 14)
      let col = index % 14

      region.draw_x = col * draw_x_bias
      region.draw_y = 30 + row * draw_y_bias
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
    margin: 12% 0% 0% 10%;
    min-height: 100vh;
    display: flex;
    align-items: center;
  }
}
</style>
