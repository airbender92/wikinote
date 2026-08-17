# -*- coding: utf-8 -*-
"""2026-08-17 午盘行情拉取：腾讯行情(指数+个股) + 东财涨跌家数/涨停跌停池"""
import urllib.request, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="ignore")

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def fetch_tencent(codes):
    url = "http://qt.gtimg.cn/q=" + ",".join(codes)
    req = urllib.request.Request(url, headers=UA)
    data = urllib.request.urlopen(req, timeout=12).read().decode("gbk", errors="ignore")
    rows = {}
    for line in data.strip().split(";"):
        line = line.strip()
        if "=" not in line or not line:
            continue
        val = line.split("=", 1)[1].strip().strip('"')
        if not val:
            continue
        f = val.split("~")
        if len(f) < 50:
            continue
        rows[f[2]] = {
            "name": f[1], "price": f[3], "prev": f[4], "open": f[5],
            "vol_hand": f[6], "time": f[30], "chg": f[31], "chg_pct": f[32],
            "high": f[33], "low": f[34], "amount_wan": f[37], "turnover": f[38],
            "pe": f[39], "amp": f[43], "avg": f[51], "limit_up": f[47], "limit_dn": f[48],
            "vol_ratio": f[49],
        }
    return rows

def fetch_updown():
    """东财全市场涨跌家数"""
    url = ("https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=1&po=1&np=1&fltt=2&invt=2"
           "&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f104,f105,f106")
    req = urllib.request.Request(url, headers=UA)
    d = json.loads(urllib.request.urlopen(req, timeout=12).read().decode("utf-8"))
    return d.get("data", {}).get("diff", {})

def fetch_pool(kind, date):
    """kind: ZT(涨停) / DT(跌停)"""
    url = (f"https://push2ex.eastmoney.com/getTopic{kind}Pool?ut=7eea3edcaed734bea9cbfc24409ed989"
           f"&dpt=wz.ztzt&Pageindex=0&pagesize=200&sort=fbt%3Aasc&date={date}")
    req = urllib.request.Request(url, headers=UA)
    d = json.loads(urllib.request.urlopen(req, timeout=12).read().decode("utf-8"))
    data = d.get("data") or {}
    return data.get("tc", 0), data.get("pool", [])

if __name__ == "__main__":
    batch1 = ["sh000001","sz399001","sz399006","sh000688","sh000300",
              "sh601766","sz000538","sz002241","sz002594","sh600406",
              "sh600886","sh600999","sh603993","sh600030","sh603019",
              "sz000021","sh600584","sz300750","sh600938","sh601899"]
    batch2 = ["sh600519","sz002415","sh603501","sh600487","sh601088","sh600900",
              "sz002371","sh601318","sh601138","sh603259","sh600276","sz000063",
              "sh600011","sz000776","sh600028","sh601633","sz000895","sh600887",
              "sh600309","sh600031","sz000651","sz000333","sh600690"]
    print("===== 腾讯行情 批次1（指数+持仓+核心信号） =====")
    r1 = fetch_tencent(batch1)
    for code in batch1:
        if code in r1:
            x = r1[code]
            print(f"{code} {x['name']} | 现{x['price']} 涨跌{x['chg']}({x['chg_pct']}%) "
                  f"开{x['open']} 高{x['high']} 低{x['low']} 昨{x['prev']} | 量{x['vol_hand']}手 "
                  f"额{x['amount_wan']}万 换手{x['turnover']}% 量比{x['vol_ratio']} PE{x['pe']} | {x['time']}")
    print("\n===== 腾讯行情 批次2（观察池） =====")
    r2 = fetch_tencent(batch2)
    for code in batch2:
        if code in r2:
            x = r2[code]
            print(f"{code} {x['name']} | 现{x['price']} 涨跌{x['chg']}({x['chg_pct']}%) "
                  f"高{x['high']} 低{x['low']} 昨{x['prev']} | 额{x['amount_wan']}万 | {x['time']}")
    print("\n===== 东财涨跌家数 =====")
    try:
        ud = fetch_updown()
        print("上涨", ud.get("f104"), "家 | 下跌", ud.get("f105"), "家 | 平盘", ud.get("f106"), "家")
    except Exception as e:
        print("涨跌家数接口失败:", e)
    print("\n===== 涨停/跌停池 =====")
    for kind in ("ZT", "DT"):
        try:
            tc, pool = fetch_pool(kind, "20260817")
            names = [p.get("n") for p in pool][:30]
            print(f"{kind}: 共{tc}家 前30: {'、'.join(names) if names else '无'}")
        except Exception as e:
            print(f"{kind}接口失败:", e)
