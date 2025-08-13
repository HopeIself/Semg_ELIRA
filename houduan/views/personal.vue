<template>
  <div class="personal-container">
    <button class="back-button" @click="goBack">返回主页</button>
    <h1 class="title">个人情况</h1>

    <div class="form-card">
      <form @submit.prevent="submitForm" class="form-grid">
        <!-- 用户基本信息 -->
        <div class="form-group">
          <label>ID（只读）</label>
          <input type="text" v-model="user.id" readonly />
        </div>
        <div class="form-group">
          <label>姓名</label>
          <input type="text" v-model="user.name" required />
        </div>
        <div class="form-group">
          <label>年龄</label>
          <input type="number" v-model="user.age" required />
        </div>
        <div class="form-group">
          <label>性别</label>
          <select v-model="user.gender" required>
            <option disabled value="">请选择</option>
            <option value="male">男</option>
            <option value="female">女</option>
          </select>
        </div>

        <div class="form-group">
          <label>不适部位（可多选）</label>
          <div class="checkbox-group">
            <label v-for="part in painParts" :key="part">
              <input type="checkbox" v-model="user.ache" :value="part" /> {{ part }}
            </label>
          </div>
        </div>

        <!-- AI 模型选择 -->
        <div class="form-group">
          <label>AI 模型选择</label>
          <select v-model="user.ai_name" required>
            <option disabled value="">请选择模型</option>
            <option value="DeepSeek">DeepSeek</option>
            <option value="通义千问">通义千问</option>
            <option value="豆包">豆包</option>
          </select>
        </div>

        <!-- 医生搜索 & 选择 -->
        <div class="form-group">
          <label>选择医生</label>
          <input class="input-box" v-model="doctorKeyword" @input="onDoctorInput" placeholder="搜索医生姓名" />
          <ul v-if="doctorSuggestions.length" class="suggestion-list">
            <li v-for="doc in doctorSuggestions" :key="doc.id" @click="selectDoctor(doc)">
              {{ doc.name }} (专长: {{ doc.major }}，{{ doc.hospital }}, 简介: {{ doc.description }})
            </li>
          </ul>
          <p v-if="selectedDoctor" class="selected-doctor">
            已选医生：{{ selectedDoctor.name }}
          </p>
        </div>

        <!-- 提交按钮 & 提示 -->
        <div v-if="submitSuccess" class="success-msg">
          {{ serverMessage }}
        </div>
        <!-- 新增跳转到查看医生信息的页面 -->
        <div class="button-group">
          <button class="view-doctors-button" type="button" @click="goToDoctorsPage">
            查看所有医生信息
          </button>

          <!-- 新按钮，显示当前医生 -->
          <button class="show-doctor-button" type="button" @click="showCurrentDoctor">
            显示当前选择的医生
          </button>

          <button class="save-button" type="submit">提交</button>
        </div>
      </form>

      <div v-if="errorMessage" class="error-msg">
        <p>{{ errorMessage }}</p>
      </div>

      <div v-if="currentDoctor" class="doctor-info">
        <p>当前医生：{{ currentDoctor }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "AIUserForm",
  data() {
    return {
      user: {
        id: "",
        name: "",
        age: "",
        gender: "",
        ache: [],      // 数组格式
        ai_name: "",
        doctor_name: "",  // 新增 doctor_name 字段
      },
      painParts: ["手掌", "手腕", "手臂"],
      // 医生搜索相关
      doctorKeyword: "",
      doctorSuggestions: [],
      selectedDoctor: null,
      // 提交结果
      submitSuccess: false,
      serverMessage: "",
      errorMessage: "",
      currentDoctor: "",  // 当前医生信息
      debounceTimer: null
    };
  },
  mounted() {
  const storedId = localStorage.getItem("id");
  if (storedId) {
    this.user.id = storedId;
  } else {
    this.errorMessage = "无法获取用户ID，请确保ID已存储在 localStorage 中";
  }

  const saved = localStorage.getItem("userFormData");
  if (saved) {
    try {
      const parsed = JSON.parse(saved);
      parsed.ache = Array.isArray(parsed.ache)
        ? parsed.ache
        : (parsed.ache || "").split(",");
      this.user = { ...this.user, ...parsed };
    } catch { }
  }

  // 额外恢复 doctorKeyword
  const storedKeyword = localStorage.getItem("doctorKeyword");
  if (storedKeyword) {
    this.doctorKeyword = storedKeyword;
  }
},
  watch: {
    user: {
      handler(newVal) {
        // 每次 user 变化时保存到 localStorage
        localStorage.setItem("userFormData", JSON.stringify(newVal));
      },
      deep: true
    }
  },
  methods: {
    goBack() {
      this.$router.push({ path: "/homepage" });
    },
    onDoctorInput() {
      clearTimeout(this.debounceTimer);
      this.debounceTimer = setTimeout(this.searchDoctors, 300);
    },
    async searchDoctors() {
      if (!this.doctorKeyword.trim()) {
        this.doctorSuggestions = [];
        return;
      }
      try {
        const res = await axios.get(
          "http://115.190.118.22:5000/api/search_doctors",
          { params: { keyword: this.doctorKeyword } }
        );
        this.doctorSuggestions = res.data.doctors || [];
      } catch (err) {
        this.errorMessage = "搜索医生失败";
        this.doctorSuggestions = [];
      }
    },
    selectDoctor(doc) {
      this.selectedDoctor = doc;
      this.doctorKeyword = doc.name;
      this.doctorSuggestions = [];
    },
    async submitForm() {
      this.errorMessage = "";
      this.submitSuccess = false;
      this.serverMessage = "";

      const payload = {
        id: this.user.id,
        name: this.user.name,
        age: this.user.age,
        gender: this.user.gender,
        ache: this.user.ache.join(","),
        ai_name: this.user.ai_name,
        doctor_name: this.selectedDoctor ? this.selectedDoctor.name : "",
      };

      try {
        const resp = await axios.post(
          "http://115.190.118.22:5000/api/feature-lookup",
          payload
        );

        if (resp.data.success) {
          this.submitSuccess = true;
          this.serverMessage = resp.data.message || "提交成功";
          // 保存表单到 localStorage
          localStorage.setItem("userFormData", JSON.stringify(this.user));

          // 获取医生信息
          this.user.doctor_name = resp.data.doctor_name;

          // 如果医生已存在，展示成功信息
          if (resp.data.message && resp.data.message.includes("该医生已存在")) {
            this.serverMessage = `该医生已存在: ${resp.data.doctor_name}`;
          }
        } else {
          // 处理医生已存在的返回情况
          if (resp.data.message && resp.data.message.includes("该医生已存在")) {
            this.serverMessage = `该医生已存在: ${resp.data.doctor_name}`;
          } else {
            this.errorMessage = resp.data.error || "提交失败";
          }
        }
      } catch (err) {
        this.errorMessage =
          err.response?.data?.error || "网络或服务器错误，请稍后重试";
      }
    },

    // 新增方法：显示当前医生
    async showCurrentDoctor() {
      try {
        // 向后端发送用户的 ID 获取医生信息
        const resp = await axios.post(
          "http://115.190.118.22:5000/api/get_doctor",
          { id: this.user.id }
        );
        if (resp.data.doctor_name) {
          this.currentDoctor = resp.data.doctor_name; // 显示当前医生的名字
        } else {
          this.currentDoctor = "当前没有医生信息";
        }
      } catch (err) {
        this.errorMessage = "获取医生信息失败";
      }
    },

    // 新增方法：跳转到查看医生信息页面
    goToDoctorsPage() {
  // 保存表单数据到 localStorage
  localStorage.setItem("userFormData", JSON.stringify(this.user));
  localStorage.setItem("doctorKeyword", this.doctorKeyword); // 保存医生关键词

  // 然后跳转
  this.$router.push({ path: "/doctor" });
}
  }
};
</script>

