# -*- coding: utf-8 -*-
"""生成科技成长板块 × 金融危机情景分析 HTML"""
import json

with open("F:/codes/wikinote/docs/金融危机/assets/tech50.json", encoding="utf-8") as f:
    stocks = json.load(f)

CAT_COLOR = {
    "泡沫高危(最深跌)": "#c62828",
    "高风险高弹性": "#6a1b9a",
    "高弹性进攻": "#1565c0",
    "攻守平衡": "#2e7d32",
}

rows = ""
for i, s in enumerate(stocks, 1):
    c = CAT_COLOR.get(s["cat"], "#555")
    board_badge = {"科创板": "科创", "创业板": "创业", "沪主板": "沪主", "深主板": "深主"}[s["board"]]
    board_color = {"科创": "#7b1fa2", "创业": "#00838f", "沪主": "#1565c0", "深主": "#2e7d32"}[board_badge]
    pe_disp = "亏损" if s["pe"] < 0 else f'{s["pe"]:.0f}'
    rows += f"""<tr>
<td class="rk">{i}</td>
<td class="nm"><b>{s["name"]}</b><span class="code">{s["code"][2:]}</span><br><span class="badge" style="background:{board_color}">{board_badge}</span></td>
<td>{s["tag"]}</td>
<td>{pe_disp}</td>
<td>{s["pb"]:.1f}</td>
<td>{s["ytd"]:.0f}%</td>
<td style="color:{c};font-weight:600">{s["cat"]}</td>
<td>{s["def_score"]:.0f}</td>
<td>{s["el_score"]:.0f}</td>
<td>{s["risk_score"]:.0f}</td>
<td>{s["pre"]} → {s["mid"]} → <b>{s["post"]}</b></td>
<td><span class="zone">{s["low_zone"][0]} ~ {s["low_zone"][1]}</span><br><span class="ph">现价{s["price"]} · 52周低{s["l52"]}</span></td>
</tr>"""

scatter = []
for s in stocks:
    scatter.append(
        f'{{value:[{s["def_score"]},{s["el_score"]}],name:"{s["name"]}({s["board"]})",'
        f'itemStyle:{{color:"{CAT_COLOR.get(s["cat"],"#555")}"}},'
        f'symbolSize:{max(8,min(18,s["mv"]/1000))},'
        f'lowZone:"{s["low_zone"][0]}~{s["low_zone"][1]}",price:"{s["price"]}",'
        f'def:{s["def_score"]},el:{s["el_score"]},risk:{s["risk_score"]},tag:"{s["tag"]}"}}'
    )

