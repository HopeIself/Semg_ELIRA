<template>
  <div class="plan-choose-container">
    <h1 class="title">训练计划选择</h1>
<button class="login-button" @click="goLogin">退出登录</button>
    <div class="button-group">
      <button class="plan-button" @click="goToAssessment">
        AI计划<br />
        <span class="desc">通过AI评估肌电信号生成智能个性化方案</span>
      </button>

      <button class="plan-button" @click="useHistoryPlan">
        历史计划<br />
        <span class="desc">沿用上一次的训练方案</span>
      </button>

      <button class="plan-button" @click="goToCustomPlan">
        自定义方案<br />
        <span class="desc">根据自身需要或医生建议自主定制方案</span>
      </button>
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
      alert("功能开发中，暂未实现历史计划跳转");
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
.plan-choose-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: start;
  padding-top: 100px;
  background: linear-gradient(to bottom, #d0ebff, #f0f9ff);
  font-family: "Microsoft YaHei", Arial, sans-serif;
}

.title {
  font-size: 2.8rem;
  font-weight: 700;
  margin-bottom: 60px;
  color: #1a73e8;
}

.button-group {
  display: flex;
  flex-direction: column;
  gap: 28px;
  width: 320px;
}

.plan-button {
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 14px;
  padding: 20px 15px;
  font-size: 1.2rem;
  font-weight: 600;
  cursor: pointer;
  text-align: center;
  line-height: 1.3;
  user-select: none;
  transition: background-color 0.25s ease;
}

.plan-button .desc {
  font-size: 0.85rem;
  font-weight: 400;
  display: block;
  margin-top: 8px;
  color: #dbe9ff;
}

.plan-button:hover {
  background-color: #357ab7;
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