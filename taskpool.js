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
    },
    {
      id: "en-03",
      type: "master",
      title: "词形/词性转换（动→名/形→副/否定前缀等）",
      roi: 0.85,
      delivered_at: null,
      card: {
        title: "词形变化+词性转换",
        point: "词性转换·动→名 / 形→副 / 不规则",
        rule: "按词族记忆派生（同一词根）；注意不规则变化",
        how: "1.列词族（curious→curiosity→curiously） 2.记拼写重读 3.默写对比",
        why: "2026-08-03+04 batch 23张反复错（curious→curiosity、hopefully、success、possible、eighty→eightieth 等），频率高、确定性可攻"
      }
    },
    {
      id: "en-04",
      type: "master",
      title: "同义句改写（一般疑问/反义/保持句义）",
      roi: 0.82,
      delivered_at: null,
      card: {
        title: "同义句/反义句改写",
        point: "句型转换·一般疑问 / 反义 / 同义保持",
        rule: "一般疑问：be/do/does 提前；反义加 not 或换反义词；保持句义不变只换表达",
        how: "1.看题目要求（一般疑问/反义/同义不变） 2.对应变换 3.检查句义",
        why: "2026-08-03+04 batch Sandy/blind boy/other boys/halfway/make kids 等改写高频错，确定性可攻"
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
    },
    {
      id: "ma-02",
      type: "master",
      title: "M2 次数计算与同类项判定",
      roi: 0.82,
      delivered_at: null,
      card: {
        point: "单项式次数=字母指数之和；同类项=字母+指数全相同",
        rule: "系数不计次数；多项式次数=最高项次数",
        how: "1.列单项式字母及指数 2.相加得次数 3.对照同类项需字母与指数全等",
        why: "2026-08-03+04 batch Q17 单项式次数（学生把 3a^3 b^6 算成 11 而非 9）、Q15-16 升幂排列 多错；M2 概念清不清的确定性错误"
      }
    },
    {
      id: "ma-03",
      type: "master",
      title: "M6 完全平方公式参数判定",
      roi: 0.78,
      delivered_at: null,
      card: {
        point: "x^2 +- kxy + y^2 为完全平方时 k = 正负2",
        rule: "(x+-y)^2 = x^2 +- 2xy + y^2 中间项系数即 k",
        how: "1.看中间项符号 2.k = 中间项系数与 xy 系数关系 3.检验展开",
        why: "2026-08-04 batch Q6-7 学生答「无」（应为正负6/正负4），概念与同类项判定关联弱"
      }
    }
  ],
  chinese: [
    {
      id: "zh-01",
      type: "master",
      title: "文言实词多义（且/顷/数）",
      roi: 0.9,
      delivered_at: null,
      card: {
        title: "文言实词多义辨析",
        point: "文言实词多义",
        rule: "按语境定义项，勿死记单一义",
        how: "1.记多义清单 2.结合例句判定 3.翻译代入验证",
        why: "2026-08-02 首批 3 处实词多义失分（且=将要、顷=不久、数=屡次），确定性可攻"
      }
    },
    {
      id: "zh-02",
      type: "word",
      title: "安（安定/怎么/养）",
      roi: 0.8,
      delivered_at: null,
      card: {
        word_from: "安",
        word_to: "安（怎么·表反问）",
        collocation: "安能辨我是雄雌",
        rule: "多义：安（怎么）常表反问",
        how: "1.记三义 2.例句辨析 3.默写巩固",
        why: "《中考语文价值排序》T1·高频核心50之首"
      }
    }
  ]
};
