<template>
  <div class="header">
    <img src="../assets/favicon.png" alt="Icon" class="icon" />
    <span class="header-text">ELIRA</span>
  </div>
  <!--
  <div class="headd">在UESTC创造你自己的世界</div>-->
  <div class="login-container">
    <form @submit.prevent="handleLogin">
      <div class="input-group">
        <input type="text" v-model="email" placeholder="请输入用户名" required />
      </div>
      <div class="input-group">
        <input type="password" v-model="password" placeholder="请输入密码" required />
      </div>

      <!-- 身份选择 -->
      <div class="input-group role-group">
        <label>
          <input type="radio" value="patient" v-model="role" />
          我是患者
        </label>
        <label>
          <input type="radio" value="doctor" v-model="role" />
          我是医生
        </label>
        <!--
        <label>
          <input type="radio" value="family" v-model="role" />
          我是家属
        </label>-->
      </div>

      <div class="input-group checkbox-group">
        <input type="checkbox" id="remember" name="remember" class="checkbox" />
        <label for="remember" class="remember-label">记住密码</label>
      </div>

      <button type="submit" class="login-button">立即登录</button>
    </form>
  </div>
  <div class="links">
    <router-link to="/register" class="link-item">立即注册</router-link>
    <router-link to="/forgot-password" class="link-item">忘记密码</router-link>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      email: '',
      password: '',
      token: '',
      tokenId: '',
      id: null,
      role: '', // ✅ 选择身份
    };
  },
  methods: {
    async handleLogin() {
  if (!this.role) {
    alert('请选择身份');
    return;
  }

  try {
    const response = await axios.post('http://115.190.118.22:5000/api/user/login', {
      email: this.email,
      password: this.password,
      role: this.role
    });

    if (response.data.code === 1) {
      const id = response.data.data.id;
      this.token = response.data.data.token;

      localStorage.setItem('token', this.token);
      localStorage.setItem('id', id);
      this.id = id;
      localStorage.setItem('role', this.role);

      alert('登录成功');

      // ➤ 根据身份跳转
      let targetPath = '';
      if (this.role === 'patient') {
        targetPath = '/homepage';
      } else if (this.role === 'doctor') {
        targetPath = '/doctor_front';
      } else if (this.role === 'family') {
        targetPath = '/family';
      }

      this.$router.push({
        path: targetPath,
        query: {
          id: this.id,
          token: this.token,
          tokenId: this.tokenId
        }
      });

    } else {
      const errorMsg = response.data.error;

      if (errorMsg === '无效的邮箱或密码') {
        alert('无效的邮箱或密码');
      } else if (errorMsg === '角色不匹配') {
        alert('角色与注册时不一致，请重新选择身份');
      } else {
        alert('登录失败，请检查账号、密码或身份');
      }
    }
  } catch (error) {
    if (error.response && error.response.data && error.response.data.error) {
      const errorMsg = error.response.data.error;

      if (errorMsg === '无效的邮箱或密码') {
        alert('无效的邮箱或密码');
      } else if (errorMsg === '角色不匹配') {
        alert('角色与注册时不一致，请重新选择身份');
      } else {
        alert('登录失败：' + errorMsg);
      }
    } else {
      alert('登录请求失败，请稍后重试');
      console.error(error);
    }
  }
}

  },
};
</script>

<style>
body {
  font-family: Arial, sans-serif;
  background: #f7f4e7;
  display: flex;
  justify-content: center;
  align-items: center;
  /* 垂直居中 */
  height: 100vh;
  margin: 0;
  flex-direction: column;
  /* 使内容垂直排列 */
  padding-bottom: 15vh;
}

.header {
  display: flex;
  align-items: center;
  /* 垂直居中 */
  justify-content: center;
  /* 水平居中 */
  margin-bottom: 10px;
  /* 添加底部间距 */
}

.icon {
  width: 80px;
  /* 设置图标宽度 */
  height: 80px;
  /* 设置图标高度 */
  margin-right: 10px;
  /* 图标与文字之间的间距 */
}

.header-text {
  font-size: 50px;
  /* 设置文字大小 */
  color: rgba(16, 16, 16, 1);
  /* 设置文字颜色 */
}

.headd {
  width: 100%;
  /* 使其占满整个宽度 */
  height: 29px;
  color: rgba(16, 16, 16, 1);
  font-size: 14px;
  /* 调整字体大小 */
  text-align: center;
  /* 居中对齐 */
  margin-bottom: 10px;
  /* 添加底部间距 */
  font-family: SourceHanSansSC-regular;
}

.login-container {
  width: 450px;
  /* 增加宽度 */
  padding: 20px;
  background-color: rgba(255, 255, 255, 0.7);
  /* 进一步降低透明度 */
  border: none;
  /* 去除边框 */
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  text-align: center;
  display: flex;
  flex-direction: column;
  /* 垂直排列 */
  justify-content: center;
  /* 垂直居中 */
  border-radius: 0;
  /* 去掉圆角 */
}

.input-group {
  margin-bottom: 20px;
  /* 增加间距 */
  text-align: left;
}

input[type="text"],
input[type="password"] {
  width: 100%;
  padding: 12px;
  /* 增加内边距以提高高度 */
  border: 1px solid #ccc;
  border-radius: 5px;
  /* 添加圆角 */
  transition: border-color 0.3s;
  box-sizing: border-box;
  max-width: 100%;
}

input[type="text"]:focus,
input[type="password"]:focus {
  border-color: #5cb85c;
  outline: none;
}

.checkbox-group {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  /* 增加间距 */
}

input[type="checkbox"] {
  width: 15px;
  /* 调整复选框的宽度 */
  height: 15px;
  /* 调整复选框的高度 */
  margin-right: 5px;
  /* 右侧间距 */
  border: none;
  /* 去除边框 */
}

.remember-label {
  font-size: 12px;
  /* 缩小字体 */
}

.login-button {
  width: 100%;
  padding: 10px;
  background-color: #053f5c;
  /* 修改按钮颜色 */
  color: white;
  border: none;
  border-radius: 5px;
  /* 添加圆角 */
  cursor: pointer;
  transition: background-color 0.3s;
}

.login-button:hover {
  background-color: #042c3c;
  /* 悬停时的颜色 */
}

.links {
  margin-top: 10px;
  /* 缩小顶部间距 */
  text-align: center;
  /* 居中对齐 */
  display: flex;
  /* 使用flex布局 */
  justify-content: space-between;
  /* 使链接分散对齐 */
}

.link-item {
  color: black;
  /* 修改颜色为黑色 */
  text-decoration: none;
  font-size: 14px;
  /* 缩小字体 */
  margin: 0 15px;
  /* 设置左右间距为15px */
}

.links a:hover {
  text-decoration: underline;
}

.role-group {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20px;
  font-size: 14px;
}

.role-group label {
  display: flex;
  align-items: center;
  gap: 5px;
}
</style>