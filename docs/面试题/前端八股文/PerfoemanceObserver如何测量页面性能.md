# PerformanceObserver 测量页面完整性能

`PerformanceObserver` 是浏览器**标准性能监听API**，替代旧的 `performance.getEntriesByType()`。

> 旧API缺陷：轮询拿不全历史指标；Observer是事件回调，浏览器主动推送性能条目，支持 buffered 读取页面早期已经发生的指标。

可以监听：**LCP、FCP、FP、CLS、INP、longtask、资源加载、导航、布局偏移**等全部核心性能指标。

> 注意拼写：`PerformanceObserver`，不是 PerfoemanceObserver。

## 核心概念

1. `entryTypes` / `type`：订阅的性能条目类型
2. `buffered: true`：读取**页面已经发生过的历史指标**（页面加载早期的指标，如LCP必须开这个）
3. 回调 `list.getEntries()`：拿到性能对象数组
4. 适合埋点：页面 `visibilitychange === hidden` 汇总全部指标，用 `sendBeacon` 一次性上报。

### 条目类型一览

| entryType                  | 用途                           |
| -------------------------- | ------------------------------ |
| `largest-contentful-paint` | LCP 最大内容绘制（核心指标）   |
| `paint`                    | FP、FCP 首次绘制、首次内容绘制 |
| `layout-shift`             | CLS 布局偏移分数               |
| `event`                    | INP 交互指标                   |
| `longtask`                 | 主线程长任务(>50ms)            |
| `resource`                 | 资源加载：js/css/img/font      |
| `navigation`               | 页面导航、TTFB、DNS、TCP耗时   |

---

# 完整 TS 示例：采集全套页面性能指标

```typescript
// 存储性能结果
const perfMetrics = {
  fp: 0,
  fcp: 0,
  lcp: 0,
  cls: 0,
  inp: 0,
  ttfb: 0,
  longTaskCount: 0,
  longTaskTotalDuration: 0,
  maxLongTaskDuration: 0,
};

/**
 * 初始化性能监听
 */
export function initPerformanceObserver() {
  if (!window.PerformanceObserver) return;

  // 1. FP / FCP paint 指标
  try {
    const paintObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.name === "first-paint") {
          perfMetrics.fp = entry.startTime;
        } else if (entry.name === "first-contentful-paint") {
          perfMetrics.fcp = entry.startTime;
        }
      }
    });
    paintObserver.observe({ type: "paint", buffered: true });
  } catch (e) {}

  // 2. LCP 最大内容绘制
  try {
    const lcpObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const lastEntry = entries[entries.length - 1];
      perfMetrics.lcp = lastEntry.startTime;
    });
    lcpObserver.observe({ type: "largest-contentful-paint", buffered: true });
  } catch (e) {}

  // 3. CLS 累积布局偏移
  let clsValue = 0;
  try {
    const clsObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        // 忽略用户输入之后产生的偏移
        if (!(entry as any).hadRecentInput) {
          clsValue += entry.value;
        }
      }
      perfMetrics.cls = clsValue;
    });
    clsObserver.observe({ type: "layout-shift", buffered: true });
  } catch (e) {}

  // 4. INP 交互指标
  try {
    const inpObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      // INP取最大交互延迟
      let maxInp = 0;
      for (const entry of entries) {
        maxInp = Math.max(maxInp, entry.duration);
      }
      perfMetrics.inp = maxInp;
    });
    inpObserver.observe({
      type: "event",
      buffered: true,
      durationThreshold: 16,
    });
  } catch (e) {}

  // 5. LongTask 长任务
  try {
    const longTaskList: PerformanceEntry[] = [];
    const longTaskObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        longTaskList.push(entry);
        perfMetrics.longTaskCount = longTaskList.length;
        perfMetrics.longTaskTotalDuration = longTaskList.reduce(
          (sum, item) => sum + item.duration,
          0,
        );
        perfMetrics.maxLongTaskDuration = Math.max(
          ...longTaskList.map((i) => i.duration),
        );
      }
    });
    longTaskObserver.observe({ entryTypes: ["longtask"] });
  } catch (e) {}

  // 6. navigation 导航指标：TTFB
  try {
    const navEntries = performance.getEntriesByType("navigation");
    if (navEntries.length > 0) {
      const nav = navEntries[0] as PerformanceNavigationTiming;
      perfMetrics.ttfb = nav.responseStart;
    }
  } catch (e) {}

  // 页面隐藏时统一上报，结合之前埋点 sendBeacon
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden") {
      sendPerfReport();
    }
  });
}

// 上报性能数据
function sendPerfReport() {
  const data = {
    ...perfMetrics,
    pageUrl: location.href,
    userAgent: navigator.userAgent,
  };
  const blob = new Blob([JSON.stringify(data)], { type: "application/json" });
  navigator.sendBeacon("/api/track/perf", blob);
}
```

