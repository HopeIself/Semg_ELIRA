<template>
  <div class="assessment-container">
    <h1 class="title">尝试训练动作</h1>
    <!-- 音效播放器 -->
    <audio id="beep-single" src="/sounds/di.mp3" preload="auto"></audio>
    <audio id="beep-double" src="/sounds/didi.mp3" preload="auto"></audio>
    <!-- 右上角跳转按钮 -->
    <button class="skip-button" @click="goToNextStage">跳转到下一阶段</button>
    <button class="back-button" @click="goBack">返回训练计划</button>
    <div class="content">
      <div class="left">
        <img :src="currentActionImage" class="exercise-image" />
        <p class="image-label">{{ currentActionLabel }}</p>
      </div>

      <div class="right">
        <div v-if="!started">
          <button class="btn" @click="startTraining">开始尝试</button>
        </div>
        <div v-else>
          <p v-if="started && !trainingFinished" class="round-info">
            动作测试共有 {{ totalRounds }} 轮，现在是第 {{ currentRound + 1 }} 轮
          </p>

          <p v-if="stage === 'prepare'" class="rest-text">准备中：{{ secondsLeft }} 秒</p>
          <p v-if="stage === 'collect'" class="round-info">正在进行：{{ currentActionLabel }}</p>
          <p v-if="stage === 'collect'" class="countdown-text">采集中：{{ secondsLeft }} 秒</p>
          <p v-else-if="stage === 'rest' && !trainingFinished" class="rest-text">休息中：{{ secondsLeft }} 秒</p>
          <p v-if="stage === 'rest' && currentActionIndex + 1 < actions.length" class="rest-text">
            即将开始：{{ actions[currentActionIndex + 1].label }} - {{ actions[currentActionIndex + 1].name }}
          </p>
          <p v-else-if="trainingFinished" class="finished-msg">🎉 尝试阶段已完成</p>

          <p v-if="stage === 'collect'" class="emg-text">实时肌电信号值：{{ emgValue }}</p>
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
      baseURL: "http://115.190.118.22:5000",
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
      lastStage: "",  // 用于记录上一个阶段，避免重复播放声音
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
      const index = (this.stage === 'rest' && this.actions.length > this.currentActionIndex + 1)
        ? this.currentActionIndex + 1
        : this.currentActionIndex;

      const action = this.actions[index];
      if (action) {
        return `${action.label} - ${action.name}`;
      }
      return '';
    }
  },
  created() {
    const query = this.$route.query;
    if (query.custom === "true" && query.plan) {
      try {
        const plan = JSON.parse(query.plan);
        this.actions = plan.map((item, idx) => ({
          image: item.img,
          label: `动作${idx + 1}`,
          name: item.description || `默认名称${idx + 1}`,  // 👈 保底填充名称
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
    // 播放文本内容的语音
    playTextAudio(text) {
      const speech = new SpeechSynthesisUtterance(text);  // 创建语音对象
      speech.lang = 'zh-CN';  // 设置中文语音
      window.speechSynthesis.speak(speech);  // 播放语音
    },

    handleStageChange(newStage) {
      if (newStage === 'prepare') {
        this.playTextAudio('准备中');
      } else if (newStage === 'collect') {
        // 在每个动作的阶段播放对应语音
        this.playTextAudio(`正在进行：${this.currentActionLabel}`);
      } else if (newStage === 'rest') {
        // 休息阶段只播报 "休息中，即将开始动作x"
        if (this.currentActionIndex + 1 < this.actions.length) {
          this.playTextAudio(`休息中，即将开始：${this.actions[this.currentActionIndex + 1].label}`);
        } else {
          this.playTextAudio('休息中');
        }
      } else if (newStage === 'done') {
        this.playTextAudio('尝试阶段已完成');
      }
    },


    playSound(which = 'single') {
      const audio = document.getElementById(
        which === 'double' ? 'beep-double' : 'beep-single'
      );
      if (audio) {
        audio.currentTime = 0;
        audio.play();
      }
    },
    goBack() {
      this.$router.push({ path: "/AItrainingplan" });
    },
  setDefaultActions() {
    this.actions = [
      { image: require("@/assets/fist.gif"), label: "动作1",name: "握拳与打开手掌" },
      { image: require("@/assets/hand.gif"), label: "动作2", name: "手掌旋转" },
      { image: require("@/assets/image3.gif"), label: "动作3", name: "腕屈曲" },
      { image: require("@/assets/image4.gif"), label: "动作4", name: "腕伸展" },
      { image: require("@/assets/image5.gif"), label: "动作5", name: "内侧旋转" },
      { image: require("@/assets/image6.gif"), label: "动作6", name: "外侧旋转" },
      { image: require("@/assets/image7.gif"), label: "动作7", name: "压手" },

    ];
  },
    goToNextStage() {
      this.$router.push("/breakbeginning");
    },
     // 在收到数据后更新状态
    async startTraining() {
      if (!this.id) {
        alert('用户ID为空');
        return;
      }
      this.started = true;
      this.stage = 'prepare';
      this.secondsLeft = 3;

      // 播报“准备中”
      this.handleStageChange('prepare');

      this.eventSource = new EventSource(
        `${this.baseURL}/api/start-training-process?id=${encodeURIComponent(this.id)}&code=1`
      );

      this.eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.status === '训练过程完成') {
            this.trainingFinished = true;
            this.stage = 'done';
            if (this.eventSource) {
              this.eventSource.close();
              this.eventSource = null;
            }

            setTimeout(() => {
              this.$router.push('/breakbeginning');
            }, 2000);

            // 播报“训练完成”
            this.handleStageChange('done');

            return;
          }

          // 切换阶段时播放语音
          if (data.stage !== this.stage) {
            this.handleStageChange(data.stage);
          }

          this.stage = data.stage;
          this.secondsLeft = Math.max(0, data.seconds_left || 0);
          this.currentRound = data.current_round || 0;
          this.currentActionIndex = data.current_action_index || 0;

          if (Array.isArray(data.realtime_emg) && data.realtime_emg.length) {
            this.emgValue = data.realtime_emg[data.realtime_emg.length - 1];
          }

          if (
            this.stage === 'rest' &&
            this.currentRound === this.totalRounds - 1 &&
            this.currentActionIndex === this.actions.length - 1
          ) {
            this.trainingFinished = true;
            this.stage = 'done';
            if (this.eventSource) {
              this.eventSource.close();
              this.eventSource = null;
            }

            setTimeout(() => {
              this.$router.push('/breakbeginning');
            }, 2000);

            // 播报“训练完成”
            this.handleStageChange('done');

            return;
          }
        } catch (e) {
          console.error('解析 SSE 数据失败:', e);
        }
      };

      this.eventSource.onerror = (err) => {
        console.error('SSE 连接失败:', err);
        if (this.eventSource) {
          this.eventSource.close();
          this.eventSource = null;
        }
      };
    }
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
  }
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
  margin-bottom: 100px;

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
  margin-bottom: 300px;
}

.rest-text,
.countdown-text,
.emg-text,
.finished-msg,
.round-info {
  font-size: 22px;
  margin: 10px 0;
  font-weight: bold;
  white-space: nowrap;
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
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 22px;
  font-weight: bold;
  position: fixed;
  top: 20px;
  right: 20px;
  background: transparent;
  border: none;
  color: #333333;  /* 文字颜色改为黑色 */
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

.skip-button:hover {
  text-decoration: underline;
}

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
</style>
