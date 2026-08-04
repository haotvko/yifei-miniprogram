const app = getApp();
const { callFunction } = require('../../utils/api.js');
const bank = require('../../questionbank.js');

const COLOR = { red: '#e04646', yellow: '#ffa726', blue: '#5b8def', green: '#34c759', gray: '#c7ccd4' };
function colorOf(c) { return COLOR[c] || COLOR.gray; }
function pctText(p) { return p == null ? '未测' : Math.round(p * 100) + '%'; }

Page({
  data: {
    subjects: [],        // [{key, name}]
    currentSubject: '',  // 当前选中的科目 key
    corePoints: [],      // 当前科目的核心扣分项（红/黄优先，默认选中）= 智能提分目标
    items: [],           // 全部考点（手动下拉用）
    manualIndex: 0,
    quantity: 5,
    questions: [],
    showing: false,
    reveal: []
  },

  onLoad(options) {
    this.paramSubject = options.subject || '';
    this.paramPoint = options.point ? decodeURIComponent(options.point) : '';
    this.inited = false;
    this.load();
  },

  onShow() {
    if (!this.inited) return;       // 首次已在 onLoad 加载，避免重置选择
  },

  async load() {
    let snap = app.globalData.snapshot;
    if (!snap) {
      try {
        snap = await callFunction('getSnapshot');
        app.globalData.snapshot = snap || {};
      } catch (e) { snap = null; }
    }

    const subjects = [];
    const items = [];
    if (snap && snap.subjects) {
      snap.subjects.forEach(s => {
        subjects.push({ key: s.key, name: s.name });
        (s.points || []).forEach(p => {
          const hasBank = !!(bank[s.key] && bank[s.key][p.point]);
          items.push({
            subjectKey: s.key,
            subjectName: s.name,
            point: p.point,
            label: s.name + ' · ' + p.point,
            hasBank,
            pct: p.mastery_pct,
            status: p.status
          });
        });
      });
    }

    // 默认科目：来自参数 > 第一个有考点的科目 > 第一个科目
    let cur = this.paramSubject;
    if (!cur && subjects.length) {
      const withPoints = subjects.find(s => (snap.subjects.find(x => x.key === s.key).points || []).length);
      cur = (withPoints || subjects[0]).key;
    }

    this.buildCore(cur, snap);
    this.setData({ subjects, items, currentSubject: cur, manualIndex: 0 });
    this.inited = true;

    // 从「详细汇报-去练习」进来：精确锁定该考点并自动开始
    if (this.paramPoint) {
      const cps = this.data.corePoints.map(c => ({ ...c, picked: c.point === this.paramPoint }));
      this.setData({ corePoints: cps, currentSubject: cur });
      this.start();
    }
  },

  // 依据当前科目构建核心扣分项：红/黄优先；若都没有则取最弱
  buildCore(subjectKey, snap) {
    let pts = [];
    if (snap && snap.subjects) {
      const subj = snap.subjects.find(s => s.key === subjectKey);
      if (subj) {
        const all = (subj.points || []).slice();
        const weak = all.filter(p => p.status === 'red' || p.status === 'yellow')
          .sort((a, b) => (a.mastery_pct == null ? 2 : a.mastery_pct) - (b.mastery_pct == null ? 2 : b.mastery_pct));
        pts = (weak.length ? weak : all.slice().sort((a, b) =>
          (a.mastery_pct == null ? 2 : a.mastery_pct) - (b.mastery_pct == null ? 2 : b.mastery_pct)))
          .map(p => ({
            subjectKey,
            point: p.point,
            pct_text: pctText(p.mastery_pct),
            color: colorOf(p.status),
            hasBank: !!(bank[subjectKey] && bank[subjectKey][p.point]),
            picked: true
          }));
      }
    }
    this.setData({ corePoints: pts });
  },

  switchSubject(e) {
    const key = e.currentTarget.dataset.key;
    if (key === this.data.currentSubject) return;
    this.buildCore(key, app.globalData.snapshot);
    this.setData({ currentSubject: key, showing: false, questions: [], reveal: [] });
  },

  toggleCore(e) {
    const point = e.currentTarget.dataset.point;
    const cps = this.data.corePoints.map(c => c.point === point ? { ...c, picked: !c.picked } : c);
    this.setData({ corePoints: cps });
  },

  onPick(e) {
    const idx = +e.detail.value;
    this.setData({ manualIndex: idx, showing: false, questions: [], reveal: [] });
  },

  dec() { this.setData({ quantity: Math.max(2, this.data.quantity - 1) }); },
  inc() { this.setData({ quantity: Math.min(10, this.data.quantity + 1) }); },

  start() {
    // 目标考点：优先用选中的核心扣分项（智能提分）；若都没选则用手动下拉
    let targets = this.data.corePoints.filter(c => c.picked && c.hasBank);
    if (!targets.length) {
      const m = this.data.items[this.data.manualIndex];
      if (m && m.hasBank) targets = [m];
    }
    if (!targets.length) {
      wx.showToast({ title: '该考点题库建设中', icon: 'none' });
      return;
    }

    // 合并所有目标考点的题库，洗牌后抽 N 题
    const pool = [];
    targets.forEach(t => {
      const arr = (bank[t.subjectKey] && bank[t.subjectKey][t.point]) || [];
      arr.forEach(q => pool.push({ q, subjectName: t.subjectName, point: t.point }));
    });
    if (!pool.length) { wx.showToast({ title: '题库为空', icon: 'none' }); return; }

    const n = Math.min(this.data.quantity, pool.length);
    const idx = Array.from({ length: pool.length }, (_, i) => i);
    for (let i = idx.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [idx[i], idx[j]] = [idx[j], idx[i]];
    }
    const questions = idx.slice(0, n).map(i => {
      const q = pool[i].q;
      return {
        q: q.q,
        tag: pool[i].subjectName + ' · ' + pool[i].point,
        choices: q.options.map((o, k) => ({ l: String.fromCharCode(65 + k), t: o, correct: o === q.answer })),
        answer: q.answer,
        explain: q.explain
      };
    });
    this.setData({ questions, showing: true, reveal: questions.map(() => false) });
  },

  toggleReveal(e) {
    const i = +e.currentTarget.dataset.idx;
    const r = this.data.reveal.slice();
    r[i] = !r[i];
    this.setData({ reveal: r });
  },
  revealAll() { this.setData({ reveal: this.data.questions.map(() => true) }); },
  back() { this.setData({ showing: false, questions: [], reveal: [] }); }
});
