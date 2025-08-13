<template>
  <button class="login-button" @click="goLogin">退出登录</button>

  <div class="training-container">
    <h1 class="title">训练动作执行</h1>

    <div class="content">
      <div class="left">
        <img :src="currentAction.image" class="exercise-image" />
        <p class="image-label">{{ currentAction.label }}</p>
      </div>

      <div class="right">
        <p class="description">{{ currentAction.description }}</p>

        <!-- 训练前准备阶段 -->
        <div v-if="step === 'prepare'">
          <p class="countdown-text">5 秒后开始：{{ countdown }}</p>
        </div>

        <!-- 正在训练阶段 -->
        <div v-else-if="step === 'training'">
          <p class="countdown-text">倒计时：{{ countdown }} 秒</p>
          <p class="group-status">当前组数：{{ currentGroup }}/3</p>
          <button class="btn" @click="handleNext">
            {{ currentGroup === 3 ? (currentIndex < actions.length - 1 ? '动作间休息' : '下一步') : '下一组' }}
          </button>
        </div>

        <!-- 动作间休息阶段 -->
        <div v-else-if="step === 'rest'">
          <p class="countdown-text">动作间休息 {{ countdown }} 秒</p>
          <button class="btn" @click="endRest">下一个动作</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Training',
  data() {
    return {
      actions: [],
      currentIndex: 0,
      currentGroup: 1,
      countdown: 5,
      intervalTimer: null,
      step: 'prepare'
    };
  },
  computed: {
    currentAction() {
      return this.actions[this.currentIndex];
    }
  },
  created() {
    const query = this.$route.query;

    if (query.custom === 'true' && query.plan) {
      try {
        const plan = JSON.parse(query.plan);
        this.actions = plan.map(item => ({
          image: item.img,
          label: item.label || '自定义动作',
          description: item.description || '无描述',
          groupCount: item.groupCount || 3
        }));
      } catch (err) {
        console.error('解析自定义计划失败：', err);
        this.setDefaultActions();
      }
    } else {
      this.setDefaultActions();
    }
  },
  mounted() {
    if (this.actions.length === 0) return;
    this.startCountdown(5, () => {
      this.step = 'training';
      this.startCountdown(15, this.onTrainingFinish);
    });
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
    clearInterval(this.intervalTimer);
  },
  methods: {
    goLogin() {
      this.$router.push({ path: "/" });
    },
    setDefaultActions() {
      this.actions = [
        {
          image: require('../assets/image2.jpg'),
          label: '动作1',
          description: '动作描述：\n手掌翻转 3组，每组15秒',
          groupCount: 3
        },
        {
          image: require('../assets/image3.jpg'),
          label: '动作2',
          description: '动作描述：\n腕屈曲 3组，每组15秒',
          groupCount: 3
        },
        {
          image: require('../assets/image4.jpg'),
          label: '动作3',
          description: '动作描述：\n腕伸展 3组，每组15秒',
          groupCount: 3
        }
      ];
    },
    startCountdown(seconds, nextStep = null) {
      this.countdown = seconds;
      clearInterval(this.intervalTimer);
      this.intervalTimer = setInterval(() => {
        if (this.countdown > 1) {
          this.countdown--;
        } else {
          clearInterval(this.intervalTimer);
          if (nextStep) nextStep();
        }
      }, 1000);
    },
    handleNext() {
      this.onTrainingFinish();
    },
    onTrainingFinish() {
      const currentTotalGroup = this.currentAction.groupCount || 3;

      if (this.currentGroup < currentTotalGroup) {
        this.currentGroup++;
        this.startCountdown(15, this.onTrainingFinish);
      } else {
        if (this.currentIndex < this.actions.length - 1) {
          this.step = 'rest';
          this.startCountdown(20, this.onRestFinish);
        } else {
          this.$router.push('/breakend');
        }
      }
    },
    endRest() {
      this.onRestFinish();
    },
    onRestFinish() {
      this.currentIndex++;
      this.currentGroup = 1;
      this.step = 'training';
      this.startCountdown(15, this.onTrainingFinish);
    }
  }
};
</script>

<style scoped>
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

.training-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px;
  font-family: "Microsoft YaHei", sans-serif;
}

.title {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 30px;
}

.content {
  display: flex;
  width: 100%;
  max-width: 900px;
  justify-content: center;
}

.left {
  flex: 1;
  text-align: center;
}

.exercise-image {
  width: 300px;
  height: auto;
  border-radius: 10px;
  border: 1px solid #ccc;
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
  line-height: 1.6;
  white-space: pre-line;
}

.countdown-text {
  font-size: 24px;
  font-weight: bold;
  color: #ff6600;
  margin: 20px 0;
}

.group-status {
  font-size: 18px;
  margin-bottom: 15px;
}

.btn {
  margin-top: 20px;
  padding: 10px 24px;
  font-size: 18px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.btn:hover {
  background-color: #318ce7;
}
</style>
