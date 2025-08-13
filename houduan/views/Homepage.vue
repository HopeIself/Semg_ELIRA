<template>
  <div class="home-container">
    <div class="title-section">
      <h1>欢迎使用智能康复训练系统</h1>
      <p class="subtitle">请选择功能模块</p>
    </div>
    <!-- <button class="login-button" @click="goLogin">退出登录</button> -->

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
      <!-- 在线指导模块按钮，点击跳转到到RTC页面 -->
      <div class="card" @click="goTo('/rtcpage')">
        <div class="card-text">在线指导模块</div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'HomePage',
  data() {
    return {
      cozeApiBase: 'https://api.coze.cn',
      oauthToken: ''
    };
  },
  methods: {
    goTo(path) {
      console.log(`导航到路径: ${path}`);
      this.$router.push({ path });
    },
    goLogin() {
      console.log('用户点击退出登录');
      this.$router.push({ path: "/" });
    },
    async getAccessToken() {
      console.log('开始获取Access Token');
      const userId = localStorage.getItem('id');
      console.log(`当前用户ID: ${userId || '未获取到'}`);
      
      if (!userId || userId === 'null') {
        const warnMsg = '未获取到用户ID，无法初始化会话';
        console.warn(warnMsg);
        return;
      }
      
      try {
        console.log('发送Access Token请求到后端');
        const response = await axios.post('http://115.190.118.22:5000/api/get_access_token', {
          id: userId
        });
        console.log(`Access Token请求返回状态: ${response.status}`);
        
        if (response.data.access_token) {
          this.oauthToken = response.data.access_token;
          console.log('Access Token 获取成功');
          await this.initAISession(userId);
          this.mountCozeWebChat();
        } else {
          console.warn('无法获取 Access Token，响应中无token字段');
        }
      } catch (error) {
        console.error(`获取 Access Token 失败：${error.message}`, error);
      }
    },
    async initAISession(userId) {
      console.log('开始初始化AI会话');
      try {
        const res = await axios.post('http://115.190.118.22:5000/api/init-ai-session', { id: userId });
        console.log(`AI会话初始化成功，返回状态: ${res.status}`);
      } catch (err) {
        console.error(`AI会话初始化失败：${err.message}`, err);
      }
    },
    mountCozeWebChat() {
      if (!this.oauthToken) {
        console.warn('无法获取 Coze 数据，因为 Access Token 不可用');
        return;
      }
      
      console.log('开始加载Coze Web SDK');
      const script = document.createElement('script');
      script.src = "https://lf-cdn.coze.cn/obj/unpkg/flow-platform/chat-app-sdk/1.2.0-beta.10/libs/cn/index.js";
      script.onload = () => {
        console.log('Coze Web SDK 加载成功');
        try {
          new CozeWebSDK.WebChatClient({
            config: { bot_id: '7526864409868976143' },
            componentProps: { title: 'Coze' },
            auth: {
              type: 'token',
              token: this.oauthToken,
              onRefreshToken: () => this.oauthToken
            }
          });
          console.log('Coze WebChatClient 初始化成功');
        } catch (error) {
          console.error(`Coze客户端初始化失败：${error.message}`, error);
        }
      };
      script.onerror = (error) => {
        console.error(`Coze SDK 加载失败：${error.message}`, error);
      };
      document.body.appendChild(script);
    }
  },
  mounted() {
    console.log('主页组件挂载完成，开始初始化');
    const userId = localStorage.getItem('id');
    if (userId) {
      this.initAISession(userId);
      this.getAccessToken();
    }
  }
};
</script>

<style scoped>
.home-container {
  width: 100vw;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  background: #f7f4e7;
  padding: 40px 20px;
  font-family: "Helvetica Neue", Arial, sans-serif;
}

.title-section {
  text-align: center;
  margin-bottom: 50px;
}

.title-section h1 {
  font-size: 32px;
  color: #333333;
  margin-bottom: 8px;
}

.subtitle {
  font-size: 16px;
  color: #333333;
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
  color: #333333;
}

.login-button {
  font-size: 22px;
  font-weight: bold;
  position: fixed;
  top: 20px;
  right: 20px;
  background: transparent;
  border: none;
  color: #333333;
  cursor: pointer;
}

.login-button:hover {
  text-decoration: underline;
}
</style>
  