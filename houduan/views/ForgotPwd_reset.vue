<template>
  <div class="header">
    <img src="../assets/favicon.png" alt="Icon" class="icon" />
    <span class="header-text">UNFT</span>
  </div>
  <div class="headd">重置密码</div>

  <div class="register-container">
    <form @submit.prevent="handleRegister">
      <div class="input-group">
        <input type="text" v-model="email" placeholder="请输入用户 ID" required />
      </div>
      <div class="input-group">
        <input type="password" v-model="newPassword" placeholder="请输入新密码" required />
      </div>
      <div class="input-group">
        <input type="password" v-model="confirmPassword" placeholder="确认新密码" required />
      </div>
      <button type="submit" class="register-button">下一步</button>
    </form>
  </div>
  <div class="links">
    <router-link to="/Wallet" class="link-item">钱包</router-link>
    <router-link to="/" class="link-item">记得密码 去登陆</router-link>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      email: '',
      newPassword: '',
      confirmPassword: '',
      userId: null,
      token: null
    };
  },
  mounted() {
    this.userId = Number(localStorage.getItem('userId'));
    this.token = localStorage.getItem('token');
  },
  methods: {
    async handleRegister() {
      if (this.newPassword !== this.confirmPassword) {
        alert('密码不匹配，请重新输入。');
        return;
      }
      try {
        const requestBody = {
          email: this.email,
          newPassword: this.newPassword,
          userId: this.userId
        };
        console.log('Request Body:', requestBody);

        const response = await axios.put(
          'http://192.168.50.153:8080/user/changePassword',
          requestBody,
          {
            headers: {
              Token: `${this.token}`
            }
          }
        );

        alert(response.data.message);
        this.$router.push('/');
      } catch (error) {
        console.error('Error:', error);
        if (error.response) {
          alert(error.response.data.message);
        } else {
          alert('请求失败，请稍后再试。');
        }
      }
    }
  }
};
</script>

<style scoped>
body {
  font-family: Arial, sans-serif;
  background: linear-gradient(135deg, #74ead5, #abb6e4);
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  margin: 0;
  flex-direction: column;
  padding-bottom: 15vh;
}

.header {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
}

.icon {
  width: 80px;
  height: 80px;
  margin-right: 10px;
}

.header-text {
  font-size: 50px;
  color: rgba(16, 16, 16, 1);
}

.headd {
  width: 100%;
  height: 29px;
  color: rgba(16, 16, 16, 1);
  font-size: 14px;
  text-align: center;
  margin-bottom: 10px;
  font-family: SourceHanSansSC-regular;
}

.register-container {
  width: 450px;
  padding: 20px;
  background-color: rgba(255, 255, 255, 0.7);
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
  border-radius: 0;
}

.input-group {
  margin-bottom: 20px;
  text-align: left;
}

input[type="text"],
input[type="password"] {
  width: 100%;
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 5px;
  transition: border-color 0.3s;
}

input[type="text"]:focus,
input[type="password"]:focus {
  border-color: #5cb85c;
  outline: none;
}

.register-button {
  width: 100%;
  padding: 10px;
  background-color: #053f5c;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.register-button:hover {
  background-color: #042c3c;
}

.links {
  margin-top: 10px;
  text-align: center;
  display: flex;
  justify-content: space-between;
}

.link-item {
  color: black;
  text-decoration: none;
  font-size: 14px;
  margin: 0 15px;
}

.links a:hover {
  text-decoration: underline;
}
</style>
