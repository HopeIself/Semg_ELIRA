<template>
  <div class="wear-page">
    <!-- 图片容器 -->
    <div class="wear-image-container">
      <img src="../assets/image0.png" alt="仪器穿戴示意图" class="wear-image" />
    </div>
      
    <!-- 右侧内容容器 -->
    <div class="right-content-container">
      <!-- 提示文字容器 -->
      <div class="tip-container">
        <p class="wear-tip">提示：佩戴前请用湿巾擦净手臂，佩戴仪器直到拉动带子有到紧绷的感觉</p>
      </div>

      <!-- 实时肌电信号反馈区域 -->
      <div class="emg-feedback-container">
        <h2>实时肌电信号值反馈：</h2>
        <div id="emg-value" class="emg-value">
          {{ emgValue !== null ? `${emgValue}` : '正在加载...' }}
        </div>
        <div id="feedback" class="feedback" :class="feedbackClass">
          {{ feedback !== null ? `反馈：${feedback}` : '等待数据...' }}
        </div>
        <div class="loading">每秒更新2次肌电信号值
        </div>
      </div>
      <!-- 下一步按钮 -->
      <div class="button-container">
        <button class="next-button" @click="goToPlanChoose">下一步</button>
      </div>
    </div>

    <button class="back-button" @click="goBack">返回主页</button>
    <button class="login-button" @click="goLogin">退出登录</button>
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
    const userId = localStorage.getItem('id');
    if (!userId) {
      console.error("用户ID未找到");
      this.feedback = "缺少用户ID";
      return;
    }

    const eventSource = new EventSource(`http://115.190.118.22:5000/api/real-time-feedback?id=${userId}`);

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.error) {
        // 收到错误信息，显示错误提示
        this.feedback = data.error;
        this.feedbackClass = "bad";
        this.emgValue = null;
      } else {
        // 正常数据
        this.emgValue = data.emg !== undefined ? data.emg : "数据错误";
        this.feedback = data.feedback !== undefined ? data.feedback : null;

        if (this.feedback === "好") {
          this.feedbackClass = "good";
        } else if (this.feedback === "不好") {
          this.feedbackClass = "bad";
        } else {
          this.feedbackClass = "loading";
        }
      }
    };

    eventSource.onerror = () => {
      console.error("实时数据接收失败");
      this.feedback = "无法接收数据";
      this.feedbackClass = "loading";
    };

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
  },
  methods: {
    goToPlanChoose() {
      this.$router.push({ path: "/planchoose" });
    },
    goBack() {
      this.$router.push({ path: "/homepage" });
    },
    goLogin() {
      this.$router.push({ path: "/" });
    },
  },
};
</script>

<style scoped>
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

/* 你原有的其他样式保持不变 */
.wear-page {
  width: 100vw;
  height: 100vh;
  box-sizing: border-box;
  background: #f7f4e7;
  padding: 40px;
  position: relative;
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: flex-start;
  overflow-y: auto; /* 允许滚动，防止内容溢出 */
}

/* 图片容器 */
.wear-image-container {
  width: 50%;  /* 图片占左边40%宽度 */
  padding-right: 20px;  /* 右侧留空 */
  margin-left: 50px;
  margin-top:65px;
}
.wear-image {
  width: 100%;  /* 图片占左边45%宽度 */
  height: auto;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
  height: 60%;
}

/* 右侧内容容器 */
.right-content-container {
  width: 50%;  /* 右侧内容占据60%宽度 */
  display: flex;
  flex-direction: column; /* 让右侧内容竖着排列 */
  justify-content: flex-start;
  align-items: flex-start;
  margin-top: 40px; /* 调整右侧内容区域的间距，使其和图片不重叠 */
  margin-left: 50px;
  margin-right: 50px;
}

/* 提示文字容器 */
.tip-container {
  margin-bottom: 20px; /* 留出间距 */
  margin-top:30px
}
.wear-tip {
  font-size: 25px;
  color: #333;
  font-weight: 500;
  line-height: 1.6;
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-weight: bold;
}
/* 头部内容和按钮容器 */
.content-box {
  display: flex;
  align-items: flex-start;
  gap: 40px;
  flex-wrap: nowrap;
  width: 100%;
  justify-content: flex-start;
  margin-bottom: 40px;
}

/* 提示文字和下一步按钮放一起，垂直排列 */
.tip-and-button {
  display: flex;
  flex-direction: column;
  gap: 15px;
  width: 100%;
}

/* 实时肌电反馈区域：宽度缩小，内边距减小 */
.emg-feedback-container {
  width: 85%;
  background: white;
  padding: 20px 25px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  text-align: center;
  margin-top: 20px; /* 适当缩短间距 */
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
/* 下一步按钮 */
.button-container {
  margin-top: 45px;  /* 按钮与反馈区域之间的间距 */
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
  margin-top: 20px;
}
.next-button:hover {
  background-color: #357ab7;
}
</style>