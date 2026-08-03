const app = getApp();
const { callFunction } = require('../../../utils/api.js');

function pctText(p) {
  return p == null ? '待测' : Math.round(p * 100) + '%';
}

Page({
  data: { subject: null, points: [], loading: true },

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
    const points = (subj.points || []).slice().sort((a, b) =>
      (order[a.status] != null ? order[a.status] : 3) - (order[b.status] != null ? order[b.status] : 3)
    ).map(p => ({
      ...p,
      pct_text: pctText(p.mastery_pct),
      status_label: p.status === 'red' ? '待补' : (p.status === 'yellow' ? '薄弱' : '已掌握')
    }));

    wx.setNavigationBarTitle({ title: subj.name + ' · 掌握情况' });
    this.setData({
      subject: { ...subj, mastery_text: pctText(subj.mastery_pct) },
      points,
      loading: false
    });
  }
});
