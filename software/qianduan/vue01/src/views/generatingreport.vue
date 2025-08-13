<template>
  <div class="container">
    <!-- 顶部按钮 -->
    <div class="button-group-top">
      <button @click="startGeneration" :disabled="assessing" class="generate-btn">
        生成报告文件
      </button>
    </div>

    <!-- 生成中提示 -->
    <div v-if="assessing" class="generating-text">
      报告生成中，这可能需要 2~3 分钟，请耐心等待...
    </div>

    <!-- 下载按钮 -->
    <div v-if="reportUrl" class="download-section">
      <a :href="reportUrl" download="训练报告.txt" class="download-btn">📄 下载报告</a>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-msg">
      错误：{{ error }}
    </div>

    <!-- 固定右下角按钮 -->
    <div class="button-bottom-right">
      <button @click="goToHomepage" class="next-btn">
        回到主页
      </button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      assessing: false,
      error: null,
      reportUrl: null, // PDF 下载地址
    };
  },
  methods: {
    goToHomepage() {
      this.$router.push({ path: '/Homepage' });
    },

    startGeneration() {
      if (this.assessing) return;

      const userId = localStorage.getItem('id');
      if (!userId || userId === 'null') {
        this.error = '未找到用户ID，请重新登录';
        return;
      }

      this.assessing = true;
      this.error = null;
      this.reportUrl = null;

      // 第一步：请求报告生成接口，获取 file_url
      axios
        .post('http://115.190.134.66:5000/api/get_latest_report', { id: userId })
        .then((res) => {
          const data = res.data;

          if (data.error) {
            this.error = data.error;
            this.assessing = false;
            return;
          }

          const fileUrl = data.file_url;
          if (!fileUrl) {
            this.error = '未获取到报告地址';
            this.assessing = false;
            return;
          }

          // 第二步：下载 PDF 文件并生成可用 Blob 链接
          return axios.get(fileUrl, { responseType: 'blob' });
        })
        .then((pdfRes) => {
          if (!pdfRes) return;

          const blob = new Blob([pdfRes.data], { type: 'application/pdf' });
          this.reportUrl = URL.createObjectURL(blob);
          this.assessing = false;
        })
        .catch((err) => {
          console.error(err);
          this.error = '报告生成失败，请稍后重试';
          this.assessing = false;
        });
    },
  },
};
</script>

<style scoped>
.generating-text {
  font-size: 16px;
  margin: 20px 0;
  color: #666;
}

.download-section {
  margin-top: 30px;
}

.download-btn {
  padding: 12px 24px;
  font-size: 16px;
  background-color: #409eff;
  border: none;
  border-radius: 6px;
  color: white;
  text-decoration: none;
  cursor: pointer;
}

.download-btn:hover {
  background-color: #337ecc;
}

.container {
  max-width: 600px;
  margin: 50px auto;
  text-align: center;
  font-family: "Microsoft YaHei", Arial, sans-serif;
  position: relative; /* 为右下角按钮定位提供参照 */
  min-height: 500px; /* 防止右下角按钮被裁切 */
}

.button-group-top {
  text-align: center;
  margin-bottom: 20px;
}

.generate-btn {
  padding: 12px 30px;
  font-size: 18px;
  background-color: #409eff;
  border: none;
  border-radius: 6px;
  color: white;
  cursor: pointer;
}

.generate-btn:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

.progress-bar-container {
  margin-top: 20px;
  width: 100%;
  height: 26px;
  border: 1px solid #409eff;
  border-radius: 13px;
  overflow: hidden;
  background-color: #e0e0e0;
  position: relative;
}

.progress-bar {
  height: 100%;
  background-color: #409eff;
  transition: width 0.1s linear;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 14px;
}

.progress-percent {
  z-index: 2;
}

.plan-display {
  margin-top: 30px;
  text-align: left;
  background: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
  max-height: 400px;
  overflow-y: auto;
  font-family: Consolas, monospace;
}

.plan-content {
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: break-word;
}

.error-msg {
  margin-top: 20px;
  color: #f44336;
  font-weight: 600;
}

/* 固定右下角跳转按钮 */
.button-bottom-right {
  position: absolute;
  right: 20px;
  bottom: 20px;
}

.next-btn {
  padding: 10px 20px;
  font-size: 16px;
  background-color: #67c23a;
  border: none;
  border-radius: 6px;
  color: white;
  cursor: pointer;
}

.next-btn:hover {
  background-color: #5daf34;
}
</style>