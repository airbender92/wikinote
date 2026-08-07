# -*- coding: utf-8 -*-
"""生成 HTML 研报：A股沪深主板优质标的 × 金融危机情景分析"""
import json

with open("F:/codes/wikinote/docs/金融危机/assets/top50.json", encoding="utf-8") as f:
    top50 = json.load(f)

CAT_COLOR = {
    "避险核心": "#c62828",   # 红
    "稳健防御": "#e07b39",   # 橙
    "攻守兼备": "#2e7d32",   # 绿
    "高弹性反弹": "#1565c0", # 蓝
    "高波动弹性": "#6a1b9a", # 紫
}
CAT_DESC = {
    "避险核心": "危机全周期抗跌，避险资金首选",
    "稳健防御": "中期抗跌，后期修复，攻守平衡",
    "攻守兼备": "前期小跌，中期抗跌，后期弹性",
    "高弹性反弹": "前期/中期大跌，政策底后弹性先锋",
    "高波动弹性": "高Beta，深跌深弹，波动剧烈",
}

def fmt(s):
    return s["name"]

rows = ""
for i, s in enumerate(top50, 1):
    c = CAT_COLOR[s["cat"]]
    rows += f"""<tr>
<td class="rk">{i}</td>
<td class="nm"><b>{s["name"]}</b><span class="code">{s["code"][2:]}</span></td>
<td>{s["pe"]:.1f}</td>
<td>{s["pb"]:.2f}</td>
<td>{s["div"]:.2f}%</td>
<td>{s["mv"]/10000:.2f}万亿</td>
<td style="color:{c};font-weight:600">{s["cat"]}</td>
<td>{s["def_score"]:.0f}</td>
<td>{s["el_score"]:.0f}</td>
<td>{s["risk_score"]:.0f}</td>
<td>{s["pre"]}<br><span class="ph">{s["mid"]} → {s["post"]}</span></td>
<td><span class="zone">{s["low_zone"][0]} ~ {s["low_zone"][1]}</span><br><span class="ph">现价{s["price"]}</span></td>
</tr>"""

cat_data = []
for k, v in CAT_DESC.items():
    cat_data.append(f'{{name:"{k}",desc:"{v}",color:"{CAT_COLOR[k]}"}}')

scatter = []
for s in top50:
    scatter.append(
        f'{{value:[{s["def_score"]},{s["el_score"]}],name:"{s["name"]}({s["cat"]})",'
        f'itemStyle:{{color:"{CAT_COLOR[s["cat"]]}"}},'
        f'symbolSize:{max(8,min(20,s["mv"]/1500))},'
        f'lowZone:"{s["low_zone"][0]}~{s["low_zone"][1]}",price:"{s["price"]}",'
        f'def:{s["def_score"]},el:{s["el_score"]},risk:{s["risk_score"]}}}'
    )

