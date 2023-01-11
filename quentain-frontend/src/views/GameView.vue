<script setup>
import 'vfonts/FiraSans.css'
import 'vfonts/FiraCode.css'
import { NButton, NSpace, NIcon, NAlert, NCard, NModal} from 'naive-ui'
import { FistRaised } from '@vicons/fa'
import { PlayCard } from '@vicons/tabler'
import { Trophy16Filled } from '@vicons/fluent'
import axios from 'axios'
import config from '../../config'
</script>

<template>
  <div class="container">
    <div class="canvas">
      <img ref="pokerImg" :style="{display: 'none'}" src='@/assets/deck.svg' />
      <canvas ref="canvas" width="2000" height="550" @click="onCanvasClick"></canvas>
    </div>
    <n-modal
      v-model:show="throwError"
      :mask-closable="false"
      preset="dialog"
      title="Unable to throw"
      :content="throwErrorContent"
      positive-text="Got it"
      @positive-click="throwError = false"
    />
    <n-modal
      v-model:show="finished"
      :mask-closable="false"
    >
      <n-card
        style="width: 600px"
        title="Game Finished"
        :bordered="false"
        size="huge"
        role="dialog"
        aria-modal="true"
      >
        <n-space>
          <n-icon size="25" color="#0e7a0d">
            <Trophy16Filled />
          </n-icon>
          Your rank: {{ rank }}
        </n-space>
        <template #footer>
          <n-button type="primary" @click="returnToIndex">
            Return to index
          </n-button>
        </template>
      </n-card>
    </n-modal>
    <div class="form">
      <n-space vertical>
      <n-alert v-if="showWarning" :title="alertTitle" :type="alertType">
        {{ alertContent }}..
      </n-alert>
      <n-space v-else align="center">
        <n-button strong secondary type="success" size="large" @click="throw_cards">
          <template #icon>
            <n-icon>
              <play-card v-if="selectSomething"/>
              <fist-raised v-else/>
            </n-icon>
          </template>
          {{ selectSomething ? 'Throw' : 'Pass'}}
        </n-button>
      </n-space>
      <n-button strong type="warning" @click="end_game">
            Quit (Return with token {{ token }})
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
const draw_y_bias = 105
const deck_x_offset = 320
const deck_y_offset = 345
const comp_y_offset = 170
const green = '#4db6ac'
const pink = '#ff69b4'
const turn_pos = [
  {x: 210, y: 450},
  {x: 1150, y: 160},
  {x: 500, y: 65},
  {x: 130, y: 160}
]

const color_map = {
  'Club': 0,
  'Diamond': 1,
  'Heart': 2,
  'Spade': 3
}

