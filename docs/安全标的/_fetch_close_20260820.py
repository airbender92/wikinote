# -*- coding: utf-8 -*-
"""2026-08-20 收盘数据拉取：A股指数 + 观察池55只 + 持仓7只（腾讯行情接口）+ 涨跌家数（东财）"""
import urllib.request
import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="ignore")

# 批量≤20只/批
def fetch_batch(codes):
    url = "http://qt.gtimg.cn/q=" + ",".join(codes)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://gu.qq.com/"})
    data = urllib.request.urlopen(req, timeout=15).read().decode("gbk", errors="ignore")
    out = {}
    for line in data.strip().split(";"):
        line = line.strip()
        if not line or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip().replace("v_", "")
        v = v.strip().strip('"')
        f = v.split("~")
        if len(f) < 40:
            continue
        out[k] = {
            "name": f[1],
            "code": f[2],
            "price": float(f[3]) if f[3] else 0,
            "prev": float(f[4]) if f[4] else 0,
            "open": float(f[5]) if f[5] else 0,
            "pct": float(f[32]) if f[32] else 0,
            "high": float(f[33]) if f[33] else 0,
            "low": float(f[34]) if f[34] else 0,
            "vol_hand": float(f[36]) if f[36] else 0,
            "amount_wan": float(f[37]) if f[37] else 0,
            "turnover": float(f[38]) if f[38] else 0,
            "pe_ttm": float(f[39]) if f[39] else 0,
            "amp": float(f[43]) if f[43] else 0,
            "pb": float(f[46]) if f[46] else 0,
        }
    return out

INDEX_CODES = ["sh000001", "sz399001", "sz399006", "sh000688", "sh000300", "sh000016", "sz399905"]
INDEX_LABEL = {
    "sh000001": "上证指数", "sz399001": "深证成指", "sz399006": "创业板指",
    "sh000688": "科创50", "sh000300": "沪深300", "sh000016": "上证50", "sz399905": "中证500",
}

# 55只观察池（沪深主板+创/科观察5只）
POOL = [
    # 通信/算力
    "sh601138", "sh600487",
    # 科技/半导体
    "sz002415", "sz002475", "sz002371", "sh603501", "sh688981", "sh603019", "sh600584", "sz000021", "sz002273",
    # 高端制造/电力设备
    "sh601766", "sh600406", "sh600031", "sz002241",
    # 消费/食品饮料
    "sh600519", "sh600809", "sz000568", "sh600887", "sz000895", "sh603288", "sh600309",
    # 家电
    "sz000333", "sz000651", "sh600690",
    # 医药/医疗
    "sh600276", "sz300760", "sz000538", "sh600436", "sh603259",
    # 金融
    "sh601318", "sh600030", "sz000776", "sh601939", "sh601328",
    # 新能源/汽车
    "sz300750", "sz002594", "sz300274", "sh600660", "sh601633",
    # 能源/资源/公用
    "sh600900", "sh601088", "sh601225", "sh600938", "sh600028", "sh600011", "sh600674", "sh600886", "sh601899", "sh601600", "sh603993",
    # 降级观察
    "sz000063", "sz002714", "sh601668", "sz300124",
]

# 持仓（8/20晚用户确认：中车已清仓@6.27，持仓7只）
HOLD = {
    "sz000538": {"name": "云南白药", "hands": 4, "cost": 50.685},
    "sz002241": {"name": "歌尔股份", "hands": 1, "cost": 4.045},
    "sz002594": {"name": "比亚迪", "hands": 3, "cost": 89.187},
    "sh600406": {"name": "国电南瑞", "hands": 5, "cost": 23.854},
    "sh600886": {"name": "国投电力", "hands": 4, "cost": 13.970},
    "sh600999": {"name": "招商证券", "hands": 8, "cost": 19.100},
    "sh603993": {"name": "洛阳钼业", "hands": 8, "cost": 18.284},
}

def fetch_updown():
    """东财：上证+深证涨跌家数"""
    try:
        url = "https://push2.eastmoney.com/api/qt/stock/get?secid=1.000001&fields=f104,f105,f106"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        d = json.loads(urllib.request.urlopen(req, timeout=15).read().decode("utf-8"))
        print(f"===UPDOWN(上证)===")
        if d.get("data"):
            print(f"上证上涨{d['data'].get('f104')} 下跌{d['data'].get('f105')} 平盘{d['data'].get('f106')}")
        url2 = "https://push2.eastmoney.com/api/qt/stock/get?secid=0.399001&fields=f104,f105,f106"
        req2 = urllib.request.Request(url2, headers={"User-Agent": "Mozilla/5.0"})
        d2 = json.loads(urllib.request.urlopen(req2, timeout=15).read().decode("utf-8"))
        if d2.get("data"):
            print(f"深证上涨{d2['data'].get('f104')} 下跌{d2['data'].get('f105')} 平盘{d2['data'].get('f106')}")
    except Exception as e:
        print("UPDOWN ERR", e, file=sys.stderr)

def main():
    allcodes = INDEX_CODES + POOL + list(HOLD.keys())
    result = {}
    for i in range(0, len(allcodes), 20):
        batch = allcodes[i:i+20]
        try:
            result.update(fetch_batch(batch))
        except Exception as e:
            print("ERR batch", batch[:3], e, file=sys.stderr)

    # 输出指数
    print("===INDEX===")
    for c in INDEX_CODES:
        if c in result:
            r = result[c]
            print(f"{INDEX_LABEL[c]}\t{c}\t收盘{r['price']:.2f}\t涨跌{r['pct']:+.2f}%\t成交额{r['amount_wan']/10000:.0f}亿\t振幅{r['amp']:.2f}%")

    # 输出观察池
    print("===POOL===")
    for c in POOL:
        if c in result:
            r = result[c]
            print(f"{r['name']}\t{c}\t{r['price']:.2f}\t{r['pct']:+.2f}%\t成交{r['amount_wan']/10000:.1f}亿\t换手{r['turnover']:.1f}%\tPE{r['pe_ttm']:.1f}")

    # 输出持仓
    print("===HOLD===")
    total_val = 0
    for c, h in HOLD.items():
        if c in result:
            r = result[c]
            shares = h["hands"] * 100
            val = shares * r["price"]
            cost_val = shares * h["cost"]
            pnl = val - cost_val
            pnl_pct = (r["price"] / h["cost"] - 1) * 100
            total_val += val
            print(f"{h['name']}\t{c}\t收盘{r['price']:.3f}\t{r['pct']:+.2f}%\t成本{h['cost']:.3f}\t市值{val:.0f}\t浮盈亏{pnl:+.0f}({pnl_pct:+.1f}%)")
    print(f"持仓总市值(股票部分)≈{total_val:.0f}元")

    fetch_updown()

if __name__ == "__main__":
    main()
