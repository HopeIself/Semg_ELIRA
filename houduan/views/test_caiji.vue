<template>
  <div class="assessment-container">
    <!-- 右下角“下一步”浮动按钮 -->
<button class="next-step-button" @click="handleNextStep">
  下一步
</button>

    <h1 class="title">肌肉状况评估</h1>

    <div class="content">
      <!-- 左侧图片和动作标签 -->
      <div class="left">
        <img :src="actions[currentActionIndex].image" class="exercise-image" />
        <p class="image-label">{{ actions[currentActionIndex].label }}</p>
      </div>

      <!-- 右侧详细区域 -->
      <div class="right">
        <!-- 用户ID输入及评估类型选择 -->
        <div class="input-section">
          <label for="userId">用户ID:</label>
          <input
            id="userId"
            v-model="id"
            :disabled="isAssessing"
            placeholder="请输入用户ID"
          />

          <label for="assessmentType">评估类型:</label>
          <select
            id="assessmentType"
            v-model="code"
            :disabled="isAssessing"
          >
            <option value="1">初始评估</option>
            <option value="2">状态记录</option>
          </select>

          <!-- 控制按钮 -->
          <button
            class="btn"
            @click="startAssessment"
            :disabled="isAssessing || !id || !code"
          >
            {{ isAssessing ? '评估进行中...' : '开始评估' }}
          </button>
          <button
            class="btn stop-btn"
            @click="stopAssessment"
            :disabled="!isAssessing"
          >
            停止评估
          </button>
        </div>

        <!-- 状态展示区 -->
        <div class="status-display" v-if="isAssessing || assessmentComplete">
          <!-- 倒计时 -->
          <p class="countdown-text" v-if="currentCountdown !== null && currentCountdown > 0">
            倒计时: {{ currentCountdown }} 秒
          </p>

          <!-- 评估阶段 -->
          <p class="phase-text" v-if="assessmentPhase">
            当前阶段: {{ assessmentPhase }}
          </p>

          <!-- 实时肌电值 -->
          <p class="emg-text">
            实时肌电值：{{ currentEmgValue }}
          </p>

          <!-- 条形图 -->
          <div class="emg-chart">
            <div
              class="emg-bar"
              :style="{ width: Math.min(currentEmgValue * 2, 100) + '%' }"
            ></div>
          </div>

          <!-- 数据采集历史 -->
          <div class="data-history">
            <h4>数据采集历史:</h4>
            <div class="history-list">
              <div
                v-for="(data, index) in emgHistory"
                :key="index"
                class="history-item"
              >
                时间: {{ data.timestamp }} | 肌电值: {{ data.value }} | 倒计时: {{ data.countdown }}
              </div>
            </div>
          </div>

          <!-- 连接状态和错误信息 -->
          <div class="connection-status">
            <label>连接状态:</label>
            <span :class="connectionStatus">{{ connectionStatusText }}</span>
          </div>
          <div v-if="errorMessage" class="error-message">
            错误信息: {{ errorMessage }}
          </div>
        </div>

        <!-- 评估完成后的操作按钮 -->
        <div class="completion-buttons" v-if="assessmentComplete">
          <button class="btn" @click="restart">
            重新评估
          </button>
          <button class="btn" @click="goToNext">
            下一步
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AssessmentFusion',
  data() {
    return {
      // 用户与评估类型
      id: localStorage.getItem("id") || "",
      code: '1', // 默认初始评估

      // 动作和图片相关
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
      ],

      // 评估状态相关
      isAssessing: false,
      assessmentComplete: false,
      currentCountdown: null,
      currentEmgValue: 0,
      finalEmgValue: 0,
      errorMessage: null,
      connectionStatus: 'disconnected',
      assessmentPhase: null,
      emgHistory: [],
      totalDataReceived: 0,
      eventSource: null,
    }
  },
  computed: {
    connectionStatusText() {
      switch(this.connectionStatus) {
        case 'connected': return '已连接';
        case 'connecting': return '连接中';
        case 'disconnected': return '未连接';
        case 'error': return '连接错误';
        default: return '未知状态';
      }
    }
  },
  methods: {
    handleNextStep() {
  if (this.code === '1') {
    this.$router.push({ path: '/generatingplan' });
  } else if (this.code === '2') {
    this.$router.push({ path: '/generatingreport' });
  }
},

    startAssessment() {
      if (!this.id) {
        this.errorMessage = "请输入用户ID";
        return;
      }
      this.resetState();
      this.isAssessing = true;
      this.connectionStatus = 'connecting';
      localStorage.setItem("id", this.id);

      // 这里依据评估类型，决定动作索引
      this.currentActionIndex = 0;

      // SSE连接地址
      const url = `http://115.190.118.22:5000/api/initial_assessment?id=${encodeURIComponent(this.id)}&code=${encodeURIComponent(this.code)}`;

      this.eventSource = new EventSource(url);

      this.eventSource.onopen = () => {
        this.connectionStatus = 'connected';
        this.errorMessage = null;
      };

      this.eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleIncomingData(data);
        } catch (error) {
          this.errorMessage = `数据解析错误: ${error.message}`;
        }
      };

      this.eventSource.onerror = (error) => {
        this.connectionStatus = 'error';
        this.errorMessage = "连接服务器失败，请检查网络连接";
        this.stopAssessment();
      };
    },

    handleIncomingData(data) {
      this.totalDataReceived++;

      // 处理倒计时和评估阶段
      if (data.countdown !== undefined) {
        this.currentCountdown = data.countdown;

        // 简单判断评估阶段（可根据后端协议调整）
        if (data.emg !== undefined) {
          if (this.totalDataReceived <= 10) {
            this.assessmentPhase = "第一次采集 (1_RMS, 1_MNF, 1_MF)";
          } else {
            this.assessmentPhase = "第二次采集 (2_RMS, 2_MNF, 2_MF)";
          }
        } else {
          this.assessmentPhase = "休息阶段";
        }
      }

      // 更新肌电值及历史记录
      if (data.emg !== undefined) {
        this.currentEmgValue = data.emg;
        this.finalEmgValue = data.emg;

        this.emgHistory.unshift({
          timestamp: new Date().toLocaleTimeString(),
          value: data.emg,
          countdown: data.countdown || 0
        });

        // 限制历史记录最多50条
        if (this.emgHistory.length > 50) {
          this.emgHistory.pop();
        }
      }

      // 评估完成判断（举例）
      if (data.countdown === 0 && this.totalDataReceived > 20) {
        setTimeout(() => {
          this.completeAssessment();
        }, 2000);
      }
    },

    stopAssessment() {
      if (this.eventSource) {
        this.eventSource.close();
        this.eventSource = null;
      }
      this.isAssessing = false;
      this.connectionStatus = 'disconnected';
    },

    completeAssessment() {
      this.stopAssessment();
      this.assessmentComplete = true;
      this.assessmentPhase = "评估完成";
    },

    restart() {
      this.resetState();
      this.currentActionIndex = 0;
    },

    resetState() {
      this.assessmentComplete = false;
      this.currentCountdown = null;
      this.currentEmgValue = 0;
      this.finalEmgValue = 0;
      this.errorMessage = null;
      this.connectionStatus = 'disconnected';
      this.assessmentPhase = null;
      this.emgHistory = [];
      this.totalDataReceived = -3;
      if(this.eventSource){
        this.eventSource.close();
        this.eventSource = null;
      }
      this.isAssessing = false;
    },

    goToNext() {
      this.$router.push({ path: '/generatingplan' });
    }
  },

  beforeUnmount() {
    this.stopAssessment();
  }
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
  text-align: center;
}

