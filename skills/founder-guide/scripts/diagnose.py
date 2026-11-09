#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""创业阶段自测：15 题 -> 阶段判定 + 瓶颈维度 + 三个动作（纯标准库）

AI 用法：把用户的回答映射成 0/1/2，用 --answers 传入。
人用法：加 --interactive 逐题问。

  python3 diagnose.py --answers "2,1,2,1,0,0,1,0,0,1,1,0,1,0,0"
  python3 diagnose.py --interactive
"""

import argparse
import sys

QUESTIONS = [
    # (维度, 题干, [0分描述, 1分描述, 2分描述])
    ("需求", "过去 30 天，有多少非熟人主动问过你这个东西？", ["0 人", "1-4 人", "5 人以上"]),
    ("需求", "有没有人已经为相邻的产品付过钱，你亲眼见过订单或账单？", ["没见过", "听说过", "见过 3 例以上"]),
    ("需求", "用户现在用什么替代，那东西一年花多少钱，你能说清并核对过吗？", ["说不出", "大致知道", "能说清且核对过"]),
    ("交付", "有没有一个能给外人看的东西（原型、样品、试做成品）？", ["没有", "有但很粗糙", "有且外人能看懂"]),
    ("交付", "最近一次把东西交到别人手上，对方实际用了或付钱了吗？", ["没有", "用了没付钱", "付过钱"]),
    ("交付", "交付流程写下来过吗，别人能照着做吗？", ["在脑子里", "写了部分", "完整且别人能照着做"]),
    ("经济", "你的单价和单份变动成本各是多少？", ["都说不清", "知道单价", "两个都清楚"]),
    ("经济", "固定成本 ÷ 单位毛利 = 每月要卖多少件，你算过并知道能触达多少客户吗？", ["没算", "算过", "算过且知道可触达客户数"]),
    ("经济", "花多少钱能换来 1 个付费客户，你测过吗？", ["不知道", "靠估算", "实测过"]),
    ("现金", "账上现金 ÷ 每月净流出 = 几个月，你知道并且做过预案吗？", ["不知道", "算过", "算过且低于 6 个月时已有预案"]),
    ("现金", "这半年如果全亏，生活会不会崩？", ["会崩", "很紧", "能扛"]),
    ("现金", "现在有没有正在产生收入的东西，哪怕很小？", ["没有", "偶发", "稳定小额"]),
    ("纪律", "最近一周你有没有算过现金、新增付费订单、交付件数这三个数？", ["没算", "算了部分", "三个都算了"]),
    ("纪律", "手上的事有没有写在纸上的止损线（钱、时间、指标）？", ["没有", "有模糊的", "写在纸上"]),
    ("纪律", "上一个判断，你事后回看过对错吗？", ["没有", "想过没记", "记账回看过"]),
]

DIMS = ["需求", "交付", "经济", "现金", "纪律"]

ACTIONS = {
    "需求": [
        "7 天内找 10 个非熟人，只问三句：现在怎么解决、为此花多少钱、上次为什么没换（脚本见 references/interview-and-offer.md）",
        "把最贵的那类拒绝理由写成你的设计约束，不要先改文案",
        "若 10 人里 0 人愿付，换人群或换问题，不要换说法",
    ],
    "交付": [
        "先把一个最小可卖单元做出来，可以先手工，不追求完整",
        "定一个具体日期对外承诺演示，只讲它替你省了什么",
        "把交付步骤写成一页 SOP，标出最慢那一环，只改这一环",
    ],
    "经济": [
        "用 startup_calc.py 跑一遍 unit：单价、变动成本、固定成本、可触达客户",
        "获客成本必须实测一次（花小钱投一轮，记花费÷新增付费）",
        "毛利率低于 30% 先修成本结构，别加投放",
    ],
    "现金": [
        "现在就填 startup-profile.json 的 cash 与 monthly_burn，跑 check 看 runway",
        "见效果超过 runway 60% 的，先做一个 30 天内能收钱的小版本",
        "停掉所有不产生交付和收入的支出，砍到只剩三笔",
    ],
    "纪律": [
        "每周固定一天只看三个数字：现金、新增付费订单、交付件数",
        "给当前这件事写下止损线：钱烧到多少、时间到多久、指标低于多少",
        "用 profile.py log 记一条决策，设个日历提醒 30 天后回填结果",
    ],
}

MATURE_ACTIONS = [
    "确认护城河属于哪一类：专有技术 / 网络效应 / 规模经济 / 转换成本 / 品牌；一年只强化一类",
    "把依赖你本人的关键决策改成规则或流程，让组织不再等你的判断",
    "每季度重跑一次 S0 的十人访谈，防止半年前的判断依据过期",
]

MATURE_BOOKS = "15 从0到1、19 基业长青、47 埃隆之书（拆墙与去指挥链）"

BOOKS = {
    "需求": "02 低风险创业、25 世界上最伟大的推销员、15 从0到1",
    "交付": "47 埃隆之书（原型先行、五步法）、04 创业36条军规、31 微习惯",
    "经济": "17 一本书读懂财报、01 小米创业思考、26 影响力",
    "现金": "05 创业维艰、17 一本书读懂财报、13 逃不开的经济周期",
    "纪律": "16 原则、33 认知觉醒、46 谁动了我的奶酪",
}


def stage_of(scores):
    """阶段由第一个未达标维度决定，关键维度与阶段天然一致。"""
    order = ["需求", "交付", "经济", "现金", "纪律"]
    stages = ["S0", "S1", "S2", "S3", "S4"]
    reasons = {
        "需求": "还没有付费需求证据",
        "交付": "有人问，但还没有能交付的东西",
        "经济": "做出来了，但账还没算",
        "现金": "能算账，但现金撑不住",
        "纪律": "该有的都有了，但节奏和复盘没建立",
    }
    for i, d in enumerate(order):
        if scores[d] < 3:
            return stages[i], reasons[d], d
    mn = min(scores.values())
    key = min(order, key=lambda d: scores[d])
    if mn >= 5:
        return "S5", "四个维度都过硬，进入规模化与护城河", key
    return "S4", "主要维度已经过关，补最弱那一项", key


def main():
    ap = argparse.ArgumentParser(description="创业阶段自测 15 题")
    ap.add_argument("--answers", help="15 个 0/1/2 用逗号分隔")
    ap.add_argument("--interactive", action="store_true")
    args = ap.parse_args()

    answers = []
    if args.interactive:
        for i, (dim, q, opts) in enumerate(QUESTIONS, 1):
            print("\n{}. [{}] {}".format(i, dim, q))
            for j, o in enumerate(opts):
                print("   {} = {}".format(j, o))
            while True:
                try:
                    v = input("   输入 0/1/2：").strip()
                except EOFError:
                    v = "0"
                if v in ("0", "1", "2"):
                    answers.append(int(v))
                    break
    elif args.answers:
        parts = [p.strip() for p in args.answers.replace("，", ",").split(",") if p.strip()]
        if len(parts) != 15:
            print("需要 15 个答案，收到 {} 个".format(len(parts)))
            return 1
        try:
            answers = [int(p) for p in parts]
        except ValueError:
            print("答案只能是 0/1/2")
            return 1
    else:
        ap.print_help()
        return 1

    if any(a < 0 or a > 2 for a in answers):
        print("答案只能是 0/1/2")
        return 1

    scores = {d: 0 for d in DIMS}
    for (dim, _q, _o), a in zip(QUESTIONS, answers):
        scores[dim] += a

    total = sum(scores.values())
    stage, reason, weakest = stage_of(scores)
    if weakest != "现金" and scores["现金"] <= 1:
        reason = reason + "（但现金维度几乎空白，先算清还能撑多久）"
        weakest = "现金"

    print("\n===== 维度得分（每维满分 6，总分 {} / 30）=====".format(total))
    for d in DIMS:
        bar = "#" * scores[d] + "." * (6 - scores[d])
        print("  {:<3} {} {}".format(d, bar, scores[d]))

    print("\n阶段判定：{} — {}".format(stage, reason))
    print("本阶段关键维度：{}（{} / 6）".format(weakest, scores[weakest]))

    if scores[weakest] >= 5:
        acts, books = MATURE_ACTIONS, MATURE_BOOKS
        print("\n基础动作已经做完，按规模化推进这三件：")
    else:
        acts, books = ACTIONS[weakest], BOOKS[weakest]
        print("\n本周只做这三件（按顺序）：")
    for i, a in enumerate(acts, 1):
        print("  {}. {}".format(i, a))

    print("\n取件：{}".format(books))

    strong = [d for d in DIMS if scores[d] >= 5]
    if strong and len(strong) < len(DIMS):
        print("\n已经稳的维度：{}——不要在这上面继续加投入".format("、".join(strong)))
    low = [d for d in DIMS if scores[d] <= 1 and d != weakest]
    if low:
        print("另有归零维度：{}——做完上面的三件事就补它".format("、".join(low)))

    print("\n下一步：把结果写进 startup-profile.json（stage={}），跑 profile.py check 看还缺哪几个数。".format(
        stage.replace("+", "")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
