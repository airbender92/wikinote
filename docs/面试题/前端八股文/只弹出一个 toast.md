# 批量请求失败，只弹出 1 个 Toast

问题：并发多个请求，多个同时失败，会连续弹出一堆 toast，体验很差。

核心思路：**失败提示做防抖/锁，短时间内的批量错误，只展示一次提示；不要每个 error 都直接调用 toast**。

两种主流方案：

1. **错误提示防抖锁（简单，适合 axios 拦截器全局）**，短时间内的错误合并，只弹一次。
2. **错误收集器：收集一段时间内全部错误，统一只弹一次**。

> 注意：业务上，**不同类型错误有时候需要区分**，比如 401 登录失效要单独处理，不要和业务错误合并。

## 方案1：防抖锁（最简单，推荐 axios 全局拦截器）

维护一个标记，正在展示错误toast时，忽略后续短时间内的错误；延时清空锁。

```js
let isShowErrorToast = false;
const ERROR_DELAY = 800; // 800ms内的批量失败只弹一次

/**
 * 统一错误toast，批量失败只弹一次
 * @param {string} msg 错误信息
 */
function showSingleErrorToast(msg) {
  if (isShowErrorToast) return;
  isShowErrorToast = true;
  // 这里调用你的toast组件
  console.error("toast提示：", msg);
  // toast(msg)

  setTimeout(() => {
    isShowErrorToast = false;
  }, ERROR_DELAY);
}
```

### 在 axios 响应拦截器使用

```js
axios.interceptors.response.use(
  (res) => res,
  (err) => {
    // 特殊错误单独处理，不进入合并toast
    const code = err.response?.status;
    if (code === 401) {
      // 跳转登录，不要合并
      return Promise.reject(err);
    }

    const message = err.response?.data?.message || "请求失败";
    showSingleErrorToast(message);
    return Promise.reject(err);
  },
);
```

> 缺点：800ms窗口内，不管多少个接口报错，只显示**第一个报错的文案**；后面错误直接丢弃提示。适合大部分后台业务。

## 方案2：错误队列收集（进阶：收集一批错误，统一提示）

如果希望感知到批量出错，但依然只弹1次toast，可以把错误收集，等待一小段时间，汇总提示。

```js
let errorTimer = null;
let errorList = [];

function batchErrorToast(msg) {
  errorList.push(msg);
  if (errorTimer) return;

  errorTimer = setTimeout(() => {
    // 去重错误文案，相同错误只留一条
    const uniqueMsgs = [...new Set(errorList)];
    // 可以展示：`共${uniqueMsgs.length}个请求失败`，或者展示第一条
    const tip = uniqueMsgs.length > 1 ? `多个请求发生异常` : uniqueMsgs[0];
    // toast(tip)
    console.log("toast：", tip);

    // 清空
    errorList = [];
    clearTimeout(errorTimer);
    errorTimer = null;
  }, 300);
}
```

使用：拦截器里面调用 `batchErrorToast(message)`。

特点：

- 300ms窗口期，所有失败全部收集；
- 如果多个不同错误，你可以选择展示「多个请求异常」，也可以展示第一条；
- 不会像方案1直接丢弃错误信息。

## ⚠️边界场景处理（非常重要）

1. **401、403、token过期**：不要合并，必须单独拦截，直接跳转登录，不要走批量toast逻辑。
2. **abort取消的请求**：不要弹出错误toast。

```js
// axios 判断是否手动取消
if (axios.isCancel(err)) {
  return Promise.reject(err);
}
```

3. 网络断网（无response）：`!err.response`，统一提示“网络异常”。
4. 不要把**业务主动reject**、表单校验错误混入这个全局toast。

## 方案3：组件层批量Promise场景（Promise.all 并发）

代码里手动写 `Promise.all([api1(), api2(), api3()])`，如果希望多个失败只弹一次toast。

> Promise.all 只要一个失败就直接 reject，其余请求继续跑。
> 如果要全部跑完收集所有错误，用 `Promise.allSettled`

```js
async function batchRequest() {
  const [res1, res2, res3] = await Promise.allSettled([api1(), api2(), api3()]);

  // 收集失败
  const fails = [res1, res2, res3].filter((i) => i.status === "rejected");
  if (fails.length > 0) {
    // 只弹一次toast
    toast("部分请求执行失败");
  }
}
```

> 这种是**业务代码层面控制**，适合局部批量请求；上面拦截器方案是**全局所有请求生效**。

## 三种方案对比

| 方案                         | 行为                                   | 适用场景                           |
| ---------------------------- | -------------------------------------- | ---------------------------------- |
| 防抖锁 showSingleErrorToast  | 窗口期只弹第一个错误，其余忽略提示     | 全局axios拦截器，90%后台项目首选   |
| 错误队列收集 batchErrorToast | 收集一批错误，汇总提示，知道有多个失败 | 需要感知批量出错，不希望丢错误信息 |
| Promise.allSettled           | 局部手动批量请求，业务代码控制         | 页面内明确的并发请求，不作用于全局 |

## 常见踩坑

1. ❌不要在每个catch里面直接调用toast，并发批量失败必然弹一堆。
2. ❌锁一定要用setTimeout释放，不要依赖toast的回调；toast组件如果出错，锁永久锁住，后续所有错误都不提示。
3. ❌`Abort`取消请求一定要过滤，取消请求属于正常业务，不应该报错误提示。

如果你需要，我可以给一份完整可直接复制的 axios 响应拦截器完整代码，包含：401处理、cancel过滤、批量错误只弹一个toast。
