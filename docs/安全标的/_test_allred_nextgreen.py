# -*- coding: utf-8 -*-
"""回测：持仓5只"全红日"次日是否"全绿"（验证用户假设）
持仓：云南白药000538、比亚迪002594、国电南瑞600406、国投电力600886、招商证券600999
数据：腾讯日K前复权，近320个交易日（约1.3年）
"""
import json
import urllib.request

HOLDINGS = [
    ("sz000538", "云南白药"),
    ("sz002594", "比亚迪"),
    ("sh600406", "国电南瑞"),
    ("sh600886", "国投电力"),
    ("sh600999", "招商证券"),
]


def fetch_kline(code, n=320):
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},day,,,{n},qfq"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        raw = json.loads(r.read().decode("utf-8"))
    d = raw["data"][code]
    key = "qfqday" if "qfqday" in d else "day"
    rows = d[key]
    out = {}
    for row in rows:
        # row: [date, open, close, high, low, volume, ...]
        out[row[0]] = float(row[2])  # 收盘价
    return out


def main():
    series = {}
    for code, name in HOLDINGS:
        series[name] = fetch_kline(code)
        print(f"{name}({code}) 拉取 {len(series[name])} 根日K")

    # 对齐日期（取5只共有的交易日）
    dates = sorted(set.intersection(*[set(v.keys()) for v in series.values()]))
    print(f"共同交易日: {len(dates)} 个（{dates[0]} ~ {dates[-1]}）")

    # 计算每日涨跌幅
    pcts = {}  # date -> {name: pct}
    for i in range(1, len(dates)):
        d0, d1 = dates[i - 1], dates[i]
        day_pct = {}
        for name, s in series.items():
            pct = (s[d1] - s[d0]) / s[d0] * 100
            day_pct[name] = pct
        pcts[d1] = day_pct

    day_list = list(pcts.keys())
    print(f"涨跌幅样本: {len(day_list)} 个交易日")

    def all_red(d):
        return all(v > 0 for v in pcts[d].values())

    def all_green(d):
        return all(v < 0 for v in pcts[d].values())

    red_days = [d for d in day_list if all_red(d)]
    green_days = [d for d in day_list if all_green(d)]

    print(f"\n【核心统计】")
    print(f"全红日（5只全涨）次数: {len(red_days)} / {len(day_list)} = {len(red_days)/len(day_list)*100:.1f}%")
    print(f"全绿日（5只全跌）次数: {len(green_days)} / {len(day_list)} = {len(green_days)/len(day_list)*100:.1f}%")

    # 全红次日
    next_after_red = []
    for i in range(len(day_list) - 1):
        if all_red(day_list[i]):
            nxt = day_list[i + 1]
            next_after_red.append((day_list[i], nxt, pcts[nxt]))

    n_next_all_green = sum(1 for _, _, np in next_after_red if all(v < 0 for v in np.values()))
    n_next_all_red = sum(1 for _, _, np in next_after_red if all(v > 0 for v in np.values()))
    avg_next_pct = sum(sum(np.values()) / len(np) for _, _, np in next_after_red) / len(next_after_red) if next_after_red else 0

    print(f"\n全红日次日表现（样本 {len(next_after_red)} 个）:")
    print(f"  次日全绿: {n_next_all_green} 次 = {n_next_all_green/len(next_after_red)*100:.1f}%")
    print(f"  次日全红: {n_next_all_red} 次 = {n_next_all_red/len(next_after_red)*100:.1f}%")
    print(f"  次日平均涨跌幅: {avg_next_pct:+.2f}%")

    # 基准：任意日次日全绿的概率（无条件）
    n_any_next_green = sum(1 for i in range(len(day_list) - 1) if all(v < 0 for v in pcts[day_list[i + 1]].values()))
    print(f"\n【基准对照】任意交易日次日为全绿日的概率: {n_any_next_green/(len(day_list)-1)*100:.1f}%")
    print(f"任意交易日当天为全红日的概率: {len(red_days)/len(day_list)*100:.1f}%")

    # 全红次日：组合平均收益 vs 全市场（非全红日次日平均）
    non_red_next = []
    for i in range(len(day_list) - 1):
        if not all_red(day_list[i]):
            non_red_next.append(sum(pcts[day_list[i + 1]].values()) / 5)
    avg_non = sum(non_red_next) / len(non_red_next) if non_red_next else 0
    print(f"\n全红次日组合均值: {avg_next_pct:+.2f}%  vs  非全红日次日组合均值: {avg_non:+.2f}%")
    print(f"（若两者接近 → 全红不是次日下跌的有效预测信号）")

    # 全红日明细（近12个）
    print(f"\n【近12个全红日及次日】")
    for d, nxt, np in next_after_red[-12:]:
        pct_str = ", ".join(f"{k}:{v:+.1f}" for k, v in np.items())
        verdict = "次日全绿" if all(v < 0 for v in np.values()) else ("次日全红" if all(v > 0 for v in np.values()) else "次日分歧")
        print(f"  {d} 全红 → {nxt} [{verdict}] {pct_str}")


if __name__ == "__main__":
    main()
