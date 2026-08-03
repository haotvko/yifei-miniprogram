# -*- coding: utf-8 -*-
"""
一次性 / 可重复执行：向三科 00-最新状况.md 追加「看板数据」与「任务池候选」YAML 块。
幂等：若块已存在则不重复追加。
这是「本地管道 <-> Obsidian 单一事实源」的数据契约入口。
"""
import os

BLOCKS = {
    "english": (
        "## 看板数据\n"
        "# 本块由本地管道自动读取，导出看板快照 JSON。请勿手改数字，改数请改上方正文。\n"
        "subject_key: english\n"
        "mastery_pct: 0.60\n"
        "predicted_score_150: 27\n"
        "weak_count: 4\n"
        "key_hint: \"最该补：完形填空（长语境类，约20%）\"\n"
        "points:\n"
        "  - point: \"完形填空·长语境\"\n"
        "    mastery_pct: 0.20\n"
        "    status: red\n"
        "    evidence: \"\\U0001F7E2真题\"\n"
        "  - point: \"词汇辨析/易混词\"\n"
        "    mastery_pct: 0.46\n"
        "    status: yellow\n"
        "    evidence: \"\\U0001F7E2真题\"\n"
        "  - point: \"词性转换·名→形\"\n"
        "    mastery_pct: 0.58\n"
        "    status: yellow\n"
        "    evidence: \"\\U0001F7E2真题\"\n"
        "  - point: \"词性转换·动→名\"\n"
        "    mastery_pct: 0.52\n"
        "    status: yellow\n"
        "    evidence: \"\\U0001F7E2真题\"\n"
        "  - point: \"阅读问答（开放题）\"\n"
        "    mastery_pct: 0.60\n"
        "    status: yellow\n"
        "    evidence: \"\\U0001F7E2真题\"\n"
        "untested:\n"
        "  - \"听力30\"\n"
        "  - \"口语10\"\n"
        "  - \"作文20\"\n"
        "\n"
        "## 任务池候选\n"
        "# AI 在线重整时维护：按 ROI 排序的待出卡片队列（delivered_at 由抽卡云函数回填）。\n"
        "- id: en-01\n"
        "  type: master\n"
        "  title: \"完形填空·长语境逻辑\"\n"
        "  roi: 0.95\n"
        "  delivered_at: null\n"
        "  card:\n"
        "    title: \"完形填空·长语境逻辑\"\n"
        "    rule: \"先通读抓主线，再按上下文选词\"\n"
        "    how: \"①读首句定主题 ②空前后找线索 ③排除明显错项\"\n"
        "    why: \"长语境类是英语当前最大确定性失分面\"\n"
        "- id: en-02\n"
        "  type: word\n"
        "  title: \"experience 经历/经验\"\n"
        "  roi: 0.80\n"
        "  delivered_at: null\n"
        "  card:\n"
        "    word_from: \"experience\"\n"
        "    word_to: \"experienced / experience(n.经历)\"\n"
        "    ipa: \"/\\u026ak\\u02c8sp\\u026a\\u0259ri\\u0259ns/\"\n"
        "    collocation: \"an experience / work experience\"\n"
        "    rule: \"作'经历'可数、作'经验'不可数\"\n"
        "    how: \"①记双义 ②练单复数 ③造句\"\n"
        "    why: \"价值排序 T1，易混 countable/uncountable\"\n"
    ),
    "math": (
        "## 看板数据\n"
        "# 本块由本地管道自动读取，导出看板快照 JSON。请勿手改数字，改数请改上方正文。\n"
        "subject_key: math\n"
        "mastery_pct: 0.76\n"
        "predicted_score_150: null\n"
        "weak_count: 5\n"
        "key_hint: \"最该补：符号管理（负号/去括号/代入负数）\"\n"
        "points:\n"
        "  - point: \"符号管理（负号奇偶/去括号分配）\"\n"
        "    mastery_pct: 0.76\n"
        "    status: yellow\n"
        "    evidence: \"\\U0001F7E2真题\"\n"
        "  - point: \"指数法则混淆\"\n"
        "    mastery_pct: 0.80\n"
        "    status: yellow\n"
        "    evidence: \"\\U0001F7E2真题\"\n"
        "  - point: \"分配律漏项\"\n"
        "    mastery_pct: 0.83\n"
        "    status: blue\n"
        "    evidence: \"\\U0001F7E2真题\"\n"
        "  - point: \"完全平方变形与逆用\"\n"
        "    mastery_pct: 0.80\n"
        "    status: yellow\n"
        "    evidence: \"\\U0001F7E2真题\"\n"
        "  - point: \"多项式除以单项式\"\n"
        "    mastery_pct: 0.82\n"
        "    status: yellow\n"
        "    evidence: \"\\U0001F7E2真题\"\n"
        "  - point: \"分数系数合并同类项\"\n"
        "    mastery_pct: 0.77\n"
        "    status: yellow\n"
        "    evidence: \"\\U0001F7E2真题\"\n"
        "untested:\n"
        "  - \"几何\"\n"
        "  - \"函数\"\n"
        "  - \"综合应用题\"\n"
        "\n"
        "## 任务池候选\n"
        "- id: ma-01\n"
        "  type: master\n"
        "  title: \"符号管理·去括号负号\"\n"
        "  roi: 0.90\n"
        "  delivered_at: null\n"
        "  card:\n"
        "    point: \"去括号遇负号全变号\"\n"
        "    rule: \"-(a-b) = -a + b\"\n"
        "    how: \"①标负号 ②逐项变号 ③复查\"\n"
        "    why: \"符号错占数学丢分约 1/3\"\n"
    ),
    "chinese": (
        "## 看板数据\n"
        "# 本块由本地管道自动读取，导出看板快照 JSON。请勿手改数字，改数请改上方正文。\n"
        "subject_key: chinese\n"
        "mastery_pct: null\n"
        "predicted_score_150: null\n"
        "weak_count: 0\n"
        "key_hint: \"待评估·未上传\"\n"
        "points: []\n"
        "untested: []\n"
        "\n"
        "## 任务池候选\n"
        "# 语文尚未上传作业，任务池为空。\n"
        "# (空)\n"
    ),
}

PATHS = {
    "english": "D:/Obsidian/伊菲英语学习管理/00-最新状况.md",
    "math": "D:/Obsidian/伊菲数学学习管理/00-最新状况.md",
    "chinese": "D:/Obsidian/伊菲语文学习管理/00-最新状况.md",
}


def ensure_block(path, header, body):
    text = open(path, encoding="utf-8").read()
    if ("## " + header) in text:
        print(f"[skip] {path} 已有「{header}」")
        return
    with open(path, "a", encoding="utf-8") as f:
        if not text.endswith("\n"):
            f.write("\n")
        f.write("\n" + body + "\n")
    print(f"[add ] {path} 追加「{header}」")


if __name__ == "__main__":
    for key, path in PATHS.items():
        if not os.path.exists(path):
            print(f"[warn] 不存在: {path}")
            continue
        block = BLOCKS[key]
        # 拆分看板数据 / 任务池候选 两个块分别幂等追加
        head, _, tail = block.partition("## 任务池候选")
        ensure_block(path, "看板数据", head.strip())
        if tail.strip():
            ensure_block(path, "任务池候选", ("## 任务池候选" + tail).strip())
