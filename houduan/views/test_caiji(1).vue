<template>
  <div id="app">
    <h1>初始评估测试页面</h1>
    
    <!-- 用户输入区域 -->
    <div class="input-section">
      <label>用户ID: </label>
      <input 
        v-model="id" 
        placeholder="请输入用户ID" 
        :disabled="isAssessing"
      />
      <label>评估类型:</label>
      <select v-model="code" :disabled="isAssessing">
        <option value="1">初始评估</option>
        <option value="2">肌肉评估</option>
      </select>
      <button 
        @click="startAssessment" 
        :disabled="isAssessing || !id || !code"
        class="start-btn"
      >
        {{ isAssessing ? '评估进行中...' : '开始评估' }}
      </button>
      <button 
        @click="stopAssessment" 
        :disabled="!isAssessing"
        class="stop-btn"
      >
        停止评估
      </button>
    </div>

    <!-- 实时数据显示区域 -->
    <div v-if="isAssessing" class="assessment-section">
      <h3>实时肌电信号监测</h3>
      
      <!-- 倒计时显示 -->
      <div class="countdown-display">
        <h2 v-if="currentCountdown > 0">
          倒计时: {{ currentCountdown }} 秒
        </h2>
        <div v-if="assessmentPhase" class="phase-indicator">
          当前阶段: {{ assessmentPhase }}
        </div>
      </div>

      <!-- 肌电值显示 -->
      <div class="emg-display">
        <div class="emg-value">
          <label>当前肌电值:</label>
          <span class="value">{{ currentEmgValue }}</span>
        </div>
        
        <!-- 肌电值趋势图（简单的条形图） -->
        <div class="emg-chart">
          <div 
            class="emg-bar" 
            :style="{ width: Math.min(currentEmgValue * 2, 100) + '%' }"
          ></div>
        </div>
      </div>

      <!-- 采集数据历史 -->
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
    </div>

    <!-- 评估结果显示 -->
    <div v-if="assessmentComplete" class="result-section">
      <h3>评估完成</h3>
      <div class="result-info">
        <p>评估已完成，数据已保存到服务器</p>
        <p>最终肌电值: {{ finalEmgValue }}</p>
      </div>
    </div>

    <!-- 错误信息显示 -->
    <div v-if="errorMessage" class="error-section">
      <h4>错误信息:</h4>
      <p>{{ errorMessage }}</p>
    </div>

    <!-- 连接状态显示 -->
    <div class="status-section">
      <div class="status-item">
        <label>连接状态:</label>
        <span :class="connectionStatus">{{ connectionStatusText }}</span>
      </div>
      <div class="status-item">
        <label>数据接收总数:</label>
        <span>{{ totalDataReceived }}</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'InitialAssessmentTest',
  data() {
    return {
      id: localStorage.getItem("id") || "",  // 从 localStorage 获取用户ID
      code: '1',  // 默认设置为初始评估（code=1）
      isAssessing: false,
      assessmentComplete: false,
      currentCountdown: null,
      currentEmgValue: 0,
      finalEmgValue: 0,
      errorMessage: null,
      eventSource: null,
      emgHistory: [],
      totalDataReceived: 0,
      connectionStatus: 'disconnected',
      assessmentPhase: null
    };
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
    startAssessment() {
      if (!this.id) {
        this.errorMessage = "请输入用户ID";
        return;
      }

      this.resetState();
      this.isAssessing = true;
      this.connectionStatus = 'connecting';
      
      // 保存用户ID到localStorage
      localStorage.setItem("id", this.id);

      // 创建SSE连接，传递用户ID和code
      const url = `http://115.190.118.22:5000/api/initial_assessment?id=${encodeURIComponent(this.id)}&code=${encodeURIComponent(this.code)}`;
      
      this.eventSource = new EventSource(url);

      this.eventSource.onopen = () => {
        console.log("SSE连接已建立");
        this.connectionStatus = 'connected';
        this.errorMessage = null;
      };

      this.eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleIncomingData(data);
        } catch (error) {
          console.error("解析数据失败:", error);
          this.errorMessage = `数据解析错误: ${error.message}`;
        }
      };

      this.eventSource.onerror = (error) => {
        console.error("SSE连接错误:", error);
        this.connectionStatus = 'error';
        this.errorMessage = "连接服务器失败，请检查网络连接";
        this.stopAssessment();
      };
    },

    handleIncomingData(data) {
      this.totalDataReceived++;
      
      // 处理倒计时
      if (data.countdown !== undefined) {
        this.currentCountdown = data.countdown;
        
        // 判断评估阶段
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

      // 处理肌电值
      if (data.emg !== undefined) {
        this.currentEmgValue = data.emg;
        this.finalEmgValue = data.emg;
        
        // 记录历史数据
        this.emgHistory.unshift({
          timestamp: new Date().toLocaleTimeString(),
          value: data.emg,
          countdown: data.countdown || 0
        });
        
        // 限制历史记录数量
        if (this.emgHistory.length > 50) {
          this.emgHistory = this.emgHistory.slice(0, 50);
        }
      }

      // 检查是否评估完成（倒计时结束且没有更多数据）
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

    resetState() {
      this.assessmentComplete = false;
      this.currentCountdown = null;
      this.currentEmgValue = 0;
      this.finalEmgValue = 0;
      this.errorMessage = null;
      this.emgHistory = [];
      this.totalDataReceived = -3;
      this.assessmentPhase = null;
    }
  },

  beforeDestroy() {
    // 组件销毁时关闭SSE连接
    this.stopAssessment();
  }
};
</script>

<style scoped>
/* 样式略，同之前 */
</style>
