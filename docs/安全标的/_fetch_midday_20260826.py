# -*- coding: utf-8 -*-
"""午盘研判取数：指数+持仓6只实时行情（腾讯接口，GBK）"""
import json
import urllib.request

CODES = [
    "sh000001", "sz399001", "sz399006", "sh000688",  # 上证/深成/创业板/科创50
    "sz000538",  # 云南白药
    "sz002594",  # 比亚迪
    "sh600406",  # 国电南瑞
    "sh600886",  # 国投电力
    "sh600999",  # 招商证券
    "sh603993",  # 洛阳钼业
]

def fetch_quote(codes):
    url = "https://qt.gtimg.cn/q=" + ",".join(codes)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://gu.qq.com/"})
    with urllib.request.urlopen(req, timeout=15) as r:
        raw = r.read().decode("gbk", errors="ignore")
    out = {}
    for line in raw.strip().split(";"):
        line = line.strip()
        if not line or "=" not in line:
            continue
        key, val = line.split("=", 1)
        code = key.split("_")[-1]
        fields = val.strip('"').split("~")
        if len(fields) < 45:
            continue
        out[code] = {
            "name": fields[1],
            "code": fields[2],
            "price": float(fields[3]),
            "pre_close": float(fields[4]),
            "open": float(fields[5]),
            "volume": float(fields[6]),       # 手
            "high": float(fields[33]) if fields[33] else None,
            "low": float(fields[34]) if fields[34] else None,
            "change": float(fields[31]),
            "pct": float(fields[32]),
            "amount": float(fields[37]),      # 万元
            "turnover": fields[38],           # 换手率%
            "pe": fields[39],
            "date_time": fields[30],
        }
    return out

if __name__ == "__main__":
    data = fetch_quote(CODES)
    print(json.dumps(data, ensure_ascii=False, indent=1))
