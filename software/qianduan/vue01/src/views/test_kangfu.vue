<template>
  <div id="app">
    <h1>EMG Training Prediction</h1>

    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="status === '准备'" class="status">
      <p>准备阶段: {{ secondsLeft }}秒</p>
    </div>

    <div v-if="status === '采集中'" class="status">
      <p>采集中: {{ actionName }} - 剩余 {{ secondsLeft }}秒</p>
      <p v-for="(emg, index) in realtimeEmg" :key="index">EMG数据: {{ emg }}</p>
      
      <!-- 显示计算的百分比 -->
      <p v-if="percentRms !== null">百分比 RMS: {{ percentRms }}%</p>
      <p v-if="percentMnf !== null">百分比 MNF: {{ percentMnf }}%</p>
      <p v-if="percentMf !== null">百分比 MF: {{ percentMf }}%</p>
    </div>

    <div v-if="status === '休息'" class="status">
      <p>休息阶段: {{ secondsLeft }}秒</p>
      
      <!-- 统一显示特征值和AI反馈 -->
      <div>
        <p v-if="percentRms !== null">百分比 RMS: {{ percentRms }}%</p>
        <p v-if="percentMnf !== null">百分比 MNF: {{ percentMnf }}%</p>
        <p v-if="percentMf !== null">百分比 MF: {{ percentMf }}%</p>

        <!-- 只有当剩余时间 <= 13秒时才显示AI反馈 -->
        <p v-if="secondsLeft <= 13 && aiFeedback">AI反馈: {{ aiFeedback }}</p>
      </div>
    </div>

    <div v-if="status === '动作完成'" class="status">
      <p>{{ actionName }} 完成</p>
      <p>RMS: {{ rms }}</p>
      <p>MNF: {{ mnf }}</p>
      <p>MF: {{ mf }}</p>
      <p>百分比 RMS: {{ percentRms }}%</p>
      <p>百分比 MNF: {{ percentMnf }}%</p>
      <p>百分比 MF: {{ percentMf }}%</p>
    </div>

    <div v-if="status === '预测过程完成'" class="status">
      <p>预测过程完成!</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";

export default {
  name: "App",
  setup() {
    const status = ref("");
    const secondsLeft = ref(0);
    const realtimeEmg = ref([]);
    const actionName = ref("");
    const rms = ref(0);
    const mnf = ref(0);
    const mf = ref(0);
    const percentRms = ref(null); // 用于存储百分比RMS
    const percentMnf = ref(null); // 用于存储百分比MNF
    const percentMf = ref(null); // 用于存储百分比MF
    const error = ref("");
    const aiFeedback = ref(""); // 用于存储AI反馈

    // 从 localStorage 获取 id
    const id = localStorage.getItem("id"); // 确保localStorage中有id
    if (!id) {
      error.value = "未找到用户ID，请登录后再试";
    }

    const startTraining = async () => {
      if (!id) return;

      try {
        const eventSource = new EventSource(`http://115.190.134.66:5000/api/predict?id=${id}`);

        eventSource.onmessage = (event) => {
          const data = JSON.parse(event.data);
          console.log(data);

          if (data.error) {
            error.value = data.error;
            return;
          }

          status.value = data.status;
          secondsLeft.value = data.seconds_left || 0;
          realtimeEmg.value = data.realtime_emg || [];
          actionName.value = data.action_name || "";
          rms.value = data.rms || 0;
          mnf.value = data.mnf || 0;
          mf.value = data.mf || 0;
          if (data.percent_rms !== null) {
            percentRms.value = data.percent_rms || null; // 更新百分比RMS
          }
          if (data.percent_mnf !== null) {
            percentMnf.value = data.percent_mnf || null; // 更新百分比MNF
          }
          if (data.percent_mf !== null) {
            percentMf.value = data.percent_mf || null; // 更新百分比MF
          }
          // 只有当剩余时间 <= 13秒时，才更新AI反馈
          if (data.feedback && secondsLeft.value <= 13) {
            aiFeedback.value = data.feedback; // 更新AI反馈信息
          }
        };

        eventSource.onerror = (err) => {
          console.error("EventSource failed:", err);
          error.value = "无法连接到服务器，请检查后端服务";
        };
      } catch (err) {
        console.error("启动训练失败:", err);
        error.value = "启动训练失败，请稍后重试";
      }
    };

    onMounted(() => {
      startTraining();
    });

    return {
      status,
      secondsLeft,
      realtimeEmg,
      actionName,
      rms,
      mnf,
      mf,
      percentRms,
      percentMnf,
      percentMf,
      error,
      aiFeedback, // 暴露AI反馈信息
    };
  },
};
</script>

<style scoped>
#app {
  font-family: Arial, sans-serif;
  text-align: center;
  padding: 20px;
}

h1 {
  color: #42b983;
}

.status {
  margin-top: 20px;
}

.error {
  color: red;
  font-weight: bold;
}
</style>
