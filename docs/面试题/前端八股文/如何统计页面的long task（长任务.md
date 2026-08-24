# JS 统计 Long Task 长任务

**Long Task（长任务）：主线程阻塞任务，执行时间超过 **50ms** 的任务**。
主线程被长任务占用，会造成卡顿、输入延迟、页面掉帧、交互响应慢，影响 FID / INP 性能指标。

> 50ms 阈值来源：RAIL模型，用户交互需要在50ms内完成，超过就感知卡顿。

## 核心 API：PerformanceObserver

> ❗不要用 `performance.getEntriesByType('longtask')` 轮询！
> 该方法拿不到历史全部长任务，**标准做法是 PerformanceObserver 监听**。

### 基础监听代码

```typescript
interface LongTaskEntry {
  duration: number;
  startTime: number;
  attribution: Array<{
    name: string;
    containerType: string;
    containerSrc?: string;
  }>;
}

// 收集长任务列表
const longTasks: LongTaskEntry[] = [];

function observeLongTask() {
  if (!window.PerformanceObserver) return;

  try {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      for (const entry of entries) {
        // entry.entryType === 'longtask'
        const item = {
          startTime: entry.startTime, // 开始时间(相对于页面timeOrigin)
          duration: entry.duration, // 阻塞耗时 ms，>50ms
          attribution: entry.attribution, // 归属信息：哪个脚本/iframe导致
        };
        longTasks.push(item);

        // 可以直接上报埋点
        console.log("检测到长任务", item.duration.toFixed(2) + "ms", item);
      }
    });

    // 订阅 longtask
    observer.observe({ entryTypes: ["longtask"] });
  } catch (e) {
    console.warn("LongTask 不支持", e);
  }
}

// 启动
observeLongTask();
```

### entry 属性说明

- `startTime`：任务开始时间 `performance.now()` 时间基
- `duration`：**阻塞主线程的时长，ms，大于50ms才会触发**
- `attribution`：数组，定位来源
  - `name`：`unknown` / `script` / `layout` / `style` / `iframe`
  - `containerSrc`：iframe的src，如果是iframe引起长任务
  > ⚠️ **长任务API无法给出具体函数名、代码行号！只能告诉你是脚本/布局/iframe导致，拿不到堆栈。**

---

## 指标计算：统计页面长任务汇总指标

业务埋点一般上报这些：

1. `longTaskCount`：页面一共发生多少个长任务
2. `longTaskTotalDuration`：长任务总阻塞时长（总和）
3. `maxLongTaskDuration`：最大单次长任务耗时
4. `longTaskList`：采样部分长任务列表（不要全量上报，避免数据过大）

```typescript
function getLongTaskMetrics() {
  const count = longTasks.length;
  const total = longTasks.reduce((sum, i) => sum + i.duration, 0);
  const max = longTasks.length
    ? Math.max(...longTasks.map((i) => i.duration))
    : 0;
  return {
    longTaskCount: count,
    longTaskTotalDuration: Math.round(total),
    maxLongTaskDuration: Math.round(max),
    sampleLongTasks: longTasks.slice(-5), // 只采样最后5条，控制上报大小
  };
}
```

一般在页面卸载 `visibilitychange hidden` 的时候，把 `getLongTaskMetrics()` 通过 `sendBeacon` 上报埋点。

```typescript
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "hidden") {
    const metrics = getLongTaskMetrics();
    navigator.sendBeacon(
      "/api/track/perf",
      new Blob([JSON.stringify(metrics)], { type: "application/json" }),
    );
  }
});
```

## LongTask 的局限（非常重要）

1. **无法获取 JS 调用栈，不知道是哪段业务代码造成卡顿**，只能知道是script类型。
2. 阈值固定 **>=50ms**，小于50ms不会产出 longtask 条目。
3. Web Worker 的任务**不会产生 longtask**，Worker不占用主线程。
4. 部分浏览器：Safari 对 longtask 支持较差。
5. 合并任务：连续一堆48ms任务，每个都不到50ms，不会生成longtask，但依然会造成卡顿；这也是 INP 指标想要解决的。

## 如何定位到底哪段代码导致长任务？

> PerformanceObserver只能统计，**不能定位源码**，定位要靠 DevTools

1. Chrome DevTools → Performance 录制，看红色三角标记 Long Task，火焰图看到具体函数。
2. 如果线上想要拿到堆栈：可以使用 **PerformanceObserver + `event.type: 'script'` 搭配实验性 API，生产环境兼容性差，不建议业务使用**。

## 补充：新API —— 监听 INP（交互下一次绘制，Core Web Vital）

INP 是核心网页指标，衡量页面交互响应，内部也是基于长任务计算：

```typescript
function observeINP() {
  if (!window.PerformanceObserver) return;
  try {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      for (const entry of entries) {
        console.log("INP entry", entry);
      }
    });
    observer.observe({ type: "event", buffered: true, durationThreshold: 16 });
  } catch (e) {}
}
observeINP();
```

## 完整整合：和你前面埋点体系结合

要点回顾：

1. 页面初始化启动 `PerformanceObserver` 监听 longtask，内存数组收集；
2. **不要实时上报每一条长任务**，会产生大量请求；
3. 在 `visibilitychange === hidden` / `beforeunload` 时刻，汇总统计指标，用 sendBeacon 批量上报；
4. 不要把全部长任务列表上报，做采样（例如取最后5条），控制报文大小，防止超过 sendBeacon 64KB限制。

## 常见误区

❌ `performance.getEntriesByType('longtask')` 在页面运行中途调用，拿不全所有历史长任务。
✅ 必须用 PerformanceObserver 并且不要忘记，浏览器会缓冲早期条目。

> observer 配置 `buffered:true` ？
> 对于 `longtask`，不需要写 buffered:true；longtask条目会实时回调。

## 拓展：长任务优化方向

1. 大循环、复杂计算拆分，使用 `setTimeout` / `requestIdleCallback` 做任务分片
2. 避免同步大JSON.parse / JSON.stringify
3. 避免大规模DOM同步操作
4. 重计算放到 WebWorker

如果你需要，我可以给你一份完整可复制的 TS 性能监控小模块，包含：longtask、FP、FCP、LCP、INP，结合之前 sendBeacon埋点一起上报。
