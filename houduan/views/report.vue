<template>
    <div class="upload-success">
      <h1>上传成功</h1>
      <p>作品上传成功，请等待审核！</p>
      <p>作品链接: <a :href="uploadedData.url" target="_blank">{{ uploadedData.url }}</a></p>
      <div class="details">
        <h2>作品名称: {{ uploadedData.name }}</h2>
        <h2>作品描述: {{ uploadedData.description }}</h2>
        <h2>作品分类: {{ uploadedData.category }}</h2>
        <h2>作品售价: {{ uploadedData.price }} 元</h2>
        <h2>作品售卖状态: {{ uploadedData.status === '1' ? '可售' : '不可售' }}</h2>
        <h2>作品标签: {{ uploadedData.tags.join(', ') }}</h2>
        <div v-if="uploadedData.form">
          <h3>作品原件:</h3>
          <a :href="uploadedData.form.url" target="_blank">{{ uploadedData.form.name }}</a>
        </div>
        <div v-if="uploadedData.workpiece">
          <h3>作品缩略图:</h3>
          <img :src="uploadedData.workpiece.url" alt="作品缩略图" />
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive, onMounted } from 'vue';
  import { useRoute } from 'vue-router';
  
  const route = useRoute();
  const uploadedData = reactive({});
  
  onMounted(() => {
    if (route.params.uploadedData) {
      Object.assign(uploadedData, route.params.uploadedData);
    }
  });
  </script>
  <script>
    export default {
      name: 'UploadSuccess'
    }
</script>

  <style>
  .upload-success {
    padding: 20px;
    max-width: 100vw;
    overflow-x: auto;
  }
  
  .details {
    margin-top: 20px;
  }
  
  h1 {
    font-size: 36px;
    margin-bottom: 20px;
  }
  
  h2, h3 {
    margin-bottom: 10px;
  }
  
  img {
    max-width: 200px;
    max-height: 200px;
    border: 1px solid #ccc;
    padding: 5px;
  }
  </style>
  