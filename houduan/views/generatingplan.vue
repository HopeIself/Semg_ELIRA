<template>
  <div class="container">
    <button class="back-button" @click="goBack">返回方案选择</button>
    <button class="login-button" @click="goLogin">退出登录</button>
    <!-- 生成按钮居中 -->
    <div class="button-group-top">
      <button @click="startGeneration" :disabled="assessing" class="generate-btn">
        个性化训练计划
      </button>
    </div>

    <!-- 进度条 -->
    <div v-if="assessing" class="progress-bar-container">
      <div class="progress-bar" :style="{ width: progress + '%' }">
        <span class="progress-percent">{{ progress }}%</span>
      </div>
    </div>

    <!-- 计划展示 -->
    <div v-if="plan" class="plan-display">
      <h2>生成的AI训练计划</h2>
      <div class="plan-content" v-html="formattedMessage"></div>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-msg">
      错误：{{ error }}
    </div>

    <!-- 固定右下角的跳转按钮 -->
    <div class="button-bottom-right">
      <button @click="goToAITrainingPlan" class="next-btn">开始训练</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      assessing: false,
      progress: 0,
      plan: null,
      pendingPlan: null, // 存储等待展示的AI计划
      error: null,
      noSignalTimeout: null,
      toast: {
        show: false,
        message: '',
        type: 'success',
      },
    };
  },
  computed: {
    formattedPlan() {
      if (!this.plan) return '';
      if (typeof this.plan === 'string') return this.plan;
      return JSON.stringify(this.plan, null, 2);
    },
    formattedMessage() {
      if (!this.plan || !this.plan.message) return '';

      const keywords = [
        "康复计划", "握拳与打开手掌", "手掌翻转", "腕屈曲", "腕伸展","压手",
        "重复", "肌肉", "每组","次","秒",
        "耐力", "放松", "疼痛",
        "1","2","3","4","5","6","7","8","9","10",
        "11","12","13","14","15","16","17","18","19","20",
      ];

      let msg = this.plan.message;
      keywords.forEach(word => {
        const regex = new RegExp(word, 'g');
        msg = msg.replace(regex, `<strong>${word}</strong>`);
      });
      
      // 每一段落前加上两个全角空格（　）
      msg = msg.replace(/(^|\n)/g, '$1　　');  // 段落缩进（中文习惯）

      return msg;
    }
  },
  methods: {
    goBack() {
      this.$router.push({ path: "/planchoose" });
    },
    goLogin() {
      this.$router.push({ path: "/" });
    },
    goToAITrainingPlan() {
  if (this.plan) {
    this.$router.push({
      path: '/AItrainingplan',
      query: {
        custom: 'true',
        plan: JSON.stringify(this.plan)
      }
    });
  } else {
    this.$router.push({ path: '/AItrainingplan' }); // 默认计划
  }
},

    async startGeneration() {
      if (this.assessing) return;

      const userId = localStorage.getItem('id');
      if (!userId || userId === 'null') {
        this.showToast('未找到用户ID，请重新登录', 'error');
        return;
      }

      // 语音播报“开始生成”按钮的功能描述
      // this.playTextAudio("正在生成AI计划，稍等片刻。");

      this.plan = null;
      this.pendingPlan = null;
      this.error = null;
      this.progress = 0;
      this.assessing = true;

      // 超时提示（用于后端异常）
      this.noSignalTimeout = setTimeout(() => {
        if (this.assessing && this.pendingPlan === null) {
          this.showToast('服务器响应超时，请稍后重试', 'error');
          this.assessing = false;
        }
      }, 5000);

      // 3秒匀速进度条
      const progressDuration = 3000;
      const intervalMs = 100;
      const totalSteps = progressDuration / intervalMs;
      let step = 0;

      const timer = setInterval(() => {
        step++;
        this.progress = Math.min(100, Math.floor((step / totalSteps) * 100));

        if (this.progress >= 100) {
          clearInterval(timer);
          clearTimeout(this.noSignalTimeout);
          this.noSignalTimeout = null;

          // 进度条完成后，自动播放AI计划内容
          if (this.pendingPlan) {
            this.plan = this.pendingPlan;

            this.playGeneratedPlanAudio(this.plan.message);  // 播报AI计划内容
          } else {
            this.showToast('AI计划加载失败，请稍后重试', 'error');
          }

          this.assessing = false;
        }
      }, intervalMs);

      // 后端请求，获取AI计划
      const url = 'http://115.190.118.22:5000/api/get-training-plan';
      axios
        .post(url, { id: userId }, {
          headers: { 'Content-Type': 'application/json' }
        })
        .then((res) => {
          if (res.data.error) {
            this.error = res.data.error;
            this.showToast(this.error, 'error');
            this.assessing = false;
            clearInterval(timer);
            return;
          }

          if (res.data.actions && res.data.message) {
            this.pendingPlan = {
              message: res.data.message,
              actions: res.data.actions
            };
          } else {
            this.pendingPlan = '无计划内容';
          }
        })
        .catch((err) => {
          this.error = '获取训练计划失败，请检查网络或服务器状态';
          this.showToast(this.error, 'error');
          this.assessing = false;
        });
    },

      // 播报AI计划内容
    playGeneratedPlanAudio() {
      if (this.plan && this.plan.message) {
        const planText = `${this.plan.message}`;
        this.playTextAudio(planText);
      }
    },

    playTextAudio(text) {
    const speech = new SpeechSynthesisUtterance(text);  // 创建语音对象
    speech.lang = 'zh-CN';  // 设置中文语音
    window.speechSynthesis.speak(speech);  // 播放语音
  },


    showToast(message, type = 'success') {
      this.toast = { show: true, message, type };
      setTimeout(() => {
        this.toast.show = false;
      }, 4000);
    },
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
};
</script>

