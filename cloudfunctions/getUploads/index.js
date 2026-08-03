// 云函数 getUploads：返回当前用户的上传记录（用于上传页列表 + 轻量纠错入口）
const cloud = require('wx-server-sdk');
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });
const db = cloud.database();

exports.main = async () => {
  const openid = cloud.getWXContext().FROM_OPENID;
  const res = await db.collection('uploads')
    .where({ openid: openid })
    .orderBy('createdAt', 'desc')
    .limit(50)
    .get();
  return { list: res.data };
};
