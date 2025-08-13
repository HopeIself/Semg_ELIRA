<template>
  <div class="p-4">
    <h2 class="text-xl mb-4">PDF 生成测试</h2>

    <div class="mb-2">
      <label class="block mb-1">用户 ID：</label>
      <input v-model="userId" class="border p-1 w-48" />
    </div>

    <div class="mb-2">
      <label class="block mb-1">网页 URL：</label>
      <input v-model="url" class="border p-1 w-96" />
    </div>

    <div class="mb-2">
      <label class="block mb-1">PDF 文件名：</label>
      <input v-model="filename" class="border p-1 w-96" />
    </div>

    <button @click="generatePDF" class="bg-blue-500 text-white px-4 py-2 rounded">
      生成 PDF
    </button>

    <div v-if="result" class="mt-4">
      <p v-if="result.success" class="text-green-600">
        ✅ 成功：{{ result.message }}<br />
        📁 路径：{{ result.path }}
      </p>
      <p v-else class="text-red-600">
        ❌ 失败：{{ result.message }}
      </p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      userId: '1',
      url: 'http://localhost:8080/report',  // 替换为你的网页地址
      filename: '康复报告_示例.pdf',
      result: null
    };
  },
  methods: {
    async generatePDF() {
      this.result = null;
      try {
        const res = await fetch('http://127.0.0.1:5000/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            userId: this.userId,
            url: this.url,
            filename: this.filename
          })
        });

        this.result = await res.json();
      } catch (err) {
        this.result = { success: false, message: '请求失败，请检查服务端是否运行。' };
      }
    }
  }
}
</script>
