<template>
  <div class="assessment-container">
    <button class="btn btn-back" @click="goBack">← 返回方案选择</button>
    <h1>初始肌电信号评估</h1>

    <div class="status-section">
      <div class="status-item">
        <span class="label">当前模型:</span>
        <span class="value">{{ currentModel || '--' }}</span>
      </div>
      <div class="status-item">
        <span class="label">评估状态:</span>
        <span class="value" :class="assessing ? 'in-progress' : 'idle'">
          {{ assessing ? '评估中...' : (finished ? '评估完成' : '等待开始') }}
        </span>
      </div>
      <div class="status-item" v-if="assessing || finished">
        <span class="label">实时肌电值:</span>
        <span class="value">{{ emgValue !== null ? emgValue : '--' }}</span>
      </div>
      <div class="status-item" v-if="assessing">
        <span class="label">剩余时间:</span>
        <span class="value">{{ remainSeconds }} 秒</span>
      </div>
    </div>

    <div class="action-section">
  <button class="btn btn-primary" :disabled="assessing" @click="startAssessment">
    🚀 开始评估
  </button>
  <button class="btn btn-secondary" :disabled="!assessing" @click="cancelAssessment">
    ❌ 取消评估
  </button>
  <button class="btn btn-skip" @click="goToAIPlan">
    跳过评估 →
  </button>
</div>


    <div class="result-section" v-if="finished && plan">
      <h2>训练计划</h2>
      <pre>{{ formattedPlan }}</pre>
      <button class="btn btn-primary" @click="goToAIPlan">AI方案已生成</button>
    </div>

    <div class="result-section" v-if="noSignalDetected">
      <h2>未检测到肌电信号</h2>
      <p>可返回方案选择进行自定义训练计划。</p>
      <button class="btn btn-primary" @click="goBack">返回方案选择</button>
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
  name: 'Assessment',
  data() {
    return {
      baseURL: 'http://115.190.134.66:5000',
      currentModel: '',
      assessing: false,
      finished: false,
      emgValue: null,
      remainSeconds: 0,
      plan: null,
      eventSource: null,
      toast: {
        show: false,
        message: '',
        type: 'success',
      },
      noSignalTimeout: null,
      noSignalDetected: false,
    }
  },
  created() {
    this.currentModel = localStorage.getItem('currentModel') || ''
    if (!this.currentModel) {
      this.showToast('请先选择模型', 'error')
      this.$router.push({ name: 'AI choose' })
    }
  },
  beforeUnmount() {
    this.closeEventSource()
  },
  methods: {
    goToAIPlan() {
      this.$router.push({ path: '/aiplan' })
    },
    goBack() {
      this.$router.push({ path: '/trainingplan' })
    },
    startAssessment() {
      if (!this.currentModel) {
        this.showToast('请先选择模型', 'error')
        this.$router.push({ name: 'AI choose' })
        return
      }

      const id = localStorage.getItem('id')
      if (!id) {
        this.showToast('未找到用户 ID，请重新登录', 'error')
        this.assessing = false
        return
      }

      this.assessing = true
      this.finished = false
      this.emgValue = null
      this.remainSeconds = 0
      this.plan = null
      this.noSignalDetected = false

      if (this.noSignalTimeout) clearTimeout(this.noSignalTimeout)
      this.noSignalTimeout = setTimeout(() => {
        if (this.assessing && this.emgValue === null) {
          this.noSignalDetected = true
          this.showToast('未检测到肌电信号值，可返回方案选择进行自定义设计', 'error')
        }
      }, 5000)

      // 先发POST请求启动评估
      axios.post(`${this.baseURL}/api/initial-assessment`, { id })
        .then(() => {
          // 成功后用EventSource监听服务端推送，url携带id参数
          this.eventSource = new EventSource(`${this.baseURL}/api/initial-assessment?id=${encodeURIComponent(id)}`)

          this.eventSource.onmessage = (event) => {
            try {
              const data = JSON.parse(event.data)
              if (data.error) {
                this.showToast(data.error, 'error')
                this.assessing = false
                this.closeEventSource()
                return
              }
              if (data.finished) {
                this.plan = data.plan || null
                this.assessing = false
                this.finished = true
                this.closeEventSource()
                return
              }
              this.emgValue = data.emg_value ?? null
              this.remainSeconds = data.remain_seconds ?? 0

              if (data.emg_value !== undefined && this.noSignalTimeout) {
                clearTimeout(this.noSignalTimeout)
                this.noSignalTimeout = null
              }
            } catch (err) {
              console.error('解析评估数据失败', err)
            }
          }

          this.eventSource.onerror = (err) => {
            console.error('评估连接错误', err)
            this.showToast('评估过程中出现错误', 'error')
            this.assessing = false
            this.closeEventSource()
          }
        })
        .catch(error => {
          console.error('启动评估失败', error)
          this.showToast('启动评估失败，请稍后重试', 'error')
          this.assessing = false
        })
    }, startAssessment() {
      if (!this.currentModel) {
        this.showToast('请先选择模型', 'error')
        this.$router.push({ name: 'AI choose' })
        return
      }

      const id = localStorage.getItem('id')
      if (!id || id === 'null') {
        this.showToast('未找到用户 ID，请重新登录', 'error')
        this.assessing = false
        return
      }

      this.assessing = true
      this.finished = false
      this.emgValue = null
      this.remainSeconds = 0
      this.plan = null
      this.noSignalDetected = false

      if (this.noSignalTimeout) clearTimeout(this.noSignalTimeout)
      this.noSignalTimeout = setTimeout(() => {
        if (this.assessing && this.emgValue === null) {
          this.noSignalDetected = true
          this.showToast('未检测到肌电信号值，可返回方案选择进行自定义设计', 'error')
        }
      }, 5000)

      // ✅ 直接开启 EventSource，不需要发 POST 请求
      this.eventSource = new EventSource(`${this.baseURL}/api/initial-assessment?id=${encodeURIComponent(id)}`)

      this.eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (data.error) {
            this.showToast(data.error, 'error')
            this.assessing = false
            this.closeEventSource()
            return
          }
          if (data.finished) {
            this.plan = data.plan || null
            this.assessing = false
            this.finished = true
            this.closeEventSource()
            return
          }
          this.emgValue = data.emg_value ?? null
          this.remainSeconds = data.remain_seconds ?? 0

          if (data.emg_value !== undefined && this.noSignalTimeout) {
            clearTimeout(this.noSignalTimeout)
            this.noSignalTimeout = null
          }
        } catch (err) {
          console.error('解析评估数据失败', err)
        }
      }

      this.eventSource.onerror = (err) => {
        console.error('评估连接错误', err)
        this.showToast('评估过程中出现错误', 'error')
        this.assessing = false
        this.closeEventSource()
      }
    },


    cancelAssessment() {
      this.assessing = false
      this.finished = false
      this.emgValue = null
      this.remainSeconds = 0
      this.plan = null
      this.noSignalDetected = false
      if (this.noSignalTimeout) {
        clearTimeout(this.noSignalTimeout)
        this.noSignalTimeout = null
      }
      this.closeEventSource()
      this.showToast('已取消评估', 'success')
    },
    closeEventSource() {
      if (this.eventSource) {
        this.eventSource.close()
        this.eventSource = null
      }
      if (this.noSignalTimeout) {
        clearTimeout(this.noSignalTimeout)
        this.noSignalTimeout = null
      }
    },
    showToast(message, type = 'success') {
      this.toast = { show: true, message, type }
      setTimeout(() => {
        this.toast.show = false
      }, 4000)
    }
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
  computed: {
    formattedPlan() {
      if (!this.plan) return ''
      if (typeof this.plan === 'string') return this.plan
      return JSON.stringify(this.plan, null, 2)
    }
  }
}
</script>

