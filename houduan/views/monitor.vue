<template>
  <div class="emg-stream-viewer">
    <div class="container">
      <h1 class="title">实时肌电信号监控</h1>
      
      <!-- 控制面板 -->
      <div class="control-panel">
        <div class="panel-header">
          <h2 class="panel-title">
            <i class="icon">📡</i>
            数据流控制
          </h2>
          <div class="connection-status" :class="connectionStatus">
            <div class="status-dot"></div>
            <span class="status-text">{{ getConnectionStatusText() }}</span>
          </div>
        </div>
        
        <div class="control-buttons">
          <button @click="startStream" class="btn btn-start" :disabled="isConnected">
            <i class="btn-icon">🚀</i>
            开始监控
          </button>
          
          <button @click="stopStream" class="btn btn-stop" :disabled="!isConnected">
            <i class="btn-icon">⏹️</i>
            停止监控
          </button>
          
          <button @click="clearData" class="btn btn-clear">
            <i class="btn-icon">🗑️</i>
            清除数据
          </button>
          
          <button @click="exportData" class="btn btn-export" :disabled="emgData.length === 0">
            <i class="btn-icon">💾</i>
            导出数据
          </button>
        </div>
      </div>

      <!-- 实时数据显示 -->
      <div class="data-dashboard">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-label">当前值</div>
            <div class="stat-value current">{{ currentValue.toFixed(3) }}</div>
            <div class="stat-unit">mV</div>
          </div>
          
          <div class="stat-card">
            <div class="stat-label">平均值</div>
            <div class="stat-value average">{{ averageValue.toFixed(3) }}</div>
            <div class="stat-unit">mV</div>
          </div>
          
          <div class="stat-card">
            <div class="stat-label">最大值</div>
            <div class="stat-value max">{{ maxValue.toFixed(3) }}</div>
            <div class="stat-unit">mV</div>
          </div>
          
          <div class="stat-card">
            <div class="stat-label">数据点数</div>
            <div class="stat-value count">{{ emgData.length }}</div>
            <div class="stat-unit">个</div>
          </div>
        </div>
      </div>

      <!-- 图表 -->
      <div class="chart-container">
        <h3 class="chart-title"><i class="icon">📈</i> 实时肌电信号波形</h3>
        <div class="chart-wrapper">
          <canvas ref="chartCanvas" :width="chartWidth" :height="chartHeight"
            @mousemove="onChartMouseMove" @mouseleave="hideTooltip"></canvas>
          
          <div v-if="tooltip.show" class="chart-tooltip"
            :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }">
            <div class="tooltip-time">{{ tooltip.time }}</div>
            <div class="tooltip-value">{{ tooltip.value }} mV</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 提示框 -->
    <transition name="toast">
      <div v-if="toast.show" class="toast" :class="toast.type">
        <i class="toast-icon">
          {{ toast.type === 'success' ? '✅' : toast.type === 'warning' ? '⚠️' : '❌' }}
        </i>
        <span class="toast-text">{{ toast.message }}</span>
      </div>
    </transition>
  </div>
</template>

