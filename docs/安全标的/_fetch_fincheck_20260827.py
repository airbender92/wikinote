# -*- coding: utf-8 -*-
"""金融危机研判取数：持仓6只 + 关键指数 + 观察池核心（8/27晚间）"""
import urllib.request
import json

def fetch_qt(codes):
    url = "http://qt.gtimg.cn/q=" + ",".join(codes)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(req, timeout=10).read().decode("gbk", errors="ignore")
    out = {}
    for line in data.strip().split(";"):
        line = line.strip()
        if not line or "=" not in line:
            continue
        try:
            code = line.split("=")[0].split("_")[-1]
            fields = line.split('"')[1].split("~")
            name = fields[1]
            price = fields[3]
            chg_pct = fields[32] if len(fields) > 32 else "?"
            chg_amt = fields[31] if len(fields) > 31 else "?"
            vol_hand = fields[6] if len(fields) > 6 else "?"  # 成交量(手)
            amount_wan = fields[37] if len(fields) > 37 else "?"  # 成交额(万)
            high52 = fields[41] if len(fields) > 41 else "?"
            low52 = fields[42] if len(fields) > 42 else "?"
            pe = fields[39] if len(fields) > 39 else "?"
            pb = fields[46] if len(fields) > 46 else "?"
            date = fields[30] if len(fields) > 30 else "?"
            out[code] = {"name": name, "price": price, "chg_pct": chg_pct, "chg_amt": chg_amt,
                         "vol_hand": vol_hand, "amount_wan": amount_wan, "high52": high52,
                         "low52": low52, "pe": pe, "pb": pb, "date": date}
        except Exception as e:
            out[code] = {"err": str(e)}
    return out

codes = [
    # 持仓6只
    "sz000538", "sz002594", "sh600406", "sh600886", "sh600999", "sh600276",
    # 指数
    "sh000001", "sz399001", "sz399006", "sh000688",
    # 观察池核心：存储链/算力/券商/防御
    "sh600584", "sz000021", "sz002475", "sz002273", "sh603019", "sh603501",
    "sh601766", "sh600031", "sh600519", "sh600809", "sh600887",
    "sh600036", "sh601318", "sh600030", "sz000776", "sh601939", "sh601328",
    "sz002594", "sh600660", "sh601633", "sh600900", "sh601088", "sh601225",
    "sh600938", "sh600028", "sh600011", "sh600674", "sh600886", "sh601899",
    "sh601600", "sh603993", "sz000063", "sz002714", "sh601668", "sh600309",
    "sh603288", "sh600436", "sh603259", "sz000568", "sh600276", "sz000651",
    "sh600690", "sz000333", "sz000895",
    # 涨跌幅榜观察
    "sh688981", "sz300760", "sz300750", "sz300274", "sz300124",
]
# 去重
codes = list(dict.fromkeys(codes))
res = fetch_qt(codes)
print(json.dumps(res, ensure_ascii=False, indent=1))
