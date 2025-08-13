<template>
  <div class="ai-model-selector">
    <div class="container">
      <h1 class="title">AI 模型选择器</h1>
      <div class="subtitle">服务器地址: 115.190.134.66:5000</div>

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

      <!-- 初始评估功能 -->
      <div class="assessment-card" v-if="currentModel">
        <h3 class="card-title">
          <i class="icon">🧪</i>
          初始评估
        </h3>

        <button @click="startAssessment" class="btn btn-primary" :disabled="assessing">
          <i class="btn-icon" v-if="!assessing">🚀</i>
          <i class="btn-icon loading-spin" v-else>⏳</i>
          {{ assessing ? '评估中...' : '开始初始评估' }}
        </button>

        <div class="assessment-status" v-if="assessing || emgValue !== null">
          <div class="status-item">
            <span class="status-label">实时肌电值:</span>
            <span class="status-value">{{ emgValue ?? '--' }}</span>
          </div>
          <div class="status-item">
            <span class="status-label">剩余时间:</span>
            <span class="status-value">{{ remainSeconds }} 秒</span>
          </div>
        </div>

        <div class="assessment-result" v-if="plan">
          <h4>训练计划:</h4>
          <pre>{{ plan }}</pre>
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
      assessing: false,
      emgValue: null,
      remainSeconds: 0,
      plan: null,
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
  async mounted() {
    await this.loadModels()
  },
  methods: {
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
        this.showToast('加载模型失败', 'error')
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
          description: `${item} 模型`,
          requiresApiKey: item.includes('gpt') || item.includes('claude'),
          apiKey: this.getStoredApiKey(item)
        }
      }
      return {
        name: item.name || item.id || 'Unknown',
        available: item.available !== false,
        description: item.description || `${item.name || item.id} 模型`,
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
        const payload = { 
          model_id: this.selectedModel.name 
        }
        if (this.selectedModel.requiresApiKey && this.selectedModel.apiKey) {
          payload.api_key = this.selectedModel.apiKey
        }
        const response = await axios.post(`${this.baseURL}/api/select-model`, payload, { timeout: 15000 })
        if (response.data.success) {
          this.currentModel = this.selectedModel.name
          this.lastSelectionTime = new Date().toLocaleString()
          this.showToast(`成功选择 ${this.selectedModel.name} 模型`, 'success')
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
    startAssessment() {
      if (!this.currentModel) {
        this.showToast('请先选择模型', 'error')
        return
      }
      this.assessing = true
      this.emgValue = null
      this.remainSeconds = 0
      this.plan = null
      const id = localStorage.getItem('id') // 获取 ID
      if (!id) {
        this.showToast('未找到用户 ID', 'error')
        this.assessing = false
        return
      }
      // 使用 POST 发送 id
      axios.post(`${this.baseURL}/api/initial-assessment`, { id: id })
        .then(response => {
          const data = response.data
          if (data.error) {
            this.showToast(data.error, 'error')
            this.assessing = false
            return
          }
          if (data.finished) {
            this.plan = JSON.stringify(data.plan, null, 2)
            this.assessing = false
            // 评估完成后跳转到 /test_train 页面
            this.$router.push('/test_train')
            return
          }
          this.emgValue = data.emg_value
          this.remainSeconds = data.remain_seconds
        })
        .catch(err => {
          console.error('评估过程出错', err)
          this.showToast('评估过程中发生错误', 'error')
          this.assessing = false
        })
    },
    showToast(message, type = 'success') {
      this.toast = { show: true, message, type }
      setTimeout(() => { this.toast.show = false }, 4000)
    },
    getMockData() {
      return [
        { name: 'gpt-3.5-turbo', available: true, description: 'OpenAI GPT-3.5 Turbo 模型', requiresApiKey: true, apiKey: this.getStoredApiKey('gpt-3.5-turbo') },
        { name: 'gpt-4', available: true, description: 'OpenAI GPT-4 模型', requiresApiKey: true, apiKey: this.getStoredApiKey('gpt-4') },
        { name: 'claude-3', available: false, description: 'Anthropic Claude 3 模型', requiresApiKey: true, apiKey: this.getStoredApiKey('claude-3') },
        { name: 'local-model', available: true, description: '本地部署模型', requiresApiKey: false, apiKey: '' }
      ]
    }
  }
}
</script>
