#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""创业判断速算器（纯标准库）

配套 references/judgment-framework.md 的三道闸门，把判断从"感觉"换成"数字"。

用法：
  python3 startup_calc.py value   --substitute-cost 3000 --my-cost 900
  python3 startup_calc.py unit    --price 199 --variable 80 --fixed 12000 --reach 500
  python3 startup_calc.py idiot   --part-cost 13000 --raw-cost 200
  python3 startup_calc.py gap     --current 1000000 --target 100
  python3 startup_calc.py runway  --cash 180000 --burn 30000 --lead-months 8
  python3 startup_calc.py all     --json payload.json

输出一律包含：算出的数字 + 判读 + 下一步动作。数字不带判读等于没算。
"""

import argparse
import json
import sys


def money(x):
    return "{:,.0f}".format(x)


def line(title):
    print("\n[{}]".format(title))


def verdict_value(substitute, mine):
    ratio = substitute / mine if mine > 0 else float("inf")
    line("有用性闸门")
    print("  替代方案成本 / 你的方案成本 = {} / {} = {:.2f} 倍".format(
        money(substitute), money(mine), ratio))
    if ratio >= 2:
        print("  判定：过。便宜一半以上，用户有换的动力")
        print("  动作：把这个倍数写进销售页的第一句，用来报价")
    elif ratio >= 1.3:
        print("  判定：边界。有优势但不足以让人换")
        print("  动作：再删一轮成本，或补一个替代方案做不到的差异点")
    else:
        print("  判定：不过。没有价值差，用户不会迁移")
        print("  动作：换问题、换人群，或改设计把成本压到替代方案的 1/3 以下")
    return ratio


def verdict_unit(price, variable, fixed, reach):
    line("单位经济")
    cm = price - variable
    if price <= 0:
        print("  单价必须大于 0")
        return None
    rate = cm / price
    print("  单位毛利 = {} - {} = {}".format(money(price), money(variable), money(cm)))
    print("  毛利率 = {:.1%}".format(rate))
    if cm <= 0:
        print("  判定：不过。卖一件亏一件，规模越大亏越多")
        print("  动作：先调价或调交付方式，不要靠融资撑")
        return cm
    be = fixed / cm
    print("  盈亏平衡量 = {} / {} = {:.0f} 件/月".format(money(fixed), money(cm), be))
    if reach:
        cover = reach / be if be > 0 else float("inf")
        print("  可触达客户 {:.0f} 件/月，覆盖盈亏平衡的 {:.1f} 倍".format(reach, cover))
        if cover >= 2:
            print("  判定：过。有安全垫")
        elif cover >= 1:
            print("  判定：边界。刚好打平，任何波动都会亏")
            print("  动作：把固定成本砍 30%，或把毛利率提高 5 个百分点")
        else:
            print("  判定：不过。触达客户数不足以覆盖固定成本")
            print("  动作：降固定成本、提单价，或换更大的客群")
    if rate < 0.3:
        print("  提醒：毛利率低于 30%，抗风险能力很弱，先修成本结构")
    return cm


def verdict_idiot(part, raw):
    line("白痴指数")
    if raw <= 0:
        print("  原材料成本必须大于 0")
        return None
    idx = part / raw
    print("  指数 = 成品 {} / 原材料 {} = {:.1f} 倍".format(money(part), money(raw), idx))
    if idx > 10:
        print("  判定：冗余严重。设计或工艺里塞了大量无效成本")
        print("  动作：先删部件、删工序，不要先谈砍价；砍价最多省 5%，删部件常省 30%")
    elif idx > 5:
        print("  判定：有明显空间")
        print("  动作：拆一遍成本构成，找出最贵的那道工序，问它为什么必须存在")
    elif idx > 2:
        print("  判定：合理区间，正常加工与利润在里面")
        print("  动作：别在这里死磕，把精力放到差距更大的部件上")
    else:
        print("  判定：已接近材料价，几乎没有压缩空间")
        print("  动作：要降成本只能换材料或换技术路线")
    return idx


def verdict_gap(current, target):
    line("目标差距")
    if target <= 0:
        print("  目标成本必须大于 0")
        return None
    gap = current / target
    print("  差距 = 当前 {} / 目标 {} = {:.1f} 倍".format(money(current), money(target), gap))
    if gap <= 2:
        print("  判定：优化能解决")
        print("  动作：走工程学五步法（质疑要求→删→简化→加速→自动化），先删再加")
    elif gap <= 10:
        print("  判定：要换设计或换工艺，靠调参数到不了")
        print("  动作：换结构、换材料、减部件数量，而不是把现有流程跑得更快")
    else:
        print("  判定：现有方案不成立")
        print("  动作：必须换技术路线或换商业模式；先在纸上确认物理上允许")
    return gap


def verdict_runway(cash, burn, lead_months):
    line("时间闸门")
    if burn <= 0:
        print("  月净流出必须大于 0，否则不适用该模型")
        return None
    months = cash / burn
    print("  runway = {} / {} = {:.1f} 个月".format(money(cash), money(burn), months))
    if months < 3:
        print("  判定：危险。少于 3 个月，任何计划都失去意义")
        print("  动作：本周内做三件事：停掉所有非交付支出、砍固定成本、找一笔立刻能到的钱")
    elif months < 6:
        print("  判定：紧张。只能做能在一个月内见到钱的动作")
    else:
        print("  判定：可执行。但成本要按两倍估，所以真实可用周期按 {} 个月算".format(
            int(months // 2)))
    if lead_months:
        ratio = lead_months / months
        print("  见效周期 {} 个月，占 runway 的 {:.0%}".format(lead_months, ratio))
        if ratio > 0.6:
            print("  判定：不过。等不到见效就先没钱了")
            print("  动作：先做一个 30 天内能收钱的小版本，或把见效周期砍掉一半")
        else:
            print("  判定：过。留有余量")
    return months


def verdict_all(payload):
    if "substitute_cost" in payload and "my_cost" in payload:
        verdict_value(payload["substitute_cost"], payload["my_cost"])
    if "price" in payload and "variable" in payload and "fixed" in payload:
        verdict_unit(payload["price"], payload["variable"],
                     payload["fixed"], payload.get("reach"))
    if "part_cost" in payload and "raw_cost" in payload:
        verdict_idiot(payload["part_cost"], payload["raw_cost"])
    if "current_cost" in payload and "target_cost" in payload:
        verdict_gap(payload["current_cost"], payload["target_cost"])
    if "cash" in payload and "burn" in payload:
        verdict_runway(payload["cash"], payload["burn"],
                       payload.get("lead_months"))
    print("\n把以上判读写进决策卡（assets/templates/decision-card.md），再决定做/验证/停。")


def main():
    ap = argparse.ArgumentParser(description="创业判断速算器")
    sub = ap.add_subparsers(dest="cmd")

    p1 = sub.add_parser("value", help="有用性闸门：价值倍数")
    p1.add_argument("--substitute-cost", type=float, required=True)
    p1.add_argument("--my-cost", type=float, required=True)

    p2 = sub.add_parser("unit", help="单位经济与盈亏平衡")
    p2.add_argument("--price", type=float, required=True)
    p2.add_argument("--variable", type=float, required=True)
    p2.add_argument("--fixed", type=float, required=True)
    p2.add_argument("--reach", type=float, default=None)

    p3 = sub.add_parser("idiot", help="白痴指数")
    p3.add_argument("--part-cost", type=float, required=True)
    p3.add_argument("--raw-cost", type=float, required=True)

    p4 = sub.add_parser("gap", help="目标差距倍数")
    p4.add_argument("--current", type=float, required=True)
    p4.add_argument("--target", type=float, required=True)

    p5 = sub.add_parser("runway", help="现金 runway 与见效周期")
    p5.add_argument("--cash", type=float, required=True)
    p5.add_argument("--burn", type=float, required=True)
    p5.add_argument("--lead-months", type=float, default=None)

    p6 = sub.add_parser("all", help="从 JSON 一次性算多项")
    p6.add_argument("--json", required=True)

    args = ap.parse_args()

    if args.cmd == "value":
        verdict_value(args.substitute_cost, args.my_cost)
    elif args.cmd == "unit":
        verdict_unit(args.price, args.variable, args.fixed, args.reach)
    elif args.cmd == "idiot":
        verdict_idiot(args.part_cost, args.raw_cost)
    elif args.cmd == "gap":
        verdict_gap(args.current, args.target)
    elif args.cmd == "runway":
        verdict_runway(args.cash, args.burn, args.lead_months)
    elif args.cmd == "all":
        payload = json.load(open(args.json, encoding="utf-8"))
        verdict_all(payload)
    else:
        ap.print_help()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
