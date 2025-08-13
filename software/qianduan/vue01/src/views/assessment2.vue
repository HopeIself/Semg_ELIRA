<template>
  <div class="assessment-container">
    <h1 class="title">肌肉状况评估</h1>

    <div class="content">
      <!-- 左边图片 -->
      <div class="left">
        <img :src="actions[currentActionIndex].image" class="exercise-image" />
        <p class="image-label">{{ actions[currentActionIndex].label }}</p>
      </div>

      <!-- 右边描述与状态 -->
      <div class="right">
        <!-- 初始状态 -->
        <div v-if="step === 0 || step === 6">
          <p class="description">{{ actions[currentActionIndex].description }}</p>
          <button class="btn" @click="startAction">开始</button>
        </div>

        <!-- 准备倒计时 -->
        <div v-else-if="step === 1 || step === 3">
          <p class="countdown-text">{{ countdown }} 秒后开始</p>
        </div>

        <!-- 测量倒计时 + 肌电值 -->
        <div v-else-if="step === 2 || step === 4">
          <p class="countdown-text">{{ countdown }} 秒后结束</p>
          <p class="emg-text">实时肌电值：{{ emgValue }}</p>
        </div>

        <!-- 显示“下一个动作”按钮 -->
        <div v-else-if="step === 10">
          <p class="description">{{ actions[1].description }}</p>
          <button class="btn" @click="startSecondAction">下一个动作</button>
        </div>

        <!-- 测评完成 -->
        <div v-else-if="step === 5">
          <button class="btn" @click="restart">重新评估</button>
          <button class="btn" @click="goToNext">下一步</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Assessment',
  data() {
    return {
      baseURL: 'http://115.190.134.66:5000',
      currentModel: '',
      step: 0,
      countdown: 3,
      emgValue: null,
      eventSource: null,
      intervalTimer: null,
      currentActionIndex: 0,
      actions: [
        {
          image: require('../assets/image1.jpg'),
          label: '动作1',
          description: '动作描述：\n保持屈臂，握拳张开\n准备好后可点击“开始”'
        },
        {
          image: require('../assets/image2.jpg'),
          label: '动作2',
          description: '动作描述：\n匀速弯曲手臂，同时握拳\n准备好后可点击“开始”'
        }
      ]
    }
  },
  created() {
    this.currentModel = localStorage.getItem('currentModel') || ''
    if (!this.currentModel) {
      this.$router.push({ name: 'AI choose' })
    }
  },
  beforeUnmount() {
    this.closeEventSource()
    clearInterval(this.intervalTimer)
  },
  methods: {
    startAction() {
      this.step = 1
      this.countdown = 3
      this.startCountdown(() => {
        this.step = 2
        this.countdown = 5
        this.connectSSE()
        this.startCountdown(() => {
          this.closeEventSource()
          this.currentActionIndex = 1
          this.step = 10 // 进入等待“下一个动作”按钮
        })
      })
    },
    startSecondAction() {
      this.currentActionIndex = 1
      this.step = 3
      this.countdown = 3
      this.startCountdown(() => {
        this.step = 4
        this.countdown = 5
        this.connectSSE()
        this.startCountdown(() => {
          this.closeEventSource()
          this.step = 5
        })
      })
    },
    startCountdown(callback) {
      this.intervalTimer = setInterval(() => {
        if (this.countdown > 1) {
          this.countdown--
        } else {
          clearInterval(this.intervalTimer)
          callback()
        }
      }, 1000)
    },
    restart() {
      this.step = 0
      this.currentActionIndex = 0
      this.emgValue = null
    },
    connectSSE() {
      const id = localStorage.getItem('id')
      if (!id || id === 'null') return

      this.emgValue = null
      this.eventSource = new EventSource(`${this.baseURL}/api/initial-assessment?id=${encodeURIComponent(id)}`)

      this.eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (data.emg_value !== undefined) {
            this.emgValue = data.emg_value
          }
        } catch (e) {
          console.error('解析数据失败:', e)
        }
      }

      this.eventSource.onerror = (err) => {
        console.error('连接出错:', err)
        this.closeEventSource()
      }
    },
    closeEventSource() {
      if (this.eventSource) {
        this.eventSource.close()
        this.eventSource = null
      }
    },
    goToNext() {
      this.$router.push({ path: '/generatingreport' })
    }
  },
  mounted() {
    // 挂载 Coze Web Chat
    const script = document.createElement('script')
    script.src = "https://lf-cdn.coze.cn/obj/unpkg/flow-platform/chat-app-sdk/1.2.0-beta.10/libs/cn/index.js"
    script.onload = () => {
      new CozeWebSDK.WebChatClient({
        config: { bot_id: '7526864409868976143' },
        componentProps: { title: 'Coze' },
        auth: {
          type: 'token',
          token: 'pat_pOwdWuNOdyj47fbSnmTR0EKWlezCrzQebx0VjeYJuNmZNAlF48EKBQZEDRK6W3ys',
          onRefreshToken: () => 'pat_pOwdWuNOdyj47fbSnmTR0EKWlezCrzQebx0VjeYJuNmZNAlF48EKBQZEDRK6W3ys'
        }
      })
    }
    document.body.appendChild(script)
  },
}
</script>

<style scoped>
.assessment-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

.title {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 30px;
}

.content {
  display: flex;
  justify-content: center;
  width: 100%;
}

.left {
  flex: 1;
  text-align: center;
}

.exercise-image {
  width: 300px;
  height: auto;
}

.image-label {
  margin-top: 10px;
  font-weight: bold;
}

.right {
  flex: 1;
  padding-left: 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.description {
  font-size: 18px;
  line-height: 1.8;
  white-space: pre-line;
}

.countdown-text {
  font-size: 24px;
  font-weight: bold;
  color: #ff6600;
  margin-bottom: 20px;
}

.emg-text {
  font-size: 18px;
  margin-top: 10px;
}

.btn {
  margin-top: 20px;
  padding: 10px 20px;
  font-size: 18px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.btn:hover {
  background-color: #337ab7;
}
</style>