<template>
  <div id="app">
    <h2 class="title">康复训练监测</h2>
    <!-- 音效播放器 -->
     <audio id="celebrate-sound" src="/sounds/celebrate.mp3" preload="auto"></audio>
    <audio id="beep-single" src="/sounds/di.mp3" preload="auto"></audio>
    <audio id="beep-double" src="/sounds/didi.mp3" preload="auto"></audio>
    <button class="skip-button" @click="goToNextStage">跳转到下一个阶段</button>

    <div class="container">
      <!-- 动作图片：准备阶段及其它阶段均显示当前动作图片 -->
      <div class="left">
        <img
          :src="imageMap[actionName] || imageMap[nextActionName]"
          alt="动作图片"
          class="img"
        />
      </div>

      <!-- 右侧状态显示 -->
      <div class="right">
        <p v-if="status !== '休息'" class="action-name">当前动作：{{ actionName }}</p>

        <!-- 准备阶段 -->
        <div v-if="status === '准备'" class="text">
          <p class="text">准备阶段：{{ secondsLeft }} 秒</p>
        </div>

        <!-- 采集中 -->
        <div v-else-if="status === '采集中'" class="text">
          <p class="text">当前轮数：{{ currentGroup }} / {{ totalRepeat }}</p>
          <p class="text">采集倒计时：{{ secondsLeft }} 秒</p>
          <p v-if="latestEmg" class="text">肌电值：{{ latestEmg }}</p>
          <p v-if="percentRms !== null" class="text" >百分比 RMS: {{ percentRms }}%</p>
          <p v-if="percentMnf !== null" class="text">百分比 MNF: {{ percentMnf }}%</p>
          <p v-if="percentMf !== null" class="text">百分比 MF: {{ percentMf }}%</p>
        </div>

        <!-- 休息阶段 -->
        <div v-else-if="status === '休息'" class="text">
          <p class="text">休息阶段：倒计时 {{ secondsLeft }} 秒</p>
          <p v-if="percentRms !== null" class="text">百分比 RMS: {{ percentRms }}%</p>
          <p v-if="percentMnf !== null" class="text">百分比 MNF: {{ percentMnf }}%</p>
          <p v-if="percentMf !== null" class="text">百分比 MF: {{ percentMf }}%</p>
          <p v-if="nextActionName" class="text">下一个动作：{{ nextActionName }}</p>
          <!-- 最后动作的反馈 -->
          <p v-if="stage === 'rest' && aiFeedback && secondsLeft <= 10" class="ai-text">AI反馈: {{ aiFeedback.message }}</p>
        </div>

        <!-- 动作完成 -->
        <div v-else-if="status === '动作完成'" class="text">
          <p class="text">{{ actionName }} 完成</p>
          <p class="text">RMS: {{ rms }}</p>
          <p class="text">MNF: {{ mnf }}</p>
          <p class="text">MF: {{ mf }}</p>
          <p class="text">百分比 RMS: {{ percentRms }}%</p>
          <p class="text">百分比 MNF: {{ percentMnf }}%</p>
          <p class="text">百分比 MF: {{ percentMf }}%</p>
        </div>

        <!-- 训练结束（仅当最后休息完成才显示） -->
        <div v-else-if="status === '训练结束' && isFinalRestOver" class="text">
          <p class="text">🎉 训练已结束</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const imageMap = {
  "握拳与打开手掌": require('@/assets/fist.gif'),
  "手掌旋转": require('@/assets/hand.gif'),
  "腕屈曲": require('@/assets/image3.gif'),
  "腕伸展": require('@/assets/image4.gif'),
  "内侧旋转": require('@/assets/image5.gif'),
  "外侧旋转": require('@/assets/image6.gif'),
  "压手": require('@/assets/image7.gif'),
  "手心向自己，手掌向内侧旋转": require('@/assets/image5.gif'),
  "手心向自己，手掌向外侧旋转": require('@/assets/image6.gif'),
}

