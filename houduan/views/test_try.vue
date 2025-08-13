<template>
  <div id="app">
    <h1>多动作多轮采集训练</h1>
    <div>
      <label>用户ID: </label>
      <input v-model="id" placeholder="请输入用户ID" />
    </div>
    <button @click="startTraining" :disabled="isTraining">
      {{ isTraining ? '训练进行中...' : '开始训练' }}
    </button>

    <div v-if="isTraining" style="margin-top: 20px;">
      <h3>训练进度</h3>
      <p v-if="stage==='prepare'">准备中，倒计时: {{ secondsLeft }} 秒</p>
      <p v-if="stage==='collect'">
        采集中，剩余: {{ secondsLeft }} 秒
        <span v-if="currentActionName">| 当前动作: {{ currentActionName }} (ID: {{ currentActionId }})</span>
      </p>
      <p v-if="stage==='rest'">休息中，剩余: {{ secondsLeft }} 秒</p>
      <p>当前轮次: {{ currentRound + 1 }} / {{ totalRounds }}</p>
      <p>采集数据点数: {{ currentRawData.length }}</p>
      <div v-if="realtimeEmg.length">
        <h4>实时采集过程（每0.5秒）</h4>
        <pre style="max-height:200px;overflow:auto;">
{{ realtimeEmg.slice(-20).map(item => JSON.stringify(item)).join('\n') }}
        </pre>
      </div>
      <div v-if="currentRawData.length">
        <h4>当前采集原始数据（前10条）</h4>
        <pre style="max-height:200px;overflow:auto;">
{{ currentRawData.slice(0, 10).map(row => JSON.stringify(row)).join('\n') }}
        </pre>
      </div>
    </div>

    <div v-if="results.length && !isTraining" style="margin-top: 20px;">
      <h3>训练完成，采集结果</h3>
      <div v-for="(round, roundIdx) in results" :key="roundIdx" style="margin-bottom: 16px;">
        <b>第 {{ roundIdx + 1 }} 轮</b>
        <div v-for="(item, actIdx) in round" :key="actIdx" style="margin-left: 16px;">
          <span>动作: {{ item.action_name }} (ID: {{ item.action_id }})</span>
          <span> | RMS: {{ item.rms.toFixed(2) }} | MNF: {{ item.mnf.toFixed(2) }} | MF: {{ item.mf.toFixed(2) }}</span>
          <span> | 数据点数: {{ item.data.length }}</span>
        </div>
      </div>
    </div>

    <div v-if="error" class="error">
      <p>{{ error }}</p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      id: localStorage.getItem("id") || "",
      isTraining: false,
      currentRound: 0,
      totalRounds: 0,
      currentActionName: "",
      currentActionId: "",
      currentRawData: [],
      results: [],
      error: "",
      stage: "",
      secondsLeft: 0,
      realtimeEmg: [],
      eventSource: null
    };
  },
  methods: {
    startTraining() {
      if (!this.id) {
        this.error = "用户ID为空，请先输入ID";
        return;
      }
      this.isTraining = true;
      this.error = "";
      this.results = [];
      this.currentRawData = [];
      this.currentActionName = "";
      this.currentActionId = "";
      this.currentRound = 0;
      this.totalRounds = 0;
      this.stage = "";
      this.secondsLeft = 0;
      this.realtimeEmg = [];
      if (this.eventSource) {
        this.eventSource.close();
        this.eventSource = null;
      }
      // SSE监听
      this.eventSource = new EventSource(`http://115.190.118.22:5000/api/start-training-process?id=${encodeURIComponent(this.id)}&code=1`);
      this.eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.error) {
            this.error = data.error;
            this.isTraining = false;
            this.eventSource.close();
            this.eventSource = null;
            return;
          }
          if (data.status === "训练过程完成") {
            this.isTraining = false;
            this.results = data.results || [];
            this.currentRawData = [];
            this.currentActionName = "";
            this.currentActionId = "";
            this.stage = "";
            this.secondsLeft = 0;
            this.eventSource.close();
            this.eventSource = null;
            return;
          }
          // 修正剩余秒数显示，保证不为负数
          this.stage = data.stage || "";
          this.secondsLeft = Math.max(0, data.seconds_left || 0);
          this.currentRound = data.current_round || 0;
          this.currentActionName = "";
          this.currentActionId = "";
          this.currentRawData = [];
          // 轮次数以results长度为准
          this.totalRounds = (data.results || []).length;
          // 当前动作数据
          if (Array.isArray(data.results) && data.results[this.currentRound]) {
            const roundArr = data.results[this.currentRound];
            const actIdx = data.current_action_index || 0;
            if (roundArr && roundArr[actIdx]) {
              this.currentActionName = roundArr[actIdx].action_name || "";
              this.currentActionId = roundArr[actIdx].action_id || "";
              this.currentRawData = roundArr[actIdx].data || [];
            }
          }
          // 采集阶段直接用后端推送的动作名和ID
          if (this.stage === "collect") {
            if (data.action_name) this.currentActionName = data.action_name;
            if (data.action_id !== undefined) this.currentActionId = data.action_id;
          }
          // 实时emg采集
          if (Array.isArray(data.realtime_emg) && data.realtime_emg.length) {
            this.realtimeEmg.push(...data.realtime_emg);
            if (this.realtimeEmg.length > 200) this.realtimeEmg = this.realtimeEmg.slice(-200);
          }
        } catch (e) {}
      };
      this.eventSource.onerror = () => {
        this.isTraining = false;
        this.eventSource && this.eventSource.close();
        this.eventSource = null;
      };
    }
  },
  beforeDestroy() {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }
};
</script>

<style scoped>
.error {
  color: red;
}
</style>