// get location from the poker deck asset 
// to correctly present a card
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
  props: {
    token: {
      type: String,
      required: true
    },
    player_id: {
      type: Number,
      required: true
    },
    server: {
      type: String,
      default: config.serverPath
    }
  },
  data() {
    return {
      deck: Array.from(
        {length: 28},
        () => ({ color: 'Cover', number: 17, selected: false})
      ),
      comp: [[], [], [], []],
      turn: 0,
      text: "turn",
      alertTitle: 'Game not ready',
      alertType: 'warning',
      alertContent: 'Waiting for others to join...',
      started: 0,
      finished: false,
      paused: 0,
      game: null,
      comp_pos : [
        {x: 320, y: 230},
        {x: 830, y: 200},
        {x: 320, y: 110},
        {x: 260, y: 200}
      ],
      pass_pos: [
        {x: 630, y: 320},
        {x: 1000, y: 250},
        {x: 630, y: 150},
        {x: 270, y: 250}
      ],
      playerStarted: [false, false, false, false],
      playerFinished: [false, false, false, false],
      rank: -1,
      throwError: false,
      throwErrorContent: '',
      intervalId : null,
      firstLoad: true
    }
  },
  methods: {
    returnToIndex() {
      this.reset()
      this.$emit('returnIndex')
    },
    onCanvasClick(event) {
      const canvas = this.$refs.canvas
      const rect = canvas.getBoundingClientRect()
      const x = event.clientX - rect.left
      const y = event.clientY - rect.top
      // Check if the mouse is clicked on a certain card
      this.deck.forEach((region, index) => {
        if (x >= region.draw_x && x <= region.draw_x + draw_x_bias && y >= region.draw_y && y <= region.draw_y + draw_height) {
          region.selected = ! region.selected
          this.redraw_canvas()
        }
      })
    },
    redraw_canvas() {
      const canvas = this.$refs.canvas
      const ctx = canvas.getContext('2d')
      const image = this.$refs.pokerImg

      function draw_deck() {
        // Clear the canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        let deck_offsetX = deck_x_offset
        let deck_offsetY = deck_y_offset
        if (this.deck.length < 14) {
          deck_offsetX += (14 - this.deck.length) / 2 * draw_x_bias
          deck_offsetY += 20
        }

        // draw deck for user
        this.deck.forEach((region, index) => {
          // Draw the image
          draw_card(region, index, deck_offsetX, deck_offsetY)
        })

        // draw the card covers for other users
        draw_cover(580, 10)
        draw_cover(80, 200)
        draw_cover(1100, 200)

        // draw the thrown comps
        for (let i = 0; i < 4; i++) {
          let j = this.get_visual_idx(i)
          if (this.comp[i] === null) {
            continue
          }
          let comp_offsetX = this.comp_pos[j].x
          if (j === 2 || j === 0) {
            comp_offsetX += (14 - this.comp[i].length) / 2 * draw_x_bias
          }
          if (j === 1) {
            comp_offsetX += (5 - this.comp[i].length) * draw_x_bias
          }
          let comp_offsetY = this.comp_pos[j].y
          this.comp[i].forEach((region, index) => {
            draw_card(region, index, comp_offsetX, comp_offsetY)
          })

          // if no comp is thrown, draw a pass sign
          if (this.comp[i].length === 0 && !this.playerFinished[i]) {
            ctx.fillStyle = green

            // draw the rectangle
            ctx.fillRect(this.pass_pos[j].x - 4, this.pass_pos[j].y - 22, 65, 28)

            // draw the pass text
            ctx.fillStyle = "#f8f8f8"
            ctx.font = "bold 24px v-mono"
            ctx.fillText('pass', this.pass_pos[j].x, this.pass_pos[j].y)
          }

          if (this.playerFinished[i]) {
            ctx.fillStyle = 'orange'

            // draw the rectangle
            ctx.fillRect(this.pass_pos[j].x - 4, this.pass_pos[j].y - 22, 65, 28)

            // draw the pass text
            ctx.fillStyle = "#f8f8f8"
            ctx.font = "bold 24px v-mono"
            ctx.fillText('done', this.pass_pos[j].x, this.pass_pos[j].y)
          }
        }

        // draw turn sign
        let visual_idx = (this.turn + 4 - this.player_id) % 4
        ctx.fillStyle = pink

        // draw the rectangle
        ctx.fillRect(turn_pos[visual_idx].x - 4, turn_pos[visual_idx].y - 22, 65, 28)

        // draw the turn text
        ctx.fillStyle = "#f8f8f8"
        ctx.shadowBlur = 0
        ctx.shadowColor = 'rgba(0, 0, 0, 0)'
        ctx.shadowOffsetX = 0
        ctx.shadowOffsetY = 0
        ctx.font = "bold 24px v-mono"
        ctx.fillText('turn', turn_pos[visual_idx].x, turn_pos[visual_idx].y)
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
      console.log('draw_deck')
      if (this.firstLoad) {
        image.onload = () => {
          draw_deck()
          this.firstLoad = false
        }
      } else {
        draw_deck()
      }

      // add click events
      // function onClick(event, region, index) {
      //   const rect = canvas.getBoundingClientRect()
      //   const x = event.clientX - rect.left
      //   const y = event.clientY - rect.top
      //   // Check if the mouse is over the image
      //   if (x >= region.draw_x && x <= region.draw_x + draw_x_bias && y >= region.draw_y && y <= region.draw_y + draw_height) {
      //     region.selected = ! region.selected
      //     draw_deck()
      //   }
      // }
      // const boundOnClick = onClick.bind(this)
      // if (this.turn === this.player_id) {
      //   this.deck.forEach((region, index) => {
      //       canvas.addEventListener('click', event => boundOnClick(event, region, index))
      //   })
      // }
    },
    throw_cards(event) {
      if (this.turn === this.player_id) {
        let choices = []
        if (event.target.textContent != 'pass') {
          this.deck.forEach((card, index) => {
            if (card.selected) {
              choices.push(index)
            }
          })
        }
        axios.post(this.server + '/throw_comp/' + this.token, {
          player_number: this.player_id,
          choices: choices
        }).then(response => {
          let game = response.data
          this.deck = game.deck
          this.comp = game.player_comp
          this.turn = game.turn
          this.redraw_canvas()
        }).catch(error => {
          this.throwError = true
          this.throwErrorContent = error.response.data.error
        })
      }
    },
    async end_game() {
      try {
        const response = await axios.post(this.server + '/end_game/' + this.token,
                        {token:this.token});               
        this.endGame = true;
        this.$emit('endGame');
      } catch (error) {
        console.error(error);
      }
    },
    get_visual_idx(idx) {
      return (idx + 4 - this.player_id) % 4
    },
    reset() {
      clearInterval(this.intervalId)
      this.deck = Array.from(
        {length: 28},
        () => ({ color: 'Cover', number: 17, selected: false})
      ),
      this.comp = [[], [], [], []],
      this.turn = 0,
      this.text = "turn",
      this.alertTitle =  'Game not ready',
      this.alertType = 'warning',
      this.alertContent = 'Waiting for others to join...',
      this.started = 0,
      this.finished = false,
      this.game = null,
      this.playerStarted = [false, false, false, false],
      this.playerFinished = [false, false, false, false],
      this.rank = -1,
      this.throwError = false,
      this.throwErrorContent = ''
      this.intervalId = null
    }
  },
  computed: {
    showWarning() {
      return (!this.started || this.turn !== this.player_id)
    },
    formMarginLeft() {
      return (!this.started || this.turn !== this.player_id) ? "27%" : "30%"
    },
    selectSomething() {
      let flag = false;
      this.deck.forEach(item => {
        if (item.selected) {
          flag = true;
        }
      })
      return flag
    }
  },
  watch: {
    turn: {
      handler() {
        if (!this.finished && this.started && this.turn !== this.player_id && this.paused === 0) {
          if (this.started) {
            this.alertTitle = 'Unable to throw'
            this.alertContent = 'It\'s not your turn yet'
          }
          // setInterval(() => {
          //   axios.get(
          //     'http://localhost:5050/get_player_game_state/' + this.token + '/' + this.player_id
          //   ).then(response => {
          //     let game = response.data
          //     this.finished = game.finished
          //     if (game.finished) {
          //       this.rank = game.rank[this.player_id]
          //     }
          //     if (game.started !== this.started) {
          //       this.deck = game.deck
          //       this.comp = game.player_comp
          //       this.turn = game.turn
          //       this.started = game.started
          //       game.finished_players.forEach(id => {
          //         this.playerFinished[id] = true
          //       })
          //       this.redraw_canvas()
          //     } else if (game.turn !== this.turn) {
          //       this.comp = game.player_comp
          //       this.turn = game.turn
          //       game.finished_players.forEach(id => {
          //         this.playerFinished[id] = true
          //       })
          //       console.log(this.playerFinished)
          //       this.redraw_canvas()
          //     }
          //   }).catch(error => {
          //     // console.log(error)
          //   })
          // }, 4000)
        }
      },
      immediate: true,
    }
  },
  mounted() {
    this.redraw_canvas()
    this.intervalId = setInterval(() => {
      axios.get(
        this.server + '/get_player_game_state/' + this.token + '/' + this.player_id
      ).then(response => {
        let game = response.data
        this.finished = game.finished
        if (game.finished) {
          this.rank = game.rank[this.player_id]
        }
        if (game.started !== this.started) {
          this.alertTitle = 'Unable to throw'
          this.alertContent = 'It\'s not your turn yet'
          this.deck = game.deck
          console.log(this.deck)
          this.comp = game.player_comp
          this.turn = game.turn
          this.started = game.started
          game.finished_players.forEach(id => {
            this.playerFinished[id] = true
          })
          this.redraw_canvas()
        } else if (game.turn !== this.turn) {
          this.comp = game.player_comp
          this.turn = game.turn
          game.finished_players.forEach(id => {
            this.playerFinished[id] = true
          })
          this.redraw_canvas()
        }
      }).catch(error => {
        // console.log(error)
      })
    }, 4000)
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
    margin-left: v-bind('formMarginLeft');
    margin-bottom: 3%;
    align-items: center;
  }
  
  .container {
    margin-top: 2%;
  }
}
</style>
