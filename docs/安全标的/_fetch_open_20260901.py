# -*- coding: utf-8 -*-
"""拉取2026-09-01开盘前行情：指数 + 持仓6只 + 观察池重点（数据截至8/31收盘）"""
import urllib.request

def fetch(codes):
    url = "http://qt.gtimg.cn/q=" + ",".join(codes)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=20).read()
    return raw.decode("gbk", errors="ignore")

def parse(txt):
    out = []
    for line in txt.strip().split(";"):
        line = line.strip()
        if not line:
            continue
        try:
            b = line.split("~")
            out.append(f"{b[2]} 现价{b[3]} 涨跌{b[31]}({b[32]}%) 开{b[5]} 高{b[33]} 低{b[34]} 昨收{b[4]} 量{b[6]}手 额{b[37]}万")
        except Exception as e:
            out.append(f"PARSE_ERR: {line[:60]} -> {e}")
    return "\n".join(out)

if __name__ == "__main__":
    groups = {
        "指数": ["sh000001", "sz399001", "sz399006", "sh000688", "sh000300", "sz399905", "sh000016"],
        "持仓6只": ["sz000538", "sz002594", "sh600406", "sh600886", "sh600999", "sh600276"],
        "存储链": ["sh600584", "sz000021", "sh688981", "sz002475", "sh603501", "sh601138", "sh600487", "sz002415", "sz002273", "sz002241"],
        "资源能源": ["sh601899", "sh601088", "sh601225", "sh600028", "sh600938", "sh601600", "sh600309", "sh600900", "sh600674", "sh600011"],
        "医药消费": ["sh600519", "sh600809", "sz000568", "sh603288", "sh600436", "sh603259", "sz000895", "sh600887", "sh603288", "sz300760"],
        "金融地产": ["sh601318", "sh600030", "sz000776", "sh601328", "sh601939", "sz000333", "sh600690", "sz000651", "sh601668", "sh601633"],
        "其他观察": ["sh601766", "sh603993", "sh603019", "sz002714", "sh600660", "sz300750", "sz300274", "sz300124"],
    }
    for gname, codes in groups.items():
        print("=" * 25, gname, "=" * 25)
        print(parse(fetch(codes)))
