#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一客一码：签发个人商业使用授权书、交付物版权页，并记入本地台账。

定位：
- 免费版：PolyForm Noncommercial 1.0.0，个人非商业学习、研究、试验免费。
- 商业版：本脚本为已付款的买家签发「个人商业使用授权」，不是技术锁，也不联网。

常用命令（在仓库根目录运行）：
    # 预生成 50 个授权编号，用于闲鱼自动发货
    python3 skills/founder-guide/scripts/issue_license.py --gen-codes 50 --output ./licenses

    # 用预生成的编号为买家签发授权书
    python3 skills/founder-guide/scripts/issue_license.py --buyer "闲鱼昵称" \
        --order "订单号" --code FG-20261113-XXXXXXXX --product skill --output ./licenses

    # 不预先取号，直接生成编号并签发
    python3 skills/founder-guide/scripts/issue_license.py --buyer "闲鱼昵称" \
        --order "订单号" --product skill --output ./licenses

    # 批量签发（CSV 表头：buyer,order,product,books,code）
    python3 skills/founder-guide/scripts/issue_license.py --batch buyers.csv --output ./licenses

    # 把授权摘要追加到交付物末尾，并嵌入零宽水印
    python3 skills/founder-guide/scripts/issue_license.py --buyer "闲鱼昵称" \
        --order "订单号" --product books --books "01,47" \
        --embed deliverables/final.md --output ./licenses

    # 从交付物读出水印中的授权编号
    python3 skills/founder-guide/scripts/issue_license.py --decode deliverables/final.md

    # 校验授权书摘要（防文本改动，不是数字签名）
    python3 skills/founder-guide/scripts/issue_license.py --verify licenses/授权书-FG-....md

设计说明：
- 编号格式 FG-YYYYMMDD-XXXXXXXX，32 进制字母表去掉易混字符 0/O/1/I。
- 台账 license-ledger.csv 默认保存在输出目录，只在本机使用，禁止提交公开仓库。
- 零宽水印是弱溯源手段，可被专业工具剥离；它不联网，也不采集任何信息。
- 授权书摘要用于发现文本被改动，不构成技术锁、数字签名或绝对权属证明。
"""

import argparse
import csv
import hashlib
import json
import re
import secrets
import sys
from datetime import datetime
from pathlib import Path

ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"  # 32 个，去掉 0/O/1/I
CODE_RE = re.compile(r"^FG-\d{8}-[2-9A-HJ-NP-Z]{8}$")
ZW_MARK = "\u2060"   # 零宽标记，用于识别水印起点
ZW_ZERO = "\u200b"   # 0
ZW_ONE = "\u200c"    # 1

SKILL_DIR = Path(__file__).resolve().parents[1]
BOOK_INDEX = SKILL_DIR / "assets" / "samples" / "books_index.json"

LICENSE_TEMPLATE = """# 「创业者指南」个人商业使用授权书

| 项目 | 内容 |
|---|---|
| 授权编号 | {code} |
| 授权类型 | 个人商业使用授权（Personal Commercial License） |
| 被授权人 | {buyer} |
| 订单/渠道 | {order} |
| 授权日期 | {date} |
| 授权标的 | {product_desc} |
| 授权范围 | {scope_desc} |
| 授权期限 | {term} |
| 适用版本 | 购买时最新公开版本（以仓库提交记录为准） |
| 签发时间 | {issued_at} |

## 授权内容

作者 GodMaking（https://github.com/GodMaking/founder-guide-skill）授予上述被授权人一项非独占、不可转让、不可再许可的个人商业使用授权：

1. {usage_clause}
2. 被授权人可使用基于授权标的生成的决策卡、计算结果、报告与内部文档。
3. 被授权人可为备份目的保留合理数量的副本，但不得向第三方提供。

## 使用限制

