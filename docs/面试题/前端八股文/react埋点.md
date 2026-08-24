# 两个问题梳理

1. ✅**普通点击、仅查看（没有调用业务接口），埋点也可以上报**
   `track()` 只是普通JS函数，**不依赖业务接口调用**。

> 示例：按钮只是弹窗、展开面板、查看详情，不发后端请求，依然可以直接调用 `track({event:'click_view'})` 完成埋点。

2. ⚠️**快速连续点击会产生多条埋点**：现在版本没有防抖/缓存，短时间疯狂点击按钮，会连续发起多个fetch请求，产生大量埋点数据。

> 解决方案：增加**内存队列攒批**（不是localStorage持久缓存），短时间多次调用先放到队列，等待一段时间后**合并成一次批量上报**，减少http请求，抑制高频重复点击。

> 选型：用内存队列即可；**不做localStorage持久缓存**，页面刷新队列直接丢弃；埋点允许少量丢失，不需要复杂持久化重试。

## 修改方案

### 1、src/services/trackRequest.js（底层不变，保持原样）

```js
// src/services/trackRequest.js
import { authUtil } from "@/utils/authUtil";

export function trackRequestMiddleware(config) {
  const { headers = {} } = config;
  const reqHead = {
    ...headers,
    "Content-Type": "application/json;charset=utf-8",
  };

  const token = authUtil.getToken();
  if (token) {
    reqHead["TOKEN_SESSION"] = token;
  }

  const reqData = config.data;
  return {
    ...config,
    headers: reqHead,
    data: reqData,
  };
}

export function trackRequest(url, options = {}) {
  const defaultOpt = {
    method: "POST",
    keepalive: true,
  };
  const opt = { ...defaultOpt, ...options };

  const reqConfig = trackRequestMiddleware(opt);
  const { headers, data } = reqConfig;

  try {
    fetch(url, {
      method: opt.method,
      keepalive: opt.keepalive,
      headers,
      body: JSON.stringify(data),
    }).catch((err) => {
      console.warn("[trackRequest]埋点上报失败", err);
    });
  } catch (syncErr) {
    console.warn("[trackRequest]埋点同步异常", syncErr);
  }
}
```

### 2、src/hooks/useTrack.js 【增加内存队列攒批】

> 配置：队列缓冲时间 300ms；300ms内所有`track()`调用全部入队，时间到一次性批量上报；
> 同时兼容 `visibilitychange`页面隐藏：**页面立刻离开的时候，立刻把队列剩余数据马上上报，不等待定时器**，防止埋点留在队列丢失。

```js
// src/hooks/useTrack.js
import { useCallback, useEffect, useRef } from "react";
import { trackRequest } from "@/services/trackRequest";

const DEFAULT_TRACK_URL = "/api/track";
// 攒批等待毫秒
const BATCH_DELAY = 300;

export function useTrack(initOptions = {}) {
  // 使用ref，保证队列、定时器跨渲染稳定，不触发重渲染
  const queueRef = useRef([]);
  const timerRef = useRef(null);

  const flush = useCallback(() => {
    // 清空定时器
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
    // 取出队列数据
    const list = [...queueRef.current];
    queueRef.current = [];
    if (list.length === 0) return;

    const url = initOptions.url || DEFAULT_TRACK_URL;
    trackRequest(url, {
      data: list,
    });
  }, [initOptions]);

  // 页面切tab隐藏时，立刻把队列剩余埋点全部上报，不等定时器
  useEffect(() => {
    const handleVisibility = () => {
      if (document.hidden) {
        flush();
      }
    };
    document.addEventListener("visibilitychange", handleVisibility);
    return () => {
      document.removeEventListener("visibilitychange", handleVisibility);
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [flush]);

  const track = useCallback(
    (payload, extOptions = {}) => {
      const url = extOptions.url || initOptions.url || DEFAULT_TRACK_URL;

      // 注入公共字段
      const injectCommon = (item) => ({
        timestamp: Date.now(),
        pageUrl: window.location.href,
        ...item,
      });

      // 入队：单条转数组，统一处理
      const items = Array.isArray(payload)
        ? payload.map(injectCommon)
        : [injectCommon(payload)];

      queueRef.current.push(...items);

      // 开启定时器，到点flush
      if (!timerRef.current) {
        timerRef.current = setTimeout(() => {
          flush();
        }, BATCH_DELAY);
      }
    },
    [initOptions, flush],
  );

  return { track, flush };
}
```

## 使用示例

### 场景1：单纯点击按钮，**不调用任何业务接口**，埋点正常上报

```jsx
const { track } = useTrack();

// 只是弹窗，没有业务接口请求
const handleClickView = () => {
  openModal();
  // 仅仅点击查看，直接调用埋点，一样上报
  track({
    event: "click_view_detail",
    id: row.id,
  });
};
```

### 场景2：用户疯狂连续点击按钮

短时间点击10次，不会发10次http；**300ms攒一批，合并为1次批量请求**，避免埋点风暴。

### 场景3：页面切tab离开

触发 `visibilitychange` → 立刻执行`flush()`，队列里面还没发出去的埋点马上上报，不等待300ms定时器，防止埋点丢失。

## 重点说明

1. **没有业务接口也可以埋点**：`track()`是独立函数，和业务接口完全解耦；弹窗、展开、tab切换、查看，都可以直接调用。
2. 是**攒批合并上报，不是去重**：多次点击的多条埋点事件都会保留，只是合并成一次http请求发给后端；后端会收到事件数组。
3. 如果想要**去重（完全丢弃重复事件）**，业务层自己控制，底层埋点不做丢弃，避免丢失真实用户行为。
4. 内存队列，页面刷新/关闭，队列未上报数据会丢失；埋点业务特性，少量丢失可以接受。
5. keepalive生效：flush的时候调用`trackRequest`，底层fetch带`keepalive:true`。
6. hook暴露`flush`，业务代码需要可以手动强制立即上报：`flush()`。

## 后端接口需要适配

埋点接口接收 `Array` 数组格式：

```json
[
  {
    "event": "click_view_detail",
    "timestamp": 1756789000000,
    "pageUrl": "xxx",
    "id": 1
  },
  {
    "event": "click_view_detail",
    "timestamp": 1756789000100,
    "pageUrl": "xxx",
    "id": 2
  }
]
```

> 如果后端只能接收单条对象，不能接收数组，我可以再改一版：不做批量http，改为**防抖（debounce），只上报最后一次事件**。你后端埋点接口现在支持批量数组吗？
