const app = getApp();
const { callFunction } = require('../../../utils/api.js');
// 本地兜底派生字段（词汇掌握 / 计算错误率），云端旧快照可能缺失
const localDerived = require('../../../snapshotfallback.js');

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
// 词汇掌握度 -> 程度分级（越低越弱）
function degreeOfVocab(p) {
  if (p == null) return { label: '未测', color: COLOR.gray };
  if (p >= 0.85) return { label: '扎实', color: COLOR.green };
  if (p >= 0.70) return { label: '良好', color: COLOR.blue };
  if (p >= 0.50) return { label: '起步', color: COLOR.yellow };
  return { label: '薄弱', color: COLOR.red };
}
// 计算错误率 -> 颜色（越低越好）
function rateColor(r) {
  if (r == null) return COLOR.gray;
  if (r <= 0.10) return COLOR.green;
  if (r <= 0.22) return COLOR.blue;
  if (r <= 0.35) return COLOR.yellow;
  return COLOR.red;
}

Page({
  data: { subject: null, items: [], core: [], vocab: null, calc: null, loading: true },

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

    // 本地兜底合并派生字段：云端旧快照可能未含 vocab_mastery_pct / calc_error
    const der = localDerived[this.key];
    if (der) {
      if (subj.vocab_mastery_pct == null && der.vocab_mastery_pct != null) {
        subj.vocab_mastery_pct = der.vocab_mastery_pct;
      }
      if ((!subj.calc_error || !subj.calc_error.total) && der.calc_error) {
        subj.calc_error = der.calc_error;
      }
    }

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
      vocab: this.buildVocab(subj),
      calc: this.buildCalc(subj),
      loading: false
    });
  },

  // 英语：词汇掌握（中考150分对照）。vocab_mastery_pct 来自真实作业词汇类考点均值。
  buildVocab(subj) {
    const p = subj.vocab_mastery_pct;
    if (p == null) return null;
    const d = degreeOfVocab(p);
    const pct = Math.round(p * 100);
    return {
      pct_text: pct + '%',
      degree: d.label,
      color: d.color,
      note: '中考英语满分150：词汇是「词汇语法(30分)+读写(80分)」的底层支撑。当前词汇掌握≈'
        + pct + '%，距满分要求仍有明确空间；具体折算分值需真题校准（低置信）。'
    };
  },

  // 数学：计算错误率（实时）。calc_error = {total, wrong, rate}，来自 reports 全部计算类考点累计。
  buildCalc(subj) {
    const c = subj.calc_error;
    if (!c || !c.total) return null;
    return {
      rate_text: Math.round(c.rate * 100) + '%',
      total: c.total,
      wrong: c.wrong,
      color: rateColor(c.rate),
      note: '所有计算类题（符号/指数/分配律/完全平方/多项式除法/分数系数）累计；实时随每次作业分析刷新。'
    };
  },

  openReport(e) {
    const point = e.currentTarget.dataset.point;
    if (!point || !this.key) return;
    wx.navigateTo({ url: '/pages/mastery/report/report?key=' + this.key + '&point=' + encodeURIComponent(point) });
  }
});