1. 不得转售、分销、再分发、公开传播、出租、出借授权标的或其任何修改版本。
2. 不得将授权标的用于付费课程、付费社群、付费知识库、付费代做服务，或打包进任何向第三方收费的产品/服务。
3. 不得将授权标的集成进对外销售或对外提供的软件、SaaS、工具站、课程、模板包。
4. 不得转授权、转让、共享给其他个人、团队或企业；多人/企业使用须另行取得书面授权。
5. 不得删除、篡改授权编号、版权页、LICENSE 或 Required Notice。
6. 不得以作者名义宣传，或声称获得超出本授权书的权利。
7. 不得将授权标的用于违法、侵权或违反平台规则的活动。

## 原书版权说明

本授权仅覆盖 Skill 软件及作者原创的模板、文档与代码，不授予任何原书正文、原书成书、译本或衍生内容的公开传播权、出版权或商业发行权。涉及蒸馏成书时，原书著作权仍归原作者与出版方；被授权人公开传播或商业发行成书，须自行取得原书权利人的授权。

## 授权期限与更新

- 授权期限：{term}
- 版本更新：按购买时订单页/交付说明载明的更新范围提供；未载明的，不承诺无限期更新。
- 授权终止：被授权人违反上述限制时，作者可书面通知终止授权；终止后不得继续商业使用。

## 正版核验

- 本授权编号与作者本地台账一一对应，可用于真伪核验与来源追溯。
- 授权书摘要：本授权书内容 SHA-256 前 16 位 = {digest}。摘要用于发现文本被改动，不是数字签名，也不构成绝对权属证明。
- 核验方式：在 GitHub 仓库开 Issue（标题：`授权核验`），提供授权编号与订单号；作者核对本地台账后回复。请勿在公开 Issue 中提交身份证、住址、电话等敏感信息。
- 维权说明：授权编号不是技术锁；公开源码无法在技术上阻止复制。发现未授权商业转售时，作者可凭编号、仓库提交记录与对比证据向平台投诉或依法维权。

## 隐私说明

作者仅在本机台账记录被授权人提供的昵称/名称、订单号、授权日期、授权标的与授权范围，用于签发、核验与维权；不联网上传，不采集身份证、住址、电话、支付信息等额外个人信息。被授权人可使用昵称，无需提供真实姓名。

## 免责声明

授权标的按现状提供。作者不承诺特定商业结果、安装成功率或收益；除法律强制规定外，作者不对被授权人使用授权标的产生的间接损失承担责任。被授权人应自行评估其项目、市场与合规风险。

## 其他

- 本授权书不构成法律意见。
- 本授权书与仓库 LICENSE（PolyForm Noncommercial 1.0.0）并行：非商业用途仍按 LICENSE 免费授权；本授权书仅补充商业使用权利，不削减任何人依 LICENSE 享有的非商业权利。
- 本授权书未尽事项，以作者与被授权人另行书面约定为准。
"""

NOTICE_TEMPLATE = """---

**版权与授权**

- 出品：创业者指南（founder-guide）
- 授权编号：{code}
- 被授权人：{buyer}
- 授权类型：个人商业使用授权
- 授权标的：{product_short}
- 授权范围：{scope_short}
- 正版核验：https://github.com/GodMaking/founder-guide-skill

