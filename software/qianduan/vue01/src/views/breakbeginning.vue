<template>
  <button class="login-button" @click="goLogin">退出登录</button>
  <!-- <button class="back-button" @click="goBack">←返回训练计划</button> -->
  <div class="break-container">
    <!-- 左侧倒计时区域 -->
    <div class="timer-box">
      <h2>倒计时</h2>
      <p class="time">{{ minutes }}:{{ seconds < 10 ? '0' + seconds : seconds }}</p>
    </div>

    <!-- 右侧文本与按钮区域 -->
    <div class="message-box">
      <h1 class="message">你做得很好！</h1>
      <p class="sub-message">我们可以休息两分钟，或者现在就开始训练</p>
      <button class="start-btn" @click="goToTraining">现在开始</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BreakMiddle',
  data() {
    return {
      remainingTime: 120, // 2分钟倒计时（单位：秒）
      timer: null
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
    goBack() {
    this.$router.push({ path: "/trainingplan" });
  },
    startCountdown() {
  this.timer = setInterval(() => {
    if (this.remainingTime > 0) {
      this.remainingTime--;
    } else {
      clearInterval(this.timer);
    }
    if (this.remainingTime === 0) {
      const query = this.$route.query;
      if (query.custom === 'true' && query.plan) {
        this.$router.push({
          path: '/training',
          query: {
            custom: 'true',
            plan: query.plan
          }
        });
      } else {
        this.$router.push({ path: '/training' });
      }
    }
  }, 1000);
},
    goToTraining() {
  clearInterval(this.timer);
  const query = this.$route.query;
  if (query.custom === 'true' && query.plan) {
    this.$router.push({
      path: '/training',
      query: {
        custom: 'true',
        plan: query.plan
      }
    });
  } else {
    this.$router.push({ path: '/training' });
  }
},
goLogin() {
      this.$router.push({ path: "/" });
    },

  }
}
</script>

<style scoped>
.back-button {
  position: fixed;
  top: 20px;
  left: 20px;
  background: transparent;
  border: none;
  font-size: 24px;
  color: #e31111;
  cursor: pointer;
  user-select: none;
  z-index: 100;

  padding: 0;
  margin: 0;
  line-height: 1;
  width: auto;
  height: auto;
  display: inline-block;
}

.back-button:hover {
  text-decoration: underline; 
}

.login-button {
  position: fixed;
  top: 20px;
  right: 20px;
  background: transparent;
  border: none;
  font-size: 24px;
  color: #e31111;
  cursor: pointer;
  user-select: none;
  z-index: 100;

  padding: 0;
  margin: 0;
  line-height: 1;
  width: auto;
  height: auto;
  display: inline-block;

}

.login-button:hover {
  text-decoration: underline; 
}

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
  margin-bottom: 20px;
  white-space: pre-line;
}

.sub-message {
  font-size: 18px;
  margin-bottom: 30px;
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