<style scoped>
.assessment-container {
  max-width: 720px;
  margin: 20px auto;
  padding: 20px;
  font-family: "Microsoft YaHei", Arial, sans-serif;
  color: #333;
  background: #fafafa;
  border-radius: 8px;
  border: 1px solid #ddd;
}

h1 {
  margin-bottom: 20px;
  font-weight: 700;
}

.status-section {
  margin-bottom: 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.status-item {
  min-width: 200px;
  font-size: 1em;
}

.label {
  font-weight: 600;
  margin-right: 6px;
}

.value {
  color: #555;
}

.in-progress {
  color: #409eff;
  font-weight: 700;
}

.idle {
  color: #999;
}

.action-section {
  margin-bottom: 20px;
  display: flex;
  gap: 12px;
}

.btn {
  padding: 8px 18px;
  font-size: 1em;
  border-radius: 5px;
  border: none;
  cursor: pointer;
  user-select: none;
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
  border: 1px solid #ccc;
}

.btn-secondary:disabled {
  color: #aaa;
  cursor: not-allowed;
}

.result-section {
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 16px;
  white-space: pre-wrap;
  font-family: Consolas, monospace;
  font-size: 0.9em;
  margin-top: 20px;
}

.result-section button {
  margin-top: 16px;
  padding: 8px 16px;
  font-size: 1em;
  border-radius: 5px;
  border: none;
  cursor: pointer;
  background-color: #409eff;
  color: white;
  transition: background-color 0.3s;
}

.result-section button:hover {
  background-color: #2c7be5;
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
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.toast.success {
  background-color: #4caf50;
}

.toast.error {
  background-color: #f44336;
}

.toast-icon {
  font-size: 1.2em;
}

.toast-text {
  font-size: 1em;
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.5s;
}

.toast-enter,
.toast-leave-to {
  opacity: 0;
}

.btn-back {
  margin-bottom: 12px;
  padding: 6px 12px;
  background-color: transparent;
  border: 1px solid #409eff;
  color: #409eff;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  user-select: none;
  transition: background-color 0.3s ease;
}

.btn-back:hover {
  background-color: #e6f0ff;
}

.btn-skip {
  background-color: #67c23a;
  color: white;
  padding: 8px 18px;
  font-size: 1em;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.btn-skip:hover {
  background-color: #5daf34;
}

</style>