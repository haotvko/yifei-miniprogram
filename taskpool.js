// 本地兜底任务池：结构与云端 snapshot.task_pool 一致（按科目分）。
// 用途：云端 getSnapshot 不可用 / 未刷新时，今日任务「高价值任务卡」仍能显示内容。
// 纪律：本文件属小程序代码包，必须 GBK 安全 —— 不含 IPA/上标/emoji/弯引号等非 GBK 字符。
module.exports = {
  english: [
    {
      id: "en-01",
      type: "master",
      title: "完形填空·长语境逻辑",
      roi: 0.95,
      delivered_at: null,
      card: {
        title: "完形填空·长语境逻辑",
        rule: "先通读抓主线，再按上下文选词",
        how: "1.读首句定主题 2.空前后找线索 3.排除明显错项",
        why: "长语境类是英语当前最大确定性失分面"
      }
    },
    {
      id: "en-02",
      type: "word",
      title: "experience 经历/经验",
      roi: 0.8,
      delivered_at: null,
      card: {
        word_from: "experience",
        word_to: "experienced / experience(n.经历)",
        collocation: "an experience / work experience",
        rule: "作「经历」可数、作「经验」不可数",
        how: "1.记双义 2.练单复数 3.造句",
        why: "价值排序 T1，易混 countable/uncountable"
      }
    }
  ],
  math: [
    {
      id: "ma-01",
      type: "master",
      title: "符号管理·去括号负号",
      roi: 0.9,
      delivered_at: null,
      card: {
        point: "去括号遇负号全变号",
        rule: "-(a-b) = -a + b",
        how: "1.标负号 2.逐项变号 3.复查",
        why: "符号错占数学丢分约 1/3"
      }
    }
  ],
  chinese: []
};
