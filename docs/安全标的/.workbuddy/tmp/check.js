
// ===== 图1：全球指数涨跌对比 =====
var gNames = ["道指","标普","纳指","费半","上证","深成","创业板","科创50","日经225","KOSPI","恒指","STOXX600"];
var gVals  = [0.28,0.62,1.30,2.56,1.02,1.42,1.35,2.51,-0.12,-0.60,0.54,0.31];
var gColors = gVals.map(function(v){ return v>=0 ? "#d9382f" : "#0a9c6d"; });
var chartGlobal = echarts.init(document.getElementById('chartGlobal'));
chartGlobal.setOption({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: 70, right: 30, top: 20, bottom: 30 },
  xAxis: { type: 'value', axisLabel: { formatter: '{value}%' } },
  yAxis: { type: 'category', data: gNames, inverse: true },
  series: [{
    name: '涨跌幅',
    type: 'bar',
    data: gVals.map(function(v,i){ return { value: v, itemStyle: { color: gColors[i] } }; }),
    label: { show: true, position: 'right', formatter: '{c}%', color: '#333' },
    barWidth: '55%'
  }]
});

// ===== 图2：55只涨跌条形图 =====
var sNames = ["工业富联","亨通光电","海康威视","立讯精密","北方华创","豪威集团","中芯国际","中科曙光","长电科技","深科技","水晶光电",
  "中国中车","国电南瑞","三一重工","歌尔股份","贵州茅台","山西汾酒","泸州老窖","伊利股份","双汇发展","海天味业","万华化学",
  "美的集团","格力电器","海尔智家","恒瑞医药","迈瑞医疗","云南白药","片仔癀","药明康德","中国平安","中信证券","广发证券","建设银行","交通银行",
  "宁德时代","比亚迪","阳光电源","福耀玻璃","长城汽车","长江电力","中国神华","陕西煤业","中国海油","中国石化","华能国际","川投能源","国投电力",
  "紫金矿业","中国铝业","洛阳钼业","中兴通讯","牧原股份","中国建筑","汇川技术"];
var sVals = [-0.13,6.00,-0.56,1.95,1.28,0.12,3.50,1.10,2.48,2.36,1.13,
  -0.84,-0.21,-0.91,-0.64,0.05,0.52,1.87,-0.42,-4.37,-0.36,1.00,
  -2.13,-0.37,-0.86,4.82,1.11,0.14,0.88,8.49,-0.22,0.11,1.16,-0.40,-0.43,
  0.02,0.66,6.99,-1.16,-0.89,0.00,-0.07,0.64,1.20,0.39,-0.29,-0.27,-0.97,
  1.88,2.50,2.26,0.00,0.26,-1.09,1.91];
var sColors = sVals.map(function(v){ return v>=0 ? "#d9382f" : "#0a9c6d"; });
var chart55 = echarts.init(document.getElementById('chart55'));
chart55.setOption({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: 95, right: 50, top: 10, bottom: 20 },
  xAxis: { type: 'value', axisLabel: { formatter: '{value}%' } },
  yAxis: { type: 'category', data: sNames, inverse: true, axisLabel: { fontSize: 10 } },
  series: [{
    name: '涨跌幅',
    type: 'bar',
    data: sVals.map(function(v,i){ return { value: v, itemStyle: { color: sColors[i] } }; }),
    label: { show: true, position: 'right', formatter: '{c}%', fontSize: 9, color: '#555' },
    barWidth: '70%'
  }]
});

// ===== 图3：持仓浮盈亏 =====
var pNames = ["工业富联","中兴通讯","招商证券","云南白药","中国中车","国电南瑞","歌尔股份"];
var pVals  = [3423,417,-848,30,5,-1,1924];
var pColors = pVals.map(function(v){ return v>=0 ? "#d9382f" : "#0a9c6d"; });
var chartPos = echarts.init(document.getElementById('chartPos'));
chartPos.setOption({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: 90, right: 60, top: 20, bottom: 30 },
  xAxis: { type: 'value', axisLabel: { formatter: '¥{value}' } },
  yAxis: { type: 'category', data: pNames, inverse: true },
  series: [{
    name: '浮盈亏(元)',
    type: 'bar',
    data: pVals.map(function(v,i){ return { value: v, itemStyle: { color: pColors[i] } }; }),
    label: { show: true, position: 'right', formatter: function(p){ return (p.value>0?'+':'') + p.value + '元'; }, color: '#333' },
    barWidth: '55%'
  }]
});

window.addEventListener('resize', function(){
  chartGlobal.resize();
  chart55.resize();
  chartPos.resize();
});