export default {
  name: 'TrainingMonitor',
  setup() {
    const status = ref('')
    const stage = ref('')
    const actionName = ref('')
    const nextActionName = ref('')
    const secondsLeft = ref(0)
    const realtimeEmg = ref([])
    const latestEmg = ref('')
    const rms = ref(0)
    const mnf = ref(0)
    const mf = ref(0)
    const percentRms = ref(null)
    const percentMnf = ref(null)
    const percentMf = ref(null)
    const currentGroup = ref(1)
    const totalRepeat = ref(null)
    const aiFeedback = ref('')
    const isFinalResting = ref(false)
    const id = localStorage.getItem('id')
    let emgIndex = 0
    let previousStatus = ''
    let previousAction = ''
    let hasPlayedCelebrate = false   // ✅ 新增

    const router = useRouter()
    let lastMessageTime = Date.now()
    let hasJumped = false

    function playCelebrateSound() {
      const audio = document.getElementById('celebrate-sound');
      if (audio) {
        audio.currentTime = 0;
        audio.play();
      }
    }

    function playTextAudio(text) {
      const speech = new SpeechSynthesisUtterance(text);  // 创建语音对象
      speech.lang = 'zh-CN';  // 设置中文语音
      window.speechSynthesis.speak(speech);  // 播放语音
    }

    onMounted(() => {
      if (!id) return
      const eventSource = new EventSource(`http://115.190.118.22:5000/api/predict?id=${id}`)

      eventSource.onmessage = (event) => {
        lastMessageTime = Date.now()  // 每次收到数据时更新
        const data = JSON.parse(event.data)

        if (data.action_name && data.action_name !== previousAction) {
          currentGroup.value = 1
        }

        // --- 播放音效控制 ---
        if (data.status && data.status !== previousStatus) {
          if (data.status === '准备') {
            playTextAudio('准备中');
          } else if (previousStatus === '准备' && data.status === '采集中') {
            playTextAudio(`正在进行：${data.action_name}`);
          } else if (previousStatus === '采集中' && data.status === '休息') {
            playTextAudio(`休息中：${data.seconds_left} 秒`);
            if (data.next_action_name) {
              playTextAudio(`下一个动作：${data.next_action_name}`);
            }
          } else if (data.status === '训练结束') {
            playTextAudio('训练已结束');
          }
        }


        if (data.status) status.value = data.status
        if (data.stage) stage.value = data.stage
        if (data.action_name) {
          actionName.value = data.action_name
          previousAction = data.action_name
        }
        if (data.next_action_name !== undefined) nextActionName.value = data.next_action_name
        if (data.seconds_left !== undefined) secondsLeft.value = data.seconds_left
        if (data.realtime_emg) {
          realtimeEmg.value = data.realtime_emg
          emgIndex = 0
        }
        if (data.rms !== undefined) rms.value = data.rms
        if (data.mnf !== undefined) mnf.value = data.mnf
        if (data.mf !== undefined) mf.value = data.mf
        if (data.percent_rms !== undefined) percentRms.value = data.percent_rms
        if (data.percent_mnf !== undefined) percentMnf.value = data.percent_mnf
        if (data.percent_mf !== undefined) percentMf.value = data.percent_mf
        if (data.repeat !== undefined) totalRepeat.value = data.repeat
        if (data.feedback) aiFeedback.value = data.feedback
        if (
          data.status === '训练结束' &&
          isFinalRestOver.value === true &&
          !hasPlayedCelebrate
        ) {
          playCelebrateSound();
          hasPlayedCelebrate = true;
        }
        // 轮次加1：采集结束 -> 休息
        if (status.value === '休息' && previousStatus === '采集中') {
          currentGroup.value++
        }

        if (status.value === '预测过程完成') {
          if (!hasJumped) {
            hasJumped = true
            router.push({ path: '/assessment', query: { from: 'breakend' } })
          }
        }

        previousStatus = status.value
      }

      eventSource.onerror = (err) => {
        console.error('SSE错误:', err)
        eventSource.close()
      }

      // 每0.5秒更新实时肌电
      setInterval(() => {
        if (realtimeEmg.value.length) {
          latestEmg.value = realtimeEmg.value[emgIndex % realtimeEmg.value.length]
          emgIndex++
        }
      }, 500)
    })

    return {
      status,
      stage,
      actionName,
      nextActionName,
      secondsLeft,
      latestEmg,
      rms,
      mnf,
      mf,
      percentRms,
      percentMnf,
      percentMf,
      currentGroup,
      totalRepeat,
      aiFeedback,
      imageMap,
    }
  },
}
</script>

<style scoped>
.title {
  text-align: center;
  margin-top: 80px;
  font-size: 28px;
  font-weight: bold;
}
.container {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px;
  margin-bottom: 80px;
}
.left {
  flex: 1;
  text-align: center;
}
.right {
  flex: 1;
  padding-left: 40px;
}
.img {
  width: 250px;
  border-radius: 10px;
  margin: 10px 0;
}
.text {
  font-weight: bold;
  margin-bottom: 16px;
  font-size: 22px;
  white-space: nowrap;
}
.ai-text {
  font-weight: bold;
  margin-bottom: 16px;
  font-size: 22px;
  text-align: left; /* 强制左对齐 */
  white-space: wrap;
}
.action-name {
  font-weight: bold;
  margin-bottom: 16px;
  font-size: 22px;
  white-space: nowrap;
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
</style>