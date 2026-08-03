const app = getApp();
const { callFunction } = require('../../utils/api.js');

Page({
  data: {
    options: [],
    selected: {},
    poolUpdated: '',
    cards: [],
    generating: false
  },

  onShow() {
    this.loadPool();
  },

  async loadPool() {
    try {
      const res = await callFunction('getSnapshot');
      const snap = res || {};
      const pool = (snap.task_pool && snap.task_pool.subjects) || snap.task_pool || {};
      const subjects = snap.subjects || [];
      const options = [];
      const selected = {};
      subjects.forEach(s => {
        const cards = pool[s.key] || [];
        const count = cards.filter(c => !c.delivered_at).length;
        if (count > 0) {
          options.push({ key: s.key, name: s.name, count });
          selected[s.key] = true;
        }
      });
      this.setData({
        options,
        selected,
        poolUpdated: (snap.task_pool && (snap.task_pool.updated_at || snap.task_pool.updatedAt)) || snap.data_as_of || ''
      });
    } catch (e) {
      wx.showToast({ title: '加载失败，请重试', icon: 'none' });
    }
  },

  toggle(e) {
    const key = e.currentTarget.dataset.key;
    const selected = Object.assign({}, this.data.selected);
    selected[key] = !selected[key];
    this.setData({ selected });
  },

  getSelectedKeys() {
    return this.data.options.filter(o => this.data.selected[o.key]).map(o => o.key);
  },

  async generate() {
    const keys = this.getSelectedKeys();
    if (!keys.length) {
      wx.showToast({ title: '请先勾选科目', icon: 'none' });
      return;
    }
    this.setData({ generating: true });
    try {
      const res = await callFunction('drawTask', { subjects: keys });
      this.setData({ cards: res.cards || [], generating: false });
    } catch (e) {
      this.setData({ generating: false });
      wx.showToast({ title: '生成失败，请重试', icon: 'none' });
    }
  },

  saveCard(e) {
    const idx = e.currentTarget.dataset.idx;
    const wrap = this.data.cards[idx];
    if (!wrap) return;
    this.drawAndSave(wrap.card, wrap.subjectName);
  },

  drawAndSave(card, subjectName) {
    const query = wx.createSelectorQuery();
    query.select('#cardCanvas').fields({ node: true, size: true }).exec((res) => {
      if (!res || !res[0] || !res[0].node) {
        wx.showToast({ title: '画布不可用', icon: 'none' });
        return;
      }
      const canvas = res[0].node;
      const ctx = canvas.getContext('2d');
      const dpr = (wx.getWindowInfo && wx.getWindowInfo().pixelRatio) || 2;
      const W = 360, H = 560;
      canvas.width = W * dpr;
      canvas.height = H * dpr;
      ctx.scale(dpr, dpr);

      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, W, H);
      ctx.fillStyle = '#eef3fb';
      ctx.fillRect(0, 0, W, 70);
      ctx.fillStyle = '#2c3038';
      ctx.font = 'bold 20px sans-serif';
      ctx.fillText(subjectName + ' · 今日任务', 20, 44);

      let y = 104;
      ctx.fillStyle = '#4a90d9';
      ctx.font = 'bold 19px sans-serif';
      y = this.wrap(ctx, card.title || '', 20, y, W - 40, 26) + 16;

      if (card.word_from) {
        ctx.fillStyle = '#2c3038';
        ctx.font = '15px sans-serif';
        y = this.wrap(ctx, '原词: ' + card.word_from, 20, y, W - 40, 22) + 6;
        y = this.wrap(ctx, '目标词: ' + card.word_to, 20, y, W - 40, 22) + 6;
        if (card.ipa) y = this.wrap(ctx, card.ipa, 20, y, W - 40, 22) + 6;
        if (card.collocation) y = this.wrap(ctx, '搭配: ' + card.collocation, 20, y, W - 40, 22) + 6;
      }
      if (card.point) {
        ctx.fillStyle = '#2c3038';
        ctx.font = '15px sans-serif';
        y = this.wrap(ctx, '考点: ' + card.point, 20, y, W - 40, 22) + 6;
      }
      ctx.fillStyle = '#e04646';
      ctx.font = 'bold 15px sans-serif';
      y = this.wrap(ctx, '规则: ' + (card.rule || ''), 20, y, W - 40, 22) + 6;
      ctx.fillStyle = '#2c3038';
      ctx.font = '15px sans-serif';
      y = this.wrap(ctx, '怎么学: ' + (card.how || ''), 20, y, W - 40, 22) + 10;
      ctx.fillStyle = '#4a90d9';
      this.wrap(ctx, '为什么: ' + (card.why || ''), 20, y, W - 40, 22);

      wx.canvasToTempFilePath({
        canvas,
        success: r => {
          wx.saveImageToPhotosAlbum({
            filePath: r.tempFilePath,
            success: () => wx.showToast({ title: '已保存到相册', icon: 'success' }),
            fail: () => wx.showToast({ title: '保存失败', icon: 'none' })
          });
        },
        fail: () => wx.showToast({ title: '生成图片失败', icon: 'none' })
      });
    });
  },

  wrap(ctx, text, x, y, maxW, lh) {
    if (!text) return y;
    let line = '';
    let cy = y;
    for (let i = 0; i < text.length; i++) {
      const test = line + text[i];
      if (ctx.measureText(test).width > maxW && line) {
        ctx.fillText(line, x, cy);
        cy += lh;
        line = text[i];
      } else {
        line = test;
      }
    }
    if (line) ctx.fillText(line, x, cy);
    return cy;
  }
});
