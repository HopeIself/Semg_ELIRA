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
      plan: [],               // 动作对象数组（适用于 AI 和 自定义）
      images: [],             // 动作图片路径数组
      descriptionText: '',    // 总描述文本（AI 的 message 或自定义拼接）
    };
  },
  created() {
  const query = this.$route.query;

  if (query.custom === 'true' && query.plan) {
    try {
      const parsed = JSON.parse(query.plan);

      // AI计划格式：包含 message 和 actions
      if (parsed.actions && parsed.message) {
        this.descriptionText = parsed.message;

        // AI计划动作名称到图片映射
        const actionMap = {
          "握拳与打开手掌": require('@/assets/image1.jpg'),
          "手掌旋转": require('@/assets/image2.jpg'),
          "腕屈曲": require('@/assets/image3.jpg'),
          "腕伸展": require('@/assets/image4.jpg'),
          "内侧旋转": require('@/assets/image5.jpg'),
          "外侧旋转": require('@/assets/image6.jpg'),
          "压手": require('@/assets/image7.jpg'),
          "手心向自己，手掌向内侧旋转": require('@/assets/image5.jpg'),
        };

        this.plan = parsed.actions.map(item => ({
          description: item.name,
          groupCount: 1,    // AI计划这里默认一组
          time: item.time,
          img: actionMap[item.name] || ''
        }));

        this.images = this.plan.map(item => item.img);
      }
      // 自定义计划格式：直接是动作数组
      else if (Array.isArray(parsed)) {
        this.plan = parsed;

        // 处理图片路径：本地资源或外链
        this.images = parsed.map(item => {
          // item.img 有可能是相对路径或绝对URL
          if (typeof item.img === 'string' && item.img.includes('image')) {
            // 从路径字符串提取文件名，再 require
            const filename = item.img.split('/').pop();
            return require(`@/assets/${filename}`);
          }
          return item.img; // 网络URL或base64直接返回
        });

        // 拼接描述文本，含组数和时长信息
        this.descriptionText = parsed.map(item => {
          const groupCount = item.groupCount || 1;
          return `${item.description} 每组15秒，共${groupCount}组`;
        }).join('；') + '。先尝试一下新动作吧！';
      }
      else {
        throw new Error('未知计划格式');
      }
    } catch (err) {
      console.error('解析训练计划失败：', err);
      this.setDefault();
    }
  } else {
    this.setDefault();
  }
},
  methods: {
    setDefault() {
      // 默认固定训练计划
      this.plan = [
        { description: '手掌翻转', groupCount: 3, time: 15, img: require('../assets/image2.jpg') },
        { description: '腕屈曲', groupCount: 3, time: 15, img: require('../assets/image3.jpg') },
        { description: '腕伸展', groupCount: 3, time: 15, img: require('../assets/image4.jpg') },
      ];
      this.images = this.plan.map(item => item.img);
      this.descriptionText = '今天的训练计划是：手掌翻转每组15秒，共3组；腕屈曲每组15秒，共3组；腕伸展每组15秒，共3组。先尝试一下新动作吧！';
    },
    goToAttempt() {
      this.$router.push({
        path: '/attempt',
        query: {
          custom: 'true',
          plan: JSON.stringify(this.plan)
        }
      });
    },
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
  }
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