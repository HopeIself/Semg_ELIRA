<template>
  <div id="app" :class="{'login-bg': hasBackground}">
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      hasBackground: false
    }
  },
  watch: {
    '$route'(to) {
      this.hasBackground = to.name === 'Login'
    }
  },
  created() {
    this.hasBackground = this.$route.name === 'Login'
  }
}
</script>

<style>
.login-bg {
  background-color: #f5f5f5;
  min-height: 100vh;
}

.component-wrapper {
  min-height: 100vh;
  position: relative;
}
</style>