<style scoped>
.container {
  max-width: 600px;
  margin: 50px auto;
  text-align: center;
  font-family: "Microsoft YaHei", Arial, sans-serif;
  position: relative; /* 为右下角按钮定位提供参照 */
  min-height: 500px; /* 防止右下角按钮被裁切 */
}

.button-group-top {
  text-align: center;
  display: flex;
  justify-content: center;  /* 居中按钮 */
  gap: 10px; /* 减小按钮之间的间距 */

}

.generate-btn {
  padding: 12px 30px;
  font-size: 24px;
  background-color: #409eff;
  border: none;
  border-radius: 6px;
  color: white;
  cursor: pointer;
  white-space: nowrap;
  min-width: 150px;
}

.generate-btn:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

.progress-bar-container {
  margin-top: 20px;
  width: 100%;
  height: 26px;
  border: 1px solid #409eff;
  border-radius: 13px;
  overflow: hidden;
  background-color: #e0e0e0;
  position: relative;
}

.progress-bar {
  height: 100%;
  background-color: #409eff;
  transition: width 0.1s linear;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 14px;
}

.progress-percent {
  z-index: 2;
}

.plan-display {
  margin-top: 30px;
  text-align: left;
  background: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
  max-height: 400px;
  overflow-y: auto;
  font-family: Consolas, monospace;
}

.plan-content {
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: break-word;
  font-family: "Microsoft YaHei", sans-serif; /* 替换为更易读字体 */
  font-size: 16px;
  line-height: 1.6;
}

.error-msg {
  margin-top: 20px;
  color: #f44336;
  font-weight: 600;
}

/* 固定右下角跳转按钮 */
.button-bottom-right {
  position: absolute;
  right: 20px;
  bottom: 20px;
  display: flex;
  justify-content: center;  /* 居中按钮 */
  gap: 10px; /* 减小按钮之间的间距 */

}

.next-btn {
  padding: 10px 20px;
  font-size: 24px;
  background-color: #67c23a;
  border: none;
  border-radius: 6px;
  color: white;
  cursor: pointer;
  white-space: nowrap;  /* 防止文字换行 */
  min-width: 200px;  /* 设置按钮的最小宽度，确保文字不被挤压 */

}

.next-btn:hover {
  background-color: #5daf34;
}

.back-button {
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-weight: bold;
  position: fixed;
  top: 30px;
  left: 35px;
  background: transparent;
  border: none;
  font-size: 22px;
  color: #333;
  cursor: pointer;
  user-select: none;
  z-index: 100;
}

.back-button:hover {
  text-decoration: underline;
}

/* 左侧图片容器 */
.login-button {
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 22px;
  font-weight: bold;
  position: fixed;
  top: 20px;
  right: 20px;
  background: transparent;
  border: none;
  color: #333333;  /* 文字颜色改为黑色 */
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
</style>