.content {
  display: flex;
  justify-content: center;
  width: 100%;
  max-width: 960px;
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
  font-size: 20px;
}

.right {
  flex: 1;
  padding-left: 40px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

.input-section {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 15px;
}

.input-section label {
  font-weight: bold;
  min-width: 60px;
}

.input-section input,
.input-section select {
  padding: 6px 10px;
  font-size: 16px;
  border-radius: 4px;
  border: 1px solid #ccc;
  min-width: 130px;
}

.btn {
  padding: 8px 16px;
  font-size: 16px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn:hover:not(:disabled) {
  background-color: #337ab7;
}

.btn:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

.stop-btn {
  background-color: #f56c6c;
}

.stop-btn:hover:not(:disabled) {
  background-color: #dd6161;
}

.status-display {
  margin-top: 10px;
  font-size: 16px;
}

.countdown-text {
  font-size: 22px;
  font-weight: bold;
  color: #ff6600;
  margin-bottom: 5px;
}

.phase-text {
  font-size: 18px;
  margin-bottom: 10px;
}

.emg-text {
  font-size: 18px;
  margin-bottom: 6px;
}

.emg-chart {
  width: 100%;
  height: 20px;
  background-color: #ddd;
  border-radius: 10px;
  margin-bottom: 15px;
  overflow: hidden;
}

.emg-bar {
  height: 100%;
  background-color: #409eff;
  transition: width 0.3s ease;
}

.data-history {
  max-height: 150px;
  overflow-y: auto;
  border: 1px solid #ccc;
  padding: 8px;
  border-radius: 6px;
  background-color: #fafafa;
  margin-bottom: 10px;
}

.history-list {
  font-size: 14px;
  color: #333;
}

.history-item {
  margin-bottom: 4px;
}

.connection-status {
  margin-top: 10px;
  font-weight: bold;
}

.connection-status span.connected {
  color: green;
}

.connection-status span.connecting {
  color: orange;
}

.connection-status span.disconnected {
  color: red;
}

.connection-status span.error {
  color: darkred;
}

.error-message {
  margin-top: 10px;
  color: red;
  font-weight: bold;
}

.completion-buttons {
  margin-top: 20px;
  display: flex;
  gap: 15px;
  justify-content: flex-start;
}

.next-step-button {
  position: fixed;
  bottom: 50px; /* 往上移一点 */
  right: 50px;  /* 往左移一点 */
  z-index: 1000;
  padding: 14px 24px; /* 稍微放大 */
  font-size: 18px;
  background-color: #67c23a;
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  box-shadow: 0 3px 12px rgba(0, 0, 0, 0.15);
  transition: background-color 0.3s ease;
}

.next-step-button:hover {
  background-color: #5daf34;
}


</style>