html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>科技成长板块 × 金融危机情景分析（补充专题）</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:#f7f8fa;color:#1f2329;line-height:1.6}
.wrap{max-width:1180px;margin:0 auto;padding:24px 20px 60px}
.hero{background:linear-gradient(135deg,#fff5f5,#fff);border:1px solid #f0e0e0;border-radius:16px;padding:28px 32px;margin-bottom:20px}
.hero h1{font-size:24px;color:#b71c1c;margin-bottom:8px}
.hero .sub{color:#666;font-size:14px}
.hero .meta{display:flex;flex-wrap:wrap;gap:10px;margin-top:16px}
.chip{background:#fff;border:1px solid #e5e5e5;border-radius:20px;padding:6px 14px;font-size:12px;color:#444}
.chip b{color:#b71c1c}
.reason{background:#fff8e1;border:1px solid #ffe082;border-radius:14px;padding:18px 24px;margin-bottom:20px}
.reason h2{font-size:16px;color:#8d6e00;margin-bottom:10px}
.reason p{font-size:13.5px;color:#6d5a00;margin-bottom:8px}
.section{background:#fff;border:1px solid #eee;border-radius:14px;padding:22px 26px;margin-bottom:20px}
.section h2{font-size:18px;margin-bottom:14px;color:#222;border-left:4px solid #b71c1c;padding-left:10px}
#scatter{width:100%;height:480px}
table{width:100%;border-collapse:collapse;font-size:12.5px}
th{background:#fafafa;color:#555;font-weight:600;padding:9px 8px;text-align:left;border-bottom:2px solid #eee;white-space:nowrap;position:sticky;top:0}
td{padding:8px;border-bottom:1px solid #f2f2f2;vertical-align:middle}
tr:hover{background:#fafafa}
.rk{color:#999;font-weight:600}
.nm b{font-size:13px}
.code{color:#aaa;font-size:11px;margin-left:6px}
.badge{display:inline-block;color:#fff;border-radius:4px;padding:1px 6px;font-size:10px;margin-top:3px}
.zone{font-weight:600;color:#b71c1c}
.ph{color:#999;font-size:11px}
.note{background:#fffbe6;border:1px solid #ffe58f;border-radius:10px;padding:14px 18px;font-size:12.5px;color:#8c6d1f;margin-top:18px}
.note b{color:#ad6800}
.footer{text-align:center;color:#999;font-size:12px;margin-top:30px}
@media(max-width:720px){.wrap{padding:12px}.hero{padding:18px}td{font-size:11px}th{font-size:11px}}
</style>
</head>
<body>
<div class="wrap">

<div class="hero">
<h1>🔴 科技成长板块 × 金融危机情景分析（补充专题）</h1>
<div class="sub">聚焦当前最火爆的 AI算力 / 半导体 / 消费电子科技股，纳入同一危机评分模型（数据：腾讯自选股 2026-08-07 收盘）</div>
<div class="meta">
<span class="chip">覆盖 <b>30</b> 只科技龙头</span>
<span class="chip">含 <b>科创板</b> · <b>创业板</b> · <b>沪深主板</b></span>
<span class="chip">景气主线：AI算力 / 半导体设备 / AI芯片 / 存储 / 消费电子</span>
</div>
</div>

<div class="reason">
<h2>❓ 为什么上一份「50标的」报告里没有它们？</h2>
<p><b>原因1（口径）：</b>上一份报告按你的要求严格限定<b>沪深主板</b>，而当前最火爆的科技股（寒武纪、中芯国际、海光信息、澜起科技、中微公司等）几乎全部在<b>科创板/创业板</b>；主板内的科技龙头（兆易创新、北方华创、生益科技等）虽入选候选池，但按"防御×弹性×风险"综合分排序时被高分蓝筹挤出前50。</p>
<p><b>原因2（模型）：</b>危机评分模型把<b>风险分</b>（估值泡沫+高Beta）权重设得很高，科技股 PE 普遍 50~300 倍、Beta≈1，风险分极高 → 在"避险型"框架下天然垫底。但这恰恰说明：<b>科技股不是避险品种，而是"危机中跌最深、政策底后反弹最猛"的进攻品种</b>，应单独一套打法。</p>
<p><b>本专题结论：</b>科技股在危机三阶段中表现最极端——前期高位深跌（-40%~-70%）、中期恐慌深跌、后期政策底（新质生产力/科技自立）大反弹（+50%~150%）。<b>适合"政策底确认后"低吸进攻，绝不适合作为危机初期避险仓。</b></p>
</div>

<div class="section">
<h2>📊 定位散点图（X=防御分，Y=弹性分）——科技股整体偏右下：低防御、高弹性</h2>
<div id="scatter"></div>
</div>

<div class="section">
<h2>📋 科技龙头危机情景清单（30只）</h2>
<table>
<thead>
<tr><th>#</th><th>标的</th><th>景气主线</th><th>PE</th><th>PB</th><th>年内涨幅</th><th>分类</th><th>防御</th><th>弹性</th><th>风险</th><th>危机三阶段</th><th>低吸区间</th></tr>
</thead>
<tbody>
__ROWS__
</tbody>
</table>
</div>

<div class="note">
<b>⚠️ 风险提示：</b>科技股 PE 普遍处于历史高位（寒武纪277x、海光252x、华虹945x、中芯218x），泡沫破裂时回撤可远超一般蓝筹（2000年纳指 -78% 即为前车之鉴）。本表低吸区间为<b>情景推算</b>，其中"泡沫高危"类（红标）应<b>等待政策底右侧信号</b>（汇金增持/降准降息/产业政策落地）再分批介入，且严格控制仓位。数据时点 2026-08-07，不构成投资建议。
</div>

<div class="footer">数据来源：腾讯自选股接口（2026-08-07收盘）· 模型：wb-finance 危机情景评分 · 仅供研究学习</div>

<script>
var chart = echarts.init(document.getElementById('scatter'));
chart.setOption({
  tooltip: {
    trigger: 'item',
    formatter: function(p) {
      var d = p.data;
      return '<b>' + d.name + '</b><br>主线:' + d.tag + '<br>防御分:' + d.def + ' 弹性分:' + d.el + ' 风险分:' + d.risk + '<br>低吸区间:' + d.lowZone + '<br>现价:' + d.price;
    }
  },
  grid: { left: 60, right: 40, top: 40, bottom: 55 },
  xAxis: { type: 'value', name: '防御分（抗跌）', min: 15, max: 60 },
  yAxis: { type: 'value', name: '弹性分（反弹）', min: 55, max: 90 },
  series: [{
    type: 'scatter',
    data: [__SCATTER__],
    label: { show: false },
    emphasis: { label: { show: true, fontSize: 12, fontWeight: 'bold' } },
    markLine: {
      silent: true,
      symbol: 'none',
      lineStyle: { type: 'dashed', color: '#ccc' },
      data: [ { xAxis: 45 }, { yAxis: 72 } ]
    }
  }]
});
</script>
</body>
</html>
"""

html = html.replace("__ROWS__", rows).replace("__SCATTER__", ",".join(scatter))
out = "F:/codes/wikinote/docs/金融危机/科技成长板块-金融危机情景分析.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print("HTML 已生成:", out)
