<template>
  <div class="personal-container">
    <button class="back-button" @click="goBack">← 主页</button>
    <h1 class="title">用户信息与 AI 模型选择</h1>

    <div class="form-card">
      <form @submit.prevent="submitForm" class="form-grid">
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
          <label>不适部位</label>
          <div class="checkbox-group">
            <label v-for="part in painParts" :key="part">
              <input type="checkbox" v-model="user.ache" :value="part" />
              {{ part }}
            </label>
          </div>
        </div>

        <div class="form-group">
          <label>AI 模型选择</label>
          <select v-model="user.ai_name" required>
            <option disabled value="">请选择模型</option>
            <option value="DeepSeek">DeepSeek</option>
            <option value="通义千问">通义千问</option>
            <option value="豆包">豆包</option>
          </select>
        </div>

        <div class="button-group">
          <button class="save-button" type="submit">提交</button>
        </div>
      </form>

      <div v-if="apiKey" class="api-result">
        <h3>所选 AI 的 API Key：</h3>
        <p>{{ apiKey }}</p>
      </div>

      <div v-if="errorMessage" class="error-msg">
        <p>{{ errorMessage }}</p>
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
        ache: [], // 确保是数组
        ai_name: "",
      },
      painParts: ["手掌", "手腕", "手臂"],
      apiKey: null,
      errorMessage: null,
    };
  },
  mounted() {
    const storedId = localStorage.getItem("id");
    if (storedId) {
      this.user.id = storedId;
    } else {
      this.errorMessage = "无法获取用户ID，请确保ID已存储在 localStorage 中";
    }

    const savedForm = localStorage.getItem("userFormData");
    if (savedForm) {
      try {
        const parsed = JSON.parse(savedForm);
        // 兼容性处理，保证 ache 是数组
        parsed.ache = Array.isArray(parsed.ache)
          ? parsed.ache
          : typeof parsed.ache === "string" && parsed.ache.length > 0
          ? parsed.ache.split(",")
          : [];
        this.user = { ...this.user, ...parsed };
      } catch (e) {
        console.error("恢复用户表单失败", e);
      }
    }
  },
  methods: {
    async submitForm() {
      this.errorMessage = null;
      this.apiKey = null;

      // 构造提交对象，确保ache是字符串
      const payload = {
        id: this.user.id,
        name: this.user.name,
        age: this.user.age,
        gender: this.user.gender,
        ache: Array.isArray(this.user.ache) ? this.user.ache.join(",") : "",
        ai_name: this.user.ai_name,
      };

      try {
        const response = await axios.post("http://115.190.118.22:5000/api/feature-lookup", payload);
        this.apiKey = response.data.api_key;

        // 保存当前表单数据，ache保持数组形式，方便恢复
        localStorage.setItem("userFormData", JSON.stringify(this.user));
      } catch (error) {
        if (error.response) {
          this.errorMessage = error.response.data.error;
        } else {
          this.errorMessage = "请求失败，请稍后再试";
        }
      }
    },
    goBack() {
      this.$router.push({ path: "/homepage" });
    },
  },
};
</script>

<style scoped>
.personal-container {
  height: 100vh;
  box-sizing: border-box;
  padding: 0 20px;
  background: linear-gradient(to right, #e9f4fc, #f4faff);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center; /* 页面垂直居中 */
  font-family: "Helvetica Neue", Arial, sans-serif;
  position: relative;
}

.title {
  font-size: 28px;
  color: #2c3e50;
  margin-bottom: 20px;
  text-align: center;
}

.form-wrapper {
  width: 100%;
  max-width: 800px;
  margin-top: 20px; /* 让表单稍微下移 */
}

.form-card {
  background: white;
  border-radius: 16px;
  padding: 30px 40px;
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
  justify-content: center;
  margin-top: 10px;
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
  color: #d32f2f;
  background-color: #ffebee;
  padding: 10px 15px;
  border-left: 4px solid #f44336;
  font-size: 14px;
}

.back-button {
  position: fixed;
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
</style>