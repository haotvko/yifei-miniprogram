const app = getApp();
const { callFunction } = require('../../utils/api.js');
// 本地题库仅作离线兜底；优先使用云端下发的 getAssets 缓存
const localBank = require('../../questionbank.js');
function getBank() {
  return app.globalData.bank || wx.getStorageSync('questionbank') || localBank;
}

const COLOR = { red: '#e04646', yellow: '#ffa726', blue: '#5b8def', green: '#34c759', gray: '#c7ccd4' };
function colorOf(c) { return COLOR[c] || COLOR.gray; }
function pctText(p) { return p == null ? '未测' : Math.round(p * 100) + '%'; }

Page({
  data: {
    subjects: [],        // [{key, name}]
    currentSubject: '',  // 当前选中的科目 key
    mode: 'practice',    // practice=智能提分练习 / roi=高价值任务卡
    corePoints: [],      // 当前科目的核心扣分项（红/黄优先，默认选中）= 智能提分目标
    items: [],           // 全部考点（手动下拉用）
    manualIndex: 0,
    quantity: 5,
    questions: [],
    showing: false,
    reveal: [],
    roiTasks: [],        // 当前科目的 ROI 排序高价值任务卡（错题提炼/今日单词）
    saving: false
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
          const hasBank = !!(getBank()[s.key] && getBank()[s.key][p.point]);
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
    this.buildRoi(cur, snap);
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
            hasBank: !!(getBank()[subjectKey] && getBank()[subjectKey][p.point]),
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
    this.buildRoi(key, app.globalData.snapshot);
    this.setData({ currentSubject: key, showing: false, questions: [], reveal: [] });
  },

  // 模式切换：practice=智能提分练习 / roi=高价值任务卡
  switchMode(e) {
    const mode = e.currentTarget.dataset.mode;
    if (mode === this.data.mode) return;
    this.setData({ mode, showing: false, questions: [], reveal: [] });
  },

  // 构建当前科目的 ROI 排序高价值任务卡（来自 snapshot.task_pool）
  buildRoi(subjectKey, snap) {
    let tasks = [];
    const pool = (snap && snap.task_pool && snap.task_pool[subjectKey]) || [];
    tasks = pool.filter(t => t && t.card)
      .sort((a, b) => (b.roi || 0) - (a.roi || 0))
      .map(t => {
        const c = t.card;
        const isWord = t.type === 'word';
        const title = isWord
          ? (c.word_from + ' → ' + c.word_to)
          : (c.title || c.point || t.title || '任务');
        const lines = [];
        if (isWord) {
          if (c.ipa) lines.push({ label: '音标', text: c.ipa });
          if (c.collocation) lines.push({ label: '搭配', text: c.collocation });
        }
        if (c.rule) lines.push({ label: '规则', text: c.rule });
        if (c.how) lines.push({ label: '怎么练', text: c.how });
        if (c.why) lines.push({ label: '为什么', text: c.why });
        return {
          id: t.id,
          type: t.type,
          typeLabel: isWord ? '今日单词' : '错题提炼',
          roi: (t.roi == null ? null : Math.round(t.roi * 100) / 100),
          title,
          lines
        };
      });
    this.setData({ roiTasks: tasks });
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
      const arr = (getBank()[t.subjectKey] && getBank()[t.subjectKey][t.point]) || [];
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
  back() { this.setData({ showing: false, questions: [], reveal: [] }); },

  // 按 A4 比例把高价值任务卡绘成图片并保存到相册（一页可打印）
  saveImage() {
    if (!this.data.roiTasks.length || this.data.saving) return;
    this.setData({ saving: true });
    const tasks = this.data.roiTasks;
    const subj = this.data.subjects.find(s => s.key === this.data.currentSubject);
    const subjName = subj ? subj.name : '';
    const dpr = ((wx.getWindowInfo && wx.getWindowInfo().pixelRatio)
      || (wx.getSystemInfoSync && wx.getSystemInfoSync().pixelRatio) || 2);
    const W = 595, H = 842; // A4 @72dpi

    wx.createSelectorQuery().select('#printCanvas').fields({ node: true, size: true }).exec(res => {
      if (!res || !res[0] || !res[0].node) {
        wx.showToast({ title: '画布初始化失败', icon: 'none' });
        this.setData({ saving: false });
        return;
      }
      const canvas = res[0].node;
      const ctx = canvas.getContext('2d');
      canvas.width = W * dpr;
      canvas.height = H * dpr;
      ctx.scale(dpr, dpr);
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, W, H);

      const M = 36;
      let y = M;
      ctx.fillStyle = '#2b2f38';
      ctx.font = 'bold 22px sans-serif';
      y = this.drawWrapped(ctx, '伊菲学习 · 高价值任务卡（' + subjName + '）', M, y + 18, W - 2 * M, 28);
      ctx.strokeStyle = '#e2e7f0';
      ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(M, y + 4); ctx.lineTo(W - M, y + 4); ctx.stroke();
      y += 22;

      tasks.forEach(t => {
        ctx.fillStyle = '#1f6feb';
        ctx.font = 'bold 16px sans-serif';
        y = this.drawWrapped(ctx, t.title, M, y + 16, W - 2 * M, 22);
        ctx.fillStyle = '#888888';
        ctx.font = '12px sans-serif';
        const roiTxt = (t.roi != null ? (' · ROI ' + t.roi.toFixed(2)) : '');
        y = this.drawWrapped(ctx, t.typeLabel + roiTxt, M, y + 14, W - 2 * M, 16);
        y += 6;
        (t.lines || []).forEach(l => {
          ctx.fillStyle = '#5b6ef0';
          ctx.font = 'bold 13px sans-serif';
          y = this.drawWrapped(ctx, l.label + '：', M, y + 15, W - 2 * M, 17);
          ctx.fillStyle = '#2b2f38';
          ctx.font = '13px sans-serif';
          y = this.drawWrapped(ctx, l.text, M + 16, y + 15, W - 2 * M - 16, 17);
          y += 4;
        });
        ctx.strokeStyle = '#eef1f7';
        ctx.beginPath(); ctx.moveTo(M, y + 2); ctx.lineTo(W - M, y + 2); ctx.stroke();
        y += 16;
      });

      wx.canvasToTempFilePath({
        canvas,
        success: r => {
          wx.saveImageToPhotosAlbum({
            filePath: r.tempFilePath,
            success: () => wx.showToast({ title: '已保存到相册' }),
            fail: e => wx.showToast({ title: '保存失败：' + (e.errMsg || ''), icon: 'none' }),
            complete: () => this.setData({ saving: false })
          });
        },
        fail: () => {
          wx.showToast({ title: '生成图片失败', icon: 'none' });
          this.setData({ saving: false });
        }
      });
    });
  },

  // 按宽度换行绘制文本，返回绘制后的 y
  drawWrapped(ctx, text, x, y, maxWidth, lineHeight) {
    if (text == null || text === '') return y;
    const chars = String(text).split('');
    let line = '';
    let yy = y;
    for (let i = 0; i < chars.length; i++) {
      const test = line + chars[i];
      if (ctx.measureText(test).width > maxWidth && line) {
        ctx.fillText(line, x, yy);
        line = chars[i];
        yy += lineHeight;
      } else {
        line = test;
      }
    }
    if (line) { ctx.fillText(line, x, yy); yy += lineHeight; }
    return yy;
  }
});
