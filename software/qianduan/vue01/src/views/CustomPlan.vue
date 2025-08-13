<template>
  <div class="custom-plan-page">
    <button class="back-button" @click="goBack">← 方案选择</button>

    <h1>自定义训练方案</h1>

    <div v-if="!started" class="config-section">
      <h2>选择动作和组数，安排顺序</h2>

      <div class="actions-list">
        <div v-for="(exercise, index) in allExercises" :key="index" class="exercise-select">
          <label>
            <input type="checkbox" v-model="selectedExercises" :value="exercise.id" />
            {{ exercise.description }}
          </label>
          <select v-if="selectedExercises.includes(exercise.id)" v-model.number="groups[exercise.id]">
            <option v-for="n in 5" :key="n" :value="n">{{ n }} 组</option>
          </select>
        </div>
      </div>

      <div v-if="selectedExercises.length > 1" class="order-section">
        <h3>调整动作顺序</h3>
        <ul>
          <li v-for="(id, idx) in selectedExercises" :key="id">
            <span class="exercise-label">{{ allExercises.find(e => e.id === id).description }}</span>
            <div class="order-buttons">
              <button @click="moveUp(idx)" :disabled="idx === 0">顺序前移</button>
              <button @click="moveDown(idx)" :disabled="idx === selectedExercises.length - 1">顺序后移</button>
            </div>
          </li>
        </ul>
      </div>

      <button :disabled="selectedExercises.length === 0" @click="startTraining" class="start-btn">
        开始训练
      </button>
    </div>

    <div v-else class="training-section">
      <h2>动作 {{ currentIndex + 1 }} / {{ totalActions }}</h2>
      <h3>{{ currentExercise.description }} — {{ Math.min(currentGroupCount, groups[currentExercise.id]) }} / {{
        groups[currentExercise.id] }} 组</h3>
      <img :src="currentExercise.img" alt="动作图片" class="exercise-image" />

      <button class="complete-btn" @click="nextStep">
        {{ isCurrentGroupComplete ? (isLastExercise ? '完成方案，返回' : '下一动作') : '完成当前组' }}
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: "CustomPlan",
  data() {
    return {
      allExercises: [
        { id: 1, description: "握拳与手掌张开", img: require("../assets/image1.jpg") },
        { id: 2, description: "手掌旋转", img: require("../assets/image2.jpg") },
        { id: 3, description: "腕屈曲", img: require("../assets/image3.jpg") },
        { id: 4, description: "腕伸展", img: require("../assets/image4.jpg") },
        { id: 5, description: "内侧旋转", img: require("../assets/image5.jpg") },
        { id: 6, description: "外侧旋转", img: require("../assets/image6.jpg") },
        { id: 7, description: "压手动作", img: require("../assets/image7.jpg") },
      ],
      selectedExercises: [],
      groups: {},
      started: false,
      currentIndex: 0,
      currentGroupCount: 1,
    };
  },
  watch: {
  selectedExercises(newVal) {
    newVal.forEach(id => {
      if (!this.groups[id]) {
        this.groups[id] = 3; // Vue 3 中直接赋值即可
      }
    });

    // 删除未勾选的项目
    Object.keys(this.groups).forEach(id => {
      if (!newVal.includes(Number(id))) {
        delete this.groups[id];
      }
    });
  }
},

  computed: {
    currentExercise() {
      const id = this.selectedExercises[this.currentIndex];
      return this.allExercises.find((e) => e.id === id);
    },
    totalActions() {
      return this.selectedExercises.length;
    },
    currentGroupTotal() {
      return this.groups[this.currentExercise.id] || 1;
    },
    isCurrentGroupComplete() {
      return this.currentGroupCount > this.currentGroupTotal;
    },
    isLastExercise() {
      return this.currentIndex === this.totalActions - 1;
    },
  },
  methods: {
    moveUp(idx) {
      if (idx === 0) return;
      const arr = [...this.selectedExercises];
      [arr[idx - 1], arr[idx]] = [arr[idx], arr[idx - 1]];
      this.selectedExercises = arr;
    },
    moveDown(idx) {
      if (idx === this.selectedExercises.length - 1) return;
      const arr = [...this.selectedExercises];
      [arr[idx + 1], arr[idx]] = [arr[idx], arr[idx + 1]];
      this.selectedExercises = arr;
    },
    startTraining() {
  const selectedPlan = this.selectedExercises.map(id => {
    const exercise = this.allExercises.find(e => e.id === id);
    return {
      id,
      description: exercise.description,
      groupCount: this.groups[id] || 3,
      img: exercise.img
    };
  });

  this.$router.push({
    path: "/customtrainingplan",
    query: {
      custom: "true",
      plan: JSON.stringify(selectedPlan)
    }
  });
},
    nextStep() {
      if (!this.isCurrentGroupComplete) {
        this.currentGroupCount++;
      } else {
        if (this.isLastExercise) {
          alert("你已完成自定义方案中所有动作！");
          this.$router.push({ path: "/customtrainingplan" });
        } else {
          this.currentIndex++;
          this.currentGroupCount = 1;
        }
      }
    },
    goBack() {
      this.$router.push({ path: "/planchoose" });
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
.custom-plan-page {
  max-width: 600px;
  margin: 30px auto;
  font-family: Arial, sans-serif;
  padding: 10px;
}

.actions-list {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.exercise-select {
  width: 45%;
  background: #f9f9f9;
  padding: 10px;
  border-radius: 8px;
}

.exercise-select label {
  cursor: pointer;
}

.exercise-select select {
  margin-left: 10px;
  width: 70px;
}

.order-section {
  margin-top: 20px;
}

.order-section ul {
  list-style: none;
  padding: 0;
}

.order-section li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  border-bottom: 1px dashed #ddd;
  padding-bottom: 6px;
}

.exercise-label {
  width: 140px;
  text-align: left;
  font-weight: bold;
}

.order-buttons button {
  margin-left: 6px;
  padding: 4px 10px;
  font-size: 14px;
  cursor: pointer;
}

.start-btn,
.complete-btn {
  margin-top: 20px;
  font-size: 18px;
  padding: 12px 30px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
}

.start-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.exercise-image {
  width: 100%;
  max-height: 300px;
  object-fit: contain;
  border-radius: 10px;
  margin: 20px 0;
  display: block;
}

.back-button {
  position: fixed;
  top: 0;
  left: 0;
  background-color: transparent;
  border: none;
  font-size: 24px;
  color: #e31111;
  cursor: pointer;
  padding: 10px;
  margin: 0;
  z-index: 1000;
}

.back-button:hover {
  text-decoration: underline;
}
</style>