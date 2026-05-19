## Item 27 详细讲解：使用 `async` 函数替代回调以改善类型流动

这一节通过具体的代码演进，展示了从**回调**到 **Promise** 再到 **`async/await`** 的逐步改进，并重点说明了这些改进如何让 **TypeScript 的类型推断更顺畅**，同时避免一类棘手的“半同步”错误。

---

### 1. 回调的“金字塔厄运”及其问题

原始代码使用回调函数处理异步请求：

```ts
declare function fetchURL(url: string, callback: (response: string) => void): void;

fetchURL(url1, function(response1) {
  fetchURL(url2, function(response2) {
    fetchURL(url3, function(response3) {
      console.log(1);
    });
    console.log(2);
  });
  console.log(3);
});
console.log(4);
```

**执行顺序**：4 → 3 → 2 → 1（与代码顺序相反）。  
**问题**：
- 深层嵌套，可读性差（“厄运金字塔”）。
- 错误处理困难（每个回调都需要单独处理）。
- 控制流（串行、并行、超时等）难以表达。
- TypeScript 几乎无法从回调参数中推断有意义的信息。

---

### 2. Promise 打破嵌套

使用 Promise 改写：

```ts
fetch(url1)
  .then(response1 => fetch(url2))
  .then(response2 => fetch(url3))
  .then(response3 => { /* ... */ })
  .catch(error => { /* ... */ });
```

**改进**：
- 扁平化链式调用，顺序与执行顺序一致。
- 统一的错误处理（`.catch`）。
- 可以轻松组合 `Promise.all`、`Promise.race` 等。

**类型流动**：  
TypeScript 可以推断每个 `then` 回调的参数类型（例如 `response1` 的类型来自 `fetch` 的返回类型 `Promise<Response>`）。但 Promise 链仍然需要手动返回 Promise，有时容易漏掉 `return`。

---

### 3. `async/await` 让异步代码像同步一样

```ts
async function fetchPages() {
  const response1 = await fetch(url1);
  const response2 = await fetch(url2);
  const response3 = await fetch(url3);
  // ...
}
```

**优点**：
- 代码更简洁、更直观。
- 可以使用 `try/catch` 捕获错误。
- TypeScript 可以完美推断每个 `await` 结果的类型（例如 `response1` 自动为 `Response`）。

---

### 4. 类型推断在组合时的优势

#### 并发请求

使用 `Promise.all` + 解构：

```ts
async function fetchPages() {
  const [response1, response2, response3] = await Promise.all([
    fetch(url1), fetch(url2), fetch(url3)
  ]);
  // TypeScript 知道 response1, response2, response3 都是 Response 类型
}
```

**回调版本**需要手动跟踪计数器、存储结果、添加类型注解，且难以泛化。

#### 超时控制

```ts
function timeout(timeoutMs: number): Promise<never> {
  return new Promise((_, reject) => setTimeout(() => reject('timeout'), timeoutMs));
}

async function fetchWithTimeout(url: string, timeoutMs: number) {
  return Promise.race([fetch(url), timeout(timeoutMs)]);
}
```

**类型推断的巧妙之处**：  
`Promise.race` 的返回类型是输入 Promise 结果类型的**联合**。  
`fetch(url)` 返回 `Promise<Response>`，`timeout(...)` 返回 `Promise<never>`。  
联合 `Response | never` 等价于 `Response`（因为 `never` 是空集）。  
所以 `fetchWithTimeout` 的返回类型自动推断为 `Promise<Response>`，无需注解。

---

### 5. `async` 函数强制返回 Promise 的重要性

`async` 函数总是返回 `Promise`，即使没有 `await`：

```ts
async function getNumber() { return 42; }
// 推断为 () => Promise<number>
```

这强制了一条重要规则：**一个函数要么完全同步，要么完全异步，不能混用**。

#### 混用的危害（回调示例）

尝试为 `fetchURL` 添加缓存，但回调可能被同步调用（缓存命中）或异步调用（缓存未命中）：

```ts
const _cache: {[url: string]: string} = {};

function fetchWithCache(url: string, callback: (text: string) => void) {
  if (url in _cache) {
    callback(_cache[url]);  // 同步调用
  } else {
    fetchURL(url, text => {  // 异步调用
      _cache[url] = text;
      callback(text);
    });
  }
}

let requestStatus: 'loading' | 'success' | 'error';
function getUser(userId: string) {
  fetchWithCache(`/user/${userId}`, profile => {
    requestStatus = 'success';
  });
  requestStatus = 'loading';
}
```

**问题**：  
- 如果缓存命中，`callback` 被同步调用，`requestStatus` 先设为 `'success'`，然后被设为 `'loading'`，最终值为 `'loading'`。  
- 如果缓存未命中，`callback` 异步调用，`requestStatus` 先设为 `'loading'`，稍后变为 `'success'`。  
- 同一个函数调用在不同条件下行为不同，极其容易出错。

#### 使用 `async` 统一为异步

```ts
async function fetchWithCache(url: string) {
  if (url in _cache) return _cache[url];
  const response = await fetch(url);
  const text = await response.text();
  _cache[url] = text;
  return text;
}

async function getUser(userId: string) {
  requestStatus = 'loading';
  const profile = await fetchWithCache(`/user/${userId}`);
  requestStatus = 'success';
}
```

现在无论缓存是否命中，`fetchWithCache` 都返回 `Promise`，调用方使用 `await` 后，`requestStatus` 的赋值顺序始终一致：先 `'loading'`，后 `'success'`。消除了“半同步”带来的不确定性。

---

### 6. 返回 Promise 不会被重复包装

```ts
async function getJSON(url: string) {
  const response = await fetch(url);
  const jsonPromise = response.json();  // jsonPromise 已经是 Promise
  return jsonPromise;                  // 直接返回，不会变成 Promise<Promise<any>>
}
// 推断的返回类型为 Promise<any>
```

TypeScript 知道 `async` 函数返回的 `Promise` 不会嵌套。

---

### 总结：为什么优先使用 `async/await`

| 方面 | 回调 | Promise | async/await |
|------|------|---------|-------------|
| 嵌套层级 | 深 | 平 | 平 |
| 错误处理 | 分散 | 统一 `.catch` | `try/catch` |
| 类型推断 | 差 | 较好 | **最佳** |
| 控制流（串行/并行/超时） | 困难 | 容易 | 容易 |
| 强制异步一致性 | 无 | 需自觉 | **强制** |
| 代码简洁度 | 差 | 中 | **好** |

**最终建议**：  
- 优先使用 `async/await`（即使需要支持旧环境，TypeScript 也会帮你转译）。  
- 仅在必须包装基于回调的 API（如 `setTimeout`、旧库）时才使用原始 `Promise` 构造器。  
- 如果一个函数返回 `Promise`，就把它声明为 `async` 以保持一致性。