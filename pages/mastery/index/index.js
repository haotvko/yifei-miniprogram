const app = getApp();
const { callFunction } = require('../../../utils/api.js');

function pctText(p) {
  return p == null ? '待测' : Math.round(p * 100) + '%';
}

Page({
  data: {
    summary: null,
    subjects: [],
    loading: true,
    updatedText: ''
  },

  onShow() {
    this.loadSnapshot();
  },

  async loadSnapshot() {
    this.setData({ loading: true });
    try {
      const res = await callFunction('getSnapshot');
      const snap = res || {};
      app.globalData.snapshot = snap;

      const subjects = (snap.subjects || []).map(s => ({
        ...s,
        mastery_text: pctText(s.mastery_pct)
      }));

      let summary = null;
      if (snap.summary) {
        const each = snap.summary.predicted_score_150_each || {};
        let total = 0, hasAny = false;
        Object.keys(each).forEach(k => {
          if (each[k] != null) { total += each[k]; hasAny = true; }
        });
        summary = {
          ...snap.summary,
          mastery_pct_text: pctText(snap.summary.mastery_pct),
          predicted_text: hasAny ? (total + ' / 450') : '待测'
        };
      }

      this.setData({
        summary,
        subjects,
        updatedText: snap.data_as_of ? ('数据截至 ' + snap.data_as_of) : '',
        loading: false
      });
    } catch (e) {
      this.setData({ loading: false });
      wx.showToast({ title: '加载失败，请重试', icon: 'none' });
    }
  },

  goDetail(e) {
    const key = e.currentTarget.dataset.key;
    wx.navigateTo({ url: '/pages/mastery/detail/detail?key=' + key });
  }
});
