const app = getApp();
const { callFunction } = require('../../../utils/api.js');

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
  data: { subject: null, items: [], core: [], loading: true },

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

    // 全项评分卡：每一项都有掌握度评分（未测排最后）
    const items = (subj.points || []).slice().sort((a, b) => {
      const av = a.mastery_pct == null ? 2 : a.mastery_pct;
      const bv = b.mastery_pct == null ? 2 : b.mastery_pct;
      return av - bv;
    }).map(p => ({
      point: p.point,
      pct_text: pctText(p.mastery_pct),
      barPct: (p.mastery_pct == null ? 4 : Math.max(4, Math.round(p.mastery_pct * 100))) + '%',
      color: colorOf(p.status),
      status_label: statusLabel(p.status)
    }));

    // 核心薄弱项：只取最该先攻的「一项」（掌握度最低的红/黄）
    const core = (subj.points || [])
      .filter(p => p.status === 'red' || p.status === 'yellow')
      .sort((a, b) => {
        const av = a.mastery_pct == null ? 2 : a.mastery_pct;
        const bv = b.mastery_pct == null ? 2 : b.mastery_pct;
        return av - bv;
      })
      .slice(0, 1)
      .map(p => ({
        point: p.point,
        pct_text: pctText(p.mastery_pct),
        status_label: statusLabel(p.status),
        pill_class: pillClass(p.status),
        why: (p.evidence && p.evidence.trim()) ? p.evidence : '建议优先安排针对性练习'
      }));

    wx.setNavigationBarTitle({ title: subj.name + ' · 掌握情况' });
    this.setData({
      subject: {
        ...subj,
        mastery_text: pctText(subj.mastery_pct),
        ringPct: subj.mastery_pct == null ? 0 : Math.round(subj.mastery_pct * 100),
        ringColor: colorOf(subj.color)
      },
      items,
      core,
      loading: false
    });
  }
});
