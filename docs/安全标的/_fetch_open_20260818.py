# -*- coding: utf-8 -*-
"""拉取2026-08-18开盘前行情：持仓8只 + 关键指数 + 观察池热点"""
import urllib.request
import sys

def fetch(codes):
    url = "http://qt.gtimg.cn/q=" + ",".join(codes)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=15).read()
    txt = raw.decode("gbk", errors="ignore")
    return txt

def parse(txt):
    out = []
    for line in txt.strip().split(";"):
        line = line.strip()
        if not line:
            continue
        try:
            body = line.split("~")
            name = body[1]
            code = body[2]
            price = body[3]
            chg_pct = body[32]
            chg = body[31]
            open_p = body[5]
            high = body[33] if len(body) > 33 else ""
            low = body[34] if len(body) > 34 else ""
            prev_close = body[4]
            vol_lot = body[6]
            amount_wan = body[37] if len(body) > 37 else ""
            out.append(f"{code} {name} 现价{price} 涨跌{chg}({chg_pct}%) 开{open_p} 高{high} 低{low} 昨收{prev_close} 量{vol_lot}手 额{amount_wan}万")
        except Exception as e:
            out.append(f"PARSE_ERR: {line[:60]} -> {e}")
    return "\n".join(out)

if __name__ == "__main__":
    # 持仓8只 + 指数 + 观察池热点（存储/光通信/证券）
    groups = {
        "持仓8只": ["sh601766", "sz000538", "sz002241", "sz002594",
                    "sh600406", "sh600886", "sh600999", "sh603993"],
        "指数": ["sh000001", "sz399001", "sz399006", "sh000688", "sh000300"],
        "观察池热点": ["sh600584", "sz000021", "sh600487", "sz002475",
                      "sh601138", "sh600030", "sz000776", "sh600519"],
    }
    for gname, codes in groups.items():
        print("=" * 20, gname, "=" * 20)
        print(parse(fetch(codes)))
