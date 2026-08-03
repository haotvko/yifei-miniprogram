// 云函数 upload：接收已上传到云存储的作业图片，登记到 uploads 表（pending）
// v1.6：仅接受图片（视频在客户端 wx.chooseMedia 已限 image，此处二次校验扩展名拒收）
const cloud = require('wx-server-sdk');
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });
const db = cloud.database();

const IMG_EXT = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'];

exports.main = async (event) => {
  const { fileID } = event;
  if (!fileID) return { ok: false, msg: '缺少文件' };

  const lower = String(fileID).toLowerCase();
  const isImg = IMG_EXT.some(ext => lower.endsWith('.' + ext));
  if (!isImg) {
    // 视频 / 其他类型：直接拒收，不落库
    return { ok: false, msg: '仅支持照片上传，不支持视频' };
  }

  const openid = cloud.getWXContext().FROM_OPENID;
  await db.collection('uploads').add({
    data: {
      fileID: fileID,
      openid: openid,
      status: 'pending',          // pending -> done / rejected_irrelevant
      subject: null,              // 由后台 AI 分析后回填
      subjectConfidence: null,
      createdAt: db.serverDate(),
      analyzedAt: null
    }
  });
  return { ok: true };
};
