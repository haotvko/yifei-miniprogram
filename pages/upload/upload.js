const { callFunction } = require('../../utils/api.js');

const SUBJ = { english: '英语', math: '数学', chinese: '语文' };

Page({
  data: { list: [], uploading: false },

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

  chooseAndUpload() {
    const that = this;
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'], // v1.6：仅照片，禁视频
      sourceType: ['album', 'camera'],
      success: async (mRes) => {
        const temp = mRes.tempFiles[0].tempFilePath;
        that.setData({ uploading: true });
        try {
          const m = temp.match(/\.(\w+)$/);
          const ext = m ? m[1] : 'jpg';
          const cloudPath = 'uploads/' + Date.now() + '-' + Math.floor(Math.random() * 1e6) + '.' + ext;
          const up = await wx.cloud.uploadFile({ cloudPath, filePath: temp });
          const r = await callFunction('upload', { fileID: up.fileID });
          if (r && r.ok) {
            wx.showToast({ title: '已提交，AI 上线后自动分析', icon: 'none' });
            that.loadList();
          } else {
            wx.showToast({ title: (r && r.msg) || '提交失败', icon: 'none' });
          }
        } catch (e) {
          wx.showToast({ title: '上传失败，请重试', icon: 'none' });
        } finally {
          that.setData({ uploading: false });
        }
      },
      fail: () => {}
    });
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
