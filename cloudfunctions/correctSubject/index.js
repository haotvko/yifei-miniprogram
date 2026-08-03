// 云函数 correctSubject：用户纠正学科误判（仅修正路由，不影响底层分析数据）
const cloud = require('wx-server-sdk');
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });
const db = cloud.database();

exports.main = async (event) => {
  const { id, subject } = event;
  if (!id || !subject) return { ok: false };
  await db.collection('uploads').doc(id).update({
    data: { subject: subject, correctedByUser: true }
  });
  return { ok: true };
};
