<template>
  <div class="assessment-container">
    <h1 class="title">训练动作尝试</h1>

    <!-- 右上角跳转按钮 -->
    <button class="skip-button" @click="goToNextStage">跳转到下一阶段</button>

    <div class="content">
      <div class="left">
        <img :src="currentActionImage" class="exercise-image" />
        <p class="image-label">{{ currentActionLabel }}</p>
      </div>

      <div class="right">
        <div v-if="!started">
          <button class="btn" @click="startTraining">开始训练</button>
        </div>
        <div v-else>
          <p v-if="started && !trainingFinished" class="round-info">
            动作测试共有 {{ totalRounds }} 轮，
            便于我们后续对您的动作进行评估<br>
            现在是第 {{ currentRound + 1 }} 轮
          </p>

          <p v-if="stage === 'prepare'">准备中：{{ secondsLeft }} 秒</p>
          <p v-else-if="stage === 'collect'">采集中：{{ secondsLeft }} 秒</p>
          <p v-else-if="stage === 'rest' && !trainingFinished">休息中：{{ secondsLeft }} 秒</p>
          <p v-else-if="trainingFinished" class="finished-msg">🎉 尝试阶段已完成</p>

          <p v-if="stage === 'collect'">实时肌电值：{{ emgValue }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      id: localStorage.getItem("id") || "",
      baseURL: "http://115.190.134.66:5000",
      started: false,
      eventSource: null,
      emgValue: null,
      secondsLeft: 0,
      stage: "",
      currentRound: 0,
      currentActionIndex: 0,
      totalRounds: 2,
      actions: [],
      trainingFinished: false,
    };
  },
  computed: {
    currentActionImage() {
      if (this.stage === "rest" && this.actions.length > this.currentActionIndex + 1) {
        return this.actions[this.currentActionIndex + 1].image;
      }
      return this.actions[this.currentActionIndex]?.image || "";
    },
    currentActionLabel() {
      if (this.stage === "rest" && this.actions.length > this.currentActionIndex + 1) {
        return this.actions[this.currentActionIndex + 1].label;
      }
      return this.actions[this.currentActionIndex]?.label || "";
    },
  },
  created() {
    const query = this.$route.query;
    if (query.custom === "true" && query.plan) {
      try {
        const plan = JSON.parse(query.plan);
        this.actions = plan.map((item, idx) => ({
          image: item.img,
          label: `动作${idx + 1}`,
        }));
      } catch (e) {
        console.error("plan 参数解析失败，使用默认动作");
        this.setDefaultActions();
      }
    } else {
      this.setDefaultActions();
    }
  },
  beforeUnmount() {
    if (this.eventSource) this.eventSource.close();
  },
  methods: {
    setDefaultActions() {
      this.actions = [
        { image: require("../assets/image1.jpg"), label: "动作1" },
        { image: require("../assets/image2.jpg"), label: "动作2" },
        { image: require("../assets/image3.jpg"), label: "动作3" },
      ];
    },
    goToNextStage() {
      this.$router.push("/breakbeginning");
    },
    startTraining() {
      if (!this.id) {
        alert("用户ID为空");
        return;
      }
      this.started = true;
      this.stage = "prepare";
      this.secondsLeft = 3;

      this.eventSource = new EventSource(
        `${this.baseURL}/api/start-training-process?id=${encodeURIComponent(this.id)}&code=1`
      );

      this.eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.status === "训练过程完成") {
            this.trainingFinished = true;
            this.stage = "done";
            if (this.eventSource) {
              this.eventSource.close();
              this.eventSource = null;
            }

            setTimeout(() => {
              this.$router.push("/breakbeginning");
            }, 2000);

            return;
          }

          this.stage = data.stage;
          this.secondsLeft = Math.max(0, data.seconds_left || 0);
          this.currentRound = data.current_round || 0;
          this.currentActionIndex = data.current_action_index || 0;

          if (Array.isArray(data.realtime_emg) && data.realtime_emg.length) {
            this.emgValue = data.realtime_emg[data.realtime_emg.length - 1];
          }

          if (
            this.stage === "rest" &&
            this.currentRound === this.totalRounds - 1 &&
            this.currentActionIndex === this.actions.length - 1
          ) {
            this.trainingFinished = true;
            this.stage = "done";
            if (this.eventSource) {
              this.eventSource.close();
              this.eventSource = null;
            }

            setTimeout(() => {
              this.$router.push("/breakbeginning");
            }, 2000);

            return;
          }
        } catch (e) {
          console.error("解析 SSE 数据失败:", e);
        }
      };

      this.eventSource.onerror = (err) => {
        console.error("SSE 连接失败:", err);
        if (this.eventSource) {
          this.eventSource.close();
          this.eventSource = null;
        }
      };
    },
  },
  mounted() {
    // 挂载 Coze Web Chat
    const script = document.createElement('script');
    script.src = "https://lf-cdn.coze.cn/obj/unpkg/flow-platform/chat-app-sdk/1.2.0-beta.10/libs/cn/index.js";
    script.onload = () => {
      new CozeWebSDK.WebChatClient({
        config: { bot_id: '7526864409868976143' },
        componentProps: { title: 'Coze' },
        auth: {
          type: 'token',
          token: 'pat_pOwdWuNOdyj47fbSnmTR0EKWlezCrzQebx0VjeYJuNmZNAlF48EKBQZEDRK6W3ys',
          onRefreshToken: () => 'pat_pOwdWuNOdyj47fbSnmTR0EKWlezCrzQebx0VjeYJuNmZNAlF48EKBQZEDRK6W3ys'
        }
      });
    };
    document.body.appendChild(script);
  },
};
</script>

<style scoped>
.assessment-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px;
}
.title {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 30px;
}
.content {
  display: flex;
  max-width: 900px;
  width: 100%;
  justify-content: center;
}
.left {
  flex: 1;
  text-align: center;
}
.exercise-image {
  width: 300px;
  height: auto;
  border-radius: 10px;
  border: 1px solid #ccc;
}
.image-label {
  margin-top: 10px;
  font-weight: bold;
}
.right {
  flex: 1;
  padding-left: 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.countdown-text,
.emg-text,
.finished-msg,
.round-info {
  font-size: 22px;
  margin: 10px 0;
}
.btn {
  padding: 10px 24px;
  font-size: 18px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.skip-button {
  position: absolute;
  top: 20px;
  right: 30px;
  background-color: #f56c6c;
  color: white;
  border: none;
  padding: 8px 16px;
  font-size: 14px;
  border-radius: 5px;
  cursor: pointer;
  z-index: 100;
}
</style>
