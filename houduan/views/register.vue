<template>
    <div class="header">
        <img src="../assets/favicon.png" alt="Icon" class="icon" />
        <span class="header-text">ELIRA</span>
    </div>
    <div class="headd">创建你的账号</div>

    <!-- 步骤指示器 -->
    <div class="step-indicator">
        <div class="step active"></div>
        <!-- <div class="step"></div> -->
        <div class="step"></div>
    </div>

    <div class="register-container">
        <form @submit.prevent="handleRegister"> <!-- Prevent default form submission -->
            <div class="input-group">
                <input type="text" v-model="email" placeholder="请输入用户名" required>
            </div>
            <div class="input-group">
                <input type="password" v-model="password" placeholder="请输入密码" required>
            </div>
            <div class="input-group">
                <input type="password" v-model="confirmPassword" placeholder="确认密码" required>
            </div>
            <div class="input-group role-group">
                <label>
                    <input type="radio" value="patient" v-model="role" />
                    我是患者
                </label>
                <label>
                    <input type="radio" value="doctor" v-model="role" />
                    我是医生
                </label>
                <!-- <label>
                    <input type="radio" value="family" v-model="role" />
                    我是家属
                </label> -->
            </div>
            <button type="submit" class="register-button">下一步</button>
        </form>
    </div>
    <div class="links">
        <router-link to="/Wallet" class="link-item"></router-link>
        <router-link to="/" class="link-item">已有账号 去登陆</router-link>
    </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      email: '',
      password: '',
      confirmPassword: '',
      role: ''
    };
  },
  methods: {
    async handleRegister() {
      if (!this.role) {
        alert('请选择身份');
        return;
      }

      if (this.password !== this.confirmPassword) {
        alert('密码不匹配，请重新输入。');
        return;
      }

      try {
        const response = await axios.post('http://115.190.118.22:5000/api/user/register', {
          email: this.email,
          password: this.password,
          role: this.role // ✅ 将角色发送给后端
        });

        alert(response.data.message);

        // 注册成功跳转下一步页面（邮箱验证）
        this.$router.push('/');
      } catch (error) {
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
    /* background: linear-gradient(135deg, #74ead5, #abb6e4); */
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

/* 步骤指示器样式 */
.step-indicator {
    display: flex;
    justify-content: center;
    /* 水平居中 */
    margin-bottom: 20px;
    /* 添加底部间距 */
}

.step {
    width: 15px;
    /* 圆点的宽度 */
    height: 15px;
    /* 圆点的高度 */
    border-radius: 50%;
    /* 圆形 */
    background-color: #053F5C;
    /* 默认颜色 */
    margin: 0 25px;
    /* 圆点之间的间距 */
}

.step.active {
    background-color: #053F5C;
    /* 激活状态的颜色 */
}

.step:nth-child(2) {
    background-color: #fcfcfc;
    /* 第二个圆点的颜色 */
}

.step:nth-child(3) {
    background-color: #fcfcfc;
    /* 第三个圆点的颜色 */
}

.register-container {
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
    /* 修改按钮颜色 */
    color: white;
    border: none;
    border-radius: 5px;
    /* 添加圆角 */
    cursor: pointer;
    transition: background-color 0.3s;
}

.register-button:hover {
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