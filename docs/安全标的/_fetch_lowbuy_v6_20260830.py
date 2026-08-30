# -*- coding: utf-8 -*-
"""低吸区间校验v6：55只取现价/PE/PB/股息率 + 52周高低（腾讯接口）"""
import json
import time
import urllib.request

STOCKS = [
    # 代码, 名称, 板块
    ("sh601138", "工业富联"), ("sh600487", "亨通光电"),
    ("sz002415", "海康威视"), ("sz002475", "立讯精密"), ("sz002371", "北方华创"),
    ("sh603501", "豪威集团"), ("sh688981", "中芯国际"), ("sh603019", "中科曙光"),
    ("sh600584", "长电科技"), ("sz000021", "深科技"), ("sz002273", "水晶光电"),
    ("sh601766", "中国中车"), ("sh600406", "国电南瑞"), ("sh600031", "三一重工"),
    ("sz002241", "歌尔股份"),
    ("sh600519", "贵州茅台"), ("sh600809", "山西汾酒"), ("sz000568", "泸州老窖"),
    ("sh600887", "伊利股份"), ("sz000895", "双汇发展"), ("sh603288", "海天味业"),
    ("sh600309", "万华化学"),
    ("sz000333", "美的集团"), ("sz000651", "格力电器"), ("sh600690", "海尔智家"),
    ("sh600276", "恒瑞医药"), ("sz300760", "迈瑞医疗"), ("sz000538", "云南白药"),
    ("sh600436", "片仔癀"), ("sh603259", "药明康德"),
    ("sh601318", "中国平安"), ("sh600030", "中信证券"), ("sz000776", "广发证券"),
    ("sh601939", "建设银行"), ("sh601328", "交通银行"),
    ("sz300750", "宁德时代"), ("sz002594", "比亚迪"), ("sz300274", "阳光电源"),
    ("sh600660", "福耀玻璃"), ("sh601633", "长城汽车"),
    ("sh600900", "长江电力"), ("sh601088", "中国神华"), ("sh601225", "陕西煤业"),
    ("sh600938", "中国海油"), ("sh600028", "中国石化"), ("sh600011", "华能国际"),
    ("sh600674", "川投能源"), ("sh600886", "国投电力"), ("sh601899", "紫金矿业"),
    ("sh601600", "中国铝业"), ("sh603993", "洛阳钼业"),
    ("sz000063", "中兴通讯"), ("sz002714", "牧原股份"), ("sh601668", "中国建筑"),
    ("sz300124", "汇川技术"),
]

def fetch_quote(codes):
    """实时行情：现价/PE/PB/股息率。返回 {code: {...}}"""
    result = {}
    for i in range(0, len(codes), 20):
        batch = codes[i:i + 20]
        url = "http://qt.gtimg.cn/q=" + ",".join(batch)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=15).read().decode("gbk", errors="ignore")
        for line in data.strip().split(";"):
            line = line.strip()
            if not line or "=" not in line:
                continue
            body = line.split("=", 1)[1].strip().strip('"')
            f = body.split("~")
            if len(f) < 50:
                continue
            code = f[2]
            result[code] = {
                "price": float(f[3]) if f[3] else 0,
                "chg_pct": f[32] if len(f) > 32 else "",
                "date": f[30] if len(f) > 30 else "",
                "pe": f[39] if len(f) > 39 else "",
                "pb": f[46] if len(f) > 46 else "",
                "div_yield": f[52] if len(f) > 52 else "",
                "amount_wan": f[37] if len(f) > 37 else "",
            }
        time.sleep(0.2)
    return result

def fetch_52w_high_low(code):
    """K线接口取260个交易日高低（前复权）。返回 (high, low)"""
    try:
        url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},day,,,260,qfq"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="ignore")
        j = json.loads(data)
        node = j["data"][code]
        key = "qfqday" if "qfqday" in node else ("day" if "day" in node else None)
        if not key:
            return None, None
        rows = node[key]
        highs = [float(r[3]) for r in rows if len(r) >= 5 and r[3]]
        lows = [float(r[4]) for r in rows if len(r) >= 5 and r[4]]
        if not highs or not lows:
            return None, None
        return max(highs), min(lows)
    except Exception as e:
        return None, None

# 主流程
codes = [c for c, _ in STOCKS]
quotes = fetch_quote(codes)

print("code,name,date,price,chg_pct,52w_high,52w_low,pe,pb,div_yield,amount_wan")
out = []
for code, name in STOCKS:
    q = quotes.get(code[2:], {})  # 接口返回纯数字代码，去掉sh/sz前缀匹配
    h, l = fetch_52w_high_low(code)
    price = q.get("price", 0)
    pct = price / (price - float(q.get("chg_pct") or 0) / 100 * price) - 1 if price else 0
    out.append({
        "code": code, "name": q.get("name", name), "date": q.get("date", ""),
        "price": price, "chg": q.get("chg_pct", ""), "h": h, "l": l,
        "pe": q.get("pe", ""), "pb": q.get("pb", ""), "div": q.get("div_yield", ""),
        "amt": q.get("amount_wan", ""),
    })
    print(f"{code},{q.get('name', name)},{q.get('date','')},{price},{q.get('chg_pct','')},{h},{l},{q.get('pe','')},{q.get('pb','')},{q.get('div_yield','')},{q.get('amount_wan','')}")
    time.sleep(0.15)

with open("_lowbuy_v6_data.json", "w", encoding="utf-8") as fp:
    json.dump(out, fp, ensure_ascii=False, indent=1)
print("saved _lowbuy_v6_data.json")
