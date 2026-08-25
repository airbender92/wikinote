# React 废弃三个 will 系列生命周期

`componentWillMount`、`componentWillReceiveProps`、`componentWillUpdate`，统称为 **unsafe 生命周期**，React16.3 打上 `UNSAFE_` 前缀，React18 并发模式下正式不推荐使用。

> 新名字：`UNSAFE_componentWillMount`
> `UNSAFE_componentWillReceiveProps`
> `UNSAFE_componentWillUpdate`

**根本原因：为了适配 Fiber 并发渲染（可中断、可重跑），这三个生命周期在可中断渲染下执行逻辑会被破坏，会产生bug。**

## 回顾Fiber并发Render阶段特点

Render阶段（构建fiber、diff）**可以暂停、可以被抢占、可以重复执行**。

> ⚠️ Render阶段不是只跑一次！高优先级任务插队时，前面低优先级的render工作可以回滚，**重新再跑一遍render流程**。

而这三个生命周期是运行在 **Render阶段**。
如果render可以重复执行，这几个钩子就会**被多次调用**，开发者几乎都会写出bug。

### 1. componentWillMount

> 挂载前执行，旧写法经常在这里做：发请求、设置state、操作DOM。

问题：

1. **Fiber并发模式下，这个钩子可能执行多次，但组件还没真正挂载到DOM上，commit还没发生**。
   你在这里写接口请求，会重复发多次网络请求。
2. SSR场景：服务端执行willMount，客户端又再执行一遍，容易数据不一致。
3. 很多人误以为在这里可以访问DOM，实际上此时DOM还不存在。

✅ 替代：

- 请求、副作用 → `componentDidMount`
- 初始化state → 直接class构造器 `constructor` 或者类字段初始化

### 2. componentWillReceiveProps(nextProps)

> props变化触发更新前执行，大量老项目在这里对比props，更新state：

```js
componentWillReceiveProps(nextProps) {
  if(nextProps.id !== this.props.id) {
    this.setState({ data: null });
    this.fetchData(nextProps.id)
  }
}
```

重大问题：
并发渲染中，**props还没真正更新到组件实例，这个钩子就可能反复执行**。
`this.props` 还是旧值，但nextProps是新的；如果render被中断重来，该钩子会重复跑，重复调用接口、重复setState。

> 很多人踩坑：以为只有props真正改变才执行，实际上React可以在更新过程中多次调用它。

✅ 替代方案：`getDerivedStateFromProps`（静态）

```js
static getDerivedStateFromProps(nextProps, prevState) {
  // 返回对象更新state，返回null不更新
}
```

静态函数，**不能访问this，不能写副作用、不能发请求**，只允许计算state。

> 注意：getDerivedStateFromProps是纯函数，只做状态推导，**不能放网络请求**。请求依然放到 `componentDidUpdate`。

### 3. componentWillUpdate(nextProps, nextState)

> state/props准备更新，DOM还没修改之前执行。

常见错误用法：在这里读取DOM，获取元素宽高。

Fiber下风险：
render阶段可中断，`componentWillUpdate`执行完，**更新被暂停/被丢弃，commit根本不会执行**。
钩子执行了，DOM却没有更新。你拿到的DOM信息是过期错误的。

✅ 替代：要读取更新后的DOM，放到 `componentDidUpdate`。

## 关键区分两个阶段（非常核心）

1. **Render阶段（可中断、可重复执行）**
   旧：`willMount / willReceiveProps / willUpdate` → 全部unsafe
   新：`static getDerivedStateFromProps`

> 这个阶段**禁止任何副作用**：网络请求、DOM读取、定时器、事件订阅都不能写！

2. **Commit阶段（同步，不可中断，只执行一次）**
   `componentDidMount`、`componentDidUpdate`、`componentWillUnmount`
   DOM已经真正变更，只会执行一次，**所有副作用放这里**。

## 为什么之前React15没事？

React15 Stack Reconciler是**同步不可中断递归**，render只会跑一次。
所以这三个钩子只会执行一次，业务代码可以正常跑。

但是Fiber并发模式，Render可以暂停、回滚、重跑。
原来依赖“钩子只执行一次”的业务逻辑全部失效，会出现：

- 重复网络请求
- state错误更新
- 获取到错误DOM尺寸
- 重复订阅事件造成内存泄漏

React不能继续保留这三个钩子，否则老代码迁移到并发模式会大量隐性bug。

> 不是钩子本身写得烂，是**并发渲染模型改变了钩子的执行时机和执行次数**。

## 补充误区

1. 不是直接删除代码，只是加上 `UNSAFE_` 前缀；你不改代码依然可以跑，但是开启并发特性后会出现不可预期bug。
2. `getSnapshotBeforeUpdate` 是新增的安全钩子，放在render结束后，commit DOM更新**之前**，安全读取DOM信息，用来替代一部分willUpdate场景。

```js
// getSnapshotBeforeUpdate，commit前读取DOM，返回值传给componentDidUpdate第三个参数
getSnapshotBeforeUpdate(prevProps, prevState) {
  return this.ref.scrollHeight;
}
componentDidUpdate(prevProps, prevState, snapshot) {
  // snapshot拿到上一轮DOM信息
}
```

