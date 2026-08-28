# -*- coding: utf-8 -*-
# 持仓组合红盘条件回测：当前6只持仓(8/27市值权重) vs 上证/创业板
import urllib.request, json

def get_kline(code, n=130):
    url = 'http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={},day,,,{},qfq'.format(code, n)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    data = urllib.request.urlopen(req, timeout=15).read().decode('utf-8')
    j = json.loads(data)
    node = j['data'][code]
    kl = node.get('qfqday') or node.get('day')
    out = {}
    for k in kl:
        out[k[0]] = float(k[2])
    return out

stocks = ['sz000538', 'sz002594', 'sh600406', 'sh600886', 'sh600999', 'sh600276']
names = {'sz000538': '白药', 'sz002594': '比亚迪', 'sh600406': '南瑞', 'sh600886': '国投', 'sh600999': '招商', 'sh600276': '恒瑞'}
weights = {'sz000538': 0.258, 'sz002594': 0.236, 'sh600406': 0.149, 'sh600886': 0.054, 'sh600999': 0.120, 'sh600276': 0.184}

kdata = {}
for code in stocks:
    kdata[code] = get_kline(code)
sh = get_kline('sh000001')
cyb = get_kline('sz399006')

dates = sorted(sh.keys())
rets = {}
for i in range(1, len(dates)):
    d = dates[i]
    pd = dates[i - 1]
    if pd not in sh:
        continue
    port = 0.0
    cnt = 0
    stock_rets = {}
    for code in stocks:
        c = kdata[code]
        if d in c and pd in c and c[pd] > 0:
            r = (c[d] / c[pd] - 1) * 100
            stock_rets[code] = r
            port += r * weights[code]
            cnt += 1
    if cnt < 6:
        continue
    shr = (sh[d] / sh[pd] - 1) * 100
    cyr = (cyb[d] / cyb[pd] - 1) * 100 if d in cyb and pd in cyb else 0.0
    rets[d] = {'port': port, 'sh': shr, 'cyb': cyr, 'stocks': stock_rets}

d0 = list(rets.keys())[0]
d1 = list(rets.keys())[-1]
print('回测区间: {} ~ {}，共{}个交易日'.format(d0, d1, len(rets)))
print()

red_days = [d for d, v in rets.items() if v['port'] > 0]
green_days = [d for d, v in rets.items() if v['port'] <= 0]
print('【1】组合红盘日: {}天 ({:.1f}%) | 绿盘日: {}天'.format(len(red_days), len(red_days) / len(rets) * 100, len(green_days)))
print()

up_up = [(d, v) for d, v in rets.items() if v['sh'] > 0 and v['port'] > 0]
up_down = [(d, v) for d, v in rets.items() if v['sh'] > 0 and v['port'] <= 0]
down_up = [(d, v) for d, v in rets.items() if v['sh'] <= 0 and v['port'] > 0]
down_down = [(d, v) for d, v in rets.items() if v['sh'] <= 0 and v['port'] <= 0]
print('【2】四象限分布:')
print('  ① 上证涨+组合红(顺风日): {}天 ({:.0f}%)'.format(len(up_up), len(up_up) / len(rets) * 100))
print('  ② 上证涨+组合绿(逆风日,如8/27): {}天 ({:.0f}%)'.format(len(up_down), len(up_down) / len(rets) * 100))
print('  ③ 上证跌+组合红(防御日): {}天 ({:.0f}%)'.format(len(down_up), len(down_up) / len(rets) * 100))
print('  ④ 上证跌+组合绿(共振跌): {}天 ({:.0f}%)'.format(len(down_down), len(down_down) / len(rets) * 100))
print()

rr = [v for d, v in rets.items() if v['port'] > 0]
print('【3】组合红盘日的市场结构:')
print('  组合平均: {:+.2f}% | 当日上证平均: {:+.2f}% | 创业板平均: {:+.2f}%'.format(
    sum(v['port'] for v in rr) / len(rr), sum(v['sh'] for v in rr) / len(rr), sum(v['cyb'] for v in rr) / len(rr)))
print('  红盘日中上证下跌的: {}天 ({:.0f}%)'.format(sum(1 for v in rr if v['sh'] <= 0), sum(1 for v in rr if v['sh'] <= 0) / len(rr) * 100))
print('  红盘日中创业板跑输上证的(价值/红利风格日): {}天 ({:.0f}%)'.format(
    sum(1 for v in rr if v['cyb'] < v['sh']), sum(1 for v in rr if v['cyb'] < v['sh']) / len(rr) * 100))
print()

print('【4】逆风日案例(上证涨但组合绿, 最近8个):')
for d, v in sorted(up_down, reverse=True)[:8]:
    print('  {}: 上证{:+.2f}% 组合{:+.2f}% 创业板{:+.2f}%'.format(d, v['sh'], v['port'], v['cyb']))
print()
print('【5】顺风日案例(上证涨且组合红, 最近8个):')
for d, v in sorted(up_up, reverse=True)[:8]:
    print('  {}: 上证{:+.2f}% 组合{:+.2f}% 创业板{:+.2f}%'.format(d, v['sh'], v['port'], v['cyb']))
print()
print('【6】防御日案例(上证跌但组合红, 最近8个):')
for d, v in sorted(down_up, reverse=True)[:8]:
    print('  {}: 上证{:+.2f}% 组合{:+.2f}% 创业板{:+.2f}%'.format(d, v['sh'], v['port'], v['cyb']))
print()

# 【7】最近5个交易日逐日明细
print('【7】最近8个交易日组合明细:')
for d in sorted(rets.keys())[-8:]:
    v = rets[d]
    parts = ['{} {:+.2f}%'.format(names[c], r) for c, r in sorted(v['stocks'].items(), key=lambda x: x[1], reverse=True)]
    print('  {}: 上证{:+.2f}% 组合{:+.2f}% | {}'.format(d, v['sh'], v['port'], '  '.join(parts)))
