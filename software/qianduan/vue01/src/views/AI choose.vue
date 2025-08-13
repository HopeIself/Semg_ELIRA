<template>
  <div class="ai-model-selector">
    <button class="back-button" @click="goback">← 个人情况</button>
    <div class="container">
      <h1 class="title">AI 模型选择器</h1>
      <div class="subtitle">服务器地址: 115.190.134.66:5000</div>

      <!-- 模型选择区块左右并排 -->
      <div class="model-selection-wrapper" v-if="models.length > 0">
        <!-- 模型列表卡片 -->
        <div class="model-card">
          <h2 class="card-title">
            <i class="icon">🤖</i>
            可用模型列表
          </h2>

          <div class="refresh-section">
            <button @click="loadModels" class="btn btn-refresh" :disabled="loading.models">
              <i class="btn-icon" :class="{ 'loading-spin': loading.models }">
                {{ loading.models ? '⏳' : '🔄' }}
              </i>
              {{ loading.models ? '加载中...' : '刷新模型列表' }}
            </button>
          </div>

          <div class="models-list" v-if="!loading.models && models.length > 0">
            <div
              v-for="model in models"
              :key="model.name"
              class="model-item"
              :class="{ 'selected': selectedModel?.name === model.name, 'unavailable': !model.available, 'current': currentModel === model.name }"
              @click="selectModel(model)"
            >
              <div class="model-header">
                <div class="model-name">{{ model.name }}</div>
                <div class="model-status">
                  <span class="status-badge" :class="model.available ? 'available' : 'unavailable'">
                    {{ model.available ? '✅ 可用' : '❌ 不可用' }}
                  </span>
                </div>
              </div>

              <div class="model-info">
                <div class="model-description">{{ model.description || '暂无描述' }}</div>
                <div v-if="model.requiresApiKey" class="api-key-hint">🔑 需要 API 密钥</div>
              </div>

              <div v-if="currentModel === model.name" class="current-badge">当前使用</div>
            </div>
          </div>

          <div v-else-if="loading.models" class="loading-state">
            <div class="loading-spinner">⏳</div>
            <div class="loading-text">正在获取模型列表...</div>
          </div>

          <div v-else class="empty-state">
            <div class="empty-icon">📭</div>
            <div class="empty-text">暂无可用模型</div>
            <button @click="loadModels" class="btn btn-secondary">重新加载</button>
          </div>
        </div>

        <!-- 选择模型卡片 -->
        <div class="selection-card" v-if="selectedModel">
          <h3 class="card-title">
            <i class="icon">🎯</i>
            选择模型: {{ selectedModel.name }}
          </h3>

          <div class="selection-info">
            <div class="info-item">
              <span class="info-label">模型名称:</span>
              <span class="info-value">{{ selectedModel.name }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">可用状态:</span>
              <span class="info-value" :class="selectedModel.available ? 'text-success' : 'text-error'">
                {{ selectedModel.available ? '可用' : '不可用' }}
              </span>
            </div>
            <div class="info-item" v-if="selectedModel.requiresApiKey">
              <span class="info-label">API 密钥:</span>
              <span class="info-value">{{ selectedModel.apiKey ? '已配置' : '未配置' }}</span>
            </div>
          </div>

          <div class="action-buttons">
            <button
              @click="confirmSelection"
              class="btn btn-primary"
              :disabled="!selectedModel.available || loading.selection || (selectedModel.requiresApiKey && !selectedModel.apiKey)"
            >
              <i class="btn-icon" v-if="!loading.selection">✅</i>
              <i class="btn-icon loading-spin" v-else>⏳</i>
              {{ loading.selection ? '选择中...' : '确认选择' }}
            </button>

            <button @click="cancelSelection" class="btn btn-secondary" :disabled="loading.selection">
              <i class="btn-icon">❌</i>
              取消
            </button>
          </div>
        </div>
      </div>

      <!-- 当前模型状态 -->
      <div class="status-card" v-if="currentModel">
        <h3 class="card-title">
          <i class="icon">ℹ️</i>
          当前状态
        </h3>
        <div class="status-content">
          <div class="status-item">
            <span class="status-label">当前模型:</span>
            <span class="status-value">{{ currentModel }}</span>
          </div>
          <div class="status-item">
            <span class="status-label">连接状态:</span>
            <span class="status-value status-connected">🟢 已连接</span>
          </div>
          <div class="status-item">
            <span class="status-label">最后选择时间:</span>
            <span class="status-value">{{ lastSelectionTime }}</span>
          </div>
        </div>
      </div>

      <transition name="toast">
        <div v-if="toast.show" class="toast" :class="toast.type">
          <i class="toast-icon">{{ toast.type === 'success' ? '✅' : '❌' }}</i>
          <span class="toast-text">{{ toast.message }}</span>
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'AIModelSelector',
  data() {
    return {
      baseURL: 'http://115.190.134.66:5000',
      models: [],
      selectedModel: null,
      currentModel: '',
      lastSelectionTime: '',
      loading: {
        models: false,
        selection: false
      },
      toast: {
        show: false,
        message: '',
        type: 'success'
      }
    }
  },
  mounted() {
    this.loadModels()
    this.currentModel = localStorage.getItem('currentModel') || ''
    this.lastSelectionTime = localStorage.getItem('lastSelectionTime') || ''
  },
  methods: {
    goback() {
      this.$router.push({ path: '/personal' });
    },

    async loadModels() {
      this.loading.models = true
      try {
        const response = await axios.get(`${this.baseURL}/api/models`, { timeout: 10000 })
        let modelData = response.data
        if (modelData.models) modelData = modelData.models
        this.models = this.processModelData(modelData)
        this.showToast('模型列表加载成功', 'success')
      } catch (error) {
        console.error('加载模型失败:', error)
        this.showToast('加载模型失败，使用模拟数据', 'error')
        this.models = this.getMockData()
      } finally {
        this.loading.models = false
      }
    },
    processModelData(data) {
      if (Array.isArray(data)) {
        return data.map(item => this.normalizeModelItem(item))
      } else if (typeof data === 'object') {
        return Object.entries(data).map(([key, value]) =>
          this.normalizeModelItem({ name: key, ...value })
        )
      }
      return []
    },
    normalizeModelItem(item) {
      if (typeof item === 'string') {
        return {
          name: item,
          available: true,
          // 删除多余“模型”文字
          description: item,
          requiresApiKey: item.includes('gpt') || item.includes('claude'),
          apiKey: this.getStoredApiKey(item)
        }
      }
      return {
        name: item.name || item.id || 'Unknown',
        available: item.available !== false,
        // 删除多余“模型”文字
        description: item.description || (item.name || item.id),
        requiresApiKey: item.requiresApiKey || item.requires_api_key || false,
        apiKey: this.getStoredApiKey(item.name || item.id)
      }
    },
    getStoredApiKey(modelName) {
      return localStorage.getItem(`apiKey_${modelName}`) || ''
    },
    storeApiKey(modelName, apiKey) {
      if (apiKey) {
        localStorage.setItem(`apiKey_${modelName}`, apiKey)
      } else {
        localStorage.removeItem(`apiKey_${modelName}`)
      }
    },
    selectModel(model) {
      if (!model.available) {
        this.showToast('该模型当前不可用', 'error')
        return
      }
      this.selectedModel = { ...model }
      if (model.requiresApiKey && !model.apiKey) {
        this.promptForApiKey()
      }
    },
    promptForApiKey() {
      const apiKey = prompt(`请输入 ${this.selectedModel.name} 的 API 密钥:`)
      if (apiKey) {
        this.selectedModel.apiKey = apiKey
        this.storeApiKey(this.selectedModel.name, apiKey)
      }
    },
    async confirmSelection() {
      if (!this.selectedModel) return
      this.loading.selection = true
      try {
        const payload = { model_id: this.selectedModel.name }
        if (this.selectedModel.requiresApiKey && this.selectedModel.apiKey) {
          payload.api_key = this.selectedModel.apiKey
        }
        const response = await axios.post(`${this.baseURL}/api/select-model`, payload, { timeout: 15000 })
        if (response.data.success) {
          this.currentModel = this.selectedModel.name
          this.lastSelectionTime = new Date().toLocaleString()

          // 保存到localStorage，供其他页面读取
          localStorage.setItem('currentModel', this.currentModel)
          localStorage.setItem('lastSelectionTime', this.lastSelectionTime)

          this.showToast(`成功选择 ${this.currentModel}`, 'success')
          this.selectedModel = null
        } else {
          throw new Error(response.data.error || '选择模型失败')
        }
        
      } catch (error) {
        console.error('选择模型失败:', error)
        this.showToast('选择模型失败', 'error')
      } finally {
        this.loading.selection = false
      }
    },
    cancelSelection() {
      this.selectedModel = null
    },
    showToast(message, type = 'success') {
      this.toast = { show: true, message, type }
      setTimeout(() => { this.toast.show = false }, 4000)
    },
    getMockData() {
      return [
        { name: 'gpt-3.5-turbo', available: true, description: 'OpenAI GPT-3.5 Turbo', requiresApiKey: true, apiKey: this.getStoredApiKey('gpt-3.5-turbo') },
        { name: 'gpt-4', available: true, description: 'OpenAI GPT-4', requiresApiKey: true, apiKey: this.getStoredApiKey('gpt-4') },
        { name: 'claude-3', available: false, description: 'Anthropic Claude 3', requiresApiKey: true, apiKey: this.getStoredApiKey('claude-3') },
        { name: 'local-model', available: true, description: '本地部署模型', requiresApiKey: false, apiKey: '' }
      ]
    }
  }
}
</script>

