<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">患者康复建议查看</h1>

    <div class="mb-4">
      <label class="block mb-2 font-semibold">患者 ID：</label>
      <input v-model="patientId"
             @change="onPatientChange"
             placeholder="请输入患者 ID（如 p1）"
             class="border p-1 rounded w-full" />
    </div>

    <div v-if="adviceList.length">
      <h2 class="text-xl mb-2">康复建议记录：</h2>
      <ul class="list-disc ml-6">
        <li v-for="(item, index) in adviceList" :key="index">
          🗓️ {{ item.date }} - {{ item.content }}
        </li>
      </ul>
    </div>
    <div v-else class="text-gray-500">暂无建议</div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      patientId: 'p2',
      adviceList: [],
      lastAdviceCount: 0,  // 记录上次建议条数
      polling: null
    }
  },
  mounted() {
    this.startPolling()
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
  beforeUnmount() {
    clearInterval(this.polling)
  },
  methods: {
    async fetchAdvice(showAlertIfNew = true) {
      if (!this.patientId) return
      try {
        const res = await axios.get(`http://localhost:5000/api/advice/${this.patientId}`)
        if (res.data.success) {
          const newAdviceList = res.data.advice || []
          if (showAlertIfNew && newAdviceList.length > this.lastAdviceCount) {
            alert("🔔 您有新的医生建议，请及时查看")
          }
          this.adviceList = newAdviceList
          this.lastAdviceCount = newAdviceList.length
        }
      } catch (e) {
        console.error("请求失败：", e)
      }
    },
    startPolling() {
      this.fetchAdvice(false)
      this.polling = setInterval(() => this.fetchAdvice(true), 10000)
    },
    onPatientChange() {
      clearInterval(this.polling)
      this.lastAdviceCount = 0
      this.startPolling()
    }
  }
}
</script>

<style>
body {
  font-family: Arial, sans-serif;
}
</style>
