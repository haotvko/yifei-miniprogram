const app = getApp();
const { callFunction } = require('../../utils/api.js');
// 本地题库仅作离线兜底；优先使用云端下发的 getAssets 缓存
const localBank = require('../../questionbank.js');
// 本地任务池兜底：云端 snapshot.task_pool 不可用 / 未刷新时，高价值任务卡仍可见
const localPool = require('../../taskpool.js');
function getBank() {
  return app.globalData.bank || wx.getStorageSync('questionbank') || localBank;
}

const COLOR = { red: '#e04646', yellow: '#ffa726', blue: '#5b8def', green: '#34c759', gray: '#c7ccd4' };
function colorOf(c) { return COLOR[c] || COLOR.gray; }
function pctText(p) { return p == null ? '未测' : Math.round(p * 100) + '%'; }

Page({
  data: {
    subjects: [],          // [{key, name}]
    selectedSubjects: [],  // 多选科目，默认全选
    mode: 'practice',      // practice=智能提分练习 / roi=高价值任务卡
    quantity: 5,           // 每科题量 2–10
    printSections: [],     // [{subjectKey, subjectName, kind:'practice'|'roi', items:[...]}]
    saving: false
  },

  onLoad(options) {
    this.paramSubject = options.subject || '';
    this.paramPoint = options.point ? decodeURIComponent(options.point) : '';
    this.lockPoint = null;
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
    if (snap && snap.subjects) {
      snap.subjects.forEach(s => {
        subjects.push({ key: s.key, name: s.name });
      });
    }

    // 默认全选；若从「详细汇报-去练习」带参数进来，则只锁该科目/考点
    let selected = subjects.map(s => s.key);
    if (this.paramSubject) {
      selected = [this.paramSubject];
    } else if (this.paramPoint) {
      const s = (snap && snap.subjects || []).find(x => (x.points || []).some(p => p.point === this.paramPoint));
      if (s) { selected = [s.key]; this.lockPoint = { subjectKey: s.key, point: this.paramPoint }; }
    }

    this.setData({ subjects, selectedSubjects: selected });
    this.inited = true;
  },

  // 科目多选：点一下切换是否被选中
  toggleSubject(e) {
    const key = e.currentTarget.dataset.key;
    const sel = this.data.selectedSubjects.slice();
    const i = sel.indexOf(key);
    if (i > -1) sel.splice(i, 1); else sel.push(key);
    this.setData({ selectedSubjects: sel, printSections: [] });
  },

  // 模式切换：practice=智能提分练习 / roi=高价值任务卡
  switchMode(e) {
    const mode = e.currentTarget.dataset.mode;
    if (mode === this.data.mode) return;
    this.setData({ mode, printSections: [] });
  },

  dec() { this.setData({ quantity: Math.max(2, this.data.quantity - 1), printSections: [] }); },
  inc() { this.setData({ quantity: Math.min(10, this.data.quantity + 1), printSections: [] }); },

  // 每个科目的核心扣分项（红/黄优先，全部作为练习目标）
  coreForSubject(subjectKey, snap) {
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
            point: p.point,
            pct_text: pctText(p.mastery_pct),
            color: colorOf(p.status),
            hasBank: !!(getBank()[subjectKey] && getBank()[subjectKey][p.point])
          }));
      }
    }
    return pts;
  },

  // ROI 任务卡条目（来自 task_pool，缺失回退本地 taskpool.js）
  roiItemsOf(subjectKey, snap) {
    const pool = (snap && snap.task_pool && snap.task_pool[subjectKey]) || localPool[subjectKey] || [];
    return pool.filter(t => t && t.card)
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
  },

  shuffle(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  },

  // 一键生成：汇总所有选中科目，出一张可打印图（含答案）
  generate() {
    if (this.data.saving) return;
    const sel = this.data.selectedSubjects;
    if (!sel.length) { wx.showToast({ title: '请至少选一个科目', icon: 'none' }); return; }

    const snap = app.globalData.snapshot || {};
    const mode = this.data.mode;
    const subjects = this.data.subjects;
    const qty = this.data.quantity;
    const sections = [];

    if (mode === 'practice') {
      sel.forEach(k => {
        const subj = subjects.find(s => s.key === k);
        if (!subj) return;
        let core = this.coreForSubject(k, snap);
        if (this.lockPoint && this.lockPoint.subjectKey === k) {
          core = core.filter(c => c.point === this.lockPoint.point);
        }
        const targets = core.filter(c => c.hasBank);
        if (!targets.length) return;
        const pool = [];
        targets.forEach(t => {
          const arr = (getBank()[k] && getBank()[k][t.point]) || [];
          arr.forEach(q => pool.push({ q, point: t.point }));
        });
        if (!pool.length) return;
        const n = Math.min(qty, pool.length);
        const items = this.shuffle(pool).slice(0, n).map(p => {
          const q = p.q;
          return {
            q: q.q,
            tag: subj.name + ' · ' + p.point,
            choices: q.options.map((o, i2) => ({ l: String.fromCharCode(65 + i2), t: o, correct: o === q.answer })),
            answer: q.answer,
            explain: q.explain
          };
        });
        sections.push({ subjectKey: k, subjectName: subj.name, kind: 'practice', items });
      });
      if (!sections.length) { wx.showToast({ title: '所选科目题库建设中', icon: 'none' }); return; }
    } else {
      sel.forEach(k => {
        const subj = subjects.find(s => s.key === k);
        if (!subj) return;
        const tasks = this.roiItemsOf(k, snap);
        if (tasks.length) sections.push({ subjectKey: k, subjectName: subj.name, kind: 'roi', items: tasks });
      });
      if (!sections.length) { wx.showToast({ title: '所选科目暂无高价值任务', icon: 'none' }); return; }
    }

    this.setData({ printSections: sections });

    const modeLabel = mode === 'practice' ? '智能提分练习' : '高价值任务卡';
    const title = '伊菲学习 · 今日任务（' + modeLabel + ' · ' + sections.length + '科）';
    this.renderPrint(title, sections, mode);
  },

  // 把汇总后的 sections 画进 A4 画布（高度自适应，内容多则拉长，不截断）
  renderPrint(title, sections, mode) {
    this.setupCanvas(title, (ctx, y, M, W) => {
      sections.forEach(sec => {
        // 科目分隔标题
        ctx.fillStyle = '#5b6ef0';
        ctx.font = 'bold 17px sans-serif';
        y = this.drawWrapped(ctx, '【' + sec.subjectName + '】', M, y + 18, W - 2 * M, 22);
        ctx.strokeStyle = '#5b6ef0';
        ctx.lineWidth = 2;
        if (!this._dry) { ctx.beginPath(); ctx.moveTo(M, y + 2); ctx.lineTo(W - M, y + 2); ctx.stroke(); }
        y += 14;

        if (sec.kind === 'practice') {
          sec.items.forEach((q, qi) => {
            ctx.fillStyle = '#1f6feb';
            ctx.font = 'bold 15px sans-serif';
            y = this.drawWrapped(ctx, '第 ' + (qi + 1) + ' 题 · ' + q.tag, M, y + 16, W - 2 * M, 20);
            ctx.fillStyle = '#2b2f38';
            ctx.font = '13px sans-serif';
            y = this.drawWrapped(ctx, q.q, M, y + 15, W - 2 * M, 18);
            y += 2;
            (q.choices || []).forEach(o => {
              // 发布内容不带答案：选项不做正确项高亮/加粗（铁律 3.11）
              ctx.fillStyle = '#2b2f38';
              ctx.font = '12px sans-serif';
              y = this.drawWrapped(ctx, o.l + '. ' + o.t, M + 8, y + 15, W - 2 * M - 8, 16);
            });
            // 答案/解析不渲染到发布图（铁律 3.11：练习后由家长核对）
            ctx.strokeStyle = '#eef1f7';
            ctx.lineWidth = 1;
            if (!this._dry) { ctx.beginPath(); ctx.moveTo(M, y + 2); ctx.lineTo(W - M, y + 2); ctx.stroke(); }
            y += 14;
          });
        } else {
          sec.items.forEach(t => {
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
            ctx.lineWidth = 1;
            if (!this._dry) { ctx.beginPath(); ctx.moveTo(M, y + 2); ctx.lineTo(W - M, y + 2); ctx.stroke(); }
            y += 16;
          });
        }
        y += 12;
      });
      return y;
    });
  },

  // 通用：初始化 A4 离屏画布，先 dry-run 量出内容高度（自适应），再白底绘制并自动存图
  setupCanvas(title, drawContent) {
    if (this.data.saving) return;
    this.setData({ saving: true });
    const dpr = ((wx.getWindowInfo && wx.getWindowInfo().pixelRatio)
      || (wx.getSystemInfoSync && wx.getSystemInfoSync().pixelRatio) || 2);
    const W = 595, M = 36; // A4 @72dpi 宽

    wx.createSelectorQuery().select('#printCanvas').fields({ node: true, size: true }).exec(res => {
      if (!res || !res[0] || !res[0].node) {
        wx.showToast({ title: '画布初始化失败', icon: 'none' });
        this.setData({ saving: false });
        return;
      }
      const canvas = res[0].node;
      const ctx = canvas.getContext('2d');

      // dry-run：仅量高度，不落笔
      const paint = (dry) => {
        this._dry = dry;
        let y = M;
        ctx.fillStyle = '#2b2f38';
        ctx.font = 'bold 22px sans-serif';
        y = this.drawWrapped(ctx, title, M, y + 18, W - 2 * M, 28);
        ctx.strokeStyle = '#e2e7f0';
        ctx.lineWidth = 1;
        if (!dry) { ctx.beginPath(); ctx.moveTo(M, y + 4); ctx.lineTo(W - M, y + 4); ctx.stroke(); }
        y += 22;
        y = drawContent(ctx, y, M, W);
        this._dry = false;
        return y;
      };

      const endY = paint(true);
      const H = Math.max(842, Math.ceil(endY + 40)); // 至少一页 A4，内容多则拉长，不截断
      canvas.width = W * dpr;
      canvas.height = H * dpr;
      ctx.scale(dpr, dpr);
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, W, H);

      paint(false);

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

  // 按宽度换行绘制文本，返回绘制后的 y；dry 模式只量不画
  drawWrapped(ctx, text, x, y, maxWidth, lineHeight) {
    if (text == null || text === '') return y;
    const chars = String(text).split('');
    let line = '';
    let yy = y;
    for (let i = 0; i < chars.length; i++) {
      const test = line + chars[i];
      if (ctx.measureText(test).width > maxWidth && line) {
        if (!this._dry) ctx.fillText(line, x, yy);
        line = chars[i];
        yy += lineHeight;
      } else {
        line = test;
      }
    }
    if (line) { if (!this._dry) ctx.fillText(line, x, yy); yy += lineHeight; }
    return yy;
  }
});
