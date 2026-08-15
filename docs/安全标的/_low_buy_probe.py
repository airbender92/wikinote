# -*- coding: utf-8 -*-
import urllib.request, json, ssl, time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
HDR = {'User-Agent':'Mozilla/5.0'}

# 55只：名称->代码（含🔒不可交易标注）
stocks = [
    ("工业富联","601138"),("亨通光电","600487"),("海康威视","002415"),("立讯精密","002475"),
    ("北方华创","002371"),("豪威集团","603501"),("中芯国际","688981","LOCK"),("中科曙光","603019"),
    ("长电科技","600584"),("深科技","000021"),("水晶光电","002273"),("中国中车","601766"),
    ("国电南瑞","600406"),("三一重工","600031"),("歌尔股份","002241"),("贵州茅台","600519"),
    ("山西汾酒","600809"),("泸州老窖","000568"),("伊利股份","600887"),("双汇发展","000895"),
    ("海天味业","603288"),("万华化学","600309"),("美的集团","000333"),("格力电器","000651"),
    ("海尔智家","600690"),("恒瑞医药","600276"),("迈瑞医疗","300760","LOCK"),("云南白药","000538"),
    ("片仔癀","600436"),("药明康德","603259"),("中国平安","601318"),("中信证券","600030"),
    ("广发证券","000776"),("建设银行","601939"),("交通银行","601328"),("宁德时代","300750","LOCK"),
    ("比亚迪","002594"),("阳光电源","300274","LOCK"),("福耀玻璃","600660"),("长城汽车","601633"),
    ("长江电力","600900"),("中国神华","601088"),("陕西煤业","601225"),("中国海油","600938"),
    ("中国石化","600028"),("华能国际","600011"),("川投能源","600674"),("国投电力","600886"),
    ("紫金矿业","601899"),("中国铝业","601600"),("洛阳钼业","603993"),
    ("中兴通讯","000063"),("牧原股份","002714"),("中国建筑","601668"),("汇川技术","300124","LOCK"),
]

def prefix(code):
    return ("sh" if code[0] in "56" else "sz") + code

def get_quote(codes):
    """腾讯实时接口，批量<=20，GBK，返回 dict code->(现价, PE)"""
    out = {}
    for i in range(0, len(codes), 20):
        batch = codes[i:i+20]
        url = "https://qt.gtimg.cn/q=" + ",".join(prefix(c) for c in batch)
        req = urllib.request.Request(url, headers=HDR)
        raw = urllib.request.urlopen(req, context=ctx, timeout=15).read().decode("gbk", errors="ignore")
        for line in raw.strip().split(";"):
            if "~" not in line: continue
            parts = line.split("~")
            if len(parts) < 47: continue
            code = parts[2]
            price = parts[3]
            pe = parts[39] if len(parts) > 39 else ""
            out[code] = (price, pe)
        time.sleep(0.3)
    return out

def get_52w(code):
    """日K 260根，qfq，返回 (52周高, 52周低, 最新收盘)"""
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={prefix(code)},day,,,260,qfq"
    req = urllib.request.Request(url, headers=HDR)
    data = json.loads(urllib.request.urlopen(req, context=ctx, timeout=15).read().decode("utf-8"))
    node = data["data"][prefix(code)]
    days = node.get("qfqday") or node.get("day")
    highs = [float(d[3]) for d in days]
    lows = [float(d[4]) for d in days]
    closes = [float(d[2]) for d in days]
    return max(highs), min(lows), closes[-1]

print("名称,代码,现价,PE,52周高,52周低,分位%,距高点%,L", flush=True)
codes = [s[1] for s in stocks]
quotes = get_quote(codes)
for s in stocks:
    name, code = s[0], s[1]
    lock = "LOCK" if len(s) > 2 else ""
    try:
        price_q, pe = quotes.get(code, ("", ""))
        h52, l52, close = get_52w(code)
        price = float(price_q) if price_q else close
        pct = (price - l52) / (h52 - l52) * 100
        dist_hi = (price / h52 - 1) * 100
        print(f"{name},{code},{price:.2f},{pe},{h52:.2f},{l52:.2f},{pct:.1f},{dist_hi:.1f},{lock}", flush=True)
        time.sleep(0.15)
    except Exception as e:
        print(f"{name},{code},ERR,{e}", flush=True)
