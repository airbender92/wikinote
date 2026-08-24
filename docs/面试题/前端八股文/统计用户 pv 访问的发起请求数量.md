# 统计PV访问对应的发起请求数量

> PV：页面访问次数；**一次PV页面打开，浏览器会发起多个HTTP请求**（html、css、js、图片、接口、字体等），所以PV数量 ≠ 请求数。
> 目标：统计**每个PV页面，浏览器一共发起多少个请求**，以及全局总请求数。

## 一、浏览器端获取（前端JS采集）

### 方案1：Performance API（推荐，原生，无埋点侵入）

浏览器 `window.performance.getEntriesByType('resource')` 可以拿到当前页面所有资源请求，包含接口、静态资源。

> 注意：该数据只属于**当前这一次页面PV生命周期**，页面刷新/跳转后重置。

```javascript
// 获取当前页面本次PV，所有发起的请求
function getPageTotalRequestCount() {
  // resource：所有资源请求(html/css/js/img/api/font等)
  const resources = performance.getEntriesByType("resource");
  // 过滤掉无效、内部请求，统计真实网络请求
  const realRequests = resources.filter((item) => {
    // 过滤data:、blob: 本地资源，不算网络请求
    return !item.name.startsWith("data:") && !item.name.startsWith("blob:");
  });
  return realRequests.length;
}

// 页面加载完成后调用
window.addEventListener("load", () => {
  const reqCount = getPageTotalRequestCount();
  console.log("本次PV页面发起请求数量：", reqCount);
  // 上报埋点：把 reqCount 和 pageUrl、pvId 一起上报后端
  // report({pvId: 'xxx', pageUrl: location.href, requestCount: reqCount})
});
```

#### 关键说明

1. `performance.getEntriesByType('resource')`：包含XHR/fetch接口请求、静态资源；
2. 单页应用SPA：路由切换不会刷新页面，**不会自动清空resource列表**，需要手动记录每次路由切换的快照，否则会累加历史请求。

##### SPA单页应用处理（Vue/React路由跳转）

SPA每次路由切换代表一次新PV，需要切换前截取快照，做差值计算：

```javascript
// 路由跳转前保存上一次资源总数
let lastResourceNum = 0;

// 每次路由变化（新PV）
function onRouteChange() {
  const now = performance
    .getEntriesByType("resource")
    .filter((i) => !i.name.startsWith("data:")).length;
  // 本次PV新增请求数 = 当前 - 上一次
  const currentPVReq = now - lastResourceNum;
  lastResourceNum = now;
  // 上报 currentPVReq 作为本次PV的请求数量
}
```

### 方案2：拦截fetch / ajax，手动计数（只统计接口请求，不含静态资源）

如果只想统计**业务接口请求**，不统计图片css等静态资源，可以重写fetch、XMLHttpRequest做计数器。

```javascript
let apiRequestCount = 0;
const originFetch = window.fetch;
window.fetch = function (...args) {
  apiRequestCount++;
  return originFetch.apply(this, args);
};

// xhr兼容
const originOpen = XMLHttpRequest.prototype.open;
XMLHttpRequest.prototype.open = function () {
  apiRequestCount++;
  originOpen.apply(this, arguments);
};
```

> 缺点：只统计接口，**无法统计css、img、script等静态资源请求**。

## 二、后端/Nginx/网关层面统计（全量真实请求，最准确）

前端JS会丢失部分数据（用户页面没加载完就关闭，performance拿不全）；后端日志统计是真实到达服务器的请求。

### 1.Nginx日志统计

Nginx access.log 每一行代表**一次http请求**。

- 字段：`$request` 请求地址，`$status` 状态码

> 区分PV和请求：PV是用户访问页面(html)；请求是全部资源。

示例日志：

```
127.0.0.1 - - [24/Aug/2026:10:00:00 +0800] "GET /index.html HTTP/1.1" 200
127.0.0.1 - - [24/Aug/2026:10:00:00 +0800] "GET /main.js HTTP/1.1" 200
127.0.0.1 - - [24/Aug/2026:10:00:00 +0800] "GET /api/list HTTP/1.1" 200
```

这里1次PV访问index.html，产生3条日志=3个请求。

**shell简单统计示例**

```bash
# 统计总请求量
wc -l access.log

# 统计页面PV（只统计html页面访问）
grep "GET /index.html" access.log | wc -l
```

> 难点：**把请求和对应PV做关联**，需要在请求头带上 `pvId`，Nginx日志打印pvId，实现：每条请求日志归属到某一个PV会话。

Nginx配置记录pvId（前端埋点把pvId放到请求header `X-Pv-Id`）

```nginx
log_format main '$remote_addr [$time_local] "$request" $status $http_x_pv_id';
```

日志就会带上pvId，可以按pvId分组统计，算出：**每个pvId对应多少条请求**。

### 2.网关/APM工具（现成方案，企业常用）

- SkyWalking、Pinpoint：可以追踪一次用户会话下所有http请求，自动统计每个页面PV对应的请求数；
- 阿里云SLS、ELK：采集Nginx/网关日志，以pvId做分组聚合，`group by pvId count(*) as request_num`；

## 三、两种方案对比

| 维度                 | 前端Performance API                    | 后端Nginx/网关日志   |
| -------------------- | -------------------------------------- | -------------------- |
| 统计范围             | 浏览器发出的请求（包含失败、跨域资源） | 真实到达服务端的请求 |
| SPA支持              | 需要手动处理路由快照                   | 依赖pvId透传         |
| 数据丢失             | 用户快速关闭页面会丢数据               | 数据完整             |
| 能否区分单次PV请求数 | 可以，采集上报                         | 可以，靠pvId分组     |

## 四、业务指标口径定义（非常重要，避免统计歧义）

1. **PV**：页面浏览次数（路由跳转/页面打开）
2. **单次PV发起请求数**：打开这个页面期间浏览器发起的全部网络请求（html、js、css、图片、接口）
3. **单次PV接口请求数**：仅统计业务接口(fetch/xhr)，排除静态资源
4. 平均每PV请求数 = 总请求数 / PV总数

> 坑：浏览器缓存资源不会发起网络请求，不会计入请求数量；304缓存资源依然会发起http请求。

## 五、落地建议

1. 如果做页面性能埋点：优先前端`performance resource`，每次PV上报`pvId + requestCount`；
2. 如果要做真实服务端流量统计：前端生成全局唯一`pvId`，所有请求header带上`X‑Pv‑Id`，网关/nginx记录该字段，日志平台按pvId分组count；
3. SPA项目，路由切换时重置快照，不要直接累加resource列表。

如果你需要，我可以给一份完整可直接复制的SPA埋点上报完整demo，或者一份es/sql统计语句。
