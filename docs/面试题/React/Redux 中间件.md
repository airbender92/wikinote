# Redux 中间件理解

> Redux 本身的核心流程：`dispatch(action) → reducer → 更新state`
> **原生redux的dispatch只能接收普通action对象，只能做同步逻辑；中间件就是架在 `dispatch` 和 `reducer` 中间的一段代码。**

执行链路：

```
dispatch(action) → 【中间件链】 → 原生dispatch → reducer → state更新
```

中间件可以**拦截、加工、延迟、丢弃、改写action**，用来处理副作用：异步请求、日志、埋点、报错上报等。

## 源码形态（中间件函数签名）

redux中间件是三层柯里化函数：

```js
const middleware = (store) => (next) => (action) => {
  // 这里写你的逻辑
  // next：把action交给下一个中间件；调用next(action)流转下去
  return next(action);
};
```

- `store`：redux的store实例（getState、dispatch）
- `next`：下一个中间件；最后一个next就是redux原生dispatch
- `action`：当前派发的action

## applyMiddleware

`applyMiddleware(m1,m2,m3)`，用来把多个中间件组合，重写store的dispatch。

> 中间件执行顺序：**从左到右进入，从右到左next执行**。

```js
import { createStore, applyMiddleware } from "redux";
const store = createStore(reducer, applyMiddleware(m1, m2, m3));
```

---

# 最常用两个中间件对比：thunk vs saga

## 1. redux‑thunk

> 作用：让 `dispatch` 不仅可以传普通对象，还可以传**函数**。

当 `dispatch(asyncFunc)`：

- thunk拦截action，如果是函数，就执行这个函数，传入 `dispatch、getState`；
- 如果是普通对象，直接交给下一个中间件。

```js
// thunk异步action
export const fetchData = () => {
  return async (dispatch, getState) => {
    dispatch({ type: "LOADING" });
    const res = await fetch("/api/list");
    dispatch({ type: "SUCCESS", payload: res.data });
  };
};

// 组件调用
dispatch(fetchData());
```

优点：简单，上手快；RTK已经**内置thunk中间件**，开箱即用。
缺点：复杂异步（轮询、取消请求、竞态、串行并行嵌套）代码会嵌套很乱。

## 2. redux‑saga

> 使用Generator函数 `function*`，把异步逻辑抽离到saga中，不写回调嵌套。
> 监听action，执行异步，再dispatch普通action给reducer。

```js
function* fetchUserSaga(action) {
  try {
    const res = yield call(api.getUser, action.payload.id);
    yield put({ type: "USER_SUCCESS", payload: res });
  } catch (e) {
    yield put({ type: "USER_ERROR" });
  }
}

// 监听USER_FETCH，触发上面的异步
function* rootSaga() {
  yield takeLatest("USER_FETCH", fetchUserSaga);
}
```

- `call`：调用异步函数
- `put`：等价dispatch
- `takeLatest`：只执行最新一次请求，取消上一次（解决接口竞态）

优点：复杂异步、请求取消、轮询、并发控制能力很强。
缺点：学习成本高，generator语法晦涩；新项目RTK一般优先thunk。

---

# 中间件能干什么、不能干什么

✅能干：

1. 日志：打印每一个action、变更前后state
2. 埋点上报
3. 处理异步副作用（thunk/saga）
4. 修改、过滤、延迟、丢弃action
5. 报错捕获

❌不能干：

1. **不能修改state**，state修改依旧交给reducer纯函数；
2. 不要把业务计算逻辑写在中间件。

> 区分：
>
> - **中间件：处理副作用（异步、请求）**
> - **reducer：纯函数，只负责根据action计算新state**

## 完整数据流（带中间件）

```
组件 dispatch(action)
    ↓
中间件链(thunk/saga/log)
    ↓
原生dispatch
    ↓
reducer(纯函数)
    ↓
生成新state更新store
    ↓
useSelector订阅的组件对比返回值，决定是否重渲染
```

## 面试高频问题

### 1. 中间件执行顺序？

`applyMiddleware(A,B,C)`
进入顺序：A → B → C
next传递顺序：C next → B next → A next → 原生dispatch

### 2. thunk和saga怎么选？

- 简单异步、普通项目：**thunk足够，RTK内置**
- 大量复杂异步：轮询、取消请求、接口竞态、多任务编排，选saga。

### 3. RTK里面为什么不用手动写applyMiddleware？

`configureStore` 内部自动做，默认内置 `thunk`，还内置序列化检查中间件。

### 4. 中间件和reducer的边界

> 副作用（请求、定时器）放中间件；reducer必须是纯函数，不能有接口请求。

## 面试简短背诵版

> Redux中间件是位于dispatch和reducer之间的拦截层，是三层柯里化函数；通过applyMiddleware组合多个中间件。
> 它可以拦截action，处理日志、埋点、异步副作用；
> redux‑thunk允许dispatch传函数，简单异步首选，RTK内置；
> redux‑saga基于Generator，擅长复杂异步场景，可做请求取消、竞态处理；
> 中间件负责副作用，reducer保持纯函数，只做状态计算。

如果你需要，我可以手写极简版简易thunk中间件，帮助理解原理。

---

# Redux中间件做埋点：不是替代业务埋点，是**全局统一埋点**

你的理解是对的：**绝大多数点击、按钮触发的埋点，写在业务组件onClick里，这是业务埋点。**

中间件埋点，是**另一套场景：基于状态变更、action事件做埋点**，二者不冲突，各司其职。