本交付物仅限上述被授权人在其本人经营项目中使用，禁止转售、再分发、公开传播或转授权。原书著作权归原作者与出版方，本授权不授予原书公开传播权。
"""

PRODUCTS = {
    "skill": "founder-guide Skill 软件（代码、模板、参考文档与脚本）",
    "books": "指定成书（蒸馏产物）",
    "bundle": "founder-guide Skill 软件 + 指定成书",
}

LEDGER_HEADER = [
    "code", "buyer", "order", "books", "date", "issued_at", "sha256_16",
    "type", "product", "term",
]
OLD_LEDGER_HEADER = ["code", "buyer", "order", "books", "date", "issued_at", "sha256_16"]


def gen_code(day: str) -> str:
    body = "".join(secrets.choice(ALPHABET) for _ in range(8))
    return "FG-{}-{}".format(day.replace("-", ""), body)


def load_book_stats():
    """返回（书目编号数，去重书名数）。读不到索引时退回 47/46。"""
    try:
        data = json.loads(BOOK_INDEX.read_text(encoding="utf-8"))
        titles = {
            str(v.get("书名") or key.split("-", 1)[-1]).strip()
            for key, v in data.items()
        }
        return len(data), len(titles)
    except Exception:
        return 47, 46


def books_desc(books: str) -> str:
    total_entries, total_titles = load_book_stats()
    if total_entries == total_titles:
        all_text = "全部 {} 本书".format(total_entries)
    else:
        all_text = "全部 {} 个书目编号（去重 {} 本）".format(total_entries, total_titles)

    raw = (books or "all").strip()
    if raw.lower() == "all":
        return all_text
    items = [b.strip() for b in raw.replace("，", ",").split(",") if b.strip()]
    if not items:
        return all_text
    return "指定书目编号：{}（共 {} 个）".format("、".join(items), len(items))


def product_and_scope(product: str, books: str):
    if product == "skill":
        return (
            PRODUCTS["skill"],
            "被授权人本人在其经营项目中的商业使用（不含转售、分销、代做、付费课程/社群/产品集成与多人/企业使用）",
            "founder-guide Skill 软件",
            "本人经营项目中的商业使用",
            "被授权人可在其本人经营的项目中安装、运行、修改和使用授权标的，用于自身的商业分析、经营决策与内部交付。",
        )
    book_scope = books_desc(books)
    if product == "books":
        return (
            "{}：{}".format(PRODUCTS["books"], book_scope),
            "指定成书在本人经营项目中的内部使用（不含公开传播、出版、转售、再分发）",
            "指定成书",
            "本人经营项目中的内部使用",
            "被授权人可在其本人经营的项目中阅读、引用和使用授权标的，用于自身的商业分析、经营决策与内部交付；不得公开传播、出版或再分发。",
        )
    return (
        "{}：{}".format(PRODUCTS["bundle"], book_scope),
        "Skill 软件与指定成书在本人经营项目中的商业使用（不含转售、分销、代做、付费课程/社群/产品集成与多人/企业使用）",
        "Skill 软件 + 指定成书",
        "本人经营项目中的商业使用",
        "被授权人可在其本人经营的项目中安装、运行、修改和使用 Skill 软件，并阅读、引用和使用指定成书，用于自身的商业分析、经营决策与内部交付；不得公开传播、出版或再分发。",
    )


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


def ensure_ledger(ledger: Path) -> None:
    """建立台账；旧版 7 列表头会原地迁移为 10 列，保留已有行。"""
    if not ledger.exists():
        ledger.parent.mkdir(parents=True, exist_ok=True)
        with ledger.open("w", encoding="utf-8-sig", newline="") as f:
            csv.writer(f).writerow(LEDGER_HEADER)
        return

    with ledger.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    if not rows:
        with ledger.open("w", encoding="utf-8-sig", newline="") as f:
            csv.writer(f).writerow(LEDGER_HEADER)
        return

    header = rows[0]
    if header == LEDGER_HEADER:
        return
    if header == OLD_LEDGER_HEADER:
        migrated = [LEDGER_HEADER]
        for row in rows[1:]:
            padded = row + [""] * (len(LEDGER_HEADER) - len(row))
            migrated.append(padded[:len(LEDGER_HEADER)])
        with ledger.open("w", encoding="utf-8-sig", newline="") as f:
            csv.writer(f).writerows(migrated)
        return
    raise RuntimeError(
        "台账表头与当前版本不一致，请先备份并移走旧台账：{}".format(ledger)
    )


def ledger_codes(ledger: Path) -> set:
    if not ledger.exists():
        return set()
    with ledger.open(encoding="utf-8-sig", newline="") as f:
        return {(row.get("code") or "").strip() for row in csv.DictReader(f)}


def issue_one(buyer: str, order: str, books: str, day: str, out_dir: Path, ledger: Path,
              embed: Path = None, quiet: bool = False, product: str = "skill",
              code: str = None, term: str = "永久（限所购版本）") -> dict:
    if product not in PRODUCTS:
        raise ValueError("product 只能是 skill / books / bundle")
    buyer = (buyer or "").strip()
    if not buyer:
        raise ValueError("被授权人不能为空；可使用昵称")

    code = (code or gen_code(day)).strip().upper()
    if not CODE_RE.match(code):
        raise ValueError("授权编号格式不正确：{}（应形如 FG-20261113-XXXXXXXX）".format(code))
    if code in ledger_codes(ledger):
        raise RuntimeError("授权编号已存在，未重复签发：{}".format(code))

    issued_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    product_desc, scope_desc, product_short, scope_short, usage_clause = product_and_scope(product, books)

    license_text = LICENSE_TEMPLATE.format(
        code=code, buyer=buyer, order=order or "-", date=day,
        product_desc=product_desc, scope_desc=scope_desc, term=term,
        usage_clause=usage_clause, issued_at=issued_at, digest="__DIGEST__",
    )
    digest = hashlib.sha256(license_text.replace("__DIGEST__", "").encode("utf-8")).hexdigest()[:16]
    license_text = license_text.replace("__DIGEST__", digest)

    notice = NOTICE_TEMPLATE.format(
        code=code, buyer=buyer, product_short=product_short, scope_short=scope_short,
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    lic_path = out_dir / "授权书-{}.md".format(code)
    notice_path = out_dir / "版权页-{}.md".format(code)
    lic_path.write_text(license_text, encoding="utf-8")
    notice_path.write_text(notice, encoding="utf-8")

    row = [
        code, buyer, order or "", "" if product == "skill" else (books or "all"),
        day, issued_at, digest, "personal-commercial", product, term,
    ]
    with ledger.open("a", encoding="utf-8", newline="") as f:
        csv.writer(f).writerow(row)

    if embed:
        if not embed.exists():
            raise FileNotFoundError("找不到要嵌入的交付物：{}".format(embed))
        body = embed.read_text(encoding="utf-8")
        if code in body:
            raise RuntimeError("该交付物已包含授权编号 {}，未重复嵌入".format(code))
        body = body.rstrip() + "\n\n" + notice + "\n" + encode_zero_width(code) + "\n"
        embed.write_text(body, encoding="utf-8")

    if not quiet:
        print("授权编号 : {}".format(code))
        print("被授权人 : {}".format(buyer))
        print("授权标的 : {}".format(product_desc))
        print("授权范围 : {}".format(scope_desc))
        print("授权书   : {}".format(lic_path))
        print("版权页   : {}".format(notice_path))
        print("台账     : {}".format(ledger))
        if embed:
            print("已嵌入   : {}".format(embed))
    return {"code": code, "license": str(lic_path), "notice": str(notice_path)}


def generate_codes(count: int, day: str, out_dir: Path) -> int:
    if count < 1:
        print("--gen-codes 必须大于 0", file=sys.stderr)
        return 2
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "codes-{}.csv".format(day.replace("-", ""))
    if path.exists():
        print("编号文件已存在，拒绝覆盖：{}".format(path), file=sys.stderr)
        return 2

    existing = set()
    ledger = out_dir / "license-ledger.csv"
    if ledger.exists():
        existing |= ledger_codes(ledger)

    codes = set()
    while len(codes) < count:
        c = gen_code(day)
        if c not in existing:
            codes.add(c)

    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["code", "date", "status"])
        for c in sorted(codes):
            writer.writerow([c, day, "unused"])
    print("已生成 {} 个授权编号：{}".format(count, path))
    print("下一步：把编号逐条上传到平台自动发货；买家下单后再用 --code 签发授权书。")
    return 0


def verify_license(path: Path) -> int:
    if not path.exists():
        print("找不到授权书：{}".format(path), file=sys.stderr)
        return 2
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r"(SHA-256 前 16 位 = )([0-9a-f]{16})")
    m = pattern.search(text)
    if not m:
        print("FAIL 未找到授权书摘要")
        return 1
    digest = m.group(2)
    calc = hashlib.sha256(pattern.sub(r"\1", text, count=1).encode("utf-8")).hexdigest()[:16]
    if calc == digest:
        print("PASS 摘要匹配：{}".format(digest))
        return 0
    print("FAIL 摘要不匹配：文件可能被改动（记录 {}，实算 {}）".format(digest, calc))
    return 1


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="创业者指南：一客一码商业授权签发")
    p.add_argument("--buyer", help="被授权人名称或昵称；可使用昵称，无需真实姓名")
    p.add_argument("--order", default="", help="订单号或销售渠道，可选")
    p.add_argument("--product", choices=sorted(PRODUCTS), default="skill",
                   help="授权标的：skill=仅 Skill 软件，books=指定成书，bundle=两者")
    p.add_argument("--books", default="all", help="成书范围：all 或逗号分隔的编号，如 01,47")
    p.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"), help="授权日期 YYYY-MM-DD")
    p.add_argument("--term", default="永久（限所购版本）", help="授权期限，默认：永久（限所购版本）")
    p.add_argument("--code", default="", help="使用预生成的授权编号；不填则自动生成")
    p.add_argument("--output", default="./licenses", help="授权书输出目录")
    p.add_argument("--ledger", default="", help="台账 CSV 路径，默认 <output>/license-ledger.csv")
    p.add_argument("--embed", default="", help="把版权页追加到该交付物末尾并嵌入零宽水印")
    p.add_argument("--batch", default="", help="批量 CSV（表头 buyer,order,product,books,code）")
    p.add_argument("--gen-codes", type=int, default=0, help="预生成 N 个授权编号并输出 CSV")
    p.add_argument("--decode", default="", help="从文件读出水印中的授权编号")
    p.add_argument("--verify", default="", help="校验授权书摘要是否与内容匹配")
    args = p.parse_args(argv)

    if args.decode:
        text = Path(args.decode).read_text(encoding="utf-8")
        code = decode_zero_width(text)
        print(code if code else "未找到授权编号水印")
        return 0 if code else 2

    if args.verify:
        return verify_license(Path(args.verify))

    out_dir = Path(args.output)
    if args.gen_codes:
        return generate_codes(args.gen_codes, args.date, out_dir)

    ledger = Path(args.ledger) if args.ledger else out_dir / "license-ledger.csv"
    try:
        ensure_ledger(ledger)
    except Exception as exc:
        print("台账检查失败：{}".format(exc), file=sys.stderr)
        return 2

    if args.batch:
        batch = Path(args.batch)
        if not batch.exists():
            print("找不到批量文件：{}".format(batch), file=sys.stderr)
            return 2
        count, errors = 0, []
        with batch.open(encoding="utf-8-sig", newline="") as f:
            for line_no, row in enumerate(csv.DictReader(f), 2):
                buyer = (row.get("buyer") or "").strip()
                if not buyer:
                    continue
                product = (row.get("product") or "skill").strip() or "skill"
                try:
                    issue_one(
                        buyer, (row.get("order") or "").strip(),
                        (row.get("books") or "all").strip(),
                        args.date, out_dir, ledger, quiet=False,
                        product=product, code=(row.get("code") or "").strip() or None,
                        term=args.term,
                    )
                    count += 1
                except Exception as exc:
                    errors.append("第 {} 行 {}：{}".format(line_no, buyer, exc))
        print("批量完成：成功 {} 份，失败 {} 份".format(count, len(errors)))
        for err in errors:
            print("  失败：{}".format(err), file=sys.stderr)
        return 1 if errors else 0

    if not args.buyer:
        p.print_help()
        return 2

    try:
        issue_one(
            args.buyer, args.order, args.books, args.date, out_dir, ledger,
            embed=Path(args.embed) if args.embed else None,
            product=args.product, code=args.code or None, term=args.term,
        )
    except Exception as exc:
        print("签发失败：{}".format(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
