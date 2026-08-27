# -*- coding: utf-8 -*-
"""午盘研判取数 2026-08-27：指数+持仓5只+低吸挂单+板块观察（腾讯接口，GBK，两批）"""
import json
import urllib.request

BATCH1 = [
    "sh000001", "sz399001", "sz399006", "sh000688", "sz399106",  # 上证/深成/创业板/科创50/深证综指(深市总额)
    "sz000538",  # 云南白药
    "sz002594",  # 比亚迪
    "sh600406",  # 国电南瑞
    "sh600886",  # 国投电力
    "sh600999",  # 招商证券
    "sh600011",  # 华能国际(低吸挂单)
    "sz000021",  # 深科技(存储/等不再创新低)
    "sh600276",  # 恒瑞医药(低吸)
    "sh603019",  # 中科曙光(算力/等回踩)
    "sh600938",  # 中国海油(低吸)
    "sh600030",  # 中信证券(低吸)
    "sz300750",  # 宁德时代(观察/不可交易)
    "sz002241",  # 歌尔股份(观察/等回踩)
    "sh600584",  # 长电科技(存储链)
    "sz002463",  # 沪电股份(AI PCB)
]

BATCH2 = [
    "sh688981",  # 中芯国际(科创/观察)
    "sz000776",  # 广发证券(券商)
    "sz002475",  # 立讯精密(苹果链)
    "sh601138",  # 工业富联(AI服务器)
    "sh600487",  # 亨通光电(光通信)
    "sz002415",  # 海康威视(观察)
    "sh600519",  # 贵州茅台(消费)
    "sh600900",  # 长江电力(公用)
    "sh601088",  # 中国神华(煤炭)
    "sh601899",  # 紫金矿业(有色)
    "sz000568",  # 泸州老窖(白酒)
    "sh600887",  # 伊利股份(消费)
    "sh603259",  # 药明康德(高位勿追)
    "sz002273",  # 水晶光电(光学)
    "sh600028",  # 中国石化(能源)
    "sh601939",  # 建设银行(银行)
    "sz000333",  # 美的集团(家电)
    "sh601766",  # 中国中车(已清仓/观察)
    "sh603993",  # 洛阳钼业(已清仓/观察)
    "sz300124",  # 汇川技术(不可交易/观察)
]


def fetch_quote(codes):
    url = "https://qt.gtimg.cn/q=" + ",".join(codes)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://gu.qq.com/"})
    with urllib.request.urlopen(req, timeout=20) as r:
        raw = r.read().decode("gbk", errors="ignore")
    out = {}
    for line in raw.strip().split(";"):
        line = line.strip()
        if not line or "=" not in line:
            continue
        key, val = line.split("=", 1)
        code = key.split("_")[-1]
        fields = val.strip('"').split("~")
        if len(fields) < 46:
            continue
        out[code] = {
            "name": fields[1],
            "code": fields[2],
            "price": float(fields[3]),
            "pre_close": float(fields[4]),
            "open": float(fields[5]),
            "volume": float(fields[6]),        # 手
            "high": float(fields[33]) if fields[33] else None,
            "low": float(fields[34]) if fields[34] else None,
            "change": float(fields[31]),
            "pct": float(fields[32]),
            "amount": float(fields[37]),       # 万元
            "turnover": fields[38],            # 换手率%
            "pe": fields[39],
            "amp": fields[43],                 # 振幅%
            "date_time": fields[30],
        }
    return out


if __name__ == "__main__":
    data = {}
    data.update(fetch_quote(BATCH1))
    data.update(fetch_quote(BATCH2))
    print(json.dumps(data, ensure_ascii=False, indent=1))
