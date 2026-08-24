# axios 取消请求

**axios 支持取消请求**，底层基于浏览器原生 `AbortController`（axios v0.22.0+ 官方推荐）；旧版本用已经废弃的 `CancelToken`。

> ✅ 新版本优先使用 **AbortController**
> ❌ `CancelToken` 已经废弃，不建议新项目使用。

## 1. 基础示例 AbortController

```
const controller = new AbortController()

axios.get('/api/list', {
  signal: controller.signal   // 把信号传入axios配置
})
.then(res=>{
  console.log(res.data)
})
.catch(err=>{
  // 判断是否手动取消
  if(axios.isCancel(err)){
    console.log('请求被手动取消')
  }else{
    console.log('真实错误', err)
  }
})

// 需要取消的时候调用 abort()
controller.abort()
```

调用 `controller.abort()`，请求立刻终止，进入catch，`axios.isCancel(err)` 判断是手动取消。

## 2. 常见业务场景：搜索框防抖，输入新关键词取消上一次请求

```
let controller = null

async function search(keyword) {
  // 如果上一个请求还在，直接取消
  if(controller){
    controller.abort()
  }
  controller = new AbortController()
  try{
    const res = await axios.get('/api/search', {
      params:{ keyword },
      signal: controller.signal
    })
    console.log(res.data)
  }catch(e){
    if(!axios.isCancel(e)){
      // 不是手动取消才处理报错
      console.error(e)
    }
  }
}
```

> 场景：快速输入搜索，丢弃旧请求，防止旧请求覆盖新请求结果。

## 3. 组件卸载时取消请求（Vue React防止内存泄漏、警告）

Vue3 组件销毁，还没回来的请求要取消，避免组件销毁后还去修改state。

```
<script setup>
import {ref,onUnmounted} from 'vue'
let controller = new AbortController()

async function fetchData(){
  await axios.get('/api/data',{
    signal: controller.signal
  })
}

// 组件卸载，取消正在进行的请求
onUnmounted(()=>{
  controller.abort()
})
</script>
```

## 4. 旧版 CancelToken（已废弃，了解即可）

axios ≤0.21 版本使用，官方已经标记废弃，新项目不要写。

```
const source = axios.CancelToken.source()
axios.get('/api',{
  cancelToken: source.token
})
source.cancel('手动取消')
```

## 5. 封装axios实例全局怎么处理取消

> 注意：**每个请求需要独立的 AbortController**，不能共用同一个 signal。
> 拦截器不能全局统一取消，每个调用方自己维护 controller。

## 6. 关键坑点

1. **取消请求≠告诉后端停止执行逻辑**
   浏览器只是**断掉浏览器这边的http连接**；后端接口已经收到请求，代码依然会继续跑完成，只是响应回不到前端。

> 数据库写入等操作不会因为前端abort回滚。

2. 取消会进入catch，**一定要区分：是手动取消，还是真实业务错误**，不要把取消当成错误上报前端监控！

> 前端监控SDK里面，要判断 `axios.isCancel(error)`，如果true，跳过错误上报，不然会产生大量无效错误。

3. 同一个 `controller.abort()` 只能生效一次；abort之后 signal 变成终止状态，复用会直接立刻取消请求，每次请求要新建 `AbortController`。
4. fetch原生同样使用 `AbortController`，API是浏览器标准，不光axios在用。

## 7. 判断是否为取消请求

```
import axios from 'axios'

try{
  await axios.get('/xxx', {signal})
}catch(err){
  if(axios.isCancel(err)){
    // 用户手动取消，忽略
    return
  }
  // 真实异常，处理报错、上报监控
}
```

## 简短面试总结

1. axios **可以取消请求**，v0.22.0+ 推荐标准API `AbortController`；旧版 `CancelToken` 废弃。
2. `controller.abort()` 终止浏览器侧网络；后端服务依旧执行，不会停止后端逻辑。
3. 业务场景：搜索框丢弃旧请求、路由切换/组件卸载取消请求。
4. catch 中用 `axios.isCancel(err)` 判断手动取消，**取消请求不要当做错误上报监控**。
5. 每次请求创建新的 AbortController，不能重复复用已经abort过的实例。

---

# controller.abort() 怎么知道取消哪一个请求

核心一句话：

> **不是 `abort()` 去查找、取消某个axios请求；而是每一个请求绑定自己独立的 `signal` 对象，`abort()` 触发这个 signal 内部状态变为「已终止」，监听这个signal的请求就自己终止。**

`AbortController`、`AbortSignal` 是浏览器原生标准，**和axios没有强绑定**。

## 对象关系拆解

1. `const controller = new AbortController()`
   - `controller.signal` 得到一个 **AbortSignal** 信号对象
   - signal 内部维护一个布尔状态：`aborted`，默认 `false`
