<template>
  <div class="plan1-page">
    <button class="back-button" @click="goBack">← 返回</button>

    <!-- 顶部动作标题，居中 -->
    <h2 class="top-action-title">动作练习：{{ currentAction.description }}</h2>

    <!-- 第二行：数据流控制按钮组 + 4个统计指标 -->
<div class="data-control-row">
  <!-- 数据流控制按钮 -->
  <div class="control-panel">
    <div class="panel-header">
      <h2 class="panel-title"><i class="icon">📡</i> 数据流控制</h2>
      <div class="connection-status" :class="connectionStatus">
        <div class="status-dot"></div>
        <span class="status-text">{{ getConnectionStatusText() }}</span>
      </div>
    </div>
    <div class="control-buttons">
      <button @click="startStream" class="btn btn-start" :disabled="isConnected">
        <i class="btn-icon">🚀</i> 开始监控
      </button>
      <button @click="stopStream" class="btn btn-stop" :disabled="!isConnected">
        <i class="btn-icon">⏹️</i> 停止监控
      </button>
      <button @click="clearData" class="btn btn-clear">🗑️ 清除数据</button>
      <button @click="exportData" class="btn btn-export" :disabled="emgData.length === 0">
        💾 导出数据
      </button>
    </div>
  </div>

  <!-- 当前值、平均值、最大值、数据点数 显示 -->
  <div class="current-stats">
    <div class="stat-card small">
      <div class="stat-label">当前值</div>
      <div class="stat-value current">{{ currentValue.toFixed(3) }}</div>
      <div class="stat-unit">mV</div>
    </div>
    <div class="stat-card small">
      <div class="stat-label">平均值</div>
      <div class="stat-value">{{ averageValue.toFixed(3) }}</div>
      <div class="stat-unit">mV</div>
    </div>
    <div class="stat-card small">
      <div class="stat-label">最大值</div>
      <div class="stat-value">{{ maxValue.toFixed(3) }}</div>
      <div class="stat-unit">mV</div>
    </div>
    <div class="stat-card small">
      <div class="stat-label">数据点数</div>
      <div class="stat-value count">{{ emgData.length }}</div>
      <div class="stat-unit">个</div>
    </div>
  </div>
</div>

    <!-- 第三行：左右布局 -->
    <div class="bottom-row">
      <!-- 左侧80%：实时肌电信号波形 -->
      <div class="chart-section">
        <h3 class="chart-title"><i class="icon">📈</i> 实时肌电信号波形</h3>
        <div class="chart-wrapper">
          <canvas
            ref="chartCanvas"
            :width="chartWidth"
            :height="chartHeight"
            @mousemove="onChartMouseMove"
            @mouseleave="hideTooltip"
            style="border:1px solid #ccc;"
          ></canvas>
          <div
            v-if="tooltip.show"
            class="chart-tooltip"
            :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
          >
            <div class="tooltip-time">{{ tooltip.time }}</div>
            <div class="tooltip-value">{{ tooltip.value }} mV</div>
          </div>
        </div>
      </div>

      <!-- 右侧20%：动作图片和完成动作按钮 -->
      <div class="action-panel">
        <img :src="currentImage" alt="动作图片" class="action-image" />
        <button class="complete-btn" :disabled="assessing" @click="nextAction">
          完成动作
        </button>

        <div v-if="completedAll" class="completed-section">
          <h2>恭喜，所有动作完成！</h2>
          <button class="return-btn" @click="goBack">返回训练计划页</button>
        </div>
      </div>
    </div>

    <!-- 提示框 -->
    <transition name="toast">
      <div v-if="toast.show" class="toast" :class="toast.type">
        <i class="toast-icon">
          {{
            toast.type === "success"
              ? "✅"
              : toast.type === "warning"
              ? "⚠️"
              : "❌"
          }}
        </i>
        <span class="toast-text">{{ toast.message }}</span>
      </div>
    </transition>
  </div>
</template>

