
var allData = [
  {n:'工业富联',p:65.92,v:9.99},{n:'亨通光电',p:54.41,v:8.24},{n:'北方华创',p:734.20,v:6.87},{n:'洛阳钼业',p:20.47,v:6.67},
  {n:'紫金矿业',p:34.10,v:6.16},{n:'深科技',p:38.70,v:5.91},{n:'长电科技',p:68.97,v:5.44},{n:'水晶光电',p:27.14,v:4.75},
  {n:'药明康德',p:147.50,v:4.35},{n:'中科曙光',p:88.65,v:3.62},{n:'中芯国际',p:125.45,v:3.59},{n:'豪威集团',p:90.83,v:3.27},
  {n:'歌尔股份',p:23.71,v:2.60},{n:'宁德时代',p:405.20,v:2.56},{n:'广发证券',p:21.37,v:2.20},{n:'中国铝业',p:9.77,v:1.98},
  {n:'阳光电源',p:108.25,v:1.80},{n:'中兴通讯',p:34.74,v:1.08},{n:'万华化学',p:74.45,v:1.10},{n:'牧原股份',p:38.36,v:0.89},
  {n:'立讯精密',p:55.87,v:0.70},{n:'中信证券',p:28.18,v:0.64},{n:'三一重工',p:19.62,v:0.46},{n:'汇川技术',p:64.39,v:0.45},
  {n:'美的集团',p:85.47,v:0.39},{n:'恒瑞医药',p:53.54,v:0.22},{n:'中国平安',p:54.02,v:0.17},{n:'迈瑞医疗',p:154.30,v:0.02},
  {n:'伊利股份',p:26.37,v:0.00},{n:'陕西煤业',p:23.89,v:-0.13},{n:'中国神华',p:43.00,v:-0.35},{n:'比亚迪',p:90.82,v:-0.36},
  {n:'海康威视',p:38.44,v:-0.49},{n:'片仔癀',p:136.83,v:-0.49},{n:'福耀玻璃',p:56.58,v:-0.61},{n:'长城汽车',p:15.97,v:-0.62},
  {n:'格力电器',p:40.27,v:-0.62},{n:'海尔智家',p:22.34,v:-0.67},{n:'山西汾酒',p:121.01,v:-0.69},{n:'双汇发展',p:25.33,v:-0.74},
  {n:'海天味业',p:36.97,v:-0.96},{n:'华能国际',p:7.12,v:-1.25},{n:'中国建筑',p:4.58,v:-1.29},{n:'中国中车',p:5.95,v:-1.33},
  {n:'建设银行',p:9.96,v:-1.39},{n:'交通银行',p:6.93,v:-1.56},{n:'国投电力',p:14.79,v:-1.60},{n:'贵州茅台',p:1306.45,v:-1.65},
  {n:'国电南瑞',p:24.54,v:-1.72},{n:'长江电力',p:27.76,v:-1.91},{n:'泸州老窖',p:87.52,v:-1.99},{n:'中国石化',p:4.98,v:-2.35},
  {n:'川投能源',p:14.98,v:-2.54},{n:'中国海油',p:30.69,v:-2.76},{n:'云南白药',p:50.90,v:-1.55}
];
var colors = allData.map(function(d){ return d.v >= 0 ? '#d9382f' : '#0a9c6d'; });
echarts.init(document.getElementById('chartAll')).setOption({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: function(ps){ var p = ps[0]; return p.name + '：' + p.value + '%'; } },
  grid: { left: 40, right: 16, top: 10, bottom: 120 },
  xAxis: { type: 'category', data: allData.map(function(d){ return d.n; }), axisLabel: { rotate: 60, fontSize: 10, interval: 0 } },
  yAxis: { type: 'value', name: '涨跌幅%', axisLabel: { formatter: '{value}%' } },
  series: [{ type: 'bar', data: allData.map(function(d, i){ return { value: d.v, itemStyle: { color: colors[i], borderRadius: [2,2,0,0] } }; }), barMaxWidth: 14 }]
});

echarts.init(document.getElementById('chartIdx')).setOption({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: function(ps){ var p = ps[0]; return p.name + '：' + p.value + '%'; } },
  grid: { left: 80, right: 30, top: 10, bottom: 20 },
  xAxis: { type: 'value', name: '%', axisLabel: { formatter: '{value}%' } },
  yAxis: { type: 'category', data: ['上证指数','沪深300','深证成指','创业板指','中证500','中证1000','科创50'] },
  series: [{
    type: 'bar', barMaxWidth: 18,
    data: [
      { value: 1.47, itemStyle: { color: '#d9382f' } },
      { value: 1.24, itemStyle: { color: '#d9382f' } },
      { value: 1.86, itemStyle: { color: '#d9382f' } },
      { value: 1.32, itemStyle: { color: '#d9382f' } },
      { value: 2.65, itemStyle: { color: '#d9382f' } },
      { value: 2.94, itemStyle: { color: '#d9382f' } },
      { value: 4.78, itemStyle: { color: '#d9382f' } }
    ]
  }]
});

var tblHtml = '<table><tr><th>标的</th><th>现价</th><th>今日涨跌幅</th></tr>';
allData.forEach(function(d){
  tblHtml += '<tr><td>' + d.n + '</td><td>' + d.p + '</td><td class="' + (d.v >= 0 ? 'up' : 'down') + '">' + d.v + '%</td></tr>';
});
tblHtml += '</table>';
document.getElementById('tblWrap').innerHTML = tblHtml;
function toggleTable(){
  var w = document.getElementById('tblWrap');
  w.classList.toggle('hidden');
}
