<template>
  <div class="assessment-container">
    <button class="back-button" @click="goBack">返回方案选择</button>
    <button class="login-button" @click="goLogin">退出登录</button>

    <h1 class="title">肌肉状况记录</h1>
  

    <div class="content">
      <!-- 左侧图片和动作标签 -->
      <div class="left horizontal-action-list">
        <div
          class="action-block"
          v-for="(action, index) in actions"
          :key="index"
        >
          <img :src="action.image" class="exercise-image" />
          <p class="image-label">
            {{ action.label }}：{{ action.description }}
          </p>
        </div>
      </div>

      <!-- 右侧详细区域 -->
      <div class="right">
        <div class="assessment-type-container">
          <label for="assessmentType">记录用途：</label>
          <select
            id="assessmentType"
            v-model="code"
            :disabled="isAssessing"
          >
            <option value="1">记录康复前肌肉状态</option>
            <option value="2">记录康复后肌肉状态</option>
          </select>
        </div>
        
        <div class="button-container">
          <button
            class="btn"
            @click="startAssessment"
            :disabled="isAssessing || !id || !code"
          >
            {{ isAssessing ? '记录进行中...' : '开始记录' }}
          </button>
          <button
            class="btn stop-btn"
            @click="stopAssessment"
            :disabled="!isAssessing"
          >
            停止记录
          </button>
        </div>

        <!-- 状态显示区 -->
        <div class="status-display" v-if="isAssessing || assessmentComplete">
          <div v-if="isGeneratingPlan">
            <p>{{ generationStatus }}</p>
            <div class="progress-bar">
              <div class="progress-bar-fill" :style="{ width: progress + '%' }"></div>
            </div>
            <p class="generation-info">
              根据用户个人信息、医生建议等内容生成个性化训练计划
            </p>
          </div>

          <div class="connection-status" v-if="!isGeneratingPlan">
            <label>连接状态：</label>
            <span :class="connectionStatus">{{ connectionStatusText }}</span>
          </div>
          <div v-if="errorMessage && !isGeneratingPlan" class="error-message">
            错误信息：{{ errorMessage }}
          </div>
          
          <p class="phase-text" v-if="assessmentPhase && !isGeneratingPlan">
            当前阶段：{{ assessmentPhase }}
          </p>
          
          <p class="countdown-text" v-if="currentCountdown !== null && currentCountdown > 0 && !isGeneratingPlan">
            倒计时：{{ currentCountdown }} 秒
          </p>

          <p class="emg-text" v-if="!isGeneratingPlan">
            采集阶段实时肌电信号值：{{ currentEmgValue }}
          </p>

          
        </div>

        <div class="completion-buttons" v-if="assessmentComplete">
          <p class="completion-tip">记录已完成，请点击“下一步”继续</p>
          <div class="button-row">
            <button class="btn" @click="goToNext">下一步</button>
          </div>
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
      id: localStorage.getItem("id") || "",
      code: '1', 

      currentActionIndex: 0,
      actions: [
        {
          image: require('../assets/image1.gif'),
          label: '动作1',
          description: '保持屈臂，握拳张开'
        },
        {
          image: require('../assets/image2.gif'),
          label: '动作2',
          description: '匀速弯曲手臂，同时握拳'
        }
      ],

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

      showProgressBar: false,
      progress: 0,

      isGeneratingPlan: false,
      generationStatus: "正在生成计划...",  
      phaseSpoken: "",  // 用来记录当前播报的阶段
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
  mounted() {
    const fromPath = this.$route.query.from;
    if (fromPath === 'planchoose') {
      this.code = '1'; 
    } else if (fromPath === 'breakend') {
      this.code = '2'; 
    }
  },
  methods: {
    playStatusSpeech(statusText) {
      const utterance = new SpeechSynthesisUtterance(statusText);
      utterance.lang = 'zh-CN';
      utterance.rate = 1;
      utterance.pitch = 1;
      window.speechSynthesis.speak(utterance);
    },

    goBack() {
      this.$router.push({ path: "/planchoose" });
    },
    goLogin() {
      this.$router.push({ path: "/" });
    },
    handleNextStep() {
      if (this.code === '1') {
        this.$router.push({ path: '/generatingplan' });
      } else if (this.code === '2') {
        this.$router.push({ path: '/generatingreport' });
      }
    },

    async startAssessment() {
      if (!this.id) {
        this.errorMessage = "请输入用户ID";
        return;
      }
      this.resetState();
      this.isAssessing = true;
      this.connectionStatus = 'connecting';
      localStorage.setItem("id", this.id);

      this.currentActionIndex = 0;

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

      // 收到 done === 2，跳转页面
      if (data.done === 2) {
        this.stopAssessment();
        this.$router.push('/generatingreport');
        return;
      }

      // 阶段管理逻辑
      // 初始阶段（前3条数据）：休息中
      if (this.totalDataReceived <= 3) {
        this.assessmentPhase = "休息中";
        if (this.phaseSpoken !== "初始休息") {
          this.playStatusSpeech('评估准备开始，请准备');
          this.phaseSpoken = "初始休息";
        }
      }
      // 动作1采集阶段（4-13条数据，共10条）
      else if (this.totalDataReceived <= 13) {
        this.assessmentPhase = "正在采集动作1";
        if (this.phaseSpoken !== "动作1") {
          this.playStatusSpeech('正在采集动作1：保持屈臂，握拳张开');
          this.phaseSpoken = "动作1";
        }
      }
      // 动作间休息阶段（14-18条数据，共5条）
      else if (this.totalDataReceived <= 18) {
        this.assessmentPhase = "休息中";
        if (this.phaseSpoken !== "动作间休息") {
          this.playStatusSpeech('休息中，请准备动作2');
          this.phaseSpoken = "动作间休息";
        }
      }
      // 动作2采集阶段（19-28条数据，共10条）
      else if (this.totalDataReceived <= 28) {
        this.assessmentPhase = "正在采集动作2";
        if (this.phaseSpoken !== "动作2") {
          this.playStatusSpeech('正在采集动作2：匀速弯曲手臂，同时握拳');
          this.phaseSpoken = "动作2";
        }
      }
      // 两个动作完成后：生成计划
      else {
        if (!this.isGeneratingPlan) {
          this.startGeneratingPlan();
        }
      }

      if (data.countdown !== undefined) {
        this.currentCountdown = data.countdown;

        // 当倒计时为0时切换动作
        if (this.currentCountdown <= 0 && this.totalDataReceived <= 13) {
          this.switchToNextAction();
        }

        // 所有数据接收完成，结束评估
        if (data.countdown === 0 && this.totalDataReceived > 28) {
          this.completeAssessment();
        }
      }

      if (data.emg !== undefined) {
        this.currentEmgValue = data.emg;
        this.finalEmgValue = data.emg;

        this.emgHistory.unshift({
          timestamp: new Date().toLocaleTimeString(),
          value: data.emg,
          countdown: data.countdown || 0
        });

        if (this.emgHistory.length > 50) {
          this.emgHistory.pop();
        }
      }

      // 后端触发生成计划
      if (data.done === 5) {
        this.startGeneratingPlan();
      }

      // 计划生成完成
      if (data.done === 1) {
        this.isGeneratingPlan = true;
        this.generationStatus = "计划已生成";
        this.progress = 100;
        this.showProgressBar = true;
        this.assessmentComplete = true;
        this.playStatusSpeech('训练计划已生成');
      }
    },

    // 开始生成个性化训练计划
    startGeneratingPlan() {
      this.isGeneratingPlan = true;
      this.assessmentPhase = null;
      this.generationStatus = "正在生成计划...";
      this.progress = 0;
   //   this.phaseSpoken = "正在根据用户个人信息、医生建议等内容生成个性化训练计划";
      this.playStatusSpeech('正在根据用户个人信息、医生建议等内容生成个性化训练计划');
      this.updateProgress();
    },

    updateProgress() {
      if (this.progress < 90) {
        setTimeout(() => {
          this.progress += 5;
          this.updateProgress();
        }, 500);
      }
    },

    switchToNextAction() {
      if (this.currentActionIndex < this.actions.length - 1) {
        this.currentActionIndex++;
        this.$nextTick(() => {
          console.log('当前动作索引:', this.currentActionIndex);
        });
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
      if (!this.isGeneratingPlan) {
        this.assessmentPhase = "记录完成";
      }
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
      this.totalDataReceived = 0;
      this.isGeneratingPlan = false;
      this.progress = 0;
      this.generationStatus = "正在生成计划...";
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
/* 样式部分保持不变 */
.completion-buttons {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 30px;
}

.button-row {
  display: flex;
  flex-direction: row;
  gap: 40px;
  margin-top: 15px;
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
.status-display,
.generation-info,
.generation-ingeneratiofo,
.connection-status,
.phase-text,
.countdown-text,
.emg-text,
.completion-tip {
  font-size: 20px;
  margin-top: 10px;
  font-weight: bold;
  white-space: nowrap;
}

.assessment-type-container select {
  font-size: 18px;
  padding: 6px 10px;
}
/* 图片 */
.exercise-image {
  width: 360px;
  height: 360px;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
} 

.title {
  font-size: 28px;
  font-weight: bold;
  text-align: center;
  margin-bottom: 40px;
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
  color: #333333;
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

.image-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.image-label {
  font-size: 18px;
  color: #333333;
  margin-top: 15px;
  text-align: center;
  font-weight: bold;
}
/* 按钮容器 */
.button-container {
  display: flex;
  gap: 10px; 
  justify-content: space-between; 
  margin-top: 20px;
}

/* 评估用途容器 */
.assessment-type-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 10px;
  margin-top: 20px;
  margin-bottom: 20px;
  font-size: 24px;
  font-weight: bold;
}

/* 主容器调整左右布局 */
.content {
  display: flex;
  justify-content: space-between;
  width: 100%;
  max-width: 960px;
}

/* 左侧区域 */
.left {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* 右侧区域 */
.right {
  flex: 1;
  padding-left: 40px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start; 
  margin-top: 20px;
}

/* 控制评估按钮 */
.btn {
  padding: 8px 16px;
  font-size: 16px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  min-width: 150px;
  gap: 10px;
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

/* 进度条 */
.progress-bar {
  width: 100%;
  height: 20px;
  background-color: #ddd;
  border-radius: 10px;
  margin-bottom: 15px;
}

.progress-bar-fill {
  height: 100%;
  background-color: #409eff;
  transition: width 0.3s ease;
}

.horizontal-action-list {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  justify-content: center;
  gap: 30px;
}

.action-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 200px;
  flex-shrink: 0;
}

/* 图片样式 */
.exercise-image {
  width: 210px;
  height: 210px;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
}
</style>