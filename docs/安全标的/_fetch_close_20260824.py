# -*- coding: utf-8 -*-
"""2026-08-24 开盘前数据拉取：A股指数 + 持仓6只（歌尔已清仓）+ 重点观察标的（腾讯行情接口，周五8/21收盘数据）"""
import urllib.request
import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="ignore")

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
            "name": f[1], "code": f[2],
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

# 持仓6只（歌尔8/24早用户确认23.43清空）
HOLD = {
    "sz000538": {"name": "云南白药", "hands": 4, "cost": 50.685},
    "sz002594": {"name": "比亚迪", "hands": 3, "cost": 89.187},
    "sh600406": {"name": "国电南瑞", "hands": 5, "cost": 23.854},
    "sh600886": {"name": "国投电力", "hands": 4, "cost": 13.970},
    "sh600999": {"name": "招商证券", "hands": 8, "cost": 19.100},
    "sh603993": {"name": "洛阳钼业", "hands": 8, "cost": 18.284},
}

# 已清仓确认 + 重点观察（今日低吸/映射相关）
WATCH = {
    "sz002241": "歌尔股份(已清仓确认)",
    "sh600028": "中国石化", "sh600938": "中国海油", "sh600011": "华能国际",
    "sh601899": "紫金矿业", "sh601600": "中国铝业", "sh603993": "洛阳钼业",
    "sh600487": "亨通光电", "sh603019": "中科曙光", "sz000021": "深科技",
    "sz000651": "格力电器", "sh600887": "伊利股份", "sh600030": "中信证券",
    "sh600276": "恒瑞医药", "sh600519": "贵州茅台", "sh601318": "中国平安",
    "sh600809": "山西汾酒", "sz000568": "泸州老窖", "sh600309": "万华化学",
    "sh600690": "海尔智家", "sh600674": "川投能源", "sh600900": "长江电力",
}

def main():
    allcodes = INDEX_CODES + list(HOLD.keys()) + list(WATCH.keys())
    result = {}
    for i in range(0, len(allcodes), 20):
        batch = allcodes[i:i+20]
        try:
            result.update(fetch_batch(batch))
        except Exception as e:
            print("ERR batch", batch[:3], e, file=sys.stderr)

    print("===INDEX(2026-08-21收盘)===")
    for c in INDEX_CODES:
        if c in result:
            r = result[c]
            print(f"{INDEX_LABEL[c]}\t{c}\t收盘{r['price']:.2f}\t涨跌{r['pct']:+.2f}%\t成交额{r['amount_wan']/10000:.0f}亿\t振幅{r['amp']:.2f}%")

    print("===HOLD(2026-08-21收盘)===")
    total_val = 0
    total_cost = 0
    for c, h in HOLD.items():
        if c in result:
            r = result[c]
            shares = h["hands"] * 100
            val = shares * r["price"]
            cost_val = shares * h["cost"]
            pnl = val - cost_val
            pnl_pct = (r["price"] / h["cost"] - 1) * 100
            total_val += val
            total_cost += cost_val
            print(f"{h['name']}\t{c}\t收盘{r['price']:.3f}\t{r['pct']:+.2f}%\t成本{h['cost']:.3f}\t市值{val:.0f}\t浮盈亏{pnl:+.0f}({pnl_pct:+.1f}%)\t换手{r['turnover']:.1f}%\tPE{r['pe_ttm']:.1f}")
    print(f"持仓总市值(股票部分)≈{total_val:.0f}元，总成本≈{total_cost:.0f}元，整体浮盈亏≈{total_val-total_cost:+.0f}元")

    print("===WATCH(2026-08-21收盘)===")
    for c, label in WATCH.items():
        if c in result:
            r = result[c]
            extra = f"({label})" if label != c else ""
            print(f"{r['name']}\t{c}\t{r['price']:.2f}\t{r['pct']:+.2f}%\t成交{r['amount_wan']/10000:.1f}亿\t换手{r['turnover']:.1f}%\tPE{r['pe_ttm']:.1f}\t{extra}")

if __name__ == "__main__":
    main()
