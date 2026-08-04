const { callFunction } = require('../../utils/api.js');

const SUBJ = { english: '英语', math: '数学', chinese: '语文' };
const MAX_PHOTOS = 30; // 一次提交最多 30 张（可分多次添加累加）

function fmtSize(n) {
  if (!n) return '';
  return n > 1024 * 1024 ? (n / 1024 / 1024).toFixed(1) + 'M' : Math.round(n / 1024) + 'K';
}

Page({
  data: {
    list: [],
    selected: [],   // [{ path, sizeText }]
    uploading: false,
    uploaded: 0,
    total: 0
  },

  onShow() {
    this.loadList();
  },

  async loadList() {
    try {
      const res = await callFunction('getUploads');
      this.setData({ list: (res.list || []).map(this.decorate) });
    } catch (e) {
      wx.showToast({ title: '列表加载失败', icon: 'none' });
    }
  },

  decorate(it) {
    let statusText = '待分析';
    if (it.status === 'done') statusText = '已分析';
    else if (it.status === 'rejected_irrelevant') statusText = '非作业·已忽略';
    return {
      ...it,
      statusText,
      subjectName: it.subject ? (SUBJ[it.subject] || it.subject) : '',
      timeText: String(it.createdAt || '').slice(0, 10)
    };
  },

  // 添加照片：可多次累加，每次最多 9 张（微信上限）
  addPhotos() {
    const remain = MAX_PHOTOS - this.data.selected.length;
    if (remain <= 0) {
      wx.showToast({ title: '一次最多提交 ' + MAX_PHOTOS + ' 张，请先提交已选', icon: 'none' });
      return;
    }
    const that = this;
    wx.chooseMedia({
      count: Math.min(9, remain),
      mediaType: ['image'], // 仅照片，禁视频
      sourceType: ['album', 'camera'],
      success: (mRes) => {
        const add = mRes.tempFiles.map(f => ({ path: f.tempFilePath, sizeText: fmtSize(f.size) }));
        that.setData({ selected: that.data.selected.concat(add) });
      },
      fail: () => {}
    });
  },

  removePhoto(e) {
    const i = +e.currentTarget.dataset.idx;
    const sel = this.data.selected.slice();
    sel.splice(i, 1);
    this.setData({ selected: sel });
  },

  clearSelected() {
    if (this.data.uploading) return;
    this.setData({ selected: [] });
  },

  // 批量上传所有已选照片（顺序上传，实时进度）
  async submitAll() {
    const sel = this.data.selected;
    if (!sel.length) {
      wx.showToast({ title: '请先选择照片', icon: 'none' });
      return;
    }
    if (this.data.uploading) return;
    this.setData({ uploading: true, uploaded: 0, total: sel.length });
    try {
      for (let i = 0; i < sel.length; i++) {
        const temp = sel[i].path;
        const m = temp.match(/\.(\w+)$/);
        const ext = m ? m[1] : 'jpg';
        const cloudPath = 'uploads/' + Date.now() + '-' + Math.floor(Math.random() * 1e6) + '.' + ext;
        const up = await wx.cloud.uploadFile({ cloudPath, filePath: temp });
        const r = await callFunction('upload', { fileID: up.fileID });
        if (!r || !r.ok) {
          throw new Error((r && r.msg) || '提交失败');
        }
        this.setData({ uploaded: i + 1 });
      }
      wx.showToast({ title: '已提交 ' + sel.length + ' 张，AI 上线后自动分析', icon: 'none' });
      this.setData({ selected: [] });
      this.loadList();
    } catch (e) {
      wx.showToast({ title: (e && e.message) || '上传失败，请重试', icon: 'none' });
    } finally {
      this.setData({ uploading: false, uploaded: 0, total: 0 });
    }
  },

  correct(e) {
    const id = e.currentTarget.dataset.id;
    wx.showActionSheet({
      itemList: ['实际是：语文', '实际是：数学', '实际是：英语'],
      success: (r) => {
        const map = ['chinese', 'math', 'english'];
        const subject = map[r.tapIndex];
        callFunction('correctSubject', { id, subject }).then(() => {
          wx.showToast({ title: '已修正', icon: 'success' });
          this.loadList();
        }).catch(() => wx.showToast({ title: '修正失败', icon: 'none' }));
      }
    });
  }
});
