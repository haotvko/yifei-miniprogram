const app = getApp();
const { callFunction } = require('../../../utils/api.js');
const reports = require('../../reports.js');

const COLOR = { red: '#e04646', yellow: '#ffa726', blue: '#5b8def', green: '#34c759', gray: '#c7ccd4' };
function colorOf(c) { return COLOR[c] || COLOR.gray; }
function pctText(p) { return p == null ? '未测' : Math.round(p * 100) + '%'; }
function statusLabel(s) {
  return s === 'red' ? '待补' : s === 'yellow' ? '薄弱' : s === 'blue' ? '良好' : s === 'green' ? '已掌握' : '未测';
}
function pillClass(s) {
  return s === 'red' ? 'pill-red' : s === 'yellow' ? 'pill-yellow' : s === 'blue' ? 'pill-blue'
    : s === 'green' ? 'pill-green' : 'pill-gray';
}

Page({
  data: {
    subjectName: '',
    point: '',
    pct_text: '未测',
    ringPct: 0,
    ringColor: COLOR.gray,
    status_label: '未测',
    pill_class: 'pill-gray',
    report: null,        // 详细汇报对象（AI 维护）
    hasReport: false,
    loading: true
  },

  onLoad(options) {
    this.key = options.key;
    this.pointName = options.point;
    this.load();
  },

  async load() {
    let snap = app.globalData.snapshot;
    if (!snap) {
      try {
        const res = await callFunction('getSnapshot');
        snap = res || {};
        app.globalData.snapshot = snap;
      } catch (e) { snap = null; }
    }

    let subjectName = '', pct = null, status = null;
    if (snap && snap.subjects) {
      const subj = snap.subjects.find(s => s.key === this.key);
      if (subj) {
        subjectName = subj.name;
        const p = (subj.points || []).find(x => x.point === this.pointName);
        if (p) { pct = p.mastery_pct; status = p.status; }
      }
    }

    const r = (reports[this.key] && reports[this.key][this.pointName]) || null;

    wx.setNavigationBarTitle({ title: (this.pointName || '考点') + ' · 详细汇报' });
    this.setData({
      subjectName,
      point: this.pointName,
      pct_text: pctText(pct),
      ringPct: pct == null ? 0 : Math.round(pct * 100),
      ringColor: colorOf(status),
      status_label: statusLabel(status),
      pill_class: pillClass(status),
      report: r,
      hasReport: !!r,
      loading: false
    });
  },

  goPractice() {
    if (!this.key || !this.pointName) return;
    wx.navigateTo({ url: '/pages/tasks/tasks?subject=' + this.key + '&point=' + encodeURIComponent(this.pointName) });
  }
});
