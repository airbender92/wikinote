# -*- coding: utf-8 -*-
"""获取持仓6只+指数最新收盘行情（腾讯接口，GBK）"""
import urllib.request

codes = [
    "sh000001", "sz399001", "sz399006", "sh000688",  # 指数
    "sz000538",  # 云南白药
    "sz002594",  # 比亚迪
    "sh600406",  # 国电南瑞
    "sh600886",  # 国投电力
    "sh600999",  # 招商证券
    "sh600276",  # 恒瑞医药
    "sh601318",  # 中国平安(参考)
    "sz000001",  # 平安银行(参考)
]
url = "http://qt.gtimg.cn/q=" + ",".join(codes)
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
data = urllib.request.urlopen(req, timeout=10).read().decode("gbk", errors="ignore")

for line in data.strip().split(";"):
    line = line.strip()
    if not line or "=" not in line:
        continue
    body = line.split("=", 1)[1].strip().strip('"')
    fields = body.split("~")
    if len(fields) < 40:
        continue
    name = fields[1]
    code = fields[2]
    price = fields[3]        # 现价
    prev_close = fields[4]   # 昨收
    change_pct = fields[32]  # 涨跌幅%
    high = fields[33]
    low = fields[34]
    vol = fields[6]          # 成交量(手)
    amount = fields[37]      # 成交额(万)
    date = fields[30]
    print(f"{name}({code}) 日期{date} 收{price} 涨跌幅{change_pct}% 高{high} 低{low} 成交额{amount}万")
