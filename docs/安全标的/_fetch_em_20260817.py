# -*- coding: utf-8 -*-
"""备用：东财push2批量行情（2026-08-17午盘）"""
import urllib.request, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="ignore")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def em_secid(code):
    """沪市sh/sz前缀 -> 东财secid"""
    if code.startswith("sh"):
        return "1." + code[2:]
    return "0." + code[2:]

def fetch(secids):
    url = ("https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&invt=2"
           "&fields=f2,f3,f4,f5,f6,f8,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21"
           "&secids=" + ",".join(secids))
    req = urllib.request.Request(url, headers=UA)
    d = json.loads(urllib.request.urlopen(req, timeout=15).read().decode("utf-8"))
    out = {}
    for x in (d.get("data") or {}).get("diff", []):
        out[x["f12"]] = {
            "name": x.get("f14"), "price": x.get("f2"), "pct": x.get("f3"),
            "chg": x.get("f4"), "vol": x.get("f5"), "amt": x.get("f6"),
            "turnover": x.get("f8"), "volratio": x.get("f10"),
            "high": x.get("f15"), "low": x.get("f16"), "open": x.get("f17"),
            "prev": x.get("f18"), "mcap": x.get("f20"), "fcap": x.get("f21"),
        }
    return out

if __name__ == "__main__":
    batch1 = ["sh000001","sz399001","sz399006","sh000688","sh000300","sh000016",
              "sh601766","sz000538","sz002241","sz002594","sh600406",
              "sh600886","sh600999","sh603993","sh600030","sh603019",
              "sz000021","sh600584","sz300750","sh600938","sh601899"]
    batch2 = ["sh600519","sz002415","sh603501","sh600487","sh601088","sh600900",
              "sz002371","sh601318","sh601138","sh603259","sh600276","sz000063",
              "sh600011","sz000776","sh600028","sh601633","sz000895","sh600887",
              "sh600309","sh600031","sz000651","sz000333","sh600690","sh601225",
              "sz002714","sh601668","sh600886"]
    print("===== 批次1 =====")
    r1 = fetch([em_secid(c) for c in batch1])
    for c in batch1:
        x = r1.get(c[2:])
        if x:
            print(f"{c[2:]} {x['name']} | 现{x['price']} {x['pct']}% 开{x['open']} 高{x['high']} 低{x['low']} 昨{x['prev']} | 额{x['amt']}元 换手{x['turnover']} 量比{x['volratio']}")
    print("\n===== 批次2 =====")
    r2 = fetch([em_secid(c) for c in batch2])
    for c in batch2:
        x = r2.get(c[2:])
        if x:
            print(f"{c[2:]} {x['name']} | 现{x['price']} {x['pct']}% 开{x['open']} 高{x['high']} 低{x['low']} 昨{x['prev']} | 额{x['amt']}元 换手{x['turnover']}")
