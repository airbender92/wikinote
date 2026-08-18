# -*- coding: utf-8 -*-
"""2026-08-18晚 外围实时：美股指数+个股、恒指、日韩、商品、汇率（腾讯接口）"""
import urllib.request

def fetch(codes):
    url = "http://qt.gtimg.cn/q=" + ",".join(codes)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://gu.qq.com/"})
    raw = urllib.request.urlopen(req, timeout=15).read()
    return raw.decode("gbk", errors="ignore")

def parse(txt):
    for line in txt.strip().split(";"):
        line = line.strip()
        if not line or "=" not in line:
            continue
        k, v = line.split("=", 1)
        v = v.strip().strip('"')
        f = v.split("~")
        if len(f) < 5:
            continue
        name = f[1]
        # 通用字段：现价/昨收/开盘/涨跌/涨跌%
        try:
            price = f[3]; prev = f[4]; pct = f[32] if len(f) > 32 else f[5]
            t = f[30] if len(f) > 30 else ""
            # 尝试时间字段
            print(f"{k} {name} 现价{price} 昨收{prev} 涨跌%{pct} 时间{t}")
        except Exception as e:
            print(f"{k} {name} PARSE_ERR {e} raw={v[:100]}")

if __name__ == "__main__":
    groups = {
        "美股指数": ["usDJI", "usIXIC", "usINX", "usSOX"],
        "美股个股": ["usNVDA", "usAMD", "usMU", "usWDC", "usAVGO", "usTSM", "usAAPL", "usMSFT", "usGOOG", "usMETA", "usTSLA", "usCOHR"],
        "商品汇率": ["hf_XAU", "hf_CL", "usDX", "hf_GC"],
        "亚太": ["hkHSI", "hkHSTECH", "r_hkHSI", "usN225", "usKS11"],
        "美债": ["usZN00Y"],
    }
    for gname, codes in groups.items():
        print("=" * 20, gname, "=" * 20)
        try:
            print(parse(fetch(codes)))
        except Exception as e:
            print("ERR", gname, e)
