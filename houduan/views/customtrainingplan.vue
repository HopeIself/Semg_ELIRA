<template>
  <button class="login-button" @click="goLogin">退出登录</button>
  <button class="back-button" @click="goBack">←返回计划选择</button>
  <div class="training-plan-container">
    <!-- 标题 -->
    <h1 class="title">训练计划</h1>



    <!-- 图片展示区 -->
    <div class="image-row">
      <div class="image-wrapper" v-for="(img, index) in images" :key="index">
        <img :src="img" class="plan-image" />
      </div>
    </div>

    <!-- 说明文字 -->
    <p class="description">
  {{ descriptionText }}
</p>


    <!-- 尝试新动作按钮 -->
    <button class="attempt-btn" @click="goToAttempt">
      尝试新动作
    </button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      images: [],
      descriptionText: '',
    };
  },
  created() {
    const query = this.$route.query;

    if (query.custom === 'true' && query.plan) {
      try {
        const plan = JSON.parse(query.plan);

        // 构造描述文字
        this.descriptionText = plan.map(item => {
          return `${item.description}每组15秒，共${item.groupCount}组`;
        }).join('；') + '。先尝试一下新动作吧！';

        // 动态设置图片数组（保持顺序）
        this.images = plan.map(item => item.img);

      } catch (err) {
        console.error('解析自定义计划失败：', err);
        this.setDefault();
      }
    } else {
      this.setDefault();
    }
  },
  methods: {
    setDefault() {
      this.images = [
        require('../assets/image1.jpg'),
        require('../assets/image2.jpg'),
        require('../assets/image3.jpg'),
      ];
      this.descriptionText =
        '今天的训练计划是：手掌翻转每组15秒，共3组；腕屈曲每组15秒，共3组；腕伸展每组15秒，共3组。先尝试一下新动作吧！';
    },
    goToAttempt() {
  const query = this.$route.query;
  if (query.custom === 'true' && query.plan) {
    this.$router.push({
      path: '/attempt',
      query: {
        custom: 'true',
        plan: query.plan  // 原样传递给 attempt 页面
      }
    });
  } else {
    this.$router.push({ path: '/attempt' });  // 默认固定计划
  }
}
,
    goLogin() {
      this.$router.push({ path: "/" });
    },
    goBack() {
      this.$router.push({ path: "/planchoose" });
    }
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

  padding: 0;
  margin: 0;
  line-height: 1;
  width: auto;
  height: auto;
  display: inline-block;
}

.back-button:hover {
  text-decoration: underline; 
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



.training-plan-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
  text-align: center;
  font-family: "Microsoft YaHei", sans-serif;
}

.title {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 30px;
}

.image-row {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 25px;
  flex-wrap: wrap;
}

.image-wrapper {
  width: 200px;
}

.plan-image {
  width: 100%;
  height: auto;
  border-radius: 10px;
  border: 1px solid #ccc;
}

.description {
  font-size: 18px;
  margin-bottom: 30px;
  color: #333;
}

.attempt-btn {
  padding: 12px 30px;
  font-size: 18px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.attempt-btn:hover {
  background-color: #318ce7;
}
</style>