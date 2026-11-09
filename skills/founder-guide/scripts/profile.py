#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""创业档案 startup-profile.json 的读写与完整度检查（纯标准库）

带人创业靠的是连续，不是每轮重问。档案落盘后，每轮只更新变化的那几个字段。

用法：
  python3 profile.py init  --path ./startup-profile.json --name "项目名"
  python3 profile.py set   --path ./startup-profile.json model=content stage=S1 facts.cash=50000
  python3 profile.py check --path ./startup-profile.json
  python3 profile.py log   --path ./startup-profile.json --verdict 验证 --basis "替代方案成本待核实" --prediction "7天内1单预付"
  python3 profile.py show  --path ./startup-profile.json
"""

import argparse
import datetime
import json
import os
import sys

MODELS = {
    "content": "内容/知识付费",
    "saas": "软件/SaaS",
    "store": "实体门店",
    "hardware": "制造/硬件",
    "service": "服务/咨询",
    "unknown": "未判定",
}

STAGES = ["S0", "S1", "S2", "S3", "S4", "S5"]

TEMPLATE = {
    "project": {"name": "", "one_liner": "", "model": "unknown", "stage": "S0"},
    "facts": {
        "substitute_cost": None,   # 用户现在解决问题的年成本（钱或折成钱）
        "payment_evidence": None,  # 付费证据等级 1-4，4=已预付/下单
        "cash": None,              # 账上现金
        "monthly_burn": None,      # 每月净流出
        "asset_level": None,       # 想法/原型/样品/已交付客户/稳定量产
        "max_loss": None,          # 最大可承受损失
    },
    "economics": {
        "price": None,
        "variable_cost": None,
        "fixed_cost": None,
        "reach": None,             # 每月可触达客户数
    },
    "gates": {
        "usefulness": None,        # 过/不过/待验证
        "unit": None,
        "time": None,
        "risk": None,
    },
    "decisions": [],
    "updated": "",
}

REQUIRED_FOR_VERDICT = ["substitute_cost", "payment_evidence"]
REQUIRED_FOR_GATES = ["cash", "monthly_burn", "price", "variable_cost", "reach"]


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def load(path):
    if not os.path.exists(path):
        print("档案不存在：{}（先执行 init）".format(path))
        sys.exit(2)
    return json.load(open(path, encoding="utf-8"))


def save(path, data):
    data["updated"] = now()
    d = os.path.dirname(os.path.abspath(path))
    if d:
        os.makedirs(d, exist_ok=True)
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


TOP_MAP = {
    "name": "project", "one_liner": "project", "model": "project", "stage": "project",
    "substitute_cost": "facts", "payment_evidence": "facts", "cash": "facts",
    "monthly_burn": "facts", "asset_level": "facts", "max_loss": "facts",
    "price": "economics", "variable_cost": "economics", "fixed_cost": "economics",
    "reach": "economics",
    "usefulness": "gates", "unit": "gates", "time": "gates", "risk": "gates",
}


def canonical(key):
    if "." in key:
        return key
    return TOP_MAP.get(key, "facts") + "." + key


def set_dotted(data, key, value):
    key = canonical(key)
    parts = key.split(".")
    cur = data
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    cur[parts[-1]] = value


def coerce(v):
    for cast in (int, float):
        try:
            return cast(v)
        except ValueError:
            pass
    return v


def cmd_init(args):
    if os.path.exists(args.path):
        data = load(args.path)
        print("档案已存在，未覆盖：{}".format(args.path))
        print("当前项目名：{}".format(data["project"].get("name") or "（空）"))
        return
    data = json.loads(json.dumps(TEMPLATE))
    data["project"]["name"] = args.name or ""
    d = os.path.dirname(os.path.abspath(args.path))
    if d:
        os.makedirs(d, exist_ok=True)
    save(args.path, data)
    print("已创建：{}".format(args.path))
    print("下一步：用 set 填 project.one_liner、project.model、facts.cash、facts.monthly_burn")


def cmd_set(args):
    data = load(args.path)
    for pair in args.pairs:
        if "=" not in pair:
            print("忽略非法参数：{}（应为 k=v）".format(pair))
            continue
        k, v = pair.split("=", 1)
        set_dotted(data, k, coerce(v))
    save(args.path, data)
    print("已更新：{}".format(", ".join(args.pairs)))


def cmd_check(args):
    data = load(args.path)
    facts = data["facts"]
    econ = data["economics"]
    missing_v = [k for k in REQUIRED_FOR_VERDICT if facts.get(k) is None]
    missing_cash = [k for k in ("cash", "monthly_burn") if facts.get(k) is None]
    missing_econ = [k for k in ("price", "variable_cost", "fixed_cost", "reach") if econ.get(k) is None]

    print("项目：{}（{}）".format(data["project"].get("name") or "未命名",
                             MODELS.get(data["project"].get("model", "unknown"), "未判定")))
    print("阶段：{}".format(data["project"].get("stage", "S0")))

    if missing_v:
        print("\n[还不能给方向结论] 缺：{}".format("、".join(missing_v)))
        print("  先问这两个：用户现在为这件事每年花多少；有没有人为相邻的东西付过钱（1-4 级）")
    else:
        print("\n[方向结论可以给] 两个关键事实已就位")

    if missing_cash:
        print("\n[现金闸门缺数] 缺：{}".format("、".join(missing_cash)))
        print("  这两项一填，就能算出还能撑几个月")
    if missing_econ:
        print("\n[单位经济缺数] 缺：{}".format("、".join(missing_econ)))
        print("  补齐后才能算盈亏平衡量，否则只能给“待验证”")

    cash, burn = facts.get("cash"), facts.get("monthly_burn")
    if isinstance(cash, (int, float)) and isinstance(burn, (int, float)) and burn > 0:
        print("\nrunway = {} / {} = {:.1f} 个月".format(cash, burn, cash / burn))
        print("  按两倍成本估，真实可用周期约 {:.1f} 个月".format(cash / burn / 2))

    stage = data["project"].get("stage", "S0")
    if stage not in STAGES:
        print("\n阶段值异常：{}，应为 S0-S5".format(stage))

    if not data["decisions"]:
        print("\n还没有决策记录：出第一张卡后用 log 记账，季度对账")
    else:
        last = data["decisions"][-1]
        print("\n最近一次结论：{}（{}）｜预测：{}".format(
            last.get("verdict"), last.get("date"), last.get("prediction")))


def cmd_log(args):
    data = load(args.path)
    data["decisions"].append({
        "date": now(),
        "verdict": args.verdict,
        "basis": args.basis or "",
        "prediction": args.prediction or "",
        "result": args.result or "未复盘",
        "deviation": args.deviation or "",
    })
    save(args.path, data)
    print("已记录第 {} 条决策：{}".format(len(data["decisions"]), args.verdict))
    print("提醒：到期后回填 result 与 deviation，连续三次同类偏差说明判据要改")


def cmd_show(args):
    data = load(args.path)
    print(json.dumps(data, ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser(description="创业档案读写")
    sub = ap.add_subparsers(dest="cmd")

    p1 = sub.add_parser("init", help="创建档案")
    p1.add_argument("--path", required=True)
    p1.add_argument("--name", default="")

    p2 = sub.add_parser("set", help="更新字段，支持点路径")
    p2.add_argument("--path", required=True)
    p2.add_argument("pairs", nargs="+")

    p3 = sub.add_parser("check", help="检查完整度与 runway")
    p3.add_argument("--path", required=True)

    p4 = sub.add_parser("log", help="追加决策记录")
    p4.add_argument("--path", required=True)
    p4.add_argument("--verdict", required=True)
    p4.add_argument("--basis", default="")
    p4.add_argument("--prediction", default="")
    p4.add_argument("--result", default="")
    p4.add_argument("--deviation", default="")

    p5 = sub.add_parser("show", help="打印完整档案")
    p5.add_argument("--path", required=True)

    args = ap.parse_args()
    if args.cmd == "init":
        cmd_init(args)
    elif args.cmd == "set":
        cmd_set(args)
    elif args.cmd == "check":
        cmd_check(args)
    elif args.cmd == "log":
        cmd_log(args)
    elif args.cmd == "show":
        cmd_show(args)
    else:
        ap.print_help()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