<style scoped>
/* 医生选择 */
.suggestion-list {
  list-style: none;
  margin: 4px 0;
  padding: 0;
  border: 1px solid #ccc;
  max-height: 160px;
  overflow-y: auto;
}

.suggestion-list li {
  padding: 6px 10px;
  cursor: pointer;
}

.suggestion-list li:hover {
  background: #f0f0f0;
}

.selected-doctor {
  margin-top: 6px;
  font-size: 14px;
  color: #333;
}

.success-msg {
  margin-top: 20px;
  color: #2e7d32;
  background-color: #e8f5e9;
  padding: 10px 15px;
  border-left: 4px solid #4caf50;
  font-size: 14px;
}

.doctor-info {
  margin-top: 10px;
  color: #333;
  font-size: 16px;
  font-weight: bold;
}

.show-doctor-button {
  background-color: #007bff;
  color: white;
  padding: 10px 24px;
  font-size: 16px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.show-doctor-button:hover {
  background-color: #0056b3;
}

.suggestion-list {
  list-style: none;
  margin: 4px 0;
  padding: 0;
  border: 1px solid #ccc;
  max-height: 160px;
  overflow-y: auto;
}

.suggestion-list li {
  padding: 6px 10px;
  cursor: pointer;
}

.suggestion-list li:hover {
  background: #f0f0f0;
}

.selected-doctor {
  margin-top: 6px;
  font-size: 14px;
  color: #333;
}

.success-msg {
  margin-top: 20px;
  color: #2e7d32;
  background-color: #e8f5e9;
  padding: 10px 15px;
  border-left: 4px solid #4caf50;
  font-size: 14px;
}

.personal-container {
  width: 120vw;
  height: 100vh;
  box-sizing: border-box;
  padding: 0 20px;
  background: #f7f4e7;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  /* 页面垂直居中 */
  font-family: "Helvetica Neue", Arial, sans-serif;
  position: relative;
}

.title {
  font-size: 28px;
  color: #2c3e50;
  margin-bottom: 20px;
  /* 减小底部间距 */
  margin-top: -30px;
  /* 调整顶部间距，向上移动 */
  text-align: center;
}

.form-wrapper {
  width: 100%;
  max-width: 800px;
  margin-top: 20px;
  /* 让表单稍微下移 */
}

.form-card {
  background: white;
  border-radius: 16px;
  padding: 50px 60px;
  width: 46%;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
  box-sizing: border-box;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  column-gap: 30px;
  row-gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  font-size: 14px;
  color: #333;
}

.form-group label {
  margin-bottom: 6px;
  font-weight: 500;
}

.form-group input,
.form-group select {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 14px;
}

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 16px;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}

.button-group {
  grid-column: 1 / -1;
  display: flex;
  justify-content: space-between;
  /* 按钮之间水平均匀分布 */
  gap: 15px;
  /* 设置按钮之间的间距 */
  margin-top: 8px;
}

.save-button {
  background-color: #28a745;
  color: white;
  padding: 10px 24px;
  font-size: 16px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.save-button:hover {
  background-color: #218838;
}

.api-result {
  margin-top: 20px;
  padding: 10px 15px;
  background-color: #e8f5e9;
  border-left: 4px solid #4caf50;
  font-size: 14px;
}

.error-msg {
  margin-top: 20px;
  color: #333;
  background-color: #ffebee;
  padding: 10px 15px;
  border-left: 4px solid #333;
  font-size: 14px;
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

.view-doctors-button {
  background-color: #6c757d;
  /* 查看医生按钮：灰色 */
  color: white;
  border-radius: 8px;
  font-size: 16px;
}

.view-doctors-button:hover {
  background-color: #5a6268;
  /* 查看医生按钮悬停时的颜色变化 */
}
</style>