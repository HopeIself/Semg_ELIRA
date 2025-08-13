<template>
  <div class="plan-choose-container">
    <h1 class="title">选择训练计划生成方式</h1>
    <button class="back-button" @click="goBack">返回佩戴设备</button>
    <button class="login-button" @click="goLogin">退出登录</button>
    <div class="button-group">
      <button class="plan-button" @click="goToAssessment">
        个性化训练计划<br />
        <span class="desc">AI助手结合医生建议、患者信息生成个性化方案</span>
      </button>

      <button class="plan-button" @click="useHistoryPlan">
        历史计划<br />
        <span class="desc">沿用上一次训练方案</span>
      </button>

      <!--
      <button class="plan-button" @click="goToCustomPlan">
        自定义计划<br />
        <span class="desc">根据自身需要或医生建议自主制定方案</span>
      </button>
      -->
    </div>
  </div>
</template>

<script>
export default {
  name: "PlanChoosePage",
  methods: {
    goToAssessment() {
      this.$router.push({ path: '/assessment', query: { from: 'planchoose' } });
    },
    goToCustomPlan() {
      this.$router.push({ path: "/customplan" });
    },
    useHistoryPlan() {
      // 这里你可以根据需求改成跳转历史方案详情页或提示
      this.$router.push({ path: "/generatingplan" });;
    },
    goBack() {
      this.$router.push({ path: "/wear" });
    },
    goLogin() {
      this.$router.push({ path: "/" });
    },
  },
  mounted() {
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
  color: #333;  /* 文字颜色改为黑色 */
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
.plan-choose-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding-top: 100px;
  background: #f7f4e7;
  font-family: "Microsoft YaHei", Arial, sans-serif;
}

.title {
  font-size: 32px;
  font-weight: 700;
  margin-top: 15px;
  color: #333;
}

.button-group {
  display: flex;
  flex-direction: column;
  gap: 28px;
  width: 580px;
  background-color: #f7f4e7
}

.plan-button {
  color: #333;
  border: none;
  border-radius: 14px;
  padding: 20px 15px;
  font-size: 32px;
  font-weight: 600;
  cursor: pointer;
  text-align: center;
  line-height: 1.3;
  user-select: none;
  transition: background-color 0.25s ease;
  background-color: #fff;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  margin: 0 auto;
  margin-top: 50px;
  width: 580px;
  height: 100px;
}

.plan-button .desc {
  font-size: 20px;
  font-weight: 400;
  display: block;
  margin-top: 8px;
  color: #767171;
}
.plan-button:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}


.login-button {
  position: fixed;
  top: 20px;
  right: 20px;
  background: transparent;
  border: none;
  font-size: 24px;
  color: #333;
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