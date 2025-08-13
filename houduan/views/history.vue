<template>
  <div class="history-test">
    <button class="back-button" @click="goBack">返回主页</button>
    <h1 class="title">历史报告</h1>
    <!--
    <button @click="loadHistory" :disabled="!userId">
      加载历史报告
    </button>
    -->
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else>
      <ul v-if="history.length" class="history-list">
        <li
          v-for="item in history"
          :key="item.report_name"
          class="report-item"
        >
          <!-- 报告名作为原生下载链接 -->
          <a
            :href="`${apiBase}/api/download/${encodeURIComponent(userName)}/${encodeURIComponent(item.report_name)}`"
            download
            class="report-link"
          >
            📄 {{ item.report_name }}
          </a>

          <ul v-if="item.advice.length" class="advice-list">
            <li v-for="adv in item.advice" :key="adv.date">
              <span class="advice-date">{{ adv.date }}</span> —
              <span class="advice-text">{{ adv.doctor_feedback }}</span>
              <span class="doctor-name">（{{ adv.doctor_name }}）</span>
              <br />
              <span class="doctor-attitude">医生态度：{{ adv.doc_judge }}</span>
            </li>
          </ul>
          <div v-else class="no-advice">暂无医生建议</div>
        </li>
      </ul>
      <p v-else class="no-history">没有找到任何历史报告</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'HistoryTest',
  data() {
    return {
      apiBase: 'http://115.190.118.22:5000', // 后端地址
      userId: '',      // 从 localStorage 中读取的用户 ID
      userName: '',    // 从 localStorage 中读取的用户名
      history: [],     // 历史数据
      loading: false   // 加载状态
    }
  },
  methods: {
    goBack() {
      this.$router.push({ path: "/homepage" });
    },
    async loadHistory() {
      if (!this.userId) {
        return alert('未找到用户ID，请先登录')
      }
      this.loading = true
      try {
        const res = await axios.get(
          `${this.apiBase}/api/history/${encodeURIComponent(this.userId)}`
        )
        if (res.data.success) {
          this.history = res.data.history
        } else {
          alert('获取失败：' + (res.data.message || '未知错误'))
          this.history = []
        }
      } catch (err) {
        console.error(err)
        alert('请求出错，请检查后端服务')
        this.history = []
      } finally {
        this.loading = false
      }
    }
  },
  mounted() {
    // 1. 先读取 ID
    this.userId = localStorage.getItem('id') || ''

    // 2. 再尝试从 userFormData 里解析出 name
    const savedData = localStorage.getItem('userFormData');
    if (savedData) {
      try {
        const parsedData = JSON.parse(savedData);
        this.userName = parsedData.name || '';  // 确保读取 name 字段
      } catch {
        this.userName = '';
      }
    }
    // 3. 如果有 userId，就直接加载历史
    if (this.userId) {
      this.loadHistory()
    }
  }
}
</script>

<style scoped>
.title {
  font-size: 28px;
  color: #2c3e50;
  margin-top: 30px; /* 调整顶部间距，向上移动 */
  margin-bottom: 30px; /* 调整底部间距 */
  text-align: center;
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
.history-test {
  max-width: 600px;
  margin: 10px auto;
  font-family: Arial, sans-serif;
}
button {
  padding: 6px 12px;
  margin: 0 8px 8px 0;
}
.loading {
  font-style: italic;
  color: #555;
}
.history-list {
  list-style: none;
  padding: 0;
}
.report-item {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}
.report-link {
  font-weight: bold;
  text-decoration: none;
  cursor: pointer;
}
.report-link:hover {
  text-decoration: underline;
}
.advice-list {
  margin: 8px 0 0 24px;
  list-style: disc;
}
.advice-date {
  color: #555;
  font-size: 0.9em;
}
.advice-text {
  margin-left: 4px;
}
.doctor-name {
  font-style: italic;
  color: #777;
}
.doctor-attitude {
  color: #444;
  margin-left: 24px;
  display: inline-block;
  font-size: 0.9em;
}
.no-history,
.no-advice {
  color: #888;
  font-style: italic;
}
</style>
