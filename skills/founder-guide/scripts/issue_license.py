#!/usr/bin/env python3
"""一客一码：为商业授权买家生成唯一授权编号、授权书、成书版权页，并记入本地台账。

用法：
    # 单个买家
    python scripts/issue_license.py --buyer "张三" --order "TB-20261109001" \
        --books "01,46" --output ./licenses

    # 批量（CSV 表头：buyer,order,books）
    python scripts/issue_license.py --batch buyers.csv --output ./licenses

    # 把版权页追加到成书末尾，并嵌入零宽水印（可选）
    python scripts/issue_license.py --buyer "张三" --books all \
        --embed deliverables/final.md --output ./licenses

    # 从文本里读出零宽水印编号（验证溯源）
    python scripts/issue_license.py --decode deliverables/final.md

设计说明：
- 编号格式 FG-YYYYMMDD-XXXXXXXX，使用去掉易混字符（0/O/1/I）的 32 进制字母表，
  单日 32^8 组合，随机不可枚举。
- 台账 license-ledger.csv 默认与输出目录同级，只保存在本地，禁止提交到公开仓库。
- 零宽水印是弱溯源手段：可被专业工具剥离，只能作为授权编号之外的补充。
"""

import argparse
import csv
import hashlib
import secrets
import sys
from datetime import datetime
from pathlib import Path

ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"  # 32 个，去掉 0/O/1/I
ZW_MARK = "\u2060"   # 零宽标记，用于识别水印起点
ZW_ZERO = "\u200b"   # 0
ZW_ONE = "\u200c"    # 1

LICENSE_TEMPLATE = """# 「创业者指南」商业使用授权书

| 项目 | 内容 |
|---|---|
| 授权编号 | {code} |
| 被授权人 | {buyer} |
| 订单/渠道 | {order} |
| 授权日期 | {date} |
| 授权范围 | {books_desc} |
| 签发时间 | {issued_at} |

## 授权内容

作者 GodMaking（https://github.com/GodMaking/founder-guide-skill）特此授权上述被授权人，就授权范围内的成书享有个人使用权，可用于个人阅读、学习与内部参考。

## 使用限制

1. 不得转售、分销、再分发、公开传播本成书或其任何部分。
2. 不得将成书用于付费课程、付费社群、付费知识库或任何付费产品。
3. 不得删除、篡改本授权编号与成书版权页信息。
4. 不得将本授权转授、转让给第三方。

超出上述范围的使用，须另行取得书面商业授权。

## 正版核验

本授权编号与作者本地台账一一对应，作为真伪核验与来源追溯依据。如发现未授权转售，可凭编号向作者举报。

- 作者：GodMaking
- 仓库：https://github.com/GodMaking/founder-guide-skill
- 编号校验：本授权书内容 SHA-256 前 16 位 = {digest}
"""

COLOPHON_TEMPLATE = """---

**版权与授权**

- 出品：创业者指南（founder-guide）
- 授权编号：{code}
- 被授权人：{buyer}
- 授权范围：{books_desc}
- 正版核验：https://github.com/GodMaking/founder-guide-skill

本成书仅供上述被授权人个人使用，禁止转售、再分发或公开传播。
"""

LEDGER_HEADER = ["code", "buyer", "order", "books", "date", "issued_at", "sha256_16"]


def gen_code(day: str) -> str:
    body = "".join(secrets.choice(ALPHABET) for _ in range(8))
    return "FG-{}-{}".format(day.replace("-", ""), body)


def books_desc(books: str) -> str:
    raw = (books or "all").strip()
    if raw.lower() == "all":
        return "全部 46 本成书"
    items = [b.strip() for b in raw.replace("，", ",").split(",") if b.strip()]
    return "第 {} 本".format("、".join(items)) if items else "全部 46 本成书"


def encode_zero_width(text: str) -> str:
    bits = "".join(format(ord(ch), "08b") for ch in text)
    payload = "".join(ZW_ONE if b == "1" else ZW_ZERO for b in bits)
    return ZW_MARK + payload + ZW_MARK


def decode_zero_width(text: str) -> str:
    chunks = text.split(ZW_MARK)
    result = ""
    for chunk in chunks:
        clean = "".join(ch for ch in chunk if ch in (ZW_ZERO, ZW_ONE))
        if len(clean) < 8 or len(clean) % 8:
            continue
        chars = []
        for i in range(0, len(clean), 8):
            bits = "".join("1" if ch == ZW_ONE else "0" for ch in clean[i:i + 8])
            chars.append(chr(int(bits, 2)))
        text_value = "".join(chars)
        if text_value.startswith("FG-"):
            result = text_value
    return result


