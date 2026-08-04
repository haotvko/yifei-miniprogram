// 本地兜底：快照的派生字段（词汇掌握 / 计算错误率）。
// 结构与 snapshot.subjects[i] 对齐，仅含云端旧快照可能缺失的派生字段。
// 云端 getSnapshot 已含这些字段时以云端为准；缺失时本文件兜底，确保详情页两卡始终可见。
// 数值来自真实作业落笔（export_snapshot.py 计算）：
//   english.vocab_mastery_pct = 词汇类考点掌握度均值
//   math.calc_error            = 全部计算类考点累计「错误/总量」错误率
module.exports = {
  english: { vocab_mastery_pct: 0.52 },
  math: { calc_error: { total: 122, wrong: 25, rate: 0.2049 } }
};
