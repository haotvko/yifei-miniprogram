// 云函数 getAssets：从云存储下发题库(questionbank)与详细汇报(reports)
// 数据以 JSON 文件存于云存储 assets/，更新内容只需重新上传文件并刷新 assets_meta，无需重新发布小程序
const cloud = require('wx-server-sdk');
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });
const db = cloud.database();

exports.main = async () => {
  let meta = null;
  try {
    const res = await db.collection('assets').doc('assets_meta').get();
    meta = res.data;
  } catch (e) {
    console.error('assets_meta 读取失败', e);
    return { questionbank: null, reports: null };
  }
  if (!meta) return { questionbank: null, reports: null };

  async function dl(fid) {
    const r = await cloud.downloadFile({ fileID: fid });
    return JSON.parse(r.fileContent.toString('utf8'));
  }

  let questionbank = null;
  let reports = null;
  try { questionbank = await dl(meta.qb); } catch (e) { console.error('questionbank 下载失败', e); }
  try { reports = await dl(meta.rp); } catch (e) { console.error('reports 下载失败', e); }

  return { questionbank, reports };
};
