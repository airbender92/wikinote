# -*- coding: utf-8 -*-
"""2026-08-26 收盘行情：指数+持仓5只+观察池55只（腾讯行情接口，批量<=18/批，GBK）"""
import json
import urllib.request

# 指数
INDEX = [("sh000001", "上证指数"), ("sz399001", "深证成指"), ("sz399006", "创业板指"), ("sh000688", "科创50")]

# 持仓5只（8/26晚间口径）
HOLD = [("sz000538", "云南白药"), ("sz002594", "比亚迪"), ("sh600406", "国电南瑞"), ("sh600886", "国投电力"), ("sh600999", "招商证券")]

# 观察池55只（代码, 名称）
WATCH = [
    ("sh601138", "工业富联"), ("sh600487", "亨通光电"),
    ("sz002415", "海康威视"), ("sz002475", "立讯精密"), ("sz002371", "北方华创"), ("sh603501", "豪威集团"),
    ("sh688981", "中芯国际"), ("sh603019", "中科曙光"), ("sh600584", "长电科技"), ("sz000021", "深科技"), ("sz002273", "水晶光电"),
    ("sh601766", "中国中车"), ("sh600406", "国电南瑞"), ("sh600031", "三一重工"), ("sz002241", "歌尔股份"),
    ("sh600519", "贵州茅台"), ("sh600809", "山西汾酒"), ("sz000568", "泸州老窖"), ("sh600887", "伊利股份"),
    ("sz000895", "双汇发展"), ("sh603288", "海天味业"), ("sh600309", "万华化学"),
    ("sz000333", "美的集团"), ("sz000651", "格力电器"), ("sh600690", "海尔智家"),
    ("sh600276", "恒瑞医药"), ("sz300760", "迈瑞医疗"), ("sz000538", "云南白药"), ("sh600436", "片仔癀"), ("sh603259", "药明康德"),
    ("sh601318", "中国平安"), ("sh600030", "中信证券"), ("sz000776", "广发证券"), ("sh601939", "建设银行"), ("sh601328", "交通银行"),
    ("sz300750", "宁德时代"), ("sz002594", "比亚迪"), ("sz300274", "阳光电源"), ("sh600660", "福耀玻璃"), ("sh601633", "长城汽车"),
    ("sh600900", "长江电力"), ("sh601088", "中国神华"), ("sh601225", "陕西煤业"), ("sh600938", "中国海油"), ("sh600028", "中国石化"),
    ("sh600011", "华能国际"), ("sh600674", "川投能源"), ("sh600886", "国投电力"), ("sh601899", "紫金矿业"), ("sh601600", "中国铝业"), ("sh603993", "洛阳钼业"),
    ("sz000063", "中兴通讯"), ("sz002714", "牧原股份"), ("sh601668", "中国建筑"), ("sz300124", "汇川技术"),
]

def fetch_quotes(codes, debug=False):
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
            if debug and code == codes[0][0]:
                for idx, val in enumerate(f[:55]):
                    print(f"  [{idx}] {val}")
            name = next((n for c, n in batch if c == code), f[1])
            out.append({
                "code": code, "name": name,
                "price": _f(f[3]), "preclose": _f(f[4]), "open": _f(f[5]),
                "vol_hand": _f(f[6]), "time": f[30],
                "chg": _f(f[31]), "pct": _f(f[32]),
                "high": _f(f[33]), "low": _f(f[34]),
                "amount_wan": _f(f[37]), "turnover": _f(f[38]),
                "pe": _f(f[39]), "pb": _f(f[46]), "mktcap_wan": _f(f[45]),
            })
    return out

def _f(s):
    try:
        return float(s)
    except (ValueError, TypeError):
        return 0.0

if __name__ == "__main__":
    print("== 字段探测（指数sh000001） ==")
    probe = fetch_quotes([("sh000001", "上证指数")], debug=True)
    print("== 拉取数据 ==")
    result = {"index": fetch_quotes(INDEX), "hold": fetch_quotes(HOLD), "watch": fetch_quotes(WATCH)}
    with open("_close_20260826.json", "w", encoding="utf-8") as fp:
        json.dump(result, fp, ensure_ascii=False, indent=1)
    print("== 指数 ==")
    for it in result["index"]:
        print(f"{it['name']}: {it['price']} ({it['pct']:+.2f}%) 成交额{it['amount_wan']/10000:.0f}亿 高{it['high']} 低{it['low']}")
    print("== 持仓 ==")
    for it in result["hold"]:
        print(f"{it['name']}: {it['price']} ({it['pct']:+.2f}%) 高{it['high']} 低{it['low']} 换手{it['turnover']}% PE{it['pe']} PB{it['pb']}")
    print("== 观察池涨跌幅前10 ==")
    ws = sorted(result["watch"], key=lambda x: -x["pct"])
    for it in ws[:10]:
        print(f"{it['name']}: {it['price']} ({it['pct']:+.2f}%)")
