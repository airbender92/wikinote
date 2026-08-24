# navigator.sendBeacon()

`navigator.sendBeacon()` 是浏览器原生 API，**用于异步、可靠地向服务器发送少量数据**，最典型场景：页面卸载（关闭、刷新、跳转）时上报埋点、日志、统计数据。

> MDN 定义：`navigator.sendBeacon(url, data?)`
> 它会把请求交给浏览器，放到后台任务队列，**不阻塞页面卸载，不阻塞主线程**。

## 语法

```javascript
const result = navigator.sendBeacon(url, data);
```

- `url`：目标接口地址（POST 请求）
- `data` 可选：要发送的数据，支持类型：
  `ArrayBuffer`、`Blob`、`FormData`、`string`、`URLSearchParams`
- 返回值 `boolean`：
  - `true`：浏览器成功把任务加入队列，不代表服务器收到成功
  - `false`：队列已满、被浏览器拒绝，发送失败，需要降级方案

> ⚠️ 请求方法固定是 **POST**，不能改为 GET。

## 核心解决什么痛点

页面要关闭/跳转时，普通请求会遇到问题：

1. **fetch / XMLHttpRequest 同步请求**：阻塞页面关闭，造成卡顿，部分现代浏览器已经禁止 unload 里同步 XHR。
2. **fetch 异步**：页面销毁时，浏览器直接终止 pending 的网络请求，**埋点直接丢失**，日志上报丢失。

`sendBeacon` 的特点：

1. **浏览器保证尽量发送**：即使页面已经卸载，浏览器在后台继续完成这个请求；
2. **非阻塞**：调用之后 JS 立刻返回，不会卡住页面关闭；
3. **受浏览器配额限制**：数据量不能太大，一般上限约 **64KB**，超过会返回 false，发送失败；适合埋点日志，不适合传大报文。

## 常见使用场景

1. 页面离开上报：`beforeunload` / `visibilitychange` 上报页面停留时长、退出埋点
2. 前端异常日志上报
3. AI 会话埋点：用户关闭页面，上报会话结束状态、统计对话时长

### 示例1：字符串上报埋点

```javascript
// 用户离开页面时上报
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "hidden") {
    const payload = JSON.stringify({
      event: "page_leave",
      page: window.location.href,
      duration: performance.now(),
    });
    const ok = navigator.sendBeacon("/api/log/report", payload);
    if (!ok) {
      // 队列满，降级：用fetch兜底
      fetch("/api/log/report", {
        method: "POST",
        body: payload,
        keepalive: true,
      }).catch(() => {});
    }
  }
});
```

### 示例2：FormData 格式

```javascript
const fd = new FormData();
fd.append("event", "close_session");
fd.append("sessionId", "sess_123456");
navigator.sendBeacon("/api/log", fd);
```

> 服务端接收字符串JSON时注意：`sendBeacon` 发送字符串时，**Content‑Type 不会自动是 application/json**；
> 如果要发 json，推荐两种方式：
>
> 1. 手动构造 Blob 指定 content‑type

```javascript
const data = JSON.stringify({ event: "leave" });
const blob = new Blob([data], { type: "application/json" });
navigator.sendBeacon("/api/log", blob);
```

## sendBeacon vs fetch keepalive

`fetch(url, { keepalive: true })` 也可以实现页面卸载后继续发送请求，两者对比：

| 特性         | navigator.sendBeacon         | fetch + keepalive:true           |
| ------------ | ---------------------------- | -------------------------------- |
| 请求方法     | 固定 POST                    | GET/POST 均可                    |
| 数据上限     | 约64KB                       | 约64KB（浏览器相同配额）         |
| 返回值       | 布尔，仅代表入队成功         | 返回 Promise，可以拿到响应状态码 |
| 自定义Header | 不方便（Blob方式有限支持）   | 完全自定义 headers               |
| 兼容性       | IE不支持；现代浏览器全部支持 | 现代浏览器                       |

> 注意：`sendBeacon` **拿不到后端返回的响应、状态码**，只能知道有没有入队成功；
> 如果你需要读取接口返回，就用 `fetch keepalive`；单纯埋点上报优先 sendBeacon。

## 事件选择：不要滥用 beforeunload

早期很多人写 `window.addEventListener('beforeunload')`，但是：

1. 移动端很多浏览器对 `beforeunload` 触发不稳定；
2. 用户刷新、tab切换、最小化不一定触发；
3. 部分浏览器会忽略里面的 beacon 请求。

✅ **推荐优先使用 `visibilitychange === 'hidden'`**，用户切tab、切后台、关闭标签页都会触发，可靠性远高于 beforeunload。

## 限制与坑点

1. **最大数据 64KB**：超出返回 false，请求直接丢弃，务必做降级；
2. 跨域：遵循 CORS，跨域 sendBeacon 需要服务端配置跨域允许；
3. 返回值 `true ≠ 请求成功`，只是加入浏览器队列，网络差依然可能丢包；
4. 浏览器会合并、延迟 beacon 请求，不保证实时到达；
5. 隐私模式、浏览器数据节省模式下，beacon 有可能被浏览器丢弃；
6. 不能设置请求超时，没有重试机制；埋点业务需要容忍少量丢失。

## 降级策略模板

```javascript
function sendReport(url: string, payload: string): boolean {
  const blob = new Blob([payload], { type: 'application/json' });
  if (navigator.sendBeacon) {
    const ok = navigator.sendBeacon(url, blob);
    if (ok) return true;
  }
  // sendBeacon不可用 / 队列满，降级 fetch keepalive
  fetch(url, {
    method: 'POST',
    body: blob,
    keepalive: true,
    mode: 'no‑cors' // 根据你的CORS情况选择
  }).catch(() => {
    // 兜底：存入localStorage，下次页面打开补发
  });
  return false;
}
```

## 和AI前端业务结合的小例子

用户正在对话，直接关闭标签页，上报会话非正常结束：

```javascript
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "hidden") {
    navigator.sendBeacon(
      "/api/chat/beacon-end",
      JSON.stringify({
        sessionId: currentSessionId,
        status: "abort",
        lastMessageId: lastMsgId,
      }),
    );
  }
});
```

> 后端需要注意：beacon 是异步后台上报，接口不要做复杂耗时逻辑，快速返回即可。

如果你需要，我可以顺带讲下埋点上报整套方案：beacon + localStorage 离线补发 + 采样策略。
