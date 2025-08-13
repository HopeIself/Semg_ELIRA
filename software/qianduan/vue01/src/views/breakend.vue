<template>
  <div class="break-container">
    <!-- 左侧倒计时区域 -->
    <div class="timer-box">
      <h2>倒计时</h2>
      <p class="time">{{ minutes }}:{{ seconds < 10 ? '0' + seconds : seconds }}</p>
    </div>

    <!-- 右侧文本与按钮区域 -->
    <div class="message-box">
      <h1 class="message">请休息一分钟，随后开始肌肉状态评估</h1>
      <button class="start-btn" @click="goToAssessment">开始评估</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BreakEnd',
  data() {
    return {
      remainingTime: 60, // 1分钟倒计时
      timer: null,
    }
  },
  computed: {
    minutes() {
      return Math.floor(this.remainingTime / 60)
    },
    seconds() {
      return this.remainingTime % 60
    }
  },
  mounted() {
    this.startCountdown()
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
  beforeUnmount() {
    clearInterval(this.timer)
  },
  methods: {
    startCountdown() {
      this.timer = setInterval(() => {
        if (this.remainingTime > 0) {
          this.remainingTime--
        } else {
          clearInterval(this.timer)
          this.goToAssessment()
        }
      }, 1000)
    },
    goToAssessment() {
      clearInterval(this.timer)
      this.$router.push({ path: '/assessment', query: { from: 'breakend' } });
    }
  }
}
</script>

<style scoped>
.break-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 50px;
  font-family: "Microsoft YaHei", sans-serif;
  max-width: 900px;
  margin: auto;
}

.timer-box {
  flex: 1;
  text-align: center;
  border-right: 2px solid #ccc;
  padding-right: 40px;
}

.timer-box h2 {
  font-size: 24px;
  margin-bottom: 10px;
}

.time {
  font-size: 48px;
  font-weight: bold;
  color: #ff6600;
}

.message-box {
  flex: 2;
  padding-left: 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
}

.message {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 30px;
  white-space: pre-line;
}

.start-btn {
  padding: 12px 28px;
  font-size: 18px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.start-btn:hover {
  background-color: #318ce7;
}
</style>