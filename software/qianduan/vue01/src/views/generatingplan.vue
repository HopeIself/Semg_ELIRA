<template>
  <div class="container">
    <!-- 生成按钮居中 -->
    <div class="button-group-top">
      <button @click="startGeneration" :disabled="assessing" class="generate-btn">
        生成AI计划
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
      <div class="plan-content">{{ formattedPlan }}</div>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-msg">
      错误：{{ error }}
    </div>

    <!-- 固定右下角的跳转按钮 -->
    <div class="button-bottom-right">
      <button @click="goToAITrainingPlan" class="next-btn">
        前往训练方案页面
      </button>
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
  },
  methods: {
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

    startGeneration() {
      if (this.assessing) return;

      const userId = localStorage.getItem('id');
      if (!userId || userId === 'null') {
        this.showToast('未找到用户ID，请重新登录', 'error');
        return;
      }

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

          // 3秒后展示 AI 计划（如果已有）
          if (this.pendingPlan) {
            this.plan = this.pendingPlan;
          } else {
            this.showToast('AI计划加载失败，请稍后重试', 'error');
          }

          this.assessing = false;
        }
      }, intervalMs);

      // 后端请求
      const url = 'http://115.190.134.66:5000/api/get-training-plan';

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
            clearTimeout(this.noSignalTimeout);
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

          // 不立即展示，让定时器来控制显示时机
        })
        .catch((err) => {
          clearInterval(timer);
          clearTimeout(this.noSignalTimeout);
          this.noSignalTimeout = null;

          this.error = '获取训练计划失败，请检查网络或服务器状态';
          this.showToast(this.error, 'error');
          this.assessing = false;
        });
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
  margin-bottom: 20px;
}

.generate-btn {
  padding: 12px 30px;
  font-size: 18px;
  background-color: #409eff;
  border: none;
  border-radius: 6px;
  color: white;
  cursor: pointer;
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
}

.next-btn {
  padding: 10px 20px;
  font-size: 16px;
  background-color: #67c23a;
  border: none;
  border-radius: 6px;
  color: white;
  cursor: pointer;
}

.next-btn:hover {
  background-color: #5daf34;
}
</style>