2. 把这个 `signal` 传给 axios 请求配置：`signal: controller.signal`
   - axios 内部会监听这个 signal 的 `abort` 事件
3. 调用 `controller.abort()`
   - 把内部 `signal.aborted = true`
   - 触发 signal 上的 `abort` 事件
   - **所有监听这个 signal 的请求，收到事件，立刻终止自己**

> ⚠️关键点：**abort() 没有传参数、没有请求ID，它根本不知道有哪些请求；它只修改自己这个signal实例的状态。**

### 示意图

```
controller ──→ signal(aborted: false)
                     ↓
          axios请求A 监听 signal 的 abort事件

调用 controller.abort()
    ↓
signal.aborted = true，触发 abort 事件
    ↓
axios请求A监听到事件 → 终止本次http请求
```

---

## 多个请求场景演示

### 场景1：每个请求独立 controller（正确）

```js
// 请求1，独立控制器
const c1 = new AbortController();
axios.get("/api/a", { signal: c1.signal });

// 请求2，独立控制器
const c2 = new AbortController();
axios.get("/api/b", { signal: c2.signal });

c1.abort(); // 只会终止 /api/a，c2.signal不受任何影响
```

`c1.abort()` 只会修改 `c1.signal`，`c2.signal` 完全不受影响，所以只取消第一个请求。

### 场景2：多个请求共用同一个 signal（全部一起取消）

```js
const controller = new AbortController();

axios.get("/api/a", { signal: controller.signal });
axios.get("/api/b", { signal: controller.signal });
axios.get("/api/c", { signal: controller.signal });

controller.abort();
// 三个请求全部一起被取消！
```

> 同一个signal绑定多个请求，abort会全部终止。这个特性可以用来批量取消一组请求。

### 场景3：abort过的signal不能复用（高频坑）

一旦执行 `controller.abort()`，`signal.aborted` 永久变成true，**无法复原**。
后续如果你把这个已经abort的signal传给新请求，请求会**直接被立刻取消，不会发网络**。
✅所以：**每一轮新请求，都必须 new AbortController() 创建全新实例**。

错误示范：

```js
// ❌错误复用
const controller = new AbortController();
axios.get("/api/list", { signal: controller.signal });
controller.abort();

// 再次发请求，继续用旧controller
axios.get("/api/list", { signal: controller.signal });
// 这个新请求直接取消，不会发起http，因为signal已经aborted=true
```

---

## axios内部简单伪代码（理解它如何监听signal）

axios内部大致逻辑，简化版：

```js
function request(config) {
  const { signal } = config;
  return new Promise((resolve, reject) => {
    // 如果signal已经是终止状态，直接取消
    if (signal?.aborted) {
      return reject(createCancelError());
    }

    // 监听 signal 的 abort事件
    function onAbort() {
      // 停止底层http请求
      xhr.abort();
      reject(createCancelError());
    }

    if (signal) {
      signal.addEventListener("abort", onAbort);
    }

    // ...正常发起xhr/fetch
  });
}
```

> axios**不会保存一份请求列表，也不会根据ID去查找请求**。
> 完全靠：**把signal实例绑定给请求，signal状态变更，请求自己响应事件**。

## 业务经典案例：搜索框取消上一次请求

```js
let controller = null;

async function search(keyword) {
  // 如果上一次请求存在，触发它的signal abort
  if (controller) {
    controller.abort();
  }
  // ✅每次新建全新控制器
  controller = new AbortController();
  try {
    await axios.get("/api/search", {
      params: { keyword },
      signal: controller.signal,
    });
  } catch (e) {
    if (!axios.isCancel(e)) {
      console.error(e);
    }
  }
}
```

流程拆解：

1. 第一次搜索：`controller = new AbortController()`，请求绑定这个signal
2. 用户快速输入，再次调用search：
3. `controller.abort()`，触发上一个signal的abort事件 → **上一次请求终止**
4. 重新 `controller = new AbortController()`，新请求绑定全新signal。

## 面试核心回答总结

1. `controller.abort()` **内部不保存请求列表，没有请求ID，不会去查找匹配哪个请求**；它只修改自身 `AbortSignal` 对象的 `aborted` 状态并触发 `abort` 事件。
2. axios请求接收 `signal`，内部监听该signal的`abort`事件；**哪一些请求监听了这个signal，哪些就被取消**。
3. 一个signal可以绑定1个或N个请求；abort会把所有监听该signal的请求全部取消。
4. signal一旦abort就永久终止，不能复用；新请求必须创建新的 `AbortController`。
5. 想要精准取消某一个请求：**给这个请求分配独立的AbortController实例**。

### 延伸

浏览器原生fetch也是完全同一套AbortController机制，逻辑一模一样。
