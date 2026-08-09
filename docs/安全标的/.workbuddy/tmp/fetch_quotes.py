# -*- coding: utf-8 -*-
import urllib.request, json, sys

def fetch(codes):
    url = "http://qt.gtimg.cn/q=" + ",".join(codes)
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Referer":"http://gu.qq.com/"})
    raw = urllib.request.urlopen(req, timeout=15).read()
    txt = raw.decode("gbk", errors="replace")
    out = {}
    for line in txt.strip().split("\n"):
        if "=" not in line: continue
        key = line.split("=")[0].replace("v_","").strip()
        val = line.split("=",1)[1].strip().strip(";").strip('"')
        out[key] = val
    return out

def parse(val):
    f = val.split("~")
    if len(f) < 40: return None
    return {
        "name": f[1], "code": f[2], "price": f[3], "prev": f[4], "open": f[5],
        "vol": f[6], "chg": f[31], "chg_pct": f[32], "high": f[33], "low": f[34],
        "amount_wan": f[37], "turnover": f[38], "pe": f[39]
    }

groups = {
 "a_index": ["sh000001","sz399001","sz399006","sh000688","sh000300"],
 "a_stocks": ["sh601138","sh600487","sz002415","sz002475","sz002371","sh603501","sh688981","sh603019","sh600584","sz000021","sz002273",
   "sh601766","sh600406","sh600031","sz002241","sh600519","sh600809","sz000568","sh600887","sz000895","sh603288","sh600309",
   "sz000333","sz000651","sh600690","sh600276","sz300760","sz000538","sh600436","sh603259","sh601318","sh600030","sz000776","sh601939","sh601328",
   "sz300750","sz002594","sz300274","sh600660","sh601633","sh600900","sh601088","sh601225","sh600938","sh600028","sh600011","sh600674","sh600886",
   "sh601899","sh601600","sh603993","sz000063","sz002714","sh601668","sz300124","sh600999"],
 "us_index": ["usDJI","usIXIC","usINX","usSOX"],
 "us_stocks": ["usNVDA","usAMD","usMU","usWDC","usSTX","usAVGO","usTSM","usAAPL","usGOOGL","usMSFT","usAMAT","usLRCX","usKLAC","usINTC","usTSLA","usSMCI"],
 "fx_comm": ["fx_susdcny","fx_susdjpy","fx_susdindex","hf_GC","hf_CL","hf_OIL","fx_saudcny"]
}

res = {}
for g, codes in groups.items():
    for i in range(0, len(codes), 15):
        batch = codes[i:i+15]
        try:
            data = fetch(batch)
            for k, v in data.items():
                p = parse(v)
                if p: res[k] = p
        except Exception as e:
            res["__err_"+g+"_"+str(i)] = str(e)

print(json.dumps(res, ensure_ascii=False, indent=1))
