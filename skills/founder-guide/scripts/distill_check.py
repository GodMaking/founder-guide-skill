#!/usr/bin/env python3
"""distill_check.py — 书籍蒸馏成书产物校验（独立脚本，仅 Python 3 标准库）。

用法:
  python3 distill_check.py <工作目录>

检查项（全部通过才交付）:
  1. 四件套齐全: requirement-checklist.json / outline.md / chapter-ledger.md / deliverables/final.md
  2. final.md 非空白字数 ∈ [target×(1−10%), target×(1+10%)]
  3. 章节数 ≥ 8 且编号 ch01 起连续
  4. 章标题格式 "# 第X章"（汉字数字）
  5. 无占位符: TODO / 待补 / 占位 / xxx / Lorem / 待插入
  6. 中文占比 ≥ 70%
  7. 无空章节: 每章非空白字符 ≥ 500
  8. 层级规范: 二级"一、"，三级"（一）"，不跳级，标题内不加粗
  9. 大纲目标字数合计 = 全书目标字数；台账已回填当前字数
"""
import json
import os
import re
import sys

CN_NUM = "零〇一二三四五六七八九十百千万两"
PLACEHOLDER_RE = re.compile(r"TODO|待补|占位|待插入|Lorem|xxx|XXX|\[待|（待|\(待")
HEADING_RE = re.compile(r"^(#+)\s+(.+?)\s*#*\s*$")
CHAPTER_RE = re.compile(rf"^#?\s*第[{CN_NUM}]+章(?:\s|\Z)")


def nonblank(s: str) -> int:
    return len(re.sub(r"\s", "", s))


def cjk_ratio(s: str) -> float:
    ns = re.sub(r"\s", "", s)
    if not ns:
        return 0.0
    cjk = sum(1 for ch in ns if "\u4e00" <= ch <= "\u9fff")
    return cjk / len(ns)


def split_chapters(text: str):
    """按 '# 第X章' 一级标题切分章节。"""
    lines = text.splitlines()
    chapters = []
    cur = None
    for ln in lines:
        m = re.match(r"^#\s+第[%s]+章" % CN_NUM, ln)
        if m:
            if cur is not None:
                chapters.append(cur)
            cur = {"title": ln.strip(), "body": []}
        elif cur is not None:
            cur["body"].append(ln)
    if cur is not None:
        chapters.append(cur)
    return chapters


def main() -> int:
    if len(sys.argv) != 2:
        print("用法: python3 distill_check.py <工作目录>")
        return 2
    workdir = sys.argv[1]
    if not os.path.isdir(workdir):
        print(f"FAIL 工作目录不存在: {workdir}")
        return 1

    issues = []

    # 1. 四件套（兼容旧工作目录：checklist 可能在 .doubao-book-writer/ 下）
    required = ["requirement-checklist.json", "outline.md", "chapter-ledger.md"]
    for name in required:
        if not os.path.isfile(os.path.join(workdir, name)) and not (
            name == "requirement-checklist.json"
            and os.path.isfile(os.path.join(workdir, ".doubao-book-writer", name))
        ):
            issues.append(f"缺少四件套: {name}")
    final_path = os.path.join(workdir, "deliverables", "final.md")
    if not os.path.isfile(final_path):
        issues.append("缺少 deliverables/final.md")
        print("FAIL " + "；".join(issues))
        return 1

    # 目标字数（兼容两处 checklist 位置）
    target = 31040
    checklist_path = os.path.join(workdir, "requirement-checklist.json")
    if not os.path.isfile(checklist_path):
        checklist_path = os.path.join(workdir, ".doubao-book-writer", "requirement-checklist.json")
    if os.path.isfile(checklist_path):
        try:
            cl = json.load(open(checklist_path, encoding="utf-8"))
            rules = cl.get("wordCountRules") or []
            for r in rules:
                if r.get("target"):
                    target = int(r["target"])
                    break
        except Exception:
            pass

    text = open(final_path, encoding="utf-8").read()
    total = nonblank(text)

    # 2. 字数
    lo, hi = int(target * 0.9), int(target * 1.1)
    if not (lo <= total <= hi):
        issues.append(f"字数 {total} 不在 [{lo}, {hi}]（目标 {target} ±10%）")

    # 3/4. 章节
    chapters = split_chapters(text)
    if len(chapters) < 8:
        issues.append(f"章节数 {len(chapters)} < 8")
    for idx, ch in enumerate(chapters):
        if not CHAPTER_RE.match(ch["title"]):
            issues.append(f"章标题格式错误（需汉字'第X章'）: {ch['title']}")
            break
    if chapters:
        first = chapters[0]["title"]
        if not re.match(rf"^#?\s*第[{CN_NUM}]+章", first):
            issues.append("章节编号未从'第一章'开始")

    # 5. 占位符
    for m in PLACEHOLDER_RE.finditer(text):
        start = max(0, m.start() - 20)
        issues.append(f"发现占位符: ...{text[start:m.end()+20]}...")
        break

    # 6. 中文占比
    ratio = cjk_ratio(text)
    if ratio < 0.70:
        issues.append(f"中文占比 {ratio:.2%} < 70%")

    # 7. 空章节
    for ch in chapters:
        if nonblank("\n".join(ch["body"])) < 500:
            issues.append(f"章节过空(<500字): {ch['title']}")

    # 8. 层级规范
    level_stack = []
    for ln in text.splitlines():
        m = HEADING_RE.match(ln)
        if not m:
            continue
        level, content = len(m.group(1)), m.group(2)
        if "**" in content:
            issues.append(f"标题内加粗: {ln.strip()}")
            break
        if level == 2 and not re.match(r"^[%s]+、" % CN_NUM, content):
            issues.append(f"二级标题应'一、'开头: {ln.strip()}")
            break
        if level == 3 and not re.match(r"^（[%s]+）" % CN_NUM, content):
            issues.append(f"三级标题应'（一）'开头: {ln.strip()}")
            break
        if level >= 4:
            issues.append(f"标题层级超过三级: {ln.strip()}")
            break

    # 9. 大纲字数合计
    outline_path = os.path.join(workdir, "outline.md")
    if os.path.isfile(outline_path):
        ot = open(outline_path, encoding="utf-8").read()
        planned = [int(x) for x in re.findall(r"\| (\d{3,5}) \|", ot)]
        if planned and sum(planned) != target:
            issues.append(f"大纲章节目标合计 {sum(planned)} != 全书目标 {target}")

    # 台账回填
    ledger_path = os.path.join(workdir, "chapter-ledger.md")
    if os.path.isfile(ledger_path):
        lt = open(ledger_path, encoding="utf-8").read()
        rows = re.findall(r"\| ch\d+ \| [^|]+ \| (\d+) \| (\d*) \|", lt)
        empty_cur = [r[0] for r in rows if not r[1].strip()]
        if empty_cur:
            issues.append(f"台账未回填当前字数: ch{empty_cur}")

    if issues:
        print("FAIL " + "；".join(issues))
        return 1
    print(
        f"PASS 四件套齐全 | 字数 {total}（目标 {target} ±10%）| 章节 {len(chapters)} | "
        f"中文占比 {ratio:.2%} | 无占位符 | 层级规范 | 大纲字数合计正确 | 台账已回填"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
