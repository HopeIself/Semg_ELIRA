<template>
  <div class="container">
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
    async submitDoctorInfo() {
      try {
        const response = await fetch('http://115.190.134.66:5000/api/save_doctor', {
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
.container {
  max-width: 800px;
  margin: 40px auto;
  padding: 20px;
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
</style>