<script>
export default {
  name: "Plan1",
  data() {
    return {
      actions: [
        { description: "手掌旋转", img: require("../assets/image1.jpg") },
        { description: "腕屈曲", img: require("../assets/image2.jpg") },
        { description: "腕伸展", img: require("../assets/image3.jpg") },
      ],
      currentIndex: 0,
      completedAll: false,

      emgValue: null,
      remainSeconds: 0,
      assessing: false,

      eventSourceAssessment: null,
      countdownTimer: null,

      baseURL: "http://115.190.118.22:5000",
      isConnected: false,
      connectionStatus: "disconnected",
      eventSourceStream: null,

      emgData: [],
      timestamps: [],
      currentValue: 0,

      basePointWidth: 8,
      maxDataPoints: 500,
      chartWidth: 800,
      chartHeight: 400,
      chartContext: null,

      tooltip: { show: false, x: 0, y: 0, time: "", value: "" },
      toast: { show: false, message: "", type: "success" },

      xOffset: 0,
      slideSpeed: 0.3,
    };
  },
  computed: {
    currentAction() {
      return this.actions[this.currentIndex];
    },
    currentImage() {
      return this.actions[this.currentIndex].img;
    },
    averageValue() {
      if (this.emgData.length === 0) return 0;
      return this.emgData.reduce((acc, val) => acc + val, 0) / this.emgData.length;
    },
    maxValue() {
      if (this.emgData.length === 0) return 0;
      return Math.max(...this.emgData);
    },
  },
  watch: {
    emgData() {
      if (this.emgData.length > this.maxDataPoints) {
        this.emgData.splice(0, this.emgData.length - this.maxDataPoints);
        this.timestamps.splice(0, this.timestamps.length - this.maxDataPoints);
      }
      if (this.$refs.chartCanvas) {
        this.$refs.chartCanvas.width = this.chartWidth;
        this.$refs.chartCanvas.height = this.chartHeight;
      }
    },
  },
  mounted() {
    this.restartAssessment();
    this.initChart();
    this.drawChart();
  },
  beforeUnmount() {
    console.log("[Plan1] 页面卸载，执行资源清理");
    this.closeEventSourceAssessment();
    this.stopCountdown();
    this.stopStream(); // 确保 SSE 被关闭
  },
  methods: {
    nextAction() {
      if (this.currentIndex < this.actions.length - 1) {
        this.currentIndex++;
        this.restartAssessment();
      } else {
        this.completedAll = true;
        this.closeEventSourceAssessment();
        this.stopCountdown();
      }
    },
    goBack() {
      this.$router.push({ path: "/aiplan" });
    },
    closeEventSourceAssessment() {
      if (this.eventSourceAssessment) {
        this.eventSourceAssessment.close();
        this.eventSourceAssessment = null;
      }
    },
    stopCountdown() {
      if (this.countdownTimer) {
        clearInterval(this.countdownTimer);
        this.countdownTimer = null;
      }
    },
    startCountdown() {},
    restartAssessment() {
      this.closeEventSourceAssessment();
      this.stopCountdown();
      this.assessing = false;
      this.emgValue = null;
      this.remainSeconds = 0;
    },
    startStream() {
      // 防止重复连接
      if (this.eventSourceStream || this.isConnected) {
        console.warn("[Plan1] 已存在 SSE 连接，避免重复连接");
        return;
      }

      this.stopStream(); // 清理旧连接（保险）

      try {
        this.eventSourceStream = new EventSource(`${this.baseURL}/api/udp-emg-stream`);

        this.eventSourceStream.onopen = () => {
          this.isConnected = true;
          this.connectionStatus = "connected";
          this.showToast("数据流连接成功", "success");
        };

        this.eventSourceStream.onmessage = (event) => {
          if (!this.isConnected) return;
          this.handleStreamData(event);
        };

        this.eventSourceStream.onerror = () => {
          this.isConnected = false;
          this.connectionStatus = "error";
          this.showToast("连接出错，正在重试...", "error");
          this.stopStream();
          setTimeout(() => {
            this.startStream();
          }, 3000);
        };
      } catch (err) {
        this.showToast("启动失败: " + err.message, "error");
      }
    },
    stopStream() {
      if (this.eventSourceStream) {
        console.log("[Plan1] 关闭 SSE 数据流连接");
        try {
          this.eventSourceStream.close();
        } catch (err) {
          console.warn("[Plan1] 关闭 SSE 出现异常：", err);
        }
        this.eventSourceStream.onopen = null;
        this.eventSourceStream.onmessage = null;
        this.eventSourceStream.onerror = null;
        this.eventSourceStream = null;
      }
      this.isConnected = false;
      this.connectionStatus = "disconnected";
      this.showToast("数据流已停止", "warning");
    },
    handleStreamData(event) {
      try {
        const data = JSON.parse(event.data);
        if (!data || typeof data.emg === "undefined") return;
        const value = parseFloat(data.emg);
        if (isNaN(value)) return;
        this.emgData.push(value);
        this.timestamps.push(Date.now());

        if (this.emgData.length > this.maxDataPoints) {
          this.emgData.shift();
          this.timestamps.shift();
        }
        this.currentValue = value;
      } catch (err) {
        console.error("数据解析错误:", err);
      }
    },
    initChart() {
      const canvas = this.$refs.chartCanvas;
      if (canvas) {
        canvas.width = this.chartWidth;
        canvas.height = this.chartHeight;
        this.chartContext = canvas.getContext("2d");
      }
    },
    drawChart() {
      if (!this.chartContext) return;
      requestAnimationFrame(this.drawChart);
      this.chartContext.clearRect(0, 0, this.chartWidth, this.chartHeight);

      const len = this.emgData.length;
      if (len < 2) return;

      const scaleX = this.chartWidth / (this.maxDataPoints - 1);
      let dataMax = Math.max(...this.emgData);
      if (dataMax < 0.1) dataMax = 0.1;
      const maxAmplitude = dataMax * 1.2;
      const scaleY = this.chartHeight / maxAmplitude;

      this.chartContext.beginPath();
      this.emgData.forEach((val, idx) => {
        let x = idx * scaleX - this.xOffset;
        if (x < 0) return;
        let y = this.chartHeight - val * scaleY;
        y = Math.min(Math.max(y, 0), this.chartHeight);
        if (idx === 0) {
          this.chartContext.moveTo(x, y);
        } else {
          this.chartContext.lineTo(x, y);
        }
      });

      this.chartContext.strokeStyle = "#0078ff";
      this.chartContext.lineWidth = 2;
      this.chartContext.stroke();

      this.xOffset += this.slideSpeed;
      if (this.xOffset >= scaleX) {
        this.xOffset -= scaleX;
      }
    },
    onChartMouseMove(e) {
      const x = e.offsetX;
      const y = e.offsetY;
      if (this.emgData.length === 0) return;
      const len = this.emgData.length;
      const scaleX = this.chartWidth / (len - 1);
      const idx = Math.floor(x / scaleX);

      if (idx >= 0 && idx < this.emgData.length) {
        this.tooltip.show = true;
        this.tooltip.x = x + 10;
        this.tooltip.y = y - 30;
        this.tooltip.time = new Date(this.timestamps[idx]).toLocaleTimeString();
        this.tooltip.value = this.emgData[idx].toFixed(3);
      } else {
        this.tooltip.show = false;
      }
    },
    hideTooltip() {
      this.tooltip.show = false;
    },
    clearData() {
      this.emgData = [];
      this.timestamps = [];
      this.currentValue = 0;
      this.showToast("数据已清除", "success");
    },
    exportData() {
      if (this.emgData.length === 0) return this.showToast("无数据可导出", "warning");
      let csv = "Timestamp,EMG_Value\n";
      this.emgData.forEach((v, i) => {
        csv += `${new Date(this.timestamps[i]).toISOString()},${v}\n`;
      });
      const blob = new Blob([csv], { type: "text/csv" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `emg_data_${new Date().toISOString().slice(0, 19)}.csv`;
      a.click();
      URL.revokeObjectURL(url);
      this.showToast("数据导出成功", "success");
    },
    getConnectionStatusText() {
      return this.connectionStatus === "connected"
        ? "已连接"
        : this.connectionStatus === "disconnected"
        ? "未连接"
        : "连接错误";
    },
    showToast(msg, type = "success") {
      this.toast.message = msg;
      this.toast.type = type;
      this.toast.show = true;
      setTimeout(() => {
        this.toast.show = false;
      }, 2000);
    },
  },
};
</script>

<style scoped>
.plan1-page {
  max-width: 1200px;
  margin: 30px auto;
  font-family: Arial, sans-serif;
  position: relative;
  height: 85vh;
  display: flex;
  flex-direction: column;
}

/* 返回按钮 */
.back-button {
  position: absolute;
  top: 10px;
  left: 10px;
  background: transparent;
  border: none;
  font-size: 24px;
  color: #e31111;
  cursor: pointer;
  user-select: none;
  z-index: 100;
}

.back-button:hover {
  text-decoration: underline;
}

/* 顶部动作标题，居中 */
.top-action-title {
  text-align: center;
  margin: 0 0 12px 0;
  font-weight: 700;
  font-size: 24px;
  color: #333;
  user-select: none;
}

/* 第二行：数据流控制与当前值统计放同一行 */
.data-control-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  gap: 12px;
}

/* 控制面板 */
.control-panel {
  flex: 1 1 auto;
  background: white;
  padding: 12px 16px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgb(0 0 0 / 0.1);
  user-select: none;
}

.current-stats {
  display: flex;
  gap: 12px;
  flex: 0 0 auto;
  justify-content: flex-end;
  align-items: center;
  flex-wrap: nowrap;
}

/* 统计卡片小尺寸 */
.stat-card.small {
  background-color: #f7f9fc;
  border-radius: 8px;
  padding: 10px 14px;
  text-align: center;
  box-shadow: inset 0 0 5px rgb(0 0 0 / 0.05);
  width: 100px;
  user-select: none;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 6px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #333;
}

.stat-value.current {
  color: #0078ff;
}

.stat-unit {
  font-size: 12px;
  color: #999;
  margin-top: 2px;
}

/* 第三行左右分栏 */
.bottom-row {
  flex: 1;
  display: flex;
  gap: 16px;
  overflow: hidden;
}

/* 左侧 80% 实时波形图 */
.chart-section {
  flex: 0 0 70%;
  background-color: #f4f4f9;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgb(0 0 0 / 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  user-select: none;
}

.chart-title {
  font-size: 18px;
  margin-bottom: 10px;
  color: #333;
  display: flex;
  align-items: center;
  gap: 6px;
}

.chart-wrapper {
  flex: 1;
  width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  border: 1px solid #ccc;
  border-radius: 8px;
  position: relative;
}

/* canvas宽度和高度适应 */
.chart-wrapper > canvas {
  min-width: 800px;
  height: auto !important;
  max-height: 320px;
  border-radius: 8px;
  display: block;
  border: 1px solid #ccc;
}

/* tooltip */
.chart-tooltip {
  position: absolute;
  background-color: rgba(0, 0, 0, 0.75);
  color: white;
  padding: 6px 10px;
  border-radius: 4px;
  font-size: 12px;
  pointer-events: none;
  white-space: nowrap;
  user-select: none;
  z-index: 200;
}

/* 右侧 20% 动作图片和按钮 */
.action-panel {
  flex: 0 0 30%;
  background-color: #fff;
  border-radius: 12px;
  padding: 16px 12px;
  box-shadow: 0 4px 12px rgb(0 0 0 / 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  user-select: none;
}

.action-image {
  width: 100%;
  max-height: 320px;
  object-fit: contain;
  border-radius: 10px;
  margin-bottom: 20px;
}

.complete-btn {
  font-size: 18px;
  padding: 12px 20px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  user-select: none;
  transition: background-color 0.3s;
  width: 100%;
  max-width: 200px;
  margin-bottom: 20px;
}

.complete-btn:hover:not(:disabled) {
  background-color: #388e3c;
}

.complete-btn:disabled {
  background-color: #a0d6a0;
  cursor: not-allowed;
}

/* 完成全部动作提示 */
.completed-section {
  text-align: center;
  user-select: none;
}

.return-btn {
  font-size: 18px;
  padding: 12px 20px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  user-select: none;
  transition: background-color 0.3s;
  margin-top: 12px;
  width: 100%;
  max-width: 200px;
}

.return-btn:hover {
  background-color: #388e3c;
}

/* 提示框 */
.toast {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  min-width: 180px;
  max-width: 300px;
  padding: 12px 20px;
  border-radius: 25px;
  font-size: 16px;
  color: white;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 2px 10px rgb(0 0 0 / 0.2);
  user-select: none;
  z-index: 1000;
}

.toast.success {
  background-color: #4caf50;
}

.toast.warning {
  background-color: #f0ad4e;
}

.toast.error {
  background-color: #e31111;
}

.toast-icon {
  font-size: 20px;
}

/* 过渡动画 */
.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.3s;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
}
</style>