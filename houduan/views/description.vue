<template>
  <div>
    <!--背景容器-->
    <div class="background-layer"></div>
    <div class="container">
      <button class="back-button" @click="goBack">返回主页</button>
      <button class="login-button" @click="goLogin">退出登录</button>

      <h2>医生信息录入</h2>

      <form @submit.prevent="submitDoctorInfo" class="form">
        <label>
          医生ID（自动）:
          <input v-model="doctor.id" disabled />
        </label>

        <label>
          姓名:
          <input v-model="doctor.name" required />
        </label>

        <label>
          专业:
          <input v-model="doctor.major" required />
        </label>

        <label>
          学校:
          <input v-model="doctor.school" required />
        </label>

        <label>
          工作医院:
          <input v-model="doctor.hospital" required />
        </label>

        <label>
          描述（简要描述20字左右）:
          <textarea v-model="doctor.description" required></textarea>
        </label>

        <label>
          详细描述（可选）:
          <textarea v-model="doctor.detailedDescription" required></textarea>
        </label>

        <button type="submit">提交</button>
        <button type="button" @click="clearLocalData" style="margin-left: 12px;">清空本地缓存</button>
      </form>

      <div v-if="message" class="message">{{ message }}</div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      doctor: {
        id: '',
        name: '',
        major: '',
        school: '',
        hospital: '', // 新增字段
        description: '',
        detailedDescription: '',
      },
      message: ''
    };
  },
  methods: {
    goBack() {
      this.$router.push({ path: "/doctor_front" });
    },
    goLogin() {
      this.$router.push({ path: "/" });
    },
    async submitDoctorInfo() {
      try {
        const response = await fetch('http://115.190.118.22:5000/api/save_doctor', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.doctor)
        });
        const result = await response.json();
        if (response.ok) {
          this.message = result.message;

          // ✅ 保存所有医生信息到 localStorage
          this.saveDoctorToLocalStorage();

          // ✅ 不清空字段，以便用户继续编辑或查看
        } else {
          this.message = result.error || '提交失败';
        }
      } catch (e) {
        this.message = '连接服务器失败';
      }
    },
    saveDoctorToLocalStorage() {
      localStorage.setItem('doctor_info', JSON.stringify(this.doctor));
    },
    loadDoctorFromLocalStorage() {
      const saved = localStorage.getItem('doctor_info');
      if (saved) {
        const parsed = JSON.parse(saved);
        this.doctor = { ...this.doctor, ...parsed };
      }
    },
    clearLocalData() {
      localStorage.removeItem('doctor_info');
      this.message = '本地缓存已清空';
    }
  },
  mounted() {
    // ✅ 从 localStorage 获取 ID
    const localId = localStorage.getItem('id') || 'D0001';
    this.doctor.id = localId;

    // ✅ 加载历史填写信息
    this.loadDoctorFromLocalStorage();
  }
};
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


.container {
  max-width: 800px;
  margin: 40px auto;
  padding: 20px;
  background: #f8faff;
  position: relative;
  z-index: 1;
}

.form label {
  display: block;
  margin-bottom: 12px;
}

input, textarea {
  width: 100%;
  padding: 6px;
  margin-top: 4px;
  border: 1px solid #aaa;
  border-radius: 4px;
}

button {
  margin-top: 12px;
  padding: 8px 16px;
  font-size: 14px;
  cursor: pointer;
}

.message {
  margin-top: 12px;
  color: green;
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
.login-button {
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 22px;
  font-weight: bold;
  position: fixed;
  top: 30px;
  right: 35px;
  background: transparent;
  border: none;
  color: #333333;  /* 文字颜色改为黑色 */
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
</style>
