<template>
  <div id="app">
    <h2>康复训练监测</h2>
    <button class="skip-button" @click="goToNextStage">跳转到下一阶段</button>

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
        <div v-if="status === '准备'">
          <p>准备阶段：{{ secondsLeft }} 秒</p>
        </div>

        <!-- 采集中 -->
        <div v-else-if="status === '采集中'">
          <p>当前轮数：{{ currentGroup }} / {{ totalRepeat }}</p>
          <p>剩余采集时间：{{ secondsLeft }} 秒</p>
          <p v-if="latestEmg">肌电值：{{ latestEmg }}</p>
          <p v-if="percentRms !== null">百分比 RMS: {{ percentRms }}%</p>
          <p v-if="percentMnf !== null">百分比 MNF: {{ percentMnf }}%</p>
          <p v-if="percentMf !== null">百分比 MF: {{ percentMf }}%</p>
        </div>

        <!-- 休息阶段 -->
        <div v-else-if="status === '休息'">
          <p>休息阶段：剩余 {{ secondsLeft }} 秒</p>
          <p v-if="percentRms !== null">百分比 RMS: {{ percentRms }}%</p>
          <p v-if="percentMnf !== null">百分比 MNF: {{ percentMnf }}%</p>
          <p v-if="percentMf !== null">百分比 MF: {{ percentMf }}%</p>
          <p v-if="nextActionName">下一个动作：{{ nextActionName }}</p>
          <!-- 仅在20秒休息时显示 AI 反馈 -->
  <!-- <p v-if="secondsLeft === 20 && aiFeedback">AI反馈: {{ aiFeedback }}</p> -->
          <!-- 仅当后端 stage 为 rest 且秒数<=13时展示 AI 反馈 -->
          <p v-if="stage === 'rest' && aiFeedback && secondsLeft <= 10">AI反馈: {{ aiFeedback }}</p>
       
        </div>

        <!-- 动作完成 -->
        <div v-else-if="status === '动作完成'">
          <p>{{ actionName }} 完成</p>
          <p>RMS: {{ rms }}</p>
          <p>MNF: {{ mnf }}</p>
          <p>MF: {{ mf }}</p>
          <p>百分比 RMS: {{ percentRms }}%</p>
          <p>百分比 MNF: {{ percentMnf }}%</p>
          <p>百分比 MF: {{ percentMf }}%</p>
        </div>

        <!-- 训练结束 -->
        <div v-else-if="status === '训练结束' || status === '预测过程完成'">
          <p>🎉 训练已结束</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

// 映射表（动作名 => 图片路径）
const imageMap = {
  "握拳与打开手掌": require('@/assets/image1.jpg'),
  "手掌旋转": require('@/assets/image2.jpg'),
  "腕屈曲": require('@/assets/image3.jpg'),
  "腕伸展": require('@/assets/image4.jpg'),
  "内侧旋转": require('@/assets/image5.jpg'),
  "外侧旋转": require('@/assets/image6.jpg'),
  "压手": require('@/assets/image7.jpg'),
  "手心向自己，手掌向内侧旋转": require('@/assets/image5.jpg'),
  "手心向自己，手掌向外侧旋转": require('@/assets/image6.jpg'),
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
    const id = localStorage.getItem('id')
    let emgIndex = 0
    let previousStatus = ''
    let previousAction = ''

    onMounted(() => {
      if (!id) return

      const eventSource = new EventSource(`http://115.190.134.66:5000/api/predict?id=${id}`)

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data)

        // 动作切换时重置轮次
        if (data.action_name && data.action_name !== previousAction) {
          currentGroup.value = 1
        }

        // 更新状态、阶段、动作及下一个动作
        if (data.status) status.value = data.status
        if (data.stage) stage.value = data.stage
        if (data.action_name) {
          actionName.value = data.action_name
          previousAction = data.action_name
        }
        if (data.next_action_name) nextActionName.value = data.next_action_name
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

        // 采集 -> 休息时，轮次+1
        if (status.value === '休息' && previousStatus === '采集中') {
          currentGroup.value++
        }

        previousStatus = status.value
      }

      eventSource.onerror = (err) => {
        console.error('SSE错误:', err)
        eventSource.close()
      }

      // 每0.5秒更新一次肌电显示
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
.container {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px;
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
.action-name {
  font-weight: bold;
  margin-bottom: 16px;
  font-size: 18px;
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