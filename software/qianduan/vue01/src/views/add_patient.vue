<template>
  <div class="add-patient-container">
    <h2>添加患者</h2>

    <input
      v-model="keyword"
      @input="onInput"
      placeholder="请输入患者姓名"
      class="input-box"
    />

    <!-- 搜索建议列表 -->
    <ul v-if="suggestions.length" class="suggestion-list">
      <li
        v-for="patient in suggestions"
        :key="patient.id"
        @click="selectPatient(patient)"
      >
        {{ patient.name }}（{{ patient.id }}）
      </li>
    </ul>

    <!-- 添加/删除结果提示 -->
    <p v-if="message" class="message">{{ message }}</p>

    <!-- 已添加患者展示 -->
    <h3>已添加患者列表</h3>
    <ul v-if="patientList.length" class="added-list">
      <li
        v-for="patient in patientList"
        :key="patient.patient_id"
        class="added-item"
      >
        {{ patient.patient_name }} （{{ patient.patient_id }}）
        <button
          @click="removePatient(patient.patient_id)"
          class="remove-button"
        >❌</button>
      </li>
    </ul>
    <p v-else class="empty">暂无添加</p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      keyword: '',
      suggestions: [],
      message: '',
      patientList: [],       // 存放 {patient_id, patient_name}
      debounceTimer: null
    };
  },
  methods: {
    onInput() {
      clearTimeout(this.debounceTimer);
      this.debounceTimer = setTimeout(this.searchPatients, 300);
    },
    async searchPatients() {
      if (!this.keyword.trim()) {
        this.suggestions = [];
        return;
      }
      try {
        const res = await fetch(
          `http://115.190.134.66:5000/api/search_patients?keyword=${encodeURIComponent(this.keyword)}`
        );
        const result = await res.json();
        this.suggestions = result.patients || [];
      } catch (err) {
        this.message = '搜索失败';
        this.suggestions = [];
      }
    },
    async selectPatient(patient) {
      const doctorId = localStorage.getItem('id');
      if (!doctorId) {
        this.message = '请先设置医生ID（localStorage 中的 "id"）';
        return;
      }
      try {
        const res = await fetch(
          'http://115.190.134.66:5000/api/manage_patient',
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              doctor_id: doctorId,
              patient_id: patient.id,
              action: 'add'
            })
          }
        );
        const result = await res.json();
        this.message = result.message || '添加成功';
        this.keyword = '';
        this.suggestions = [];
        await this.loadPatientList();
      } catch (err) {
        this.message = '添加失败';
      }
    },
    async removePatient(patientId) {
      const doctorId = localStorage.getItem('id');
      if (!doctorId) return;
      try {
        const res = await fetch(
          'http://115.190.134.66:5000/api/manage_patient',
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              doctor_id: doctorId,
              patient_id: patientId,
              action: 'remove'
            })
          }
        );
        const result = await res.json();
        this.message = result.message || '删除成功';
        await this.loadPatientList();
      } catch (err) {
        this.message = '删除失败';
      }
    },
    async loadPatientList() {
      const doctorId = localStorage.getItem('id');
      if (!doctorId) return;
      try {
        const res = await fetch(
          `http://115.190.134.66:5000/api/get_patient_data?doctorId=${encodeURIComponent(doctorId)}`
        );
        const data = await res.json();
        // 后端返回 { patient_data: [ { patient_id, patient_name }, … ] }
        this.patientList = data.patient_data || [];
      } catch (e) {
        this.patientList = [];
      }
    }
  },
  mounted() {
    this.loadPatientList();
  }
};
</script>

<style scoped>
.add-patient-container {
  max-width: 600px;
  margin: 40px auto;
  padding: 20px;
}
.input-box {
  width: 100%;
  padding: 10px;
  font-size: 16px;
}
.suggestion-list {
  list-style: none;
  margin: 0;
  padding: 0;
  border: 1px solid #ccc;
  max-height: 200px;
  overflow-y: auto;
}
.suggestion-list li {
  padding: 10px;
  cursor: pointer;
}
.suggestion-list li:hover {
  background-color: #f0f0f0;
}
.message {
  color: green;
  margin-top: 10px;
}
.added-list {
  margin-top: 16px;
  padding-left: 20px;
}
.added-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 0;
}
.remove-button {
  background: none;
  border: none;
  color: red;
  font-size: 18px;
  cursor: pointer;
}
.empty {
  color: #888;
  margin-top: 10px;
}
</style>
