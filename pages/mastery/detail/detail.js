const app = getApp();
const { callFunction } = require('../../../utils/api.js');

const COLOR = { green: '#34c759', blue: '#5b8def', yellow: '#ffa726', gray: '#c7ccd4' };
function colorOf(c) { return COLOR[c] || COLOR.gray; }
function pctText(p) {
  return p == null ? '待测' : Math.round(p * 100) + '%';
}

Page({
  data: { subject: null, core: [], main: [], loading: true },

  onLoad(options) {
    this.key = options.key;
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
    if (!snap || !snap.subjects) { this.setData({ loading: false }); return; }

    const subj = snap.subjects.find(s => s.key === this.key);
    if (!subj) { this.setData({ loading: false }); return; }

    const all = (subj.points || []).map(p => ({
      ...p,
      pct_text: pctText(p.mastery_pct),
      status_label: p.status === 'red' ? '待补' : (p.status === 'yellow' ? '薄弱' : '已掌握')
    }));

    // 核心问题：红色「待补」硬伤，最该先攻
    const core = all.filter(p => p.status === 'red').map(p => ({
      point: p.point,
      pct_text: p.pct_text,
      status_label: p.status_label,
      why: (p.evidence && p.evidence.trim()) ? p.evidence : '建议优先安排针对性练习'
    }));

    // 主要问题：黄色「薄弱」需补强点
    const main = all.filter(p => p.status === 'yellow').map(p => ({
      point: p.point,
      pct_text: p.pct_text,
      status_label: p.status_label,
      why: (p.evidence && p.evidence.trim()) ? p.evidence : '建议安排巩固练习'
    }));

    wx.setNavigationBarTitle({ title: subj.name + ' · 掌握情况' });
    this.setData({
      subject: {
        ...subj,
        mastery_text: pctText(subj.mastery_pct),
        ringPct: subj.mastery_pct == null ? 0 : Math.round(subj.mastery_pct * 100),
        ringColor: colorOf(subj.color)
      },
      core,
      main,
      loading: false
    });
  }
});
