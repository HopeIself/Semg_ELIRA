<template>
  <div class="container">

    <button @click="goToHomepage" class="next-btn">
      返回主页
    </button>

    <button @click="startGeneration" :disabled="loading" class="generate-btn">
      下载报告
    </button>

    <div v-if="loading" class="progress-bar-container">
      <div class="progress-bar" :style="{ width: progress + '%' }"></div>
      <div class="progress-text">生成进度：{{ progress }}%</div>
    </div>

    <div v-if="plan" class="plan-display">
      <h2>生成的AI训练计划</h2>
      <pre>{{ formattedPlan }}</pre>
    </div>

    <div v-if="error" class="error-msg">
      错误：{{ error }}
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      assessing: false,       // 代替loading，更语义化
      progress: 0,
      plan: null,
      eventSource: null,
      error: null,
      noSignalTimeout: null,  // 超时检测
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
    goToHomepage() {
      this.$router.push({ path: '/homepage' });
    },

    startGeneration() {
      if (this.assessing) return;

      const userId = localStorage.getItem('id');
      if (!userId || userId === 'null') {
        this.showToast('未找到用户ID，请重新登录', 'error');
        return;
      }

      this.plan = null;
      this.error = null;
      this.progress = 0;
      this.assessing = true;
      this.noSignalTimeout = setTimeout(() => {
        if (this.assessing && this.plan === null) {
          this.showToast('未检测到肌电信号值，请稍后重试', 'error');
          this.assessing = false;
          this.closeEventSource();
        }
      }, 5000);

      const url = `http://115.190.134.66:5000/api/initial-assessment?id=${encodeURIComponent(userId)}`;

      // 开启 SSE
      this.eventSource = new EventSource(url);

      // 进度条匀速走满，约10秒
      const progressDuration = 10000;
      const intervalMs = 100;
      const totalSteps = progressDuration / intervalMs;
      let step = 0;
      const timer = setInterval(() => {
        step++;
        this.progress = Math.min(100, Math.floor((step / totalSteps) * 100));
        if (this.progress >= 100) {
          clearInterval(timer);
          // 计划没到继续等SSE
        }
      }, intervalMs);

      this.eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.error) {
            this.error = data.error;
            this.showToast(data.error, 'error');
            this.assessing = false;
            this.closeEventSource();
            clearInterval(timer);
            return;
          }

          if (data.finished) {
            this.plan = data.plan || '无计划内容';
            this.assessing = false;
            this.progress = 100;
            clearInterval(timer);
            this.closeEventSource();
            return;
          }

          // 这里你可以根据服务器传回的其他信息调整进度条等
          if (data.emg_value !== undefined && this.noSignalTimeout) {
            clearTimeout(this.noSignalTimeout);
            this.noSignalTimeout = null;
          }
        } catch (err) {
          this.error = '解析服务器数据失败';
          this.showToast(this.error, 'error');
          this.assessing = false;
          clearInterval(timer);
          this.closeEventSource();
        }
      };

      this.eventSource.onerror = () => {
        this.error = '与服务器连接错误';
        this.showToast(this.error, 'error');
        this.assessing = false;
        clearInterval(timer);
        this.closeEventSource();
      };
    },

    closeEventSource() {
      if (this.eventSource) {
        this.eventSource.close();
        this.eventSource = null;
      }
      if (this.noSignalTimeout) {
        clearTimeout(this.noSignalTimeout);
        this.noSignalTimeout = null;
      }
    },

    showToast(message, type = 'success') {
      this.toast = { show: true, message, type };
      setTimeout(() => {
        this.toast.show = false;
      }, 4000);
    },
  },
  beforeUnmount() {
    this.closeEventSource();
  },
};
</script>

<style scoped>
.container {
  max-width: 600px;
  margin: 50px auto;
  text-align: center;
  font-family: "Microsoft YaHei", Arial, sans-serif;
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
  height: 20px;
  border: 1px solid #409eff;
  border-radius: 10px;
  overflow: hidden;
  position: relative;
}

.progress-bar {
  height: 100%;
  background-color: #409eff;
  transition: width 0.1s linear;
}

.progress-text {
  margin-top: 8px;
  font-size: 16px;
  color: #409eff;
}

.plan-display {
  margin-top: 30px;
  text-align: left;
  background: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
  white-space: pre-wrap;
  max-height: 400px;
  overflow-y: auto;
  font-family: Consolas, monospace;
}

.error-msg {
  margin-top: 20px;
  color: #f44336;
  font-weight: 600;
}

.next-btn {
  margin-top: 20px;
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