## 极简总结

> 三个will生命周期运行在Render阶段；Fiber并发模式下Render可以暂停、回滚、多次执行。
> 业务常在will钩子写请求、读DOM、setState，多次执行就会产生bug。
> 所以废弃它们：状态推导交给`getDerivedStateFromProps`；DOM读取、接口请求等副作用全部迁移到commit阶段（didMount/didUpdate）。

---

# 什么是状态推导

**状态推导：根据 props 去计算、生成 state。**

> 外部传入 props → 组件内部基于 props 算出组件自己的 state。
> 注意：**只做计算，不能发请求、不能定时器、不能产生副作用**。

## 旧写法：componentWillReceiveProps（不安全）

以前我们经常在 `componentWillReceiveProps` 做状态推导：

```
componentWillReceiveProps(nextProps) {
  // 状态推导：props.id变化，更新内部state
  if(nextProps.userId !== this.props.userId) {
    this.setState({
      userInfo: null
    })
  }
}
```

问题：

1. Fiber并发模式 render 会重复执行，这个函数会跑多次，如果你在这里顺便写请求，就会重复请求。
2. 实例方法，可以访问 `this`，很容易顺手写副作用。

---

## getDerivedStateFromProps 就是专门用来做【状态推导】

```
static getDerivedStateFromProps(props, state) {
  // props：最新的外部传入属性
  // state：当前组件内部state

  // 返回一个对象，会合并更新state；返回 null 表示不修改state
  if(props.userId !== state.lastUserId) {
    return {
      userInfo: null,
      lastUserId: props.userId
    }
  }
  return null;
}
```

### 关键点

1. **static 静态方法！没有 this**
   不能调用 `this.setState`，不能访问组件实例，杜绝你在这里写请求、订阅事件等副作用。
2. **执行时机：每次 render 之前都会跑**
   不管是 props 变了，还是 setState 引起更新，都会执行。
3. **输出只能是新state，或者null，纯函数，输入(props,state) → 输出state**>

> ✅允许：根据props计算state
> ❌禁止：ajax请求、定时器、ref操作DOM、事件监听

### 为什么叫“推导”

> 推导 = 计算得出，不是手动触发副作用。
> 就像数学：`y = f(x)`，x是props，y是state，输入x，算出y。
> **不做别的事情，只做计算。**

## 举个完整业务例子

父组件传进来 `selectedId`，子组件内部维护 `currentSelect`，当外部 selectedId 变化，同步更新内部状态。

```
class List extends React.Component {
  state = {
    currentSelect: null,
    prevSelectId: null
  }

  static getDerivedStateFromProps(props, state) {
    // 状态推导：外部props.selectedId改变，同步内部state
    if(props.selectedId !== state.prevSelectId) {
      return {
        currentSelect: props.selectedId,
        prevSelectId: props.selectedId
      }
    }
    return null
  }

  render(){
    return <div>{this.state.currentSelect}</div>
  }
}
```

> ⚠️坑：因为每次render都会执行，**必须保存上一次的标记到state里做对比**，不能直接拿 props 和 state.currentSelect对比，否则会无限循环更新。

## getDerivedStateFromProps 不能干什么？

很多人误用，在这里写网络请求：

```
static getDerivedStateFromProps(props, state){
  // ❌绝对禁止！！这是render阶段，可重复执行，会发多次请求
  fetch(`/api/${props.id}`)
  return null
}
```

**接口请求属于副作用，放到 commit 阶段 componentDidUpdate / componentDidMount**

```
componentDidUpdate(prevProps) {
  if(this.props.id !== prevProps.id) {
    this.fetchData(this.props.id) // ✅这里才发请求
  }
}
```

## 现实开发：getDerivedStateFromProps 其实很少用

官方文档说：**大多数场景，你并不需要它**。

两种真正需要状态推导的场景：

1. prop变化，重置组件内部state（弹窗打开重置表单、id切换重置详情）
2. props作为唯一来源，内部state需要跟随props同步

很多时候可以直接在render里直接用props，根本不需要复制到state。

> ❌反模式：把props无脑复制一份到state，完全没必要。

```
// 不好，无意义的状态推导
static getDerivedStateFromProps(props){
  return { name: props.name }
}
// render直接用 this.props.name 就够了，不要存state
```

## 结合Fiber再串一遍

1. 旧 `componentWillReceiveProps`：render阶段执行，可访问实例，开发者容易写副作用；并发模式render会重复跑 → 副作用重复执行出bug。
2. `getDerivedStateFromProps`：同样render阶段执行，但是static静态函数，没有this，**强制只能做状态推导（纯计算），从语法层面杜绝写副作用**。
3. 所有IO、DOM操作、订阅等副作用，全部挪到 commit 阶段（didMount / didUpdate），commit阶段只会执行一次，不会重复跑。

## 一句话总结

> **状态推导：用props计算生成组件内部state，只做纯计算，不做任何副作用。`getDerivedStateFromProps`就是React专门给状态推导设计的静态钩子，从语法上限制你不能写网络请求等副作用，适配Fiber可中断渲染。**

如果你需要，我可以讲：getSnapshotBeforeUpdate，和它做对比，分清 render阶段 和 commit阶段两个钩子分工。