<script>
export default {
  name: 'EMGStreamViewer',
  data() {
    return {
      baseURL: 'http://115.190.118.22:5000',
      isConnected: false,
      connectionStatus: 'disconnected',
      eventSource: null,
      emgData: [],
      timestamps: [],
      currentValue: 0,
      chartWidth: 800,
      chartHeight: 400,
      chartContext: null,
      tooltip: { show: false, x: 0, y: 0, time: '', value: '' },
      toast: { show: false, message: '', type: 'success' }
    }
  },
  computed: {
    averageValue() {
      if (this.emgData.length === 0) return 0;
      return this.emgData.reduce((acc, val) => acc + val, 0) / this.emgData.length;
    },
    maxValue() {
      if (this.emgData.length === 0) return 0;
      return Math.max(...this.emgData);
    }
  },
  mounted() {
    this.initChart();
    this.drawChart();
  },
  beforeUnmount() {
    this.stopStream();
  },
  methods: {
    startStream() {
      if (this.isConnected) return;
      try {
        this.eventSource = new EventSource(`${this.baseURL}/api/udp-emg-stream`);
        this.eventSource.onopen = () => {
          this.isConnected = true;
          this.connectionStatus = 'connected';
          this.showToast('数据流连接成功', 'success');
        };
        this.eventSource.onmessage = (event) => {
          this.handleStreamData(event);
        };
        this.eventSource.onerror = () => {
          this.isConnected = false;
          this.connectionStatus = 'error';
          this.showToast('连接出错，正在重试...', 'error');
          this.stopStream();
          setTimeout(this.startStream, 3000);
        };
      } catch (err) {
        this.showToast('启动失败: ' + err.message, 'error');
      }
    },
    stopStream() {
      if (this.eventSource) {
        this.eventSource.close();
        this.eventSource = null;
      }
      this.isConnected = false;
      this.connectionStatus = 'disconnected';
      this.showToast('数据流已停止', 'warning');
    },
    handleStreamData(event) {
      try {
        const data = JSON.parse(event.data);
        if (!data || typeof data.emg === 'undefined') return;
        const value = parseFloat(data.emg);
        if (isNaN(value)) return;
        this.emgData.push(value);
        this.timestamps.push(Date.now());
        this.currentValue = value;
        if (this.emgData.length > 500) {
          this.emgData.shift();
          this.timestamps.shift();
        }
      } catch (err) {
        console.error('数据解析错误:', err);
      }
    },
    initChart() {
      this.chartContext = this.$refs.chartCanvas.getContext('2d');
    },
    drawChart() {
      if (!this.chartContext) return;
      requestAnimationFrame(this.drawChart);
      this.chartContext.clearRect(0, 0, this.chartWidth, this.chartHeight);
      const len = this.emgData.length;
      if (len < 2) return;
      const scaleX = this.chartWidth / (len - 1);
      const scaleY = this.chartHeight / 1000;
      this.chartContext.beginPath();
      this.emgData.forEach((val, idx) => {
        const x = idx * scaleX;
        const y = this.chartHeight - (val * scaleY + 500);
        if (idx === 0) {
          this.chartContext.moveTo(x, y);
        } else {
          this.chartContext.lineTo(x, y);
        }
      });
      this.chartContext.strokeStyle = '#00f';
      this.chartContext.lineWidth = 2;
      this.chartContext.stroke();
    },
    onChartMouseMove(e) {
      const x = e.offsetX;
      const idx = Math.floor(x / (this.chartWidth / this.emgData.length));
      if (idx >= 0 && idx < this.emgData.length) {
        this.tooltip.show = true;
        this.tooltip.x = x;
        this.tooltip.y = e.offsetY;
        this.tooltip.time = new Date(this.timestamps[idx]).toLocaleTimeString();
        this.tooltip.value = this.emgData[idx].toFixed(3);
      }
    },
    hideTooltip() {
      this.tooltip.show = false;
    },
    clearData() {
      this.emgData = [];
      this.timestamps = [];
      this.currentValue = 0;
      this.showToast('数据已清除', 'success');
    },
    exportData() {
      if (this.emgData.length === 0) return this.showToast('无数据可导出', 'warning');
      let csv = 'Timestamp,EMG_Value\n';
      this.emgData.forEach((v, i) => {
        csv += `${new Date(this.timestamps[i]).toISOString()},${v}\n`;
      });
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `emg_data_${new Date().toISOString().slice(0, 19)}.csv`;
      a.click();
      URL.revokeObjectURL(url);
      this.showToast('数据导出成功', 'success');
    },
    getConnectionStatusText() {
      return this.connectionStatus === 'connected' ? '已连接' :
             this.connectionStatus === 'disconnected' ? '未连接' : '连接错误';
    },
    showToast(msg, type = 'success') {
      this.toast.message = msg;
      this.toast.type = type;
      this.toast.show = true;
      setTimeout(() => { this.toast.show = false; }, 2000);
    }
  }
}
</script>

<style scoped>
.emg-stream-viewer {
  font-family: Arial, sans-serif;
  background-color: #f4f4f9;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.title {
  text-align: center;
  font-size: 28px;
  margin-bottom: 20px;
  color: #333;
}

.control-panel {
  background-color: #fff;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.panel-title {
  font-size: 18px;
  font-weight: bold;
  color: #007bff;
}

.connection-status {
  display: flex;
  align-items: center;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 5px;
  background-color: #dc3545;
}

.status-text {
  font-size: 14px;
  color: #666;
}

.control-buttons {
  display: flex;
  justify-content: space-between;
}

.btn {
  flex: 1;
  margin: 0 5px;
  padding: 10px;
  font-size: 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-start {
  background-color: #28a745;
  color: #fff;
}

.btn-stop {
  background-color: #dc3545;
  color: #fff;
}

.btn-clear {
  background-color: #ffc107;
  color: #333;
}

.btn-export {
  background-color: #007bff;
  color: #fff;
}

.btn:disabled {
  background-color: #e9ecef;
  color: #666;
  cursor: not-allowed;
}

.data-dashboard {
  background-color: #fff;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 10px;
}

.stat-card {
  background-color: #f8f9fa;
  padding: 10px;
  border-radius: 4px;
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.stat-value {
  font-size: 22px;
  font-weight: bold;
  color: #333;
}

.stat-unit {
  font-size: 14px;
  color: #999;
}

.chart-controls {
  background-color: #fff;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.chart-settings {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.setting-item {
  flex: 1;
  min-width: 150px;
}

.setting-label {
  font-size: 14px;
  color: #333;
  margin-bottom: 5px;
  display: block;
}

.chart-container {
  position: relative;
  background-color: #fff;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.chart-title {
  font-size: 18px;
  font-weight: bold;
  color: #007bff;
  margin-bottom: 10px;
}

.chart-wrapper {
  position: relative;
  width: 100%;
  height: 400px;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}

.chart-tooltip {
  position: absolute;
  background-color: rgba(0, 0, 0, 0.7);
  color: #fff;
  padding: 8px;
  border-radius: 4px;
  font-size: 14px;
  pointer-events: none;
}

.chart-info {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #666;
}

.info-label {
  font-weight: bold;
}

.spectrum-container {
  background-color: #fff;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  background-color: rgba(0, 0, 0, 0.8);
  color: #fff;
  padding: 10px 15px;
  border-radius: 4px;
  font-size: 14px;
  z-index: 1000;
  transition: opacity 0.3s;
}

.toast.success {
  background-color: rgba(40, 167, 69, 0.9);
}

.toast.warning {
  background-color: rgba(255, 193, 7, 0.9);
}

.toast.error {
  background-color: rgba(220, 53, 69, 0.9);
}
</style>