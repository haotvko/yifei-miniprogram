// 云函数 getSnapshot：返回最新看板快照（含 task_pool）
const cloud = require('wx-server-sdk');
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });
const db = cloud.database();

exports.main = async () => {
  const res = await db.collection('snapshot').doc('current').get();
  return res.data;
};
