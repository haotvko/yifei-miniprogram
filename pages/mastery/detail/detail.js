const app = getApp();
const { callFunction } = require('../../../utils/api.js');

const COLOR = { green: '#34c759', blue: '#5b8def', yellow: '#ffa726', gray: '#c7ccd4' };
function colorOf(c) { return COLOR[c] || COLOR.gray; }
function pctText(p) {
  return p == null ? '待测' : Math.round(p * 100) + '%';
}

Page({
  data: { subject: null, core: [], mastered: [], loading: true },

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

    const order = { red: 0, yellow: 1, green: 2 };
    const all = (subj.points || []).slice().sort((a, b) =>
      (order[a.status] != null ? order[a.status] : 3) - (order[b.status] != null ? order[b.status] : 3)
    ).map(p => ({
      ...p,
      pct_text: pctText(p.mastery_pct),
      status_label: p.status === 'red' ? '待补' : (p.status === 'yellow' ? '薄弱' : '已掌握')
    }));

    // 核心问题：最该攻克的薄弱点（红>黄），最多 4 条
    const core = all.filter(p => p.status === 'red' || p.status === 'yellow').slice(0, 4).map(p => ({
      point: p.point,
      status: p.status,
      pct_text: p.pct_text,
      status_label: p.status_label,
      emoji: p.status === 'red' ? '🔴' : '🟡',
      why: (p.evidence && p.evidence.trim()) ? p.evidence : '建议优先安排针对性练习'
    }));

    // 已掌握：绿色点
    const mastered = all.filter(p => p.status === 'green').map(p => ({ point: p.point }));

    wx.setNavigationBarTitle({ title: subj.name + ' · 掌握情况' });
    this.setData({
      subject: {
        ...subj,
        mastery_text: pctText(subj.mastery_pct),
        ringPct: subj.mastery_pct == null ? 0 : Math.round(subj.mastery_pct * 100),
        ringColor: colorOf(subj.color)
      },
      core,
      mastered,
      loading: false
    });
  }
});
