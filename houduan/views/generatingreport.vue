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
      <!-- 点击后自动下载报告 -->
      <button @click="downloadReport" class="download-btn">📄 下载报告</button>
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

      // 第一步：请求报告生成接口
      axios
        .post('http://115.190.118.22:5000/api/generate-report', { id: userId }, { timeout: 0 })
        .then((response) => {
          // 检查返回的消息是否是 "报告已生成"
          if (response.data.message === '报告已生成') {
            // 第二步：报告生成成功后，显示下载按钮
            this.fetchLatestReport(userId);
          } else {
            this.error = '报告生成失败，请稍后重试';
            this.assessing = false;
          }
        })
        .catch((err) => {
          console.error(err);
          this.error = '报告生成失败，请稍后重试';
          this.assessing = false;
        });
    },

    fetchLatestReport(userId) {
      // 检查是否已经在请求中，避免重复请求
      if (this.reportUrl) {
        console.log("fetchLatestReport has already been called, skipping.");
        return;
      }

      // 获取最新报告名称
      axios
        .post('http://115.190.118.22:5000/api/get_latest_report', { id: userId })
        .then((res) => {
          const data = res.data;
          if (data.file_name && data.file_url) {
            // 构造下载链接
            this.reportUrl = data.file_url; // 使用从后端获取的 URL
            console.log("Report URL:", this.reportUrl);  // 调试输出
            this.assessing = false;
          } else {
            this.error = '未获取到报告文件';
            this.assessing = false;
          }
        })
        .catch((err) => {
          console.error(err);
          this.error = '获取报告失败，请稍后重试';
          this.assessing = false;
        });
    },

    // 自动下载报告
    downloadReport() {
      // 创建一个隐藏的 <a> 元素
      const link = document.createElement('a');
      link.href = this.reportUrl; // 设置 href 为获取的报告 URL
      link.download = ''; // 自动下载文件，不需要指定文件名
      document.body.appendChild(link); // 将链接添加到 DOM 中
      link.click(); // 模拟点击下载
      document.body.removeChild(link); // 下载后移除链接
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