> 核心前提：项目把业务动作都通过redux `dispatch(action)` 来描述。
> 用户点击按钮 → 组件dispatch一个action，而不是只调用一个普通函数。

举个对比：

## 方式A：业务组件内埋点（最常见）

```
// 普通，不经过redux
const handleSubmit = ()=>{
  // 业务埋点，写在业务回调
  track('form_submit_click')
  submitApi()
}
<button onClick={handleSubmit}>保存</button>
```

特点：

- 用户点击按钮直接上报；
- 只跟UI点击绑定；
- 如果**多个地方都要提交表单**，每一处都要手动写埋点，容易漏写、复制粘贴。

## 方式B：Redux中间件埋点（全局拦截action）

假设：项目里所有提交表单，统一派发同一个action `{type:'FORM_SUBMIT'}`

```
// 组件代码，只负责dispatch，不写埋点
const handleSubmit = ()=>{
  dispatch({type:'FORM_SUBMIT', payload: formValues})
}
<button onClick={handleSubmit}>保存</button>
```

然后写一个日志埋点中间件，拦截所有action：

```
const trackMiddleware = store => next => action => {
  // 在action进入reducer之前拦截
  if(action.type === 'FORM_SUBMIT'){
    // 统一埋点上报，所有派发FORM_SUBMIT的地方都会自动上报
    track('form_submit_click', action.payload)
  }
  return next(action)
}
```

👉 **只要任何地方dispatch `FORM_SUBMIT`，不管是：**

1. 用户点击保存按钮
2. 快捷键触发保存
3. 定时器自动保存
4. 弹窗内部的保存按钮

**全部自动执行埋点，不需要每个业务地方重复写track。**

---

# 分清两种埋点的适用场景

### 1、UI交互埋点（点击按钮、弹窗打开）→ 写业务代码

> 用户点击某个DOM、打开弹窗，本身是UI行为。
> 如果这个动作**没有dispatch redux action**，就**不能用中间件埋点**，只能写在onClick、onOpen回调。

> 比如 antd Modal打开：

```
<Modal open={open} onOpenChange={(v)=>{
  if(v) track('modal_open')
  setOpen(v)
}}/>
```

这个弹窗打开只是组件state，不走redux，中间件拦截不到，中间件管不了。

### 2、业务行为埋点（业务动作，已经映射为redux action）→ 适合中间件

> 动作的本质是业务行为，而不是单纯UI点击：

- 提交表单 `FORM_SUBMIT`
- 删除条目 `ITEM_DELETE`
- 切换筛选条件 `FILTER_CHANGE`
- 登录成功 `LOGIN_SUCCESS`

这些行为，项目中多处入口可以触发，统一dispatch同一个action。
此时在中间件拦截对应`action.type`做埋点，**只写一次，全局生效，不会漏埋**。

> 关键点：中间件只能拦截**dispatch出去的action**。
> 如果你的逻辑根本不走dispatch，中间件完全感知不到，也就做不了埋点。

## 那是不是把所有状态放redux，就全部中间件埋点？

❌**不是，不推荐全部塞redux只为埋点。**

1. 局部组件状态（弹窗显隐、输入框临时状态），放组件useState，没必要进redux；这部分UI交互埋点依旧写业务回调。
2. **跨组件、多处触发的业务行为**，才抽成redux action，利用中间件统一埋点。

## 举个现实例子：筛选条件

页面有3个地方可以切换“状态筛选”：

1. 下拉框选择
2. 快捷按钮点击
3. 重置按钮

三处都会 dispatch `{type:"SET_FILTER", payload:xxx}`。

- 如果每个地方都手写埋点，容易某一个开发忘记写track；
- 中间件拦截 `SET_FILTER`，只要这个业务动作发生，自动上报筛选埋点，一处编写全局生效。

## 中间件埋点的缺点

1. **埋点逻辑和UI位置脱离**：看埋点代码找不到对应的组件，排查问题成本上升；
2. 必须业务动作都走dispatch；如果某个分支不走dispatch，埋点就丢了；
3. 无法拿到DOM相关信息（点击的dom位置等），只能拿到action payload和store state。

> 所以企业真实项目一般是混合策略：
>
> - UI点击事件（弹窗打开、按钮曝光）：业务代码写埋点；
> - 业务行为（提交、删除、筛选，多入口触发）：redux中间件统一拦截action上报埋点。

## 回答你最开始的疑问总结

> Q：埋点不是应该写业务代码，用户点击按钮上报吗，为什么放在redux中间件？
> A：
>
> 1. UI层面的点击、弹窗打开，还是写业务onClick；中间件**不能替代这部分埋点**。
> 2. 当同一个**业务行为有多个触发入口**，代码中多处会dispatch同一个action；就可以在中间件拦截这个action.type做埋点，只写一次，所有入口自动上报，避免漏埋。
> 3. 前提：该业务动作必须走dispatch；如果只是组件useState，不走redux，中间件感知不到，无法埋点。
> 4. 不是把所有状态都塞进redux只为埋点；只有跨组件、多入口的业务动作才映射为action，利用中间件。

### 面试一句话总结

> Redux中间件埋点不是用来处理普通DOM点击埋点；主要针对多处入口触发的业务行为，当业务动作会dispatch特定action时，中间件拦截action做统一上报，减少重复埋点代码；普通UI交互埋点依旧写在业务组件回调中，中间件无法拦截组件内部useState的变更。