<style scoped>
.container {
  max-width: 720px;
  margin: 0 auto;
  padding: 20px;
  font-family: "Microsoft YaHei", Arial, sans-serif;
  color: #333;
}
.title {
  font-size: 2em;
  margin-bottom: 10px;
}
.subtitle {
  font-size: 0.9em;
  margin-bottom: 20px;
  color: #666;
}

/* 新增左右排列容器 */
.model-selection-wrapper {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.model-card, .selection-card {
  flex: 1;
  min-width: 300px;
}

.model-card, .selection-card, .status-card {
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 20px;
  background: #fafafa;
}
.card-title {
  font-size: 1.2em;
  margin-bottom: 10px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 6px;
}
.model-item {
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  user-select: none;
  display: flex;
  flex-direction: column;
}
.model-item.selected {
  border-color: #409eff;
  background-color: #e6f0ff;
}
.model-item.unavailable {
  color: #999;
  cursor: not-allowed;
  background-color: #f5f5f5;
}
.model-header {
  display: flex;
  justify-content: space-between;
  font-weight: 600;
}
.status-badge.available {
  color: green;
}
.status-badge.unavailable {
  color: red;
}
.api-key-hint {
  margin-top: 4px;
  font-size: 0.85em;
  color: #999;
}
.current-badge {
  font-size: 0.75em;
  color: #409eff;
  font-weight: 600;
  margin-top: 4px;
}
.info-item {
  margin-bottom: 6px;
}
.info-label {
  font-weight: 600;
}
.text-success {
  color: green;
}
.text-error {
  color: red;
}
.action-buttons {
  margin-top: 12px;
  display: flex;
  gap: 12px;
}
.btn {
  padding: 6px 16px;
  border-radius: 4px;
  border: none;
  font-size: 1em;
  cursor: pointer;
}
.btn-primary {
  background-color: #409eff;
  color: white;
}
.btn-primary:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}
.btn-secondary {
  background-color: #f5f5f5;
  color: #333;
}
.btn-secondary:disabled {
  color: #aaa;
  cursor: not-allowed;
}
.toast {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 20px;
  color: white;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  z-index: 9999;
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}
.toast.success {
  background-color: #4caf50;
}
.toast.error {
  background-color: #f44336;
}
.loading-spin {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  0% { transform: rotate(0deg);}
  100% { transform: rotate(360deg);}
}
.back-button {
  position: fixed;
  top: 0;
  left: 0;
  background-color: transparent;
  border: none;
  font-size: 24px;
  color: #e31111;
  cursor: pointer;
  padding: 10px;
  margin: 0;
  z-index: 1000;
}
.back-button:hover {
  text-decoration: underline;
}
</style>
