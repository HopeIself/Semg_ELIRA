<template>
  <div class="rtc-page">
    <div class="header">
      <h1>在线指导模块</h1>
      <button class="back-button" @click="goBack">返回主页</button>
      <button class="login-button" @click="goLogin">退出登录</button>
    </div>

    <div class="rtc-container">
      <div id="localVideo" class="video-box"></div>
      <div id="remoteVideo" class="video-box"></div>
      <button @click="handleStartRTC" class="rtc-button">启动RTC</button>
      <div class="status-message" v-if="statusMessage">{{ statusMessage }}</div>
      <div class="debug-panel" v-if="showDebugPanel">
        <h4>调试日志</h4>
        <pre>{{ debugLogs }}</pre>
      </div>
      <button @click="toggleDebugPanel" class="debug-toggle">
        {{ showDebugPanel ? '隐藏日志' : '显示日志' }}
      </button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'RTCPage',
  data() {
    return {
      rtcEngine: null,
      roomId: 'testRoom001',
      rtcAppId: '',
      _rawRtcToken: '', // 非响应式存储
      statusMessage: '',
      isRTCSDKLoaded: false,
      rtcSdkCdnUrl: 'https://lf-unpkg.volccdn.com/obj/vcloudfe/sdk/@volcengine/rtc/4.67.2/1754293346376/index.min.js',
      debugLogs: '',
      showDebugPanel: false,
      logId: 0,
      sdkLoadTimer: null,
      localStream: null,
      remoteStream: null,
      tokenValidationRules: {
        minLength: 10,
        maxLength: 2048,
        allowedChars: /^[a-zA-Z0-9\+\/=_\-]+$/
      },
      tokenRefreshCount: 0,
      maxRefreshAttempts: 3,
      tokenStorageElement: null,

      // 防循环标志
      isRefreshingToken: false,
      retryAttempted: false,
      isRestartingRTC: false
    };
  },
  computed: {
    rtcToken() {
      return this._rawRtcToken;
    }
  },
  methods: {
    // ---- 保留原始插入方法 ----
    async ensureMediaPermissions() {
      this.addDebugLog('检查设备权限（Permissions API）...');
      try {
        const statusChecks = [];
        if (navigator.permissions && typeof navigator.permissions.query === 'function') {
          try {
            const cam = await navigator.permissions.query({ name: 'camera' });
            statusChecks.push(`camera=${cam.state}`);
          } catch (e) {
            this.addDebugLog('Permissions API camera 查询失败或不支持：' + e.message);
          }
          try {
            const mic = await navigator.permissions.query({ name: 'microphone' });
            statusChecks.push(`microphone=${mic.state}`);
          } catch (e) {
            this.addDebugLog('Permissions API microphone 查询失败或不支持：' + e.message);
          }
        } else {
          this.addDebugLog('浏览器不支持 Permissions API 或 query 方法不可用');
        }
        if (statusChecks.length) this.addDebugLog('Permissions 状态: ' + statusChecks.join(', '));
      } catch (e) {
        this.addDebugLog('检查权限时出错: ' + e.message);
      }

      if (!navigator.mediaDevices || typeof navigator.mediaDevices.getUserMedia !== 'function') {
        this.addDebugLog('浏览器不支持 navigator.mediaDevices.getUserMedia');
        this.statusMessage = '浏览器不支持摄像头/麦克风 API';
        return false;
      }

      try {
        this.addDebugLog('调用 getUserMedia 以触发权限请求...');
        const testStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        this.addDebugLog('getUserMedia 成功返回流，表示权限已授予或已存在');

        try {
          const container = document.getElementById('localVideo');
          if (container) {
            let vid = container.querySelector('video.debug-preview-video');
            if (!vid) {
              vid = document.createElement('video');
              vid.className = 'debug-preview-video';
              vid.autoplay = true;
              vid.muted = true;
              vid.playsInline = true;
              vid.style.width = '100%';
              vid.style.height = '100%';
              vid.style.objectFit = 'cover';
              container.innerHTML = '';
              container.appendChild(vid);
            }
            vid.srcObject = testStream;
            this.addDebugLog('在 localVideo 上显示临时预览（调试）');
          } else {
            this.addDebugLog('localVideo 容器未找到，无法显示临时预览');
          }
        } catch (err) {
          this.addDebugLog('临时预览失败: ' + err.message);
        }

        try {
          testStream.getTracks().forEach(t => t.stop());
          this.addDebugLog('已停止临时预览流的轨道（调试流）');
        } catch (e) {
          this.addDebugLog('停止调试流失败: ' + e.message);
        }

        this.statusMessage = '摄像头/麦克风权限已确认（调试）';
        return true;
      } catch (err) {
        const errName = err && err.name ? err.name : 'UnknownError';
        this.addDebugLog(`getUserMedia 失败: ${errName} - ${err && err.message ? err.message : err}`);
        if (errName === 'NotAllowedError' || errName === 'PermissionDeniedError') {
          this.statusMessage = '摄像头/麦克风权限被拒绝或被浏览器阻止';
        } else if (errName === 'NotFoundError' || errName === 'OverconstrainedError') {
          this.statusMessage = '未找到摄像头或麦克风设备';
        } else {
          this.statusMessage = `获取设备失败：${errName}`;
        }
        return false;
      }
    },
    // ---- 结束保留原始插入方法 ----

    addDebugLog(message) {
      this.logId++;
      const timestamp = new Date().toLocaleTimeString();
      this.debugLogs += `[${timestamp}] [${this.logId}] ${message}\n`;
      this.$nextTick(() => {
        const preElement = document.querySelector('.debug-panel pre');
        if (preElement) preElement.scrollTop = preElement.scrollHeight;
      });
      console.log(`[调试日志] ${message}`);
    },

    toggleDebugPanel() {
      this.showDebugPanel = !this.showDebugPanel;
      this.addDebugLog(`调试面板${this.showDebugPanel ? '显示' : '隐藏'}`);
    },

    goBack() {
      this.addDebugLog('返回主页');
      this.$router.push('/home');
    },

    goLogin() {
      this.addDebugLog('用户点击退出登录');
      this.$router.push({ path: "/" });
    },

    enhanceTokenCheck(token) {
      const checkResult = { valid: true, message: '' };
      if (typeof token !== 'string') {
        checkResult.valid = false;
        checkResult.message = 'Token不是字符串';
        return checkResult;
      }
      if (token.trim() === '') {
        checkResult.valid = false;
        checkResult.message = 'Token为空字符串';
        return checkResult;
      }
      const controlChars = token.match(/[\x00-\x1F\x7F]/g);
      if (controlChars) {
        checkResult.valid = false;
        checkResult.message = `Token包含控制字符`;
        return checkResult;
      }
      if (token.length < 1) {
        checkResult.valid = false;
        checkResult.message = `Token长度异常：${token.length}`;
        return checkResult;
      }
      return checkResult;
    },

    validateRtcToken(token) {
      const result = { valid: false, message: '', cleanedToken: '' };
      try {
        this.addDebugLog(`Token原始值检查: ${typeof token}`);
        token = String(token).valueOf();
        if (Object.prototype.toString.call(token) !== '[object String]') {
          result.message = `Token类型错误: ${Object.prototype.toString.call(token)}`;
          return result;
        }
        let cleanedToken = token.replace(/[\u200B-\u200D\uFEFF]/g, '').replace(/^\uFEFF/, '');
        cleanedToken = cleanedToken.trim();
        if (cleanedToken.length === 0) {
          result.message = 'Token经清理后为空';
          return result;
        }
        if (cleanedToken.length < this.tokenValidationRules.minLength || cleanedToken.length > this.tokenValidationRules.maxLength) {
          result.message = `Token长度不在允许范围: ${cleanedToken.length}`;
          return result;
        }
        if (!this.tokenValidationRules.allowedChars.test(cleanedToken)) {
          const invalidChars = cleanedToken.split('').filter(c => !this.tokenValidationRules.allowedChars.test(c));
          result.message = `Token包含不允许字符（示例）: ${Array.from(new Set(invalidChars)).slice(0, 10).join(',')}`;
          return result;
        }
        result.valid = true;
        result.message = `Token校验通过（长度 ${cleanedToken.length}）`;
        result.cleanedToken = cleanedToken;
        return result;
      } catch (err) {
        result.message = `validateRtcToken 异常: ${err.message}`;
        return result;
      }
    },

    resetTokenStorage() {
      if (this.tokenStorageElement) {
        try { document.body.removeChild(this.tokenStorageElement); } catch (e) { }
      }
      this.tokenStorageElement = document.createElement('div');
      this.tokenStorageElement.style.display = 'none';
      document.body.appendChild(this.tokenStorageElement);
      this.addDebugLog('已重置Token存储元素');
    },

    storeTokenInDom(token) {
      if (!this.tokenStorageElement) {
        this.resetTokenStorage();
      }
      let cleaned = String(token || '')
        .replace(/[\u200B-\u200D\uFEFF]/g, '')
        .replace(/^\uFEFF/, '')
        .replace(/[\x00-\x1F\x7F]/g, '')
        .trim();
      cleaned = String(cleaned).valueOf();
      this.tokenStorageElement.textContent = cleaned;
      this._rawRtcToken = cleaned;
      this.addDebugLog(`Token已存储到DOM（掩码）: 长度=${cleaned.length}`);
    },

    getPureToken() {
      if (!this.tokenStorageElement) {
        this.resetTokenStorage();
      }
      let token = this.tokenStorageElement.textContent || '';
      token = String(token).valueOf();
      this.addDebugLog(`从DOM存获取Token: 长度=${token.length}`);
      return token;
    },

    async refreshAndValidateToken() {
      if (this.isRefreshingToken) {
        this.addDebugLog('当前已有 token 刷新进行中，跳过本次刷新请求');
        return false;
      }
      if (this.tokenRefreshCount >= this.maxRefreshAttempts) {
        const errorMsg = `已达最大刷新次数(${this.maxRefreshAttempts})，不再自动刷新`;
        this.addDebugLog(errorMsg);
        this.statusMessage = errorMsg;
        return false;
      }

      this.isRefreshingToken = true;
      this.tokenRefreshCount++;
      this.addDebugLog(`开始刷新并验证Token（第${this.tokenRefreshCount}/${this.maxRefreshAttempts}次尝试）`);
      this.statusMessage = `正在重新获取RTC认证信息（${this.tokenRefreshCount}/${this.maxRefreshAttempts}）...`;

      try {
        this.storeTokenInDom('');
        const authSuccess = await this.getRtcAuth();
        if (!authSuccess) {
          this.addDebugLog('刷新Token失败：获取认证信息失败');
          this.isRefreshingToken = false;
          return false;
        }

        const pureToken = this._rawRtcToken || this.getPureToken();
        const validation = this.validateRtcToken(pureToken);
        this.addDebugLog(`Token刷新后验证结果：${validation.message}`);

        this.isRefreshingToken = false;
        if (!validation.valid) {
          this.statusMessage = `Token验证失败：${validation.message}`;
          return false;
        }

        return true;
      } catch (error) {
        const errorMsg = `刷新Token过程出错：${error.message}`;
        this.addDebugLog(`错误: ${errorMsg}`);
        this.statusMessage = errorMsg;
        this.isRefreshingToken = false;
        return false;
      }
    },

    loadRTCSDK() {
      if (this.sdkLoadTimer) {
        clearTimeout(this.sdkLoadTimer);
        this.sdkLoadTimer = null;
      }

      if (this.isRTCSDKLoaded || window.VERTC) {
        this.isRTCSDKLoaded = true;
        this.addDebugLog('RTC SDK 已加载，核心对象: VERTC');
        return;
      }

      this.statusMessage = '正在从官方CDN加载RTC SDK...';
      this.addDebugLog(`开始从CDN加载RTC SDK，地址: ${this.rtcSdkCdnUrl}`);

      const script = document.createElement('script');
      script.src = this.rtcSdkCdnUrl;
      script.type = 'text/javascript';

      this.sdkLoadTimer = setTimeout(() => {
        if (!this.isRTCSDKLoaded) {
          this.addDebugLog(`错误: RTC SDK加载超时（20秒），请检查网络连接`);
          this.statusMessage = 'RTC SDK加载超时，请检查网络';
        }
      }, 20000);

      script.onload = () => {
        clearTimeout(this.sdkLoadTimer);
        this.addDebugLog('RTC SDK 脚本加载完成，开始验证核心对象');

        if (window.VERTC) {
          this.isRTCSDKLoaded = true;
          this.statusMessage = 'RTC SDK 加载成功';
          this.addDebugLog(`RTC SDK 加载成功，核心对象: VERTC`);
          this.addDebugLog(`RTC SDK 版本信息: ${window.VERTC.version || '未知版本'}`);
        } else {
          this.isRTCSDKLoaded = false;
          this.statusMessage = 'SDK加载异常，未找到核心对象 VERTC';
          this.addDebugLog('错误: SDK加载成功，但未找到 VERTC 全局对象');
        }
      };

      script.onerror = (error) => {
        clearTimeout(this.sdkLoadTimer);
        this.isRTCSDKLoaded = false;
        this.statusMessage = 'RTC SDK 加载失败，请检查网络';
        this.addDebugLog(`错误: CDN加载RTC SDK失败 - ${error && error.message ? error.message : 'unknown'}`);
        console.error('CDN加载RTC SDK失败:', error);
      };

      const existingScript = document.querySelector(`script[src="${this.rtcSdkCdnUrl}"]`);
      if (!existingScript) {
        document.body.appendChild(script);
        this.addDebugLog('RTC SDK CDN脚本标签已添加到页面');
      } else {
        this.addDebugLog('RTC SDK 脚本已存在，等待加载完成');
      }
    },

    async getRtcAuth() {
      this.statusMessage = '正在获取RTC认证信息...';
      this.addDebugLog('开始获取RTC认证信息');

      const userId = localStorage.getItem('id');
      this.addDebugLog(`当前用户ID: ${userId || '未获取到'}`);

      if (!userId || userId === 'null' || userId === 'undefined') {
        const errorMsg = '未获取到用户ID，请重新登录';
        this.addDebugLog(`错误: ${errorMsg}`);
        console.warn(errorMsg);
        this.statusMessage = errorMsg;
        return false;
      }

      try {
        const requestData = { userId: userId, roomId: this.roomId };
        this.addDebugLog(`准备发送RTC认证请求 - 数据: ${JSON.stringify(requestData)}`);

        const response = await axios.post(
          'http://115.190.118.22:5000/api/get_rtc_auth',
          requestData,
          {
            headers: { 'Content-Type': 'application/json' },
            timeout: 10000
          }
        );

        this.addDebugLog(`RTC认证请求返回状态: ${response.status}`);

        if (!response.data) {
          const errorMsg = 'RTC认证响应数据为空';
          this.addDebugLog(`错误: ${errorMsg}`);
          this.statusMessage = errorMsg;
          return false;
        }

        const token = response.data.token ? String(response.data.token) : '';
        this._rawRtcToken = token;
        this.rtcAppId = response.data.appId ? String(response.data.appId).trim() : '';
        const mask = (s) => {
          if (!s) return '';
          if (s.length <= 24) return s;
          return `${s.slice(0, 8)}...${s.slice(-8)}`;
        };
        this.addDebugLog(`收到认证信息: appId=${this.rtcAppId}, roomId=${response.data.roomId || ''}, token_len=${token.length}, token_sample=${mask(token)}`);

        const validation = this.validateRtcToken(this._rawRtcToken);
        this.addDebugLog(`RTC Token初步验证结果: ${validation.message}`);

        if (!validation.valid) {
          this.statusMessage = `RTC认证信息无效: ${validation.message}`;
          return false;
        }

        if (!this.rtcAppId) {
          const errorMsg = 'RTC认证信息中未包含有效的appId';
          this.addDebugLog(`错误: ${errorMsg}`);
          this.statusMessage = errorMsg;
          return false;
        }

        this.statusMessage = 'RTC认证信息获取成功';
        return true;
      } catch (error) {
        let errorMsg = '获取RTC认证信息失败';
        if (error.response) errorMsg += `: 服务器错误 ${error.response.status}`;
        else if (error.request) errorMsg += ': 服务器无响应';
        else errorMsg += `: ${error.message}`;
        this.addDebugLog(`错误: ${errorMsg}`);
        this.statusMessage = errorMsg;
        return false;
      }
    },

    async startRTC() {
      if (this.isRestartingRTC) {
        this.addDebugLog('startRTC 已在进行中，忽略重复调用');
        return false;
      }
      this.isRestartingRTC = true;
      this.addDebugLog('进入startRTC方法，开始启动RTC');
      this.tokenRefreshCount = this.tokenRefreshCount || 0;

      if (!this.isRTCSDKLoaded || !window.VERTC) {
        this.statusMessage = '等待RTC SDK加载...';
        this.addDebugLog('RTC SDK尚未加载完成，进入等待状态');

        const maxWaitTime = 15000;
        const checkInterval = 500;
        let waitedTime = 0;

        while (!window.VERTC && waitedTime < maxWaitTime) {
          this.addDebugLog(`等待SDK加载中... 已等待${waitedTime / 1000}秒`);
          await new Promise(resolve => setTimeout(resolve, checkInterval));
          waitedTime += checkInterval;
        }

        if (!window.VERTC) {
          const errorMsg = `RTC SDK加载超时（${maxWaitTime / 1000}秒）`;
          this.addDebugLog(`错误: ${errorMsg}`);
          this.statusMessage = errorMsg;
          this.isRestartingRTC = false;
          return false;
        }
        this.isRTCSDKLoaded = true;
        this.addDebugLog('RTC SDK已加载完成，继续执行');
      }

      if (!this.rtcAppId || String(this.rtcAppId).trim().length === 0) {
        const errorMsg = 'RTC appId无效或为空';
        this.addDebugLog(`错误: ${errorMsg}`);
        this.isRestartingRTC = false;
        return false;
      }

      let rawCandidate = (this._rawRtcToken && String(this._rawRtcToken).length > 0) ? String(this._rawRtcToken) : this.getPureToken();
      rawCandidate = String(rawCandidate).valueOf();
      this.addDebugLog(`Token候选原始片段（掩码）: len=${rawCandidate.length}, sample=${rawCandidate.length > 0 ? `${rawCandidate.slice(0, 8)}...${rawCandidate.slice(-8)}` : '空'}`);

      let initialValidation = this.validateRtcToken(rawCandidate);
      if (!initialValidation.valid) {
        this.addDebugLog(`初始Token验证失败: ${initialValidation.message}`);
        if (!this.retryAttempted && this.tokenRefreshCount < this.maxRefreshAttempts) {
          this.addDebugLog('初始 token 验证失败，尝试一次刷新 token');
          this.retryAttempted = true;
          const refreshSuccess = await this.refreshAndValidateToken();
          if (!refreshSuccess) {
            this.statusMessage = `Token无效且刷新失败: ${initialValidation.message}`;
            this.isRestartingRTC = false;
            return false;
          }
          const refreshedCandidate = this._rawRtcToken || this.getPureToken();
          initialValidation = this.validateRtcToken(refreshedCandidate);
          this.addDebugLog(`刷新后 Token 验证: ${initialValidation.message}`);
          if (!initialValidation.valid) {
            this.statusMessage = `刷新后的Token无效: ${initialValidation.message}`;
            this.isRestartingRTC = false;
            return false;
          }
        } else {
          this.statusMessage = `Token无效：${initialValidation.message}。请重新获取认证或重试。`;
          this.isRestartingRTC = false;
          return false;
        }
      }

      let pureToken = initialValidation.cleanedToken || String(initialValidation.cleanedToken || '').valueOf();
      pureToken = String(pureToken).valueOf();

      const mask = (s) => {
        if (!s) return '';
        if (s.length <= 24) return s;
        return `${s.slice(0, 8)}...${s.slice(-8)}`;
      };
      this.addDebugLog(`准备传给 joinRoom 的 token 类型: ${typeof pureToken}, 长度: ${pureToken.length}, 掩码: ${mask(pureToken)}`);

      try {
        this.statusMessage = '正在启动RTC...';
        this.addDebugLog('开始初始化RTC引擎');

        const storedUserId = localStorage.getItem('id');
        const uid = storedUserId ? String(storedUserId) : String(Math.floor(Math.random() * 100000));
        this.addDebugLog(`生成/使用用户UID: ${uid}`);

        this.rtcEngine = window.VERTC.createEngine(this.rtcAppId);
        this.addDebugLog(`RTC引擎实例创建成功，AppId: ${this.rtcAppId}`);

        try {
          const vKeys = Object.keys(window.VERTC || {}).slice(0, 100);
          this.addDebugLog(`VERTC keys: ${vKeys.join(', ')}`);
        } catch (e) {
          this.addDebugLog('读取 window.VERTC keys 失败: ' + (e && e.message ? e.message : e));
        }
        try {
          const eKeys = Object.keys(this.rtcEngine || {}).slice(0, 200);
          this.addDebugLog(`rtcEngine keys: ${eKeys.join(', ')}`);
        } catch (e) {
          this.addDebugLog('读取 rtcEngine keys 失败: ' + (e && e.message ? e.message : e));
        }

        this.rtcEngine.on('user-published', async (user, mediaType) => {
          this.addDebugLog(`收到user-published事件 - 用户: ${user.uid}, 媒体类型: ${mediaType}`);
          await this.rtcEngine.subscribe(user, mediaType);
          if (mediaType === 'video') {
            if (user && user.videoTrack && typeof user.videoTrack.play === 'function') {
              try {
                const remoteVideo = document.getElementById('remoteVideo');
                if (remoteVideo) {
                  user.videoTrack.play('remoteVideo');
                  remoteVideo.classList.add('video-playing');
                  this.remoteStream = user.videoTrack;
                  this.addDebugLog('远端视频渲染成功');
                }
              } catch (err) {
                this.addDebugLog(`远端 videoTrack.play 渲染异常: ${err.message}`);
              }
            }
          }
          if (mediaType === 'audio') {
            if (user && user.audioTrack && typeof user.audioTrack.play === 'function') {
              try { user.audioTrack.play(); this.addDebugLog('远端音频播放'); } catch (e) { this.addDebugLog(`远端音频播放失败: ${e.message}`); }
            }
          }
        });

        this.rtcEngine.on('connection-state-change', async (state, reason) => {
          this.addDebugLog(`连接状态变化: ${state}，原因: ${reason}`);
          this.statusMessage = `RTC连接状态: ${state}`;
          if (state === 'failed' && String(reason || '').toLowerCase().includes('token')) {
            this.addDebugLog(`检测到Token相关错误导致连接失败: ${reason}`);
            if (!this.retryAttempted && this.tokenRefreshCount < this.maxRefreshAttempts) {
              this.addDebugLog('尝试一次 token 刷新（由 connection-state-change 触发）');
              this.retryAttempted = true;
              const ok = await this.refreshAndValidateToken();
              if (ok) {
                this.addDebugLog('token 刷新成功，提示用户重新点击启动或自动尝试一次重连');
                if (!this.isRestartingRTC) {
                  this.addDebugLog('尝试一次自动重启 RTC');
                  await this.startRTC();
                } else {
                  this.addDebugLog('检测到重入锁仍存在，先释放锁并延后重启');
                  this.isRestartingRTC = false;
                  setTimeout(() => {
                    this.addDebugLog('延后触发自动重启 RTC');
                    this.startRTC();
                  }, 50);
                }
              } else {
                this.addDebugLog('token 刷新失败，不再自动重试，等待用户手动重新启动');
                this.statusMessage = 'Token 刷新失败，请手动重新获取认证并重试';
              }
            } else {
              this.addDebugLog('已尝试过刷新或已达刷新上限，停止自动重试');
              this.statusMessage = '连接失败（Token 问题），请重新获取认证或联系后台';
            }
          }
        });

        this.addDebugLog('调用 rtcEngine.joinRoom（位置参数模式）开始加入房间');
        try {
          await this.rtcEngine.joinRoom(pureToken, this.roomId, { userId: uid });
          this.addDebugLog(`成功加入房间: ${this.roomId}`);
        } catch (joinErr) {
          this.addDebugLog(`joinRoom 抛错: ${joinErr && joinErr.message ? joinErr.message : joinErr}`);
        }

        this.addDebugLog('开始创建本地流（尝试 SDK 优先接口）');
        let sdkLocalStream = null;
        let nativeLocalStream = null;

        const candidateFactoryNames = ['createStream', 'createLocalStream', 'createLocalMediaStream', 'createMediaStream', 'createUserMediaStream'];
        let factoryUsed = null;
        for (const name of candidateFactoryNames) {
          try {
            if (typeof window.VERTC[name] === 'function') {
              this.addDebugLog(`检测到 VERTC.${name}，尝试调用它`);
              try {
                sdkLocalStream = await window.VERTC[name]({
                  audio: true,
                  video: true,
                  videoConfig: { width: 640, height: 480, frameRate: 15 }
                });
                factoryUsed = `VERTC.${name}`;
                this.addDebugLog(`成功通过 ${name} 创建 SDK 本地流（返回对象类型: ${typeof sdkLocalStream}）`);
                break;
              } catch (e) {
                this.addDebugLog(`${name} 调用失败: ${e && e.message ? e.message : e}`);
                sdkLocalStream = null;
              }
            }
          } catch (e) { }
        }

        if (!sdkLocalStream) {
          const engineFactoryNames = ['createStream', 'createLocalStream', 'createStreamWithOptions'];
          for (const name of engineFactoryNames) {
            try {
              if (this.rtcEngine && typeof this.rtcEngine[name] === 'function') {
                this.addDebugLog(`检测到 rtcEngine.${name}，尝试调用它`);
                try {
                  sdkLocalStream = await this.rtcEngine[name]({
                    audio: true,
                    video: true,
                    videoConfig: { width: 640, height: 480, frameRate: 15 }
                  });
                  factoryUsed = `rtcEngine.${name}`;
                  this.addDebugLog(`成功通过 rtcEngine.${name} 创建 SDK 本地流`);
                  break;
                } catch (e) {
                  this.addDebugLog(`rtcEngine.${name} 调用失败: ${e && e.message ? e.message : e}`);
                  sdkLocalStream = null;
                }
              }
            } catch (e) { }
          }
        }

        if (!sdkLocalStream) {
          try {
            this.addDebugLog('SDK 未提供 createStream-like 方法，使用 navigator.mediaDevices.getUserMedia 回退');
            nativeLocalStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
            this.addDebugLog('getUserMedia 成功返回 native MediaStream（回退流）');

            try {
              const container = document.getElementById('localVideo');
              if (container) {
                let v = container.querySelector('video.native-fallback-video');
                if (!v) {
                  v = document.createElement('video');
                  v.className = 'native-fallback-video';
                  v.autoplay = true;
                  v.playsInline = true;
                  v.muted = true;
                  v.style.width = '100%';
                  v.style.height = '100%';
                  v.style.objectFit = 'cover';
                  container.innerHTML = '';
                  container.appendChild(v);
                }
                v.srcObject = nativeLocalStream;
                container.classList.add('video-playing');
                this.addDebugLog('已在 localVideo 上显示 nativeLocalStream（仅本地预览）');
              }
            } catch (e) {
              this.addDebugLog('将 nativeLocalStream 附着到 video 失败: ' + (e && e.message ? e.message : e));
            }

            this.addDebugLog('⚠️ 注意：未发布本地音视频流到房间，仅本地预览');
          } catch (e) {
            this.addDebugLog('回退 getUserMedia 失败: ' + (e && e.message ? e.message : e));
          }
        }

        if (sdkLocalStream) {
          try {
            if (typeof sdkLocalStream.initialize === 'function') {
              await sdkLocalStream.initialize();
              this.addDebugLog('sdkLocalStream.initialize() 成功');
            }
          } catch (e) {
            this.addDebugLog('sdkLocalStream.initialize 异常: ' + (e && e.message ? e.message : e));
          }
          try {
            if (typeof sdkLocalStream.startVideoCapture === 'function') {
              await sdkLocalStream.startVideoCapture();
              this.addDebugLog('sdkLocalStream.startVideoCapture() 成功');
            }
          } catch (e) {
            this.addDebugLog('sdkLocalStream.startVideoCapture 异常: ' + (e && e.message ? e.message : e));
          }

          try {
            if (sdkLocalStream.startLocalVideoRender && typeof sdkLocalStream.startLocalVideoRender === 'function') {
              try {
                sdkLocalStream.startLocalVideoRender('localVideo');
                this.addDebugLog('sdkLocalStream.startLocalVideoRender 成功');
              } catch (e) {
                this.addDebugLog('sdkLocalStream.startLocalVideoRender 抛错: ' + (e && e.message ? e.message : e));
              }
            }
          } catch (e) { }

          try {
            if (typeof this.rtcEngine.publishStream === 'function') {
              await this.rtcEngine.publishStream(sdkLocalStream);
              this.addDebugLog('通过 rtcEngine.publishStream 发布 SDK 本地流成功');
            } else if (typeof this.rtcEngine.publish === 'function') {
              await this.rtcEngine.publish(sdkLocalStream);
              this.addDebugLog('通过 rtcEngine.publish 发布 SDK 本地流成功（使用 publish）');
            } else {
              this.addDebugLog('rtcEngine 没有 publishStream/publish 方法，无法发布本地流');
            }
          } catch (e) {
            this.addDebugLog('发布 SDK 本地流失败: ' + (e && e.message ? e.message : e));
          }
        } 
        else if (nativeLocalStream) {
          try {
            const container = document.getElementById('localVideo');
            if (container) {
              let v = container.querySelector('video.native-fallback-video');
              if (!v) {
                v = document.createElement('video');
                v.className = 'native-fallback-video';
                v.autoplay = true;
                v.playsInline = true;
                v.muted = true;
                v.style.width = '100%';
                v.style.height = '100%';
                v.style.objectFit = 'cover';
                container.innerHTML = '';
                container.appendChild(v);
              }
              v.srcObject = nativeLocalStream;
              container.classList.add('video-playing');
              this.addDebugLog('已在 localVideo 上显示 nativeLocalStream（仅本地预览）');
            }
          } catch (e) {
            this.addDebugLog('将 nativeLocalStream 附着到 video 失败: ' + (e && e.message ? e.message : e));
          }

          this._debugNativeLocalStream = nativeLocalStream;
          this.addDebugLog('⚠️ 注意：未发布本地音视频流到房间，仅本地预览');
        } else {
          this.addDebugLog('既未创建到 SDK 本地流，也未获取到 native MediaStream');
        }

        this.statusMessage = `RTC 启动流程执行完毕（注意：如果未看到本地/远端视频，请查看调试日志）`;
        this.isRestartingRTC = false;
        return true;
      } catch (error) {
        const errorMsg = `RTC启动失败: ${error && error.message ? error.message : error}`;
        this.addDebugLog(`错误: ${errorMsg}`);

        if (error && error.message && error.message.includes('Invalid token')) {
          this.addDebugLog('检测到 Invalid token 错误');
          if (!this.retryAttempted && this.tokenRefreshCount < this.maxRefreshAttempts) {
            this.addDebugLog('尝试一次 token 刷新（由 startRTC catch 触发）');
            this.retryAttempted = true;
            const refreshSuccess = await this.refreshAndValidateToken();
            if (refreshSuccess) {
              this.addDebugLog('token 刷新成功，准备重启 RTC（解除重入锁）');
              this.isRestartingRTC = false;
              await new Promise(resolve => setTimeout(resolve, 50));
              const restartOk = await this.startRTC();
              return restartOk;
            } else {
              this.statusMessage = 'RTC Token 无效且刷新失败，请手动重新获取认证后重试';
              this.addDebugLog('token 刷新失败，不再自动重试');
            }
          } else {
            this.statusMessage = 'RTC Token 无效，已停止自动刷新，请手动重新获取认证后重试';
            this.addDebugLog('已达自动重试条件，不再继续自动刷新');
          }
        } else {
          this.statusMessage = errorMsg;
        }

        this.isRestartingRTC = false;
        return false;
      }
    },

    async handleStartRTC() {
      this.addDebugLog('用户点击了启动RTC按钮');
      this.statusMessage = '';

      const ok = await this.ensureMediaPermissions();
      this.addDebugLog('ensureMediaPermissions 返回: ' + ok);
      if (!ok) {
        this.addDebugLog('权限检测失败，停止启动 RTC');
        return;
      }

      this.retryAttempted = false;
      this.tokenRefreshCount = 0;
      this.resetTokenStorage();

      if (!this.isRTCSDKLoaded && !window.VERTC) {
        this.addDebugLog('RTC SDK未加载，触发CDN加载流程');
        this.loadRTCSDK();
        await new Promise(resolve => setTimeout(resolve, 1000));
      }

      const authSuccess = await this.getRtcAuth();
      if (authSuccess) {
        this.addDebugLog('认证信息获取成功，开始启动RTC');
        await this.startRTC();
      }
    }
  },
  mounted() {
    this.addDebugLog('RTC页面组件挂载完成，开始初始化');
    this.loadRTCSDK();
    this.resetTokenStorage();
  },
  beforeDestroy() {
    this.addDebugLog('RTC页面组件即将销毁，清理资源');
    if (this.sdkLoadTimer) clearTimeout(this.sdkLoadTimer);

    if (this.localStream) {
      try {
        if (this.localStream.videoTrack && typeof this.localStream.videoTrack.stop === 'function') {
          this.localStream.videoTrack.stop();
        }
        if (typeof this.localStream.stopVideoCapture === 'function') {
          this.localStream.stopVideoCapture();
        }
        if (typeof this.localStream.stopLocalVideoRender === 'function') {
          this.localStream.stopLocalVideoRender();
        }
        this.addDebugLog('本地流资源已清理');
      } catch (err) {
        this.addDebugLog(`清理本地流失败: ${err.message}`);
      }
    }

    if (this.rtcEngine) {
      this.rtcEngine.leaveRoom().then(() => {
        this.addDebugLog('成功离开RTC房间');
        try { this.rtcEngine.destroy(); this.addDebugLog('RTC引擎已销毁'); } catch (e) { }
      }).catch(err => {
        this.addDebugLog(`离开RTC房间失败: ${err.message}`);
      });
      this.rtcEngine = null;
    }

    if (this.tokenStorageElement) {
      try { document.body.removeChild(this.tokenStorageElement); } catch (e) { }
      this.tokenStorageElement = null;
    }

    if (this.remoteStream) {
      try {
        this.remoteStream.stop();
        this.remoteStream = null;
        this.addDebugLog('远端流资源已清理');
      } catch (err) {
        this.addDebugLog(`清理远端流失败: ${err.message}`);
      }
    }
  }
};
</script>

