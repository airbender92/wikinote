# -*- coding: utf-8 -*-
"""2026-08-27 收盘：指数 + 招商证券/比亚迪 + 券商板块相关 + 恒瑞（腾讯行情接口）"""
import json
import urllib.request

CODES = [
    ("sh000001", "上证指数"), ("sz399001", "深证成指"), ("sz399006", "创业板指"), ("sh000688", "科创50"),
    ("sh600999", "招商证券"), ("sz002594", "比亚迪"), ("sh600276", "恒瑞医药"),
    ("sh600030", "中信证券"), ("sz000776", "广发证券"), ("sh601211", "国泰海通"),
    ("sh601881", "中国银河"), ("sh600837", "海通证券"), ("sz000166", "申万宏源"),
]

def _f(s):
    try:
        return float(s)
    except (ValueError, TypeError):
        return 0.0

def fetch_quotes(codes):
    out = []
    for i in range(0, len(codes), 18):
        batch = codes[i:i+18]
        q = ",".join(c for c, _ in batch)
        url = f"https://qt.gtimg.cn/q={q}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read().decode("gbk", errors="ignore")
        for line in raw.strip().split(";"):
            line = line.strip()
            if not line or "=" not in line:
                continue
            code = line.split("=")[0].replace("v_", "")
            body = line.split("=", 1)[1].strip().strip('"')
            f = body.split("~")
            if len(f) < 50:
                continue
            name = next((n for c, n in batch if c == code), f[1])
            out.append({
                "code": code, "name": name,
                "price": _f(f[3]), "preclose": _f(f[4]), "open": _f(f[5]),
                "vol_hand": _f(f[6]), "time": f[30],
                "chg": _f(f[31]), "pct": _f(f[32]),
                "high": _f(f[33]), "low": _f(f[34]),
                "amount_wan": _f(f[37]), "turnover": _f(f[38]),
                "pe": _f(f[39]), "pb": _f(f[46]),
            })
    return out

if __name__ == "__main__":
    result = fetch_quotes(CODES)
    with open("_close_20260827_zhao_by.json", "w", encoding="utf-8") as fp:
        json.dump(result, fp, ensure_ascii=False, indent=1)
    for it in result:
        print(f"{it['name']}: {it['price']} ({it['pct']:+.2f}%) 开{it['open']} 高{it['high']} 低{it['low']} 额{it['amount_wan']/10000:.1f}亿 换手{it['turnover']}% PE{it['pe']} PB{it['pb']} 时间{it['time']}")
