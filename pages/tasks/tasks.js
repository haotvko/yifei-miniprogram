const app = getApp();
const { callFunction } = require('../../utils/api.js');
const bank = require('../../questionbank.js');

Page({
  data: {
    items: [],          // [{subjectKey, subjectName, point, label, hasBank}]
    pickerIndex: 0,
    quantity: 5,
    questions: [],      // 当前抽取的题目（含 choices / answer / explain）
    showing: false,
    reveal: []          // 每题是否显示答案
  },

  onShow() {
    this.loadItems();
  },

  async loadItems() {
    let snap = app.globalData.snapshot;
    if (!snap) {
      try {
        snap = await callFunction('getSnapshot');
        app.globalData.snapshot = snap || {};
      } catch (e) { snap = null; }
    }
    const items = [];
    if (snap && snap.subjects) {
      snap.subjects.forEach(s => {
        (s.points || []).forEach(p => {
          const hasBank = !!(bank[s.key] && bank[s.key][p.point]);
          items.push({
            subjectKey: s.key,
            subjectName: s.name,
            point: p.point,
            label: s.name + ' · ' + p.point,
            hasBank
          });
        });
      });
    }
    if (!items.length) {
      wx.showToast({ title: '暂无考点，请先上传作业', icon: 'none' });
    }
    this.setData({ items });
  },

  onPick(e) {
    const idx = +e.detail.value;
    this.setData({ pickerIndex: idx, questions: [], showing: false, reveal: [] });
  },

  dec() {
    this.setData({ quantity: Math.max(2, this.data.quantity - 1) });
  },
  inc() {
    this.setData({ quantity: Math.min(10, this.data.quantity + 1) });
  },

  start() {
    const it = this.data.items[this.data.pickerIndex];
    if (!it) { wx.showToast({ title: '请先选择考点', icon: 'none' }); return; }
    if (!it.hasBank) { wx.showToast({ title: '该考点题库建设中', icon: 'none' }); return; }

    const pool = bank[it.subjectKey][it.point];
    const n = Math.min(this.data.quantity, pool.length);
    // 洗牌后取前 n 题
    const idx = Array.from({ length: pool.length }, (_, i) => i);
    for (let i = idx.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [idx[i], idx[j]] = [idx[j], idx[i]];
    }
    const questions = idx.slice(0, n).map(i => {
      const q = pool[i];
      return {
        q: q.q,
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

  revealAll() {
    this.setData({ reveal: this.data.questions.map(() => true) });
  },

  back() {
    this.setData({ showing: false, questions: [], reveal: [] });
  }
});