<style scoped>
.rtc-page {
  width: 100vw;
  min-height: 100vh;
  background: #f7f4e7;
  padding: 40px 20px;
  font-family: "Helvetica Neue", Arial, sans-serif;
  box-sizing: border-box;
}

.header {
  text-align: center;
  margin-bottom: 50px;
  position: relative;
}

.header h1 {
  font-size: 32px;
  color: #333333;
  margin: 0;
  padding: 20px 0;
}

.back-button {
  font-size: 18px;
  position: fixed;
  top: 20px;
  left: 20px;
  background: transparent;
  border: none;
  color: #333333;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}

.back-button:hover {
  text-decoration: underline;
}

.login-button {
  font-size: 22px;
  font-weight: bold;
  position: fixed;
  top: 20px;
  right: 20px;
  background: transparent;
  border: none;
  color: #333333;
  cursor: pointer;
}

.login-button:hover {
  text-decoration: underline;
}

.rtc-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  width: 100%;
  max-width: 320px;
  margin: 0 auto;
}

.video-box {
  width: 320px;
  height: 240px;
  background-color: black;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}

.video-box.video-playing::before {
  display: none;
}

.video-box::before {
  content: '等待视频流...';
  color: white;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 14px;
}

.rtc-button {
  margin-top: 20px;
  padding: 10px 20px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.rtc-button:hover {
  background-color: #337ecc;
}

.status-message {
  margin-top: 10px;
  color: #333;
  font-size: 14px;
  text-align: center;
  max-width: 320px;
  word-wrap: break-word;
  padding: 8px;
  border-radius: 4px;
  background-color: rgba(255, 255, 255, 0.8);
}

.debug-panel {
  margin-top: 15px;
  width: 320px;
  max-height: 300px;
  overflow-y: auto;
  background-color: #2d2d2d;
  color: #f0f0f0;
  padding: 10px;
  border-radius: 8px;
  font-size: 12px;
}

.debug-panel h4 {
  margin: 0 0 10px 0;
  color: #61dafb;
  text-align: center;
}

.debug-panel pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.debug-toggle {
  margin-top: 10px;
  padding: 5px 10px;
  background-color: #666;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.debug-toggle:hover {
  background-color: #444;
}
</style>