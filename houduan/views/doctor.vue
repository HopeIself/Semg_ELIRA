<template>
  <div class="big-container">
      <div class ="doctor-container">
        <div v-if="doctors.length" class="doctor-list">
          <div v-for="doctor in doctors" :key="doctor.name" class="doctor-card">
            <h3>{{ doctor.name }}</h3>
            <p><strong>专长：</strong>{{ doctor.major }}</p>
            <p><strong>学校：</strong>{{ doctor.school }}</p>
            <p><strong>医院：</strong>{{ doctor.hospital }}</p>
            <p><strong>简介：</strong>{{ doctor.description }}</p>
            <p><strong>详细信息：</strong>{{ doctor.detailedDescription }}</p>
          </div>
        </div>
      </div>
    <button class="back-button" @click="goBack">返回个人信息</button>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "Doctors",
  data() {
    return {
      doctors: []
    };
  },
  mounted() {
    this.fetchDoctors();
  },
  methods: {
    async fetchDoctors() {
      try {
        const response = await axios.post("http://115.190.118.22:5000/api/find_doctor", {
          id: localStorage.getItem("id")
        });
        this.doctors = response.data.doctors || [];
      } catch (error) {
        console.error("无法加载医生信息", error);
      }
    },

    // 返回到 Personal.vue 页面
    goBack() {
      this.$router.push({ path: "/personal" });
    }
  }
};
</script>

<style scoped>
body {
  background-color: #f7f4e7;  /* 页面背景色为浅米色 */
}
.back-button {
  font-family: "Helvetica Neue", Arial, sans-serif;  /* 字体设置 */
  font-weight: bold;  /* 加粗字体 */
  position: fixed;  /* 固定定位 */
  top: 30px;  /* 距离顶部 30px */
  left: 35px;  /* 距离左侧 35px */
  background: transparent;  /* 背景透明 */
  border: none;  /* 无边框 */
  font-size: 22px;  /* 字体大小为 22px */
  color: #333;  /* 文字颜色为深灰色 */
  cursor: pointer;  /* 鼠标悬停时显示为手形，表示可点击 */
  user-select: none;  /* 禁止文本选择 */
  z-index: 100;  /* 确保按钮显示在最上层 */
}
h1 {
  text-align: center;  /* 使标题居中 */
  font-size: 32px;  /* 可根据需要调整字体大小 */
  color: #333;  /* 字体颜色 */
  margin-bottom: 20px;  /* 设置标题与内容的间距 */
}
/* 医生卡片列表 */
.doctor-list {
  display: flex;
  flex-wrap: wrap;  /* 当一行填满时，自动换行 */
  gap: 30px;  /* 设置卡片之间的间距 */
  justify-content: flex-start;  /* 靠左排列 */
  max-width: 100%;
  padding: 20px;  /* 容器内边距 */
  box-sizing: border-box;  /* 确保内边距不会影响容器宽度 */
}

/* 医生卡片 */
.doctor-card {
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);  /* 增加阴影效果 */
  width: 300px;  /* 每个卡片宽度占据父容器的 48%，保证每行有两个卡片 */
  min-height: 250px;  /* 设置卡片的最小高度 */
  box-sizing: border-box; /* 确保内边距不会影响卡片的实际大小 */
  margin-bottom: 20px;  /* 卡片底部间距 */
  margin-top: 80px;
  margin-left: 80px;;
}
.doctor-container {
  background-color: #f7f4e7;  /* 设置大的容器背景颜色 */
  padding: 30px;
  border-radius: 12px;
  height: 100vh;
  width: 100vw;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);  /* 胶片风格的阴影效果 */
}
/* 响应式设计：在小屏幕上卡片占满屏幕宽度 */
@media (max-width: 768px) {
  .doctor-card {
    width: 100%;  /* 在小屏幕上卡片宽度占满父容器 */
    max-width: 500px;  /* 设置最大宽度 */
  }
}
</style>