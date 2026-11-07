#!/usr/bin/env python3
"""make_workspace.py — 初始化书籍蒸馏工作目录四件套。

用法:
  python3 make_workspace.py "<书名>" --output <父目录> [--target-words 31040] [--chapters 16]

从 assets/templates/ 复制模板并生成:
  NN-书名/requirement-checklist.json
  NN-书名/outline.md
  NN-书名/chapter-ledger.md
  NN-书名/manuscript/   (占位目录)
  NN-书名/deliverables/
"""
import argparse
import json
import os
import re
import shutil
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(SKILL_DIR, "assets", "templates")


def next_number(parent: str) -> int:
    """扫描父目录已有 NN- 前缀，返回下一个编号。"""
    nums = []
    if os.path.isdir(parent):
        for name in os.listdir(parent):
            m = re.match(r"^(\d{2})-", name)
            if m:
                nums.append(int(m.group(1)))
    return (max(nums) + 1) if nums else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("title", help="书名，如 影响力")
    ap.add_argument("--output", required=True, help="父目录，工作目录建在其下")
    ap.add_argument("--target-words", type=int, default=31040, help="全书目标字数（非空白字符）")
    ap.add_argument("--chapters", type=int, default=16, help="章节数")
    args = ap.parse_args()

    if not os.path.isdir(TEMPLATE_DIR):
        print(f"模板目录不存在: {TEMPLATE_DIR}")
        return 2

    n = next_number(args.output)
    workdir = os.path.join(args.output, f"{n:02d}-{args.title}")
    if os.path.exists(workdir):
        print(f"工作目录已存在，拒绝覆盖: {workdir}")
        return 2

    per = args.target_words // args.chapters
    os.makedirs(os.path.join(workdir, "manuscript"), exist_ok=True)
    os.makedirs(os.path.join(workdir, "deliverables"), exist_ok=True)

    # ---- requirement-checklist.json ----
    checklist = {
        "topic": f"将《{args.title}》蒸馏成约3万字中文成书，忠实转述原书核心内容、关键观点与表达逻辑",
        "contentProfile": {
            "id": "general",
            "genreGuide": "general",
            "audience": "想快速掌握《{0}》核心内容的读者".format(args.title),
            "purpose": "蒸馏成书，交付本地Markdown成书与原书PDF",
        },
        "structureRules": {"headingPolicy": "chinese-publication", "maxContentFilesPerBatch": 2},
        "sourcePolicy": {"mode": "user-materials-only", "minimumDirections": 3, "requireGapReview": True},
        "sourceInputs": [{"id": "source-book", "kind": "pdf", "path": "book.pdf", "writePolicy": "read-only"}],
        "delivery": {
            "mode": "markdown-only",
            "userExplicitlyRequested": True,
            "requestEvidence": "用户要求把书蒸馏成约3万字成书，落盘本地并交付",
            "requireReadBack": False,
        },
        "requirements": [
            {"id": "R1", "requirement": f"产出约3万字中文成书Markdown，与原书PDF一同交付", "priority": "main", "in_scope": "yes", "carrier": "final.md与交付链", "resolution": ""},
            {"id": "R2", "requirement": "忠实转述原书核心内容与关键原句，不虚构不发挥", "priority": "main", "in_scope": "yes", "carrier": "各章正文与must-contain校验", "resolution": ""},
            {"id": "R3", "requirement": f"全书目标字数{args.target_words}（±10%），{args.chapters}章各{per}字", "priority": "main", "in_scope": "yes", "carrier": "wordCountRules与chapter-ledger", "resolution": ""},
            {"id": "R4", "requirement": "正文去AI味，少连接词与模板句，自然具体", "priority": "main", "in_scope": "yes", "carrier": "正文修订与校验", "resolution": ""},
            {"id": "R5", "requirement": "交付本地final.md与book.pdf，按用户要求上传云盘", "priority": "main", "in_scope": "yes", "carrier": "交付链", "resolution": ""},
        ],
        "wordCountRules": [{"id": "total-length", "target": args.target_words, "tolerancePercent": 10}],
    }
    with open(os.path.join(workdir, "requirement-checklist.json"), "w", encoding="utf-8") as f:
        json.dump(checklist, f, ensure_ascii=False, indent=2)

    # ---- outline.md ----
    rows = []
    for i in range(1, args.chapters + 1):
        words = per if i < args.chapters else args.target_words - per * (args.chapters - 1)
        rows.append(f"| ch{i:02d} | 第{i}章标题待定 | 本章核心问题 | 本章用户收获 | {words} |")
    table = "\n".join(rows)
    deps = "\n".join(
        f"| ch{i:02d} | {'无' if i == 1 else 'ch' + format(i-1, '02d')} |" for i in range(1, args.chapters + 1)
    )
    outline = f"""# 全书大纲：{args.title}（蒸馏成书）

## 核心主张

（待填：全书要传达的核心主张，成书将如何组织）

## 目标读者

（待填：谁在读、带着什么任务读）

## 语气

（待填：平实/温暖/具体，保留原书表达气质）

## 章节规划

| 章节 | 标题 | 核心问题 | 用户收获 | 目标字数 |
|------|------|----------|----------|----------|
{table}

## 章节依赖关系

| 章节 | 前置章节 |
|------|----------|
{deps}

## 总字数目标

全书目标 {args.target_words} 字（非空白字符），{args.chapters} 章，上下限 {int(args.target_words*0.9)}–{int(args.target_words*1.1)}。
"""
    with open(os.path.join(workdir, "outline.md"), "w", encoding="utf-8") as f:
        f.write(outline)

    # ---- chapter-ledger.md ----
    ledger = [f"| ch{i:02d} | 第{i}章标题待定 | {per if i < args.chapters else args.target_words - per * (args.chapters - 1)} |  |" for i in range(1, args.chapters + 1)]
    with open(os.path.join(workdir, "chapter-ledger.md"), "w", encoding="utf-8") as f:
        f.write("# 章节台账\n\n| 章节 | 标题 | 目标字数 | 当前字数 |\n|------|------|----------|----------|\n" + "\n".join(ledger) + "\n")

    print(f"已创建: {workdir}")
    print(f"四件套: requirement-checklist.json / outline.md / chapter-ledger.md / manuscript+deliverables")
    print(f"下一步: 通读 full_text.txt → 填 outline 章节标题与核心问题 → 逐章成稿 → 合并 final.md → 运行 distill_check.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
