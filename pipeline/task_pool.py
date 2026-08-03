# -*- coding: utf-8 -*-
"""任务池维护工具（v1.4 任务池模式的本地辅助）。
- reset_delivered：清空某科已交付标记，使卡片重新可抽（AI 在线重整时调用）。
- summary：打印各科目待出卡片数。
真正的 ROI 排序与候选内容由 AI（WorkBuddy）在「在线重整」时编辑各 00-最新状况.md 的「任务池候选」块完成。
"""
import os
import re

SUBJECTS = {
    "english": "D:/Obsidian/伊菲英语学习管理/00-最新状况.md",
    "math": "D:/Obsidian/伊菲数学学习管理/00-最新状况.md",
    "chinese": "D:/Obsidian/伊菲语文学习管理/00-最新状况.md",
}

BLOCK_RE = re.compile(r"^##\s*任务池候选\s*$(.*?)(?=^##\s|\Z)", re.S | re.M)


def _rewrite_block(path, transformer):
    text = open(path, encoding="utf-8").read()
    m = BLOCK_RE.search(text)
    if not m:
        print(f"[warn] {path} 无「任务池候选」块")
        return
    new_body = transformer(m.group(1))
    text = text[:m.start(1)] + new_body + text[m.end(1):]
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def reset_delivered(subject):
    path = SUBJECTS[subject]
    if not os.path.exists(path):
        return
    def tf(body):
        lines = []
        for line in body.splitlines():
            if "delivered_at:" in line:
                indent = line[:len(line) - len(line.lstrip())]
                lines.append(f"{indent}delivered_at: null")
            else:
                lines.append(line)
        return "\n".join(lines)
    _rewrite_block(path, tf)
    print(f"[ok] {subject} 任务池 delivered_at 已重置")


def summary():
    for subj, path in SUBJECTS.items():
        if not os.path.exists(path):
            continue
        text = open(path, encoding="utf-8").read()
        m = BLOCK_RE.search(text)
        if not m:
            print(f"{subj}: 无任务池块")
            continue
        pending = m.group(1).count("delivered_at: null")
        print(f"{subj}: 待出卡片 {pending}")


if __name__ == "__main__":
    summary()
