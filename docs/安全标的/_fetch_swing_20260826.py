# -*- coding: utf-8 -*-
"""拉取6只熟悉标的日K，计算近4周/13周震荡区间（低位区间、高位区间）"""
import json
import urllib.request

STOCKS = [
    ("sh600999", "招商证券"),
    ("sh603993", "洛阳钼业"),
    ("sz002594", "比亚迪"),
    ("sz002241", "歌尔股份"),
    ("sh601138", "工业富联"),
    ("sh600487", "亨通光电"),
]

def fetch_kline(code, days=140):
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},day,,,{days},qfq"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read().decode("utf-8"))
    node = data["data"][code]
    klist = node.get("qfqday") or node.get("day")
    rows = []
    for it in klist:
        # [date, open, close, high, low, volume, ...]
        rows.append({
            "date": it[0],
            "open": float(it[1]),
            "close": float(it[2]),
            "high": float(it[3]),
            "low": float(it[4]),
            "vol": float(it[5]) if len(it) > 5 else 0,
        })
    return rows

def calc_zone(rows, label, last_n):
    sub = rows[-last_n:]
    if not sub:
        return None
    highs = [r["high"] for r in sub]
    lows = [r["low"] for r in sub]
    closes = [r["close"] for r in sub]
    hi = max(highs)
    lo = min(lows)
    # 分位计算：低位区间=最低~25%分位；高位区间=75%分位~最高
    def pctile(vals, p):
        s = sorted(vals)
        idx = int((len(s) - 1) * p)
        return s[idx]
    lo_p25 = pctile(lows, 0.25)
    hi_p75 = pctile(highs, 0.75)
    cur = closes[-1]
    first_d = sub[0]["date"]
    last_d = sub[-1]["date"]
    return {
        "label": label,
        "range": f"{first_d} ~ {last_d}",
        "n": len(sub),
        "high": hi,
        "low": lo,
        "low_zone": (round(lo, 2), round(lo_p25, 2)),
        "high_zone": (round(hi_p75, 2), round(hi, 2)),
        "cur": cur,
        "mid": round((lo + hi) / 2, 2),
    }

def weekly_rows(rows):
    """按自然周聚合：每周最高/最低"""
    weeks = {}
    for r in rows:
        wk = r["date"][:7] + "-W"  # 简化：按YYYY-MM分组代替周
        weeks.setdefault(r["date"][:7], []).append(r)
    out = []
    for m, lst in sorted(weeks.items()):
        out.append({
            "month": m,
            "high": max(x["high"] for x in lst),
            "low": min(x["low"] for x in lst),
            "close": lst[-1]["close"],
        })
    return out

if __name__ == "__main__":
    result = {}
    for code, name in STOCKS:
        rows = fetch_kline(code)
        # 用最近65个交易日≈13周；最近20个交易日≈4周
        z13 = calc_zone(rows, "近13周", 65)
        z4 = calc_zone(rows, "近4周", 20)
        wk = weekly_rows(rows)
        # 最近10周明细（按月分组显示）
        wk_recent = wk[-12:]
        result[name] = {
            "code": code,
            "cur": rows[-1]["close"],
            "last_date": rows[-1]["date"],
            "z13": z13,
            "z4": z4,
            "monthly": wk_recent,
        }
    print(json.dumps(result, ensure_ascii=False, indent=1))
