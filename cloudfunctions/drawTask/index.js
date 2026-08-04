// 云函数 drawTask：从 task_pool 按科目抽「未交付 / 最高 ROI」的卡，并标记 delivered_at
// 纯读快照，不依赖 AI 在线（v1.4 任务池模式）
// 注意：前端当前不调用本函数（主链路 = pages/tasks/tasks.js 本地 taskpool.js 派生）。
// delivered_at 交付标记闭环未启用；本函数保留作云端备用（启用需前端改调 drawTask 并按 delivered_at 过滤渲染）。
const cloud = require('wx-server-sdk');
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });
const db = cloud.database();

const META_KEYS = ['updated_at', 'updatedAt'];

exports.main = async (event) => {
  const subjects = (event.subjects || []).filter(Boolean);
  if (!subjects.length) return { cards: [] };

  const res = await db.collection('snapshot').doc('current').get();
  const snap = res.data;
  const pool = snap.task_pool || {};

  const poolSubjects = {};
  Object.keys(pool).forEach(k => {
    if (META_KEYS.indexOf(k) < 0) poolSubjects[k] = pool[k];
  });

  const subjName = {};
  (snap.subjects || []).forEach(s => { subjName[s.key] = s.name; });

  const cards = [];
  const deliveredIds = {};
  subjects.forEach(key => {
    const arr = (poolSubjects[key] || []).filter(c => !c.delivered_at);
    if (arr.length) {
      arr.sort((a, b) => (b.roi || 0) - (a.roi || 0));
      const top = arr[0];
      cards.push({ subject: key, subjectName: subjName[key] || key, title: top.title, card: top.card });
      deliveredIds[key] = deliveredIds[key] || [];
      deliveredIds[key].push(top.id);
    }
  });

  if (cards.length) {
    const newPool = Object.assign({}, pool);
    Object.keys(poolSubjects).forEach(key => {
      newPool[key] = poolSubjects[key].map(c => {
        if (deliveredIds[key] && deliveredIds[key].indexOf(c.id) >= 0) {
          return Object.assign({}, c, { delivered_at: new Date().toISOString() });
        }
        return c;
      });
    });
    await db.collection('snapshot').doc('current').update({ data: { task_pool: newPool } });
  }

  return { cards };
};
