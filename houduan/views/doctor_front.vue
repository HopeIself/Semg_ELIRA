<template>
  <div>
    <!-- 背景容器 -->
    <div class="background-layer"></div>
    <div id="app">
      <button class="login-button" @click="goLogin">退出登录</button>
      <!-- 顶部标题 -->
      <h1 class="main-title">医生端系统</h1>

      <!-- 患者列表视图 -->
      <div v-if="view === 'patientList'">
        <!-- 顶部按钮组 -->
        <div class="top-buttons">
          <button class="styled-btn" @click="goToDescription">个人信息</button>
          <button class="styled-btn" @click="goToAddPatient">添加患者</button>
        </div>

        <!-- 患者列表标题 -->
        <h2 class="sub-title">患者列表</h2>
        <button
          class="view-report-btn"
          v-for="patient in patientList"
          :key="patient.patient_id"
          @click="viewReport(patient)"
        >
          {{ patient.patient_name }} 的报告
        </button>
      </div>

      <!-- 报告及建议视图 -->
      <div v-if="view === 'report'">
        <h2>患者 {{ selectedPatient }} 的康复报告</h2>

        <ul>
          <li v-for="(report, index) in reportList" :key="index" style="margin-bottom: 20px;">
            <div style="display: flex; align-items: center; flex-wrap: wrap;">
              <a
                :href="`http://115.190.118.22:5000/api/download/${selectedPatient}/${report}`"
                target="_blank"
                style="flex-shrink: 0;"
              >
                📄 {{ report }}
              </a>

              <!-- 建议输入框 -->
              <input
                v-model="adviceInputs[report]"
                placeholder="请输入建议"
                style="margin: 0 10px; width: 250px;"
              />

              <!-- 态度选择下拉框 -->
              <select v-model="attitudeInputs[report]" style="margin-right: 10px;">
                <option disabled value="">请选择对于AI下一步计划的态度</option>
                <option value="接受">接受</option>
                <option value="部分接受">部分接受</option>
                <option value="不接受">不接受</option>
              </select>

              <button
                @click="submitAdvice(report)"
                :disabled="loading[report]"
                style="white-space: nowrap;"
              >
                {{ loading[report] ? '提交中...' : '提交建议' }}
              </button>
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
                  <span>{{ item.date }} — {{ item.doctor_feedback }}</span>
                  <span style="font-style: italic; color: gray;">
                    (医生: {{ item.doctor_name }}, 态度: {{ item.doc_judge || '无' }})
                  </span>
                </li>
              </ul>
            </div>
            <hr />
          </li>
        </ul>

        <button class="back-button" @click="goBack">返回患者列表</button>
      </div>

      <!-- Coze Web Chat -->
      <div id="coze-chat"></div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      view: 'patientList', // 当前视图
      patientList: [], // 患者列表
      selectedPatient: '', // 当前选中患者（user_name）
      reportList: [], // 该患者的报告文件名列表
      adviceInputs: {}, // 存储每个报告对应的建议输入内容
      attitudeInputs: {}, // 存储每个报告对应的“态度”选择
      loading: {}, // 存储每个报告提交按钮的加载状态
      adviceHistory: [] // 历史建议
    }
  },
  methods: {
    goToDescription() {
      this.$router.push({ path: '/description' })
    },
    goToAddPatient() {
      this.$router.push({ path: '/add_patient' })
    },
    goLogin() {
      this.$router.push({ path: '/' })
    },

    async fetchPatients() {
      const doctorId = localStorage.getItem('id')
      if (!doctorId) {
        return alert('未找到医生ID')
      }
      try {
        const res = await axios.get(`http://115.190.118.22:5000/api/get_patient_data?doctorId=${doctorId}`)
        this.patientList = res.data.patient_data || []
      } catch (err) {
        console.error(err)
        alert('请求失败，请检查后端服务')
      }
    },

    async fetchReports(patientId) {
      try {
        const res = await axios.get(`http://115.190.118.22:5000/api/reports?patientId=${patientId}`)
        if (res.data.success) {
          this.reportList = res.data.reports || []
          this.adviceInputs = {}
          this.attitudeInputs = {}
          this.loading = {}
          this.reportList.forEach((r) => {
            this.adviceInputs[r] = ''
            this.attitudeInputs[r] = ''
            this.loading[r] = false
          })
        } else {
          alert('无法获取报告列表')
        }
      } catch (err) {
        console.error(err)
        alert('请求失败，请检查后端服务')
      }
    },

    async fetchAdviceHistory() {
      try {
        const res = await axios.get(`http://115.190.118.22:5000/api/showadvice/${this.selectedPatient}`)
        if (res.data.success) {
          this.adviceHistory = res.data.advice
        } else {
          console.warn('获取历史建议失败：', res.data.message)
          this.adviceHistory = []
        }
      } catch (err) {
        console.error('请求历史建议时出错：', err)
        this.adviceHistory = []
      }
    },

    async viewReport(patient) {
      this.selectedPatient = patient.patient_name
      await this.fetchReports(patient.patient_id)
      await this.fetchAdviceHistory()
      this.view = 'report'
    },

    goBack() {
      this.view = 'patientList'
    },

    filteredAdvice(reportName) {
      return this.adviceHistory.filter((item) => item.report_name === reportName)
    },

    async submitAdvice(reportFile) {
      const content = this.adviceInputs[reportFile]
      const attitude = this.attitudeInputs[reportFile]
      if (!content) {
        return alert('建议内容不能为空')
      }
      if (!attitude) {
        return alert('请选择对AI的态度')
      }

      const doctorInfo = localStorage.getItem('doctor_info')
      if (!doctorInfo) {
        return alert('医生信息未找到，请重新登录')
      }
      const doctorName = JSON.parse(doctorInfo).name

      this.loading[reportFile] = true
      try {
        const res = await axios.post(
          `http://115.190.118.22:5000/api/advice/${this.selectedPatient}`,
          {
            report_name: reportFile,
            advice: content,
            doctor_name: doctorName,
            doc_judge: attitude // 传送态度字段
          }
        )
        if (res.data.success) {
          alert('建议提交成功')
          this.adviceInputs[reportFile] = ''
          this.attitudeInputs[reportFile] = ''
          await this.fetchAdviceHistory()
        } else {
          alert('提交失败：' + res.data.message)
        }
      } catch (err) {
        console.error(err)
        alert('请求失败，请检查后端服务')
      }
      this.loading[reportFile] = false
    }
  },
  mounted() {
    this.fetchPatients()

    // 挂载 Coze Web Chat
    const script = document.createElement('script')
    script.src = 'https://lf-cdn.coze.cn/obj/unpkg/flow-platform/chat-app-sdk/1.2.0-beta.10/libs/cn/index.js'
    script.onload = () => {
      new CozeWebSDK.WebChatClient({
        config: { bot_id: '7526864409868976143' },
        componentProps: { title: 'Coze' },
        auth: {
          type: 'token',
          token: 'pat_pOwdWuNOdyj47fbSnmTR0EKWlezCrzQebx0VjeYJuNmZNAlF48EKBQZEDRK6W3ys',
          onRefreshToken: () =>
            'pat_pOwdWuNOdyj47fbSnmTR0EKWlezCrzQebx0VjeYJuNmZNAlF48EKBQZEDRK6W3ys'
        }
      })
    }
    document.body.appendChild(script)
  }
}
</script>

