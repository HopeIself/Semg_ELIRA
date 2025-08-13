<template>
  <div class="min-h-screen p-10 bg-gray-100">
    <!-- 首页视图 -->
    <div v-if="currentView === 'home'">
      <h1 class="text-2xl font-bold mb-6">医生端 - 患者列表</h1>

      <!-- 添加患者功能 -->
      <div class="mb-6">
        <button
          @click="showAddForm = !showAddForm"
          class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
        >
          {{ showAddForm ? '取消添加' : '添加新患者' }}
        </button>

        <div v-if="showAddForm" class="mt-4 space-y-4">
          <input v-model="newPatient.name" placeholder="姓名" class="p-2 border rounded w-full" />
          <input v-model="newPatient.gender" placeholder="性别" class="p-2 border rounded w-full" />
          <input v-model.number="newPatient.age" placeholder="年龄" type="number" class="p-2 border rounded w-full" />
          <input v-model="newPatient.date" placeholder="训练日期（例如：2025-07-08）" class="p-2 border rounded w-full" />
          <button
            @click="addPatient"
            class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            确认添加
          </button>
        </div>
      </div>

      <!-- 患者列表 -->
      <div class="flex gap-6 flex-wrap">
        <div
          v-for="patient in patients"
          :key="patient.id"
          class="w-64 p-6 bg-white border border-gray-300 rounded-lg shadow relative"
        >
          <h2
            class="text-xl font-semibold cursor-pointer border border-blue-400 px-2 py-1 rounded text-center hover:bg-blue-50 transition"
            @click="viewReport(patient.id)"
          >
            {{ patient.name }}
          </h2>
          <p class="text-sm text-gray-500">点击查看康复训练报告</p>
          <button
            class="absolute top-2 right-2 text-red-600 hover:text-red-800"
            @click="deletePatient(patient.id)"
          >
            删除
          </button>
        </div>
      </div>
    </div>

    <!-- 报告视图 -->
    <div v-else-if="currentView === 'report'" class="bg-white p-6 rounded-xl shadow">
      <h1 class="text-2xl font-bold mb-6">患者 {{ selectedPatientId }} 的康复训练报告</h1>

      <!-- 1. 基本信息 -->
      <div class="mb-6">
        <h2 class="text-xl font-semibold mb-2">基本信息</h2>
        <ul class="text-gray-700">
          <li><strong>姓名：</strong>{{ patientInfo.name }}</li>
          <li><strong>性别：</strong>{{ patientInfo.gender }}</li>
          <li><strong>年龄：</strong>{{ patientInfo.age }} 岁</li>
          <li><strong>训练日期：</strong>{{ patientInfo.date }}</li>
        </ul>
      </div>

      <!-- 2. 康复项目概述 -->
      <div class="mb-6">
        <h2 class="text-xl font-semibold mb-2">康复项目概述</h2>
        <p class="text-gray-700">{{ patientInfo.projectDesc }}</p>
      </div>

      <!-- 3. 肌电信号图 -->
      <div class="mb-6">
        <h2 class="text-xl font-semibold mb-2">肌电信号图</h2>
        <div class="grid grid-cols-3 gap-4">
          <div v-for="(img, index) in emgImages" :key="index" class="border p-2 rounded">
            <p class="text-sm text-gray-600 mb-1">图 {{ index + 1 }}</p>
            <img :src="img" alt="EMG Signal" class="w-full h-32 object-contain" />
          </div>
        </div>
      </div>

      <!-- 4. 康复指标数据表 -->
      <div class="mb-6">
        <h2 class="text-xl font-semibold mb-2">康复指标数据</h2>
        <table class="w-full border border-gray-300 table-auto">
          <thead class="bg-gray-100 text-center">
            <tr>
              <th class="border px-4 py-2">指标名称</th>
              <th class="border px-4 py-2">单位</th>
              <th class="border px-4 py-2">训练前</th>
              <th class="border px-4 py-2">训练后</th>
              <th class="border px-4 py-2">变化趋势</th>
              <th class="border px-4 py-2">参考标准 / 意义说明</th>
            </tr>
          </thead>
          <tbody class="text-center">
            <tr v-for="(item, index) in metrics" :key="index">
              <td class="border px-4 py-2">{{ item.name }}</td>
              <td class="border px-4 py-2">{{ item.unit }}</td>
              <td class="border px-4 py-2">{{ item.before }}</td>
              <td class="border px-4 py-2">{{ item.after }}</td>
              <td class="border px-4 py-2">{{ item.trend }}</td>
              <td class="border px-4 py-2">{{ item.note }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 5. 医生评语 -->
      <div class="mb-6">
        <h2 class="text-xl font-semibold mb-2">医生评语</h2>
        <textarea
          v-model="doctorComment"
          rows="4"
          class="w-full p-3 border border-gray-300 rounded"
          placeholder="请输入医生评语..."
        />
      </div>

      <button
        class="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        @click="goBack"
      >
        返回患者列表
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const currentView = ref('home')
const selectedPatientId = ref(null)

const patients = ref([
  { id: 1, name: '患者 1' },
  { id: 2, name: '患者 2' }
])

const patientInfo = ref({
  name: '张三',
  gender: '男',
  age: 45,
  date: '2025-07-08',
  projectDesc: '本次训练主要针对下肢肌群力量恢复，进行了稳定性训练、踝关节灵活性提升训练和姿势控制训练，训练过程中患者配合度良好。'
})

const emgImages = [
  'https://via.placeholder.com/300x100?text=EMG+图1',
  'https://via.placeholder.com/300x100?text=EMG+图2',
  'https://via.placeholder.com/300x100?text=EMG+图3'
]

const metrics = [
  {
    name: 'RMS（均方根值）', unit: 'μV', before: 104.3, after: 132.5, trend: '↑27%', note: '肌肉整体激活增强'
  },
  {
    name: 'MDF（中位频率）', unit: 'Hz', before: 87.1, after: 79.4, trend: '↓8.8%', note: '疲劳有轻度增加'
  },
  {
    name: 'Activation Ratio', unit: '%', before: '43.2%', after: '66.5%', trend: '↑54%', note: '目标肌群激活能力提升'
  }
]

const doctorComment = ref('')
const showAddForm = ref(false)
const newPatient = ref({ name: '', gender: '', age: null, date: '' })

function addPatient() {
  if (!newPatient.value.name || !newPatient.value.gender || !newPatient.value.age || !newPatient.value.date) {
    alert('请填写完整信息')
    return
  }
  const newId = patients.value.length ? patients.value[patients.value.length - 1].id + 1 : 1
  patients.value.push({ id: newId, name: newPatient.value.name })
  newPatient.value = { name: '', gender: '', age: null, date: '' }
  showAddForm.value = false
}

function deletePatient(id) {
  if (confirm('确定要删除该患者吗？')) {
    patients.value = patients.value.filter(p => p.id !== id)
  }
}

function viewReport(id) {
  selectedPatientId.value = id
  const p = patients.value.find(p => p.id === id)
  patientInfo.value.name = p.name
  patientInfo.value.gender = patientInfo.value.gender || '未知'
  patientInfo.value.age = patientInfo.value.age || '--'
  patientInfo.value.date = patientInfo.value.date || '--'
  currentView.value = 'report'
}

function goBack() {
  currentView.value = 'home'
}
</script>
