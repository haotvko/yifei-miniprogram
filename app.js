// 伊菲学习管理系统 · 小程序入口
// 注意：envId / appid 需替换为你自己的微信云开发环境 ID 与小程序的 AppID
App({
  globalData: {
    // 【需替换】你的微信云开发环境 ID（在微信开发者工具「云开发」控制台查看）
    envId: 'your-cloud-env-id',
    // 看板快照缓存（由 getSnapshot 云函数填充）
    snapshot: null
  },

  onLaunch() {
    if (!wx.cloud) {
      console.error('当前基础库不支持云开发，请使用 2.2.3 或以上的基础库');
      return;
    }
    wx.cloud.init({
      env: this.globalData.envId,
      traceUser: true
    });
  }
});
