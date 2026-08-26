# -*- coding: utf-8 -*-
"""拉取2026-08-26开盘前行情：持仓6只 + 关键指数 + 低吸候选（数据截至8/25收盘）"""
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
            out.append(f"{b[2]} {b[1]} 现价{b[3]} 涨跌{b[31]}({b[32]}%) 开{b[5]} 高{b[33]} 低{b[34]} 昨收{b[4]} 量{b[6]}手 额{b[37]}万 52周高{b[47] if len(b)>47 else '-'} 52周低{b[48] if len(b)>48 else '-'}")
        except Exception as e:
            out.append(f"PARSE_ERR: {line[:60]} -> {e}")
    return "\n".join(out)

if __name__ == "__main__":
    groups = {
        "持仓6只": ["sh603993", "sh600999", "sh600886", "sh600406", "sz002594", "sz000538"],
        "指数": ["sh000001", "sz399001", "sz399006", "sh000688", "sh000300", "sz399905"],
        "低吸候选A": ["sh603019", "sh600030", "sh600809", "sz000651", "sh600276",
                      "sh601318", "sh600011", "sh601899", "sh600887", "sh603288",
                      "sh600309", "sh600436", "sh600938", "sh600660", "sh603501",
                      "sz000021", "sz002273", "sz002475", "sz000568", "sh600690"],
        "低吸候选B": ["sh601328", "sh600028", "sh601600", "sh601633", "sh600674",
                      "sz002714", "sh601668", "sh601088", "sh601225", "sz000333",
                      "sh601939", "sz000895", "sh600519", "sh601138", "sh600487",
                      "sz002415", "sh688981", "sh600584", "sz300750", "sz000776"],
        "低吸候选C": ["sh601766", "sz002241", "sz300760", "sz300274", "sz300124",
                      "sh603259", "sh600900", "sh601988", "sz000858", "sh600703",
                      "sh601179", "sz000938", "sh601377"],
    }
    for gname, codes in groups.items():
        print("=" * 25, gname, "=" * 25)
        print(parse(fetch(codes)))
