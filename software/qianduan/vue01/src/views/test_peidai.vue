<template>
  <div class="wear-page">
    <div class="content-box">
      <img src="../assets/image1.jpg" alt="穿戴示意图" class="wear-image" />
      <div class="tip-and-button">
        <p class="wear-tip">提示：拉动带子直到感受到紧绷的感觉</p>
        <button class="next-button" @click="goToPlanChoose">下一步</button>
      </div>
    </div>

    <!-- 实时肌电信号反馈区域 -->
    <div class="emg-feedback-container">
      <h2>实时肌电信号反馈</h2>
      <div id="emg-value" class="emg-value">
        {{ emgValue !== null ? `肌电信号: ${emgValue}` : '正在加载...' }}
      </div>
      <div id="feedback" class="feedback" :class="feedbackClass">
        {{ feedback !== null ? `反馈: ${feedback}` : '等待数据...' }}
      </div>
      <div class="loading">每秒更新两次信号反馈</div>
    </div>

    <button class="back-button" @click="goBack">← 主页</button>
  </div>
</template>

<script>
export default {
  name: "WearPage",
  data() {
    return {
      emgValue: null,
      feedback: null,
      feedbackClass: "loading",
    };
  },
  mounted() {
    const eventSource = new EventSource("http://115.190.134.66:5000/api/real-time-feedback");

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.emgValue = data.emg !== undefined ? data.emg : "数据错误";
      this.feedback = data.feedback !== undefined ? data.feedback : null;

      if (this.feedback === "好") {
        this.feedbackClass = "good";
      } else if (this.feedback === "坏") {
        this.feedbackClass = "bad";
      } else {
        this.feedbackClass = "loading";
      }
    };

    eventSource.onerror = () => {
      console.error("实时数据接收失败");
      this.feedback = "无法接收数据";
      this.feedbackClass = "loading";
    };
  },
  methods: {
    goToPlanChoose() {
      this.$router.push({ path: "/planchoose" });
    },
    goBack() {
      this.$router.push({ path: "/homepage" });
    },
  },
};
</script>

<style scoped>
.wear-page {
  height: 100vh;
  box-sizing: border-box;
  background: linear-gradient(to right, #f0f8ff, #ffffff);
  padding: 40px;
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: center;
  overflow-y: auto; /* 允许滚动，防止内容溢出 */
}

/* 头部内容和按钮容器 */
.content-box {
  display: flex;
  align-items: center;
  gap: 40px;
  flex-wrap: nowrap;
  margin-bottom: 40px;
}

/* 提示文字和下一步按钮放一起，垂直排列 */
.tip-and-button {
  display: flex;
  flex-direction: column;
  gap: 15px;
  max-width: 500px;
}

.wear-image {
  width: 280px;
  height: auto;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
}

.wear-tip {
  font-size: 20px;
  color: #333;
  font-weight: 500;
  line-height: 1.6;
}

/* 实时肌电反馈区域：宽度缩小，内边距减小 */
.emg-feedback-container {
  width: 100%;
  max-width: 400px;
  background: white;
  padding: 20px 25px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  text-align: center;
  margin-bottom: 40px; /* 适当缩短间距 */
}

.emg-value {
  font-size: 24px;
  font-weight: bold;
  margin-top: 20px;
  color: #333;
}

.feedback {
  font-size: 20px;
  margin-top: 20px;
  padding: 12px;
  border-radius: 6px;
  font-weight: bold;
  color: white;
}

.good {
  background-color: #28a745;
}

.bad {
  background-color: #dc3545;
}

.loading {
  font-size: 16px;
  color: #6c757d;
  background-color: transparent;
  padding: 12px 0;
}

.back-button {
  position: fixed;
  top: 20px;
  left: 20px;
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

.next-button {
  padding: 10px 24px;
  font-size: 18px;
  border: none;
  border-radius: 10px;
  background-color: #4a90e2;
  color: white;
  cursor: pointer;
  transition: background-color 0.2s ease;
  align-self: flex-start; /* 左对齐 */
}

.next-button:hover {
  background-color: #357ab7;
}
</style>
