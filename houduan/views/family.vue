<template>
  <div class="app-container">
    <!-- 家属端报告视图 -->
    <div class="report-card">
      <h1 class="page-title">康复反馈报告（面向家属）</h1>

      <!-- 1. 患者基本信息 -->
      <section class="section-block">
        <h3 class="section-title">患者基本信息</h3>
        <div class="info-grid">
          <div class="info-item"><span class="label">姓名：</span>{{ info.name }}</div>
          <div class="info-item"><span class="label">性别：</span>{{ info.gender }}</div>
          <div class="info-item"><span class="label">年龄：</span>{{ info.age }} 岁</div>
          <div class="info-item"><span class="label">训练日期：</span>{{ info.date }}</div>
        </div>
      </section>

      <!-- 2. 康复项目与目标 -->
      <section class="section-block">
        <h3 class="section-title">康复项目与目标</h3>
        <p class="desc-text">
          本次康复训练主要聚焦于下肢肌群的力量恢复与姿态控制，训练内容包括稳定性练习、步态协调与柔韧性提升，旨在提高日常生活自理能力与步行安全性。
        </p>
      </section>

      <!-- 3. 康复指标变化 -->
      <section class="section-block">
        <h3 class="section-title">康复指标变化</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>指标名称</th>
              <th>单位</th>
              <th>训练前</th>
              <th>训练后</th>
              <th>变化趋势</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in metrics" :key="index">
              <td>{{ item.name }}</td>
              <td>{{ item.unit }}</td>
              <td>{{ item.before }}</td>
              <td>{{ item.after }}</td>
              <td>{{ item.trend }}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <!-- 4. 对家属的建议 -->
      <section class="section-block">
        <h3 class="section-title">对家属的建议</h3>
        <p class="desc-text">
          建议家属协助患者继续进行康复训练，特别是步态练习和力量训练，营造鼓励与支持的家庭环境。
          平时注意观察患者情绪及疲劳反应，适当安排休息与营养，确保康复效果持续稳定。
        </p>
      </section>
    </div>
  </div>
</template>

<script setup>
const info = {
  name: '张三',
  gender: '男',
  age: 65,
  date: '2025-07-08'
}

const metrics = [
  { name: 'RMS（均方根值）', unit: 'μV', before: 104.3, after: 132.5, trend: '↑27%' },
  { name: 'MDF（中位频率）', unit: 'Hz', before: 87.1, after: 79.4, trend: '↓8.8%' },
  { name: 'Activation Ratio', unit: '%', before: '43.2%', after: '66.5%', trend: '↑54%' }
]
</script>

<style scoped>
.app-container {
  padding: 40px;
  background-color: #f4f4f4;
  min-height: 100vh;
  font-family: Arial, sans-serif;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 30px;
  text-align: left;
}

.report-card {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}

.section-block {
  margin-bottom: 32px;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 12px;
  text-align: left;
}

.info-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item {
  font-size: 15px;
  color: #333;
  text-align: left;
}

.label {
  font-weight: bold;
  margin-right: 8px;
}

.desc-text {
  font-size: 15px;
  color: #444;
  line-height: 1.6;
  text-align: left;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: center;
  font-size: 14px;
}

.data-table th,
.data-table td {
  border: 1px solid #ccc;
  padding: 10px;
}

.data-table thead {
  background-color: #f0f0f0;
}
</style>