def issue_one(buyer: str, order: str, books: str, day: str, out_dir: Path, ledger: Path,
              embed: Path = None, quiet: bool = False) -> dict:
    code = gen_code(day)
    issued_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    desc = books_desc(books)

    license_text = LICENSE_TEMPLATE.format(
        code=code, buyer=buyer, order=order or "-", date=day,
        books_desc=desc, issued_at=issued_at, digest="__DIGEST__",
    )
    digest = hashlib.sha256(license_text.replace("__DIGEST__", "").encode("utf-8")).hexdigest()[:16]
    license_text = license_text.replace("__DIGEST__", digest)

    colophon = COLOPHON_TEMPLATE.format(code=code, buyer=buyer, books_desc=desc)

    out_dir.mkdir(parents=True, exist_ok=True)
    lic_path = out_dir / "授权书-{}.md".format(code)
    col_path = out_dir / "版权页-{}.md".format(code)
    lic_path.write_text(license_text, encoding="utf-8")
    col_path.write_text(colophon, encoding="utf-8")

    row = [code, buyer, order or "", books or "all", day, issued_at, digest]
    new_file = not ledger.exists()
    with ledger.open("a", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(LEDGER_HEADER)
        writer.writerow(row)

    if embed:
        if not embed.exists():
            raise FileNotFoundError("找不到要嵌入的成书文件：{}".format(embed))
        body = embed.read_text(encoding="utf-8")
        if code in body:
            raise RuntimeError("该成书已包含授权编号 {}，未重复嵌入".format(code))
        body = body.rstrip() + "\n\n" + colophon + "\n" + encode_zero_width(code) + "\n"
        embed.write_text(body, encoding="utf-8")

    if not quiet:
        print("授权编号 : {}".format(code))
        print("被授权人 : {}".format(buyer))
        print("授权范围 : {}".format(desc))
        print("授权书   : {}".format(lic_path))
        print("版权页   : {}".format(col_path))
        print("台账     : {}".format(ledger))
        if embed:
            print("已嵌入   : {}".format(embed))
    return {"code": code, "license": str(lic_path), "colophon": str(col_path)}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="创业者指南：一客一码授权生成")
    p.add_argument("--buyer", help="被授权人名称")
    p.add_argument("--order", default="", help="订单号或销售渠道，可选")
    p.add_argument("--books", default="all", help="授权范围：all 或逗号分隔的编号，如 01,46")
    p.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"), help="授权日期 YYYY-MM-DD")
    p.add_argument("--output", default="./licenses", help="授权书输出目录")
    p.add_argument("--ledger", default="", help="台账 CSV 路径，默认 <output>/license-ledger.csv")
    p.add_argument("--embed", default="", help="把版权页追加到该成书 md 末尾并嵌入零宽水印")
    p.add_argument("--batch", default="", help="批量 CSV（表头 buyer,order,books）")
    p.add_argument("--decode", default="", help="从文件读出零宽水印中的授权编号")
    args = p.parse_args(argv)

    if args.decode:
        text = Path(args.decode).read_text(encoding="utf-8")
        code = decode_zero_width(text)
        print(code if code else "未找到授权编号水印")
        return 0 if code else 2

    out_dir = Path(args.output)
    ledger = Path(args.ledger) if args.ledger else out_dir / "license-ledger.csv"

    if args.batch:
        batch = Path(args.batch)
        if not batch.exists():
            print("找不到批量文件：{}".format(batch), file=sys.stderr)
            return 2
        count = 0
        with batch.open(encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                buyer = (row.get("buyer") or "").strip()
                if not buyer:
                    continue
                issue_one(buyer, (row.get("order") or "").strip(),
                          (row.get("books") or "all").strip(),
                          args.date, out_dir, ledger, quiet=False)
                count += 1
        print("批量完成：{} 份".format(count))
        return 0

    if not args.buyer:
        p.print_help()
        return 2

    issue_one(args.buyer, args.order, args.books, args.date, out_dir, ledger,
              embed=Path(args.embed) if args.embed else None)
    return 0


if __name__ == "__main__":
    sys.exit(main())
