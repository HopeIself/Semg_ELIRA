<template>
  <div id="app">
    <!-- 顶部标题和右上角按钮 -->
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
      <h1>医生端系统</h1>
      <div>
        <button @click="goToDescription">个人信息</button>
        <button @click="goToAddPatient">添加患者</button>
      </div>
    </div>

    <!-- 患者列表视图 -->
    <div v-if="view === 'patientList'">
      <h2>患者列表</h2>
      <button
        v-for="patient in patientList"
        :key="patient.patient_id"
        @click="viewReport(patient)"
      >
        查看 {{ patient.patient_name }} 的报告
      </button>
    </div>
    
    <!-- 报告及建议视图 -->
    <div v-if="view === 'report'">
      <h2>患者 {{ selectedPatient }} 的康复报告</h2>
      
      <ul>
        <li v-for="(report, index) in reportList" :key="index" style="margin-bottom: 20px;">
          <div style="display: flex; align-items: center;">
            <a
              :href="`http://115.190.134.66:5000/api/download/${selectedPatient}/${report}`"
              target="_blank"
            >
              📄 {{ report }}
            </a>
            <input
              v-model="adviceInputs[report]"
              placeholder="请输入建议"
              style="margin: 0 10px; width: 250px;"
            />
            <button @click="submitAdvice(report)">提交建议</button>
          </div>
          
          <!-- 历史建议列表 -->
          <div v-if="filteredAdvice(report).length" style="margin-top: 8px; padding-left: 24px;">
            <strong>历史建议：</strong>
            <ul>
              <li
                v-for="(item, i) in filteredAdvice(report)"
                :key="i"
                style="font-size: 0.9em; margin: 2px 0;"
              >
                <span>{{ item.date }} — {{ item.doctor_feedback }} </span>
                <span style="font-style: italic; color: gray;">(医生: {{ item.doctor_name }})</span>
              </li>
            </ul>
          </div>
          <hr/>
        </li>
      </ul>
      
      <button @click="goBack">返回患者列表</button>
    </div>

    <!-- Coze Web Chat -->
    <div id="coze-chat"></div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      view: 'patientList',      // 当前视图
      patientList: [],          // 患者列表
      selectedPatient: '',      // 当前选中患者（user_name）
      reportList: [],           // 该患者的报告文件名列表
      adviceInputs: {},         // 用于存储每个 report 的输入框内容
      adviceHistory: []         // 存储从后端拉来的所有历史建议
    }
  },
  methods: {
    // 新增跳转方法
    goToDescription() {
      this.$router.push({ path: '/description' })
    },
    goToAddPatient() {
      this.$router.push({ path: '/add_patient' })
    },

    // 1. 拉取患者列表
    async fetchPatients() {
      const doctorId = localStorage.getItem('id')
      if (!doctorId) {
        return alert('未找到医生ID')
      }
      try {
        const res = await axios.get(`http://115.190.134.66:5000/api/get_patient_data?doctorId=${doctorId}`)
        this.patientList = res.data.patient_data || []
      } catch (err) {
        console.error(err)
        alert('请求失败，请检查后端服务')
      }
    },

    // 2. 拉取某个患者的报告列表
    async fetchReports(patientId) {
      try {
        const res = await axios.get(`http://115.190.134.66:5000/api/reports?patientId=${patientId}`)
        if (res.data.success) {
          this.reportList = res.data.reports || []
          this.adviceInputs = {}
          this.reportList.forEach(r => { this.adviceInputs[r] = '' })
        } else {
          alert('无法获取报告列表')
        }
      } catch (err) {
        console.error(err)
        alert('请求失败，请检查后端服务')
      }
    },

    // 3. 拉取历史建议
    async fetchAdviceHistory() {
      try {
        const res = await axios.get(`http://115.190.134.66:5000/api/showadvice/${this.selectedPatient}`)
        if (res.data.success) {
          this.adviceHistory = res.data.advice
        } else {
          console.warn('获取历史建议失败：', res.data.message)
        }
      } catch (err) {
        console.error('请求历史建议时出错：', err)
      }
    },

    // 4. 点击“查看报告”时，同时拉报告与历史建议
    async viewReport(patient) {
      this.selectedPatient = patient.patient_name
      await this.fetchReports(patient.patient_id)
      await this.fetchAdviceHistory()
      this.view = 'report'
    },

    goBack() {
      this.view = 'patientList'
    },

    // 5. 提交新的建议
    async submitAdvice(reportFile) {
      const content = this.adviceInputs[reportFile]
      if (!content) {
        return alert('建议内容不能为空')
      }
      const doctorName = JSON.parse(localStorage.getItem('doctor_info')).name;
      try {
        const res = await axios.post(
          `http://115.190.134.66:5000/api/advice/${this.selectedPatient}`,
          { report_name: reportFile, advice: content, doctor_name: doctorName }
        )
        if (res.data.success) {
          alert('建议提交成功')
          this.adviceInputs[reportFile] = ''
          await this.fetchAdviceHistory()
        } else {
          alert('提交失败')
        }
      } catch (err) {
        console.error(err)
        alert('请求失败，请检查后端服务')
      }
    },

    // 辅助：过滤出某个 report 对应的历史建议
    filteredAdvice(reportName) {
      return this.adviceHistory.filter(item => item.report_name === reportName)
    }
  },

  mounted() {
    this.fetchPatients()

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
  }
}
</script>

<style scoped>
#app {
  font-family: Arial, sans-serif;
  padding: 20px;
}
button {
  margin: 5px;
  padding: 5px 10px;
}
input {
  padding: 5px;
}
#coze-chat {
  margin-top: 20px;
}
</style>
