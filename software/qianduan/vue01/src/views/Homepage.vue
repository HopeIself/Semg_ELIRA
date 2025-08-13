<template>
  <div class="home-container">
    <div class="title-section">
      <h1>欢迎使用腕部康复训练系统</h1>
      <p class="subtitle">请选择功能模块</p>
    </div>
    <button class="login-button" @click="goLogin">退出登录</button>

    <div class="card-group">
      <div class="card" @click="goTo('/personal')">
        <div class="card-text">个人情况</div>
      </div>

      <div class="card" @click="goTo('/wear')">
        <div class="card-text">开始训练</div>
      </div>

      <div class="card" @click="goTo('/history')">
        <div class="card-text">历史记录</div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'HomeNavigation',
  methods: {
    goTo(path) {
      this.$router.push({ path });
    },
    goLogin() {
      this.$router.push({ path: "/" });
    },
    async initAISession() {
      const userId = localStorage.getItem('id');
      if (!userId || userId === 'null') {
        console.warn('未获取到用户ID，无法初始化AI会话');
        return;
      }

      try {
        const res = await axios.post('http://115.190.134.66:5000/api/init-ai-session', {
          id: userId
        });
        console.log('AI会话初始化成功：', res.data);
      } catch (err) {
        console.error('AI会话初始化失败：', err);
      }
    }
  },
  mounted() {
    this.initAISession();
    // 挂载 Coze Web Chat
    const script = document.createElement('script')
    script.src = "https://lf-cdn.coze.cn/obj/unpkg/flow-platform/chat-app-sdk/1.2.0-beta.10/libs/cn/index.js"
    script.onload = () => {
      new CozeWebSDK.WebChatClient({
        config: { bot_id: '7526864409868976143' },
        componentProps: { title: 'Coze' },
        auth: {
          type: 'token',
          token: 'pat_UTnqligakKWIe8ar0NBnLqpNxyxpXURu5sE36366AD0UwjJBFgUzFcQM99WFG0d7',
          onRefreshToken: () => 'pat_UTnqligakKWIe8ar0NBnLqpNxyxpXURu5sE36366AD0UwjJBFgUzFcQM99WFG0d7'
        }
      })
    }
    document.body.appendChild(script)
  }
};
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(to right, #eaf6ff, #f5fbff);
  padding: 40px 20px;
  font-family: "Helvetica Neue", Arial, sans-serif;
}

.title-section {
  text-align: center;
  margin-bottom: 50px;
}

.title-section h1 {
  font-size: 32px;
  color: #2c3e50;
  margin-bottom: 8px;
}

.subtitle {
  font-size: 16px;
  color: #666;
}

.card-group {
  display: flex;
  flex-direction: column;
  gap: 25px;
  width: 100%;
  max-width: 320px;
}

.card {
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
  padding: 20px;
  text-align: center;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: pointer;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.card-text {
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.login-button {
  position: fixed;
  top: 20px;
  right: 20px;
  background: transparent;
  border: none;
  font-size: 24px;
  color: #e31111;
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