<style scoped>
.background-layer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: #f8faff; /* 你想设置的背景色 */
  z-index: 0;
}

/* 确保主容器内容盖在背景上 */
#app {
  position: relative;
  z-index: 1;
  height: 100vh;
}

button {
  margin: 5px;
  padding: 5px 10px;
}
input, select {
  padding: 5px;
}
#coze-chat {
  margin-top: 20px;
}

/* 居中大标题 */
.main-title {
  text-align: center;
  font-size: 28px;
  margin-bottom: 50px;
  margin-top: 150px;
  font-weight: bold;
}

/* 顶部按钮组样式（右对齐） */
.top-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-bottom: 10px;
  margin-top: 10px;
}

/* 美化按钮 */
.styled-btn {
  padding: 8px 16px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin-right: 80px;
}

.styled-btn:hover {
  background-color: #318ce7;
}
.sub-title {
  font-size: 24px;
  margin-bottom: 15px;
  margin-left: 100px;
}
button.view-report-btn {
  font-size: 16px; /* 控制文字大小 */
  padding: 10px 20px; /* 内边距更饱满 */
  background-color: #f0f0f0; /* 背景色柔和 */
  border: 1px solid #bbb; /* 边框更轻盈 */
  border-radius: 8px; /* 圆角 */
  cursor: pointer;
  margin: 5px;
  transition: all 0.2s ease-in-out;
  margin-left: 50px;
}

button.view-report-btn:hover {
  background-color: #dfefff; /* hover 高亮色 */
}

.login-button {
  font-family: 'Helvetica Neue', Arial, sans-serif;
  font-size: 22px;
  font-weight: bold;
  position: fixed;
  top: 20px;
  right: 20px;
  background: transparent;
  border: none;
  color: #333333; /* 文字颜色改为黑色 */
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
.back-button {
  font-family: 'Helvetica Neue', Arial, sans-serif;
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
</style>