html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>A股沪深主板优质标的 × 金融危机情景分析</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:#f7f8fa;color:#1f2329;line-height:1.6}
.wrap{max-width:1180px;margin:0 auto;padding:24px 20px 60px}
.hero{background:linear-gradient(135deg,#fff5f5,#fff);border:1px solid #f0e0e0;border-radius:16px;padding:28px 32px;margin-bottom:20px}
.hero h1{font-size:26px;color:#b71c1c;margin-bottom:8px}
.hero .sub{color:#666;font-size:14px}
.hero .meta{display:flex;flex-wrap:wrap;gap:10px;margin-top:16px}
.chip{background:#fff;border:1px solid #e5e5e5;border-radius:20px;padding:6px 14px;font-size:12px;color:#444}
.chip b{color:#b71c1c}
.tldr{background:#fff;border:1px solid #eee;border-radius:14px;padding:20px 24px;margin-bottom:20px}
.tldr h2{font-size:16px;margin-bottom:12px;color:#333}
.tldr-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px}
.tldr-card{background:#fafafa;border-radius:10px;padding:14px 16px;border-left:4px solid #b71c1c}
.tldr-card h3{font-size:14px;margin-bottom:6px}
.tldr-card p{font-size:12.5px;color:#555}
.section{background:#fff;border:1px solid #eee;border-radius:14px;padding:22px 26px;margin-bottom:20px}
.section h2{font-size:18px;margin-bottom:14px;color:#222;border-left:4px solid #b71c1c;padding-left:10px}
#scatter{width:100%;height:520px}
.legend-wrap{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 4px}
.lg{display:inline-flex;align-items:center;gap:6px;font-size:12px;color:#555;margin-right:14px}
.lg i{width:10px;height:10px;border-radius:50%;display:inline-block}
table{width:100%;border-collapse:collapse;font-size:12.5px}
th{background:#fafafa;color:#555;font-weight:600;padding:9px 8px;text-align:left;border-bottom:2px solid #eee;white-space:nowrap;position:sticky;top:0}
td{padding:8px;border-bottom:1px solid #f2f2f2;vertical-align:middle}
tr:hover{background:#fafafa}
.rk{color:#999;font-weight:600}
.nm b{font-size:13px}
.code{color:#aaa;font-size:11px;margin-left:6px}
.ph{color:#999;font-size:11px}
.zone{font-weight:600;color:#b71c1c}
.model-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}
.model-box{background:#fafafa;border-radius:10px;padding:16px 18px}
.model-box h3{font-size:15px;margin-bottom:10px}
.model-box ul{margin-left:18px;font-size:13px;color:#444}
.model-box li{margin-bottom:6px}
.note{background:#fffbe6;border:1px solid #ffe58f;border-radius:10px;padding:14px 18px;font-size:12.5px;color:#8c6d1f;margin-top:18px}
.note b{color:#ad6800}
.footer{text-align:center;color:#999;font-size:12px;margin-top:30px}
@media(max-width:720px){.wrap{padding:12px}.hero{padding:18px}td{font-size:11px}th{font-size:11px}}
</style>
</head>
<body>
<div class="wrap">

<div class="hero">
<h1>🔴 A股沪深主板优质标的 × 金融危机情景分析</h1>
<div class="sub">基于历史危机（2008/2015/2018/2024）行业表现规律 + 实时财务估值数据（腾讯自选股，2026-08-07收盘），三因子评分模型推算</div>
<div class="meta">
<span class="chip">覆盖 <b>50</b> 只沪深主板优质标的</span>
<span class="chip">三阶段：<b>前期</b> / <b>中期</b> / <b>后期</b></span>
<span class="chip">五大分类：<b>避险核心</b> · <b>稳健防御</b> · <b>攻守兼备</b> · <b>高弹性反弹</b> · <b>高波动弹性</b></span>
<span class="chip">每只标注 <b>危机低吸区间</b></span>
</div>
</div>

<div class="tldr">
<h2>📌 结论速览（TL;DR）</h2>
<div class="tldr-grid">
<div class="tldr-card"><h3>危机前期（高位阶段）会大跌</h3><p>高Beta+高估值：券商、科技（立讯/工业富联类）、周期（航运/有色）、医药高估值（片仔癀）。历史回撤普遍 40%~60%。</p></div>
<div class="tldr-card"><h3>危机中期（恐慌期）能抗</h3><p>公用事业（长江电力/华能国际）、黄金（紫金/山东黄金）、银行（招行/兴业）、运营商（移动/电信）、必需消费（茅台/伊利/双汇）。回撤通常 10%~25%。</p></div>
<div class="tldr-card"><h3>危机后期（政策底后）大反弹</h3><p>券商（中信/华泰）、超跌成长（片仔癀/东鹏/汾酒）、政策受益（基建/消费刺激）。政策底后 3-6 个月弹性普遍 50%~100%。</p></div>
<div class="tldr-card"><h3>避险首选</h3><p>长江电力、华能国际、招商银行、兴业银行、中国神华、紫金矿业、贵州茅台——现金流稳+高股息+低波动，危机中资金避风港。</p></div>
</div>
</div>

<div class="section">
<h2>📊 标的定位散点图（X=防御分 → 抗跌性，Y=弹性分 → 反弹力）</h2>
<div class="legend-wrap">
<div class="lg"><i style="background:#c62828"></i>避险核心</div>
<div class="lg"><i style="background:#e07b39"></i>稳健防御</div>
<div class="lg"><i style="background:#2e7d32"></i>攻守兼备</div>
<div class="lg"><i style="background:#1565c0"></i>高弹性反弹</div>
<div class="lg"><i style="background:#6a1b9a"></i>高波动弹性</div>
</div>
<div id="scatter"></div>
</div>

<div class="section">
<h2>🏷️ 五大分类说明</h2>
<table>
<tr><th>分类</th><th>危机前期</th><th>危机中期</th><th>危机后期</th><th>定位</th></tr>
<tr><td style="color:#c62828;font-weight:600">避险核心</td><td>抗跌</td><td>抗跌领涨</td><td>稳健修复</td><td>现金替代、压舱石</td></tr>
<tr><td style="color:#e07b39;font-weight:600">稳健防御</td><td>小幅震荡</td><td>相对抗跌</td><td>中幅修复</td><td>持有为主，逢低加</td></tr>
<tr><td style="color:#2e7d32;font-weight:600">攻守兼备</td><td>小幅回落</td><td>随盘下跌</td><td>强反弹</td><td>中期分批布局</td></tr>
<tr><td style="color:#1565c0;font-weight:600">高弹性反弹</td><td>承压回落</td><td>深跌</td><td>大反弹（先锋）</td><td>政策底后进攻主力</td></tr>
<tr><td style="color:#6a1b9a;font-weight:600">高波动弹性</td><td>承压回落</td><td>深跌</td><td>强反弹</td><td>高风险高收益，小仓位</td></tr>
</table>
</div>

<div class="section">
<h2>📋 前50标的完整清单（含危机三阶段行为 + 低吸区间）</h2>
<table>
<thead>
<tr><th>#</th><th>标的</th><th>PE(TTM)</th><th>PB</th><th>股息率</th><th>总市值</th><th>分类</th><th>防御</th><th>弹性</th><th>风险</th><th>三阶段行为</th><th>危机低吸区间</th></tr>
</thead>
<tbody>
__ROWS__
</tbody>
</table>
</div>

<div class="section">
<h2>🧮 评分模型与方法论</h2>
<div class="model-grid">
<div class="model-box">
<h3>① 三因子评分（0-100）</h3>
<ul>
<li><b>防御分</b> = 行业防御性40% + 估值安全垫20% + 股息率20% + ROE质量20%（抗跌性）</li>
<li><b>弹性分</b> = 政策受益度40% + 超跌修复空间30% + ROE成长15% + Beta弹性15%（反弹力）</li>
<li><b>风险分</b> = 行业Beta 40% + 估值泡沫30% + 周期波动30%（大跌风险）</li>
<li><b>综合分</b> = 防御35% + 弹性40% + (100-风险)25%，用于前50排序</li>
</ul>
</div>
<div class="model-box">
<h3>② 危机三阶段判定逻辑</h3>
<ul>
<li><b>前期</b>（泡沫高位）：风险分≥60 → 大跌；防御≥72 → 抗跌</li>
<li><b>中期</b>（恐慌期）：防御≥72且风险<45 → 抗跌领涨；风险≥55 → 深跌</li>
<li><b>后期</b>（政策底）：弹性≥75 → 大反弹先锋；62-75 → 强反弹</li>
</ul>
</div>
<div class="model-box">
<h3>③ 低吸区间算法</h3>
<ul>
<li>按分类设定回撤深度：避险10-18%、防御12-22%、攻守15-28%、高弹20-35%、高波动22-38%</li>
<li>上沿 = 现价×(1-浅回撤)；下沿 = 现价×(1-深回撤)，同时参考52周低点兜底</li>
<li>区间为<b>情景推算</b>，非精确预测，需结合政策信号二次确认</li>
</ul>
</div>
</div>
<div class="note">
<b>⚠️ 重要声明：</b>本报告为基于历史规律与公开数据的<b>情景推算研究</b>，不构成任何投资建议。金融危机的时间、幅度、政策应对均存在不确定性；低吸区间是统计区间而非保证价位。投资有风险，决策需独立判断，必要时咨询持牌投顾。
</div>
</div>

<div class="footer">数据来源：腾讯自选股接口（2026-08-07收盘）· 模型：wb-finance 危机情景评分 · 仅供研究学习</div>

<script>
var chart = echarts.init(document.getElementById('scatter'));
chart.setOption({
  tooltip: {
    trigger: 'item',
    formatter: function(p) {
      var d = p.data;
      return '<b>' + d.name + '</b><br>防御分:' + d.def + ' 弹性分:' + d.el + ' 风险分:' + d.risk + '<br>低吸区间:' + d.lowZone + '<br>现价:' + d.price;
    }
  },
  grid: { left: 60, right: 40, top: 50, bottom: 55 },
  xAxis: { type: 'value', name: '防御分（抗跌）', min: 40, max: 90, axisLine: { show: true } },
  yAxis: { type: 'value', name: '弹性分（反弹）', min: 20, max: 90 },
  series: [{
    type: 'scatter',
    data: [__SCATTER__],
    label: { show: false },
    emphasis: { label: { show: true, fontSize: 12, fontWeight: 'bold' } },
    markLine: {
      silent: true,
      symbol: 'none',
      lineStyle: { type: 'dashed', color: '#ccc' },
      data: [ { xAxis: 70 }, { yAxis: 65 } ]
    }
  }]
});
</script>
</body>
</html>
"""

html = html.replace("__ROWS__", rows).replace("__SCATTER__", ",".join(scatter))
out = "F:/codes/wikinote/docs/金融危机/A股沪深主板优质标的-金融危机情景分析.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print("HTML 已生成:", out)