## 关键参数解释

### `buffered: true`

> 对于 `type: xxx` 这种写法，**必须加 buffered:true**
> 作用：读取页面已经执行完的历史性能事件。
> 比如LCP在页面加载2s就完成了，当你JS比较晚才初始化Observer，如果没有 `buffered:true`，就收不到LCP事件。

> `entryTypes: ['longtask']` 这种旧语法，**不支持 buffered**。

两种写法区分，不要混用：

```ts
// 写法A：type + buffered（推荐新写法）
observer.observe({ type: "largest-contentful-paint", buffered: true });

// 写法B：entryTypes，老API，不支持buffered
observer.observe({ entryTypes: ["longtask"] });
```

## 各个核心指标含义

1. **FP first‑paint**：首次绘制，浏览器开始渲染像素，ms
2. **FCP first‑contentful‑paint**：首次内容绘制，DOM第一个文本/图像渲染出来，ms
3. **LCP largest‑contentful‑paint**：最大内容绘制；代表页面主内容加载完成，**核心Web指标**，理想 <2500ms
4. **CLS**：累积布局偏移；页面元素意外跳动，理想 <0.1
5. **INP**：交互响应延迟；衡量用户点击输入响应速度，理想 <200ms
6. **TTFB**：首字节时间，从请求发出去到收到服务器第一个字节，反映后端/网络耗时
7. **longTask**：主线程阻塞任务，>50ms，数量、总阻塞时长

## 重要坑点

1. **LCP 会更新多次**：页面加载过程会多次产出LCP条目，取数组最后一条才是最终LCP。
2. **CLS 需要排除用户交互后的布局跳动**：`hadRecentInput=true` 的条目不计入CLS。
3. INP 没有直接的 `largest‑interaction‑paint` entryType，只能监听 `event` 类型自己计算最大duration。
4. 页面如果一直不隐藏（用户一直开tab），指标不会上报；visibilitychange(hidden)是最佳上报时机。
5. `sendBeacon` 报文上限64KB，性能数据量很小，完全够用。
6. 部分低版本浏览器不支持某些entryType，要用 try‑catch 包裹，防止页面报错。
7. **不要在beforeunload做性能上报**，优先 `visibilitychange === 'hidden'`，移动端兼容性更好。

## resource 资源监听（监听js、图片加载）

```typescript
try {
  const resObserver = new PerformanceObserver((list) => {
    const entries = list.getEntries();
    entries.forEach((entry) => {
      // entry: name, duration, transferSize, decodedBodySize
      console.log("资源加载", entry.name, entry.duration, "ms");
    });
  });
  resObserver.observe({ type: "resource", buffered: true });
} catch (e) {}
```

> 资源条目很多，**不要全量上报**，建议采样，或者只上报慢资源（duration >2000ms）。

## navigation 导航时间指标（PerformanceNavigationTiming）

```ts
const nav = performance.getEntriesByType(
  "navigation",
)[0] as PerformanceNavigationTiming;
// nav.domainLookupStart / domainLookupEnd DNS
// nav.connectStart / connectEnd TCP
// nav.requestStart 请求开始
// nav.responseStart TTFB
// nav.responseEnd 响应结束
// nav.domContentLoadedEventEnd DOM完成
// nav.loadEventEnd load完成时间
```

## 和埋点体系整合完整流程

1. 应用初始化执行 `initPerformanceObserver()`，开启全部性能监听
2. Observer内部收集指标到内存对象，不实时上报
3. 用户切后台/关闭页面触发 `visibilitychange hidden`
4. 汇总 `perfMetrics`，使用 `navigator.sendBeacon` POST上报后端
5. 后端接收，做性能统计看板。

如果你需要，我可以把这套代码和前面埋点类合并成一份完整单文件 `track.ts`，包含埋点队列、长任务、核心性能指标、退出上报全套。
