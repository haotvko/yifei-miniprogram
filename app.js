// 伊菲学习管理系统 · 小程序入口
// 注意：envId / appid 需替换为你自己的微信云开发环境 ID 与小程序的 AppID
const { callFunction } = require('./utils/api.js');

App({
  globalData: {
    // 微信云开发环境 ID（2026-08-03 由用户在 CloudBase 控制台创建）
    envId: 'cloud1-d6gvwf6q09e5e6577',
    // 看板快照缓存（由 getSnapshot 云函数填充）
    snapshot: null,
    // 题库缓存（由 getAssets 云函数下发，本地 questionbank.js 兜底）
    bank: null,
    // 详细汇报缓存（由 getAssets 云函数下发，本地 reports.js 兜底）
    reports: null
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
    // 异步拉取云端题库/汇报并缓存：内容更新只需改云存储，无需重新发布小程序
    this.loadAssets();
  },

  // 从 getAssets 拉取题库与详细汇报，写入 globalData 并落本地缓存（离线兜底）
  async loadAssets() {
    try {
      const res = await callFunction('getAssets');
      if (res && res.questionbank) {
        this.globalData.bank = res.questionbank;
        try { wx.setStorageSync('questionbank', res.questionbank); } catch (e) {}
      }
      if (res && res.reports) {
        this.globalData.reports = res.reports;
        try { wx.setStorageSync('reports', res.reports); } catch (e) {}
      }
    } catch (e) {
      console.error('getAssets 拉取失败，将使用本地兜底题库/汇报', e);
    }
  }
});
