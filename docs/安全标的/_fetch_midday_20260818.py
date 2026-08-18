# -*- coding: utf-8 -*-
"""拉取2026-08-18午盘行情：持仓8只 + 关键指数 + 观察池热点（含分时强弱）"""
import urllib.request

def fetch(codes):
    url = "http://qt.gtimg.cn/q=" + ",".join(codes)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=15).read()
    return raw.decode("gbk", errors="ignore")

def parse(txt):
    out = []
    for line in txt.strip().split(";"):
        line = line.strip()
        if not line:
            continue
        try:
            b = line.split("~")
            name = b[1]; code = b[2]
            price = b[3]; prev = b[4]; opn = b[5]
            chg = b[31]; pct = b[32]
            high = b[33]; low = b[34]
            vol = b[6]; amount = b[37] if len(b) > 37 else ""
            t = b[30] if len(b) > 30 else ""
            # 分时：现价相对均价(b[9]为均价)的强弱
            avg = b[9] if len(b) > 9 else ""
            strong = ""
            if avg and price:
                try:
                    d = (float(price) - float(avg)) / float(avg) * 100
                    strong = f"较均价{'+' if d >= 0 else ''}{d:.2f}%"
                except Exception:
                    pass
            out.append(f"{code} {name} 现价{price} 涨跌{chg}({pct}%) 开{opn} 高{high} 低{low} 昨收{prev} 均价{avg} {strong} 量{vol}手 额{amount}万 时间{t}")
        except Exception as e:
            out.append(f"PARSE_ERR: {line[:80]} -> {e}")
    return "\n".join(out)

if __name__ == "__main__":
    groups = {
        "持仓8只": ["sh601766", "sz000538", "sz002241", "sz002594",
                    "sh600406", "sh600886", "sh600999", "sh603993"],
        "指数": ["sh000001", "sz399001", "sz399006", "sh000688", "sh000300", "bj899050"],
        "观察池热点(存储/光通信/券商/农业/石油)": ["sh600584", "sz000021", "sh600487", "sz002475",
                                            "sh601138", "sh600030", "sz000776", "sh600519",
                                            "sh600028", "sh601088", "sh601899", "sh600406"],
    }
    for gname, codes in groups.items():
        print("=" * 20, gname, "=" * 20)
        print(parse(fetch(codes)))
