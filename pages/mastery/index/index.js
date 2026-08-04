const app = getApp();
const { callFunction } = require('../../../utils/api.js');

// 状态色：绿=好 蓝=中上 橙=中 灰=未测
const COLOR = { green: '#34c759', blue: '#5b8def', yellow: '#ffa726', gray: '#c7ccd4' };
const EMOJI = { english: '英', math: '数', chinese: '语' };

function pctText(p) {
  return p == null ? '待测' : Math.round(p * 100) + '%';
}
function colorOf(c) { return COLOR[c] || COLOR.gray; }
function totalColorOf(p) {
  if (p == null) return COLOR.gray;
  if (p >= 0.7) return COLOR.green;
  if (p >= 0.4) return COLOR.blue;
  return COLOR.yellow;
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
        mastery_text: pctText(s.mastery_pct),
        ringPct: s.mastery_pct == null ? 0 : Math.round(s.mastery_pct * 100),
        ringColor: colorOf(s.color),
        emoji: EMOJI[s.key] || '·'
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
          predicted_text: hasAny ? (total + ' / 450') : '待测',
          totalPct: snap.summary.mastery_pct == null ? 0 : Math.round(snap.summary.mastery_pct * 100),
          totalColor: totalColorOf(snap.summary.mastery_pct)
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
