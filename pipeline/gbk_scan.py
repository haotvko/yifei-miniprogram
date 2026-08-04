# -*- coding: utf-8 -*-
"""扫描小程序代码包文件是否含非 GBK 字符（GBK 纪律守门员）。

小程序代码包 (js/wxml/wxss/json) 若含非 GBK 字符（emoji / 上标 / 特殊符号），
在部分真机或微信开发者工具里会乱码甚至上传失败。本脚本在提交/发版前跑一遍，
把所有非 GBK 字符定位到 文件:行号:字符，便于替换为 GBK 安全写法。

判定方法：文件按 UTF-8 读取（微信代码包标准编码），再逐个字符尝试 encode('gbk')；
无法编码的即「非 GBK 字符」。
  GBK 安全写法：指数用 ^（x^2，勿用 x²）、勾选 ●（勿用 ✓）、箭头 →←＋·、
                 括号 （）「」【】、星 ★、圈数字 ① 等。

用法:
  python pipeline/gbk_scan.py            # 默认扫 cloudfunctions/ + pages/ + 根 .js/.json
  python pipeline/gbk_scan.py 路径 ...   # 指定文件/目录
退出码 1 = 发现非 GBK 字符；0 = 全部通过。
"""
import os
import sys
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

DEFAULT_DIRS = [
    os.path.join(ROOT, "cloudfunctions"),
    os.path.join(ROOT, "pages"),
]
DEFAULT_ROOT_PATTERNS = ["*.js", "*.json", "*.wxml", "*.wxss"]
SKIP_DIRS = {"node_modules", "__pycache__", "miniprogram_npm", ".git"}


def target_files():
    files = []
    for d in DEFAULT_DIRS:
        for base, dirs, names in os.walk(d):
            dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
            for n in names:
                if n.endswith((".js", ".json", ".wxml", ".wxss")):
                    files.append(os.path.join(base, n))
    for pat in DEFAULT_ROOT_PATTERNS:
        for p in glob.glob(os.path.join(ROOT, pat)):
            files.append(p)
    return sorted(set(files))


def scan(path, limit=20):
    """返回非 GBK 字符的 (line, col, char) 列表（每文件最多 limit 条）。"""
    try:
        with open(path, "rb") as f:
            text = f.read().decode("utf-8", errors="replace")
    except Exception:
        return [(0, 0, "?")]
    bad = []
    line = 1
    col = 0
    for ch in text:
        if ch == "\n":
            line += 1
            col = 0
            continue
        col += 1
        if ch == "\ufffd":  # UTF-8 解码失败的替位符
            bad.append((line, col, "\\x??"))
            if len(bad) >= limit:
                break
            continue
        try:
            ch.encode("gbk")
        except Exception:
            bad.append((line, col, ch))
            if len(bad) >= limit:
                break
    return bad


def main():
    paths = sys.argv[1:] or target_files()
    total = 0
    for p in paths:
        if os.path.isdir(p):
            continue
        issues = scan(p)
        if issues:
            total += len(issues)
            rel = os.path.relpath(p, ROOT)
            print(f"[非GBK] {rel}")
            for line, col, ch in issues:
                print(f"    line {line}, col {col}: {ch!r}")
    if total:
        print(f"\n发现 {total} 处非 GBK 字符（已截断显示）。请改用 GBK 安全替代："
              f"指数用 ^、勾选 ●、箭头 →←＋·、括号 （）「」【】。")
        sys.exit(1)
    print("GBK 扫描通过：所有目标文件均为 GBK 安全。")


if __name__ == "__main__":
    main()
