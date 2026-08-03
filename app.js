// 伊菲学习管理系统 · 小程序入口
// 注意：envId / appid 需替换为你自己的微信云开发环境 ID 与小程序的 AppID
App({
  globalData: {
    // 微信云开发环境 ID（2026-08-03 由用户在 CloudBase 控制台创建）
    envId: 'cloud1-d6gvwf6q09e5e6577',
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
