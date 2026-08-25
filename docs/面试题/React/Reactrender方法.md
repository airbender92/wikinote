# React render() 原理 & 触发时机

> 注意区分两个概念：
>
> 1. **类组件的实例方法 `render()`**：用户写的组件 render 函数，返回 JSX
> 2. **`ReactDOM.render` / `createRoot().render()`**：根渲染入口，挂载整个应用

我们讲的是**类组件的 render()**，函数组件没有 render 方法，函数组件本身就是 render。

## 一、render() 原理

```
class Demo extends React.Component {
  render() {
    return <div>hello {this.state.count}</div>
  }
}
```

1. `render()` 是**纯函数**：输入 `this.props` + `this.state`，输出 **React Element（虚拟DOM）**
2. Babel 把 JSX 编译成 `React.createElement(type, props, children)`，返回普通 JS 对象，就是虚拟DOM。

```
<div>hello {this.state.count}</div>
//编译后
React.createElement("div", null, "hello ", this.state.count)
```

3. render **只生成虚拟DOM描述，不操作真实DOM**。
4. render执行完得到虚拟DOM树，交给Fiber协调器（Reconciler）做diff，构建Fiber节点；
   等到 **commit阶段**，才由 react‑dom 把真正DOM更新到页面。

> ✅ render里面只做计算、返回JSX
> ❌ render里面禁止：setState、发请求、定时器、订阅事件（副作用）

> 函数组件：整个函数体就等价于类组件的 render，执行函数，返回JSX。

## 二、什么时候组件 render() 会被触发（核心高频考点）

组件进入更新流程，就会调用 render，一共**4种触发场景**

### 1️⃣ 组件自身执行 `this.setState()`

state改变 → 触发当前组件更新，执行 render。

> 注意：setState 不一定立刻改state，会合并批量更新；但会标记组件需要更新。

### 2️⃣ 组件自身执行 `this.forceUpdate()`

强制更新，**忽略state是否变化，直接调用render**，不会调用 shouldComponentUpdate。

### 3️⃣ 父组件 render() 执行

**父组件重新render，默认所有子组件也会执行 render！**

> ⚠️非常重要：**子组件props没变化，子组件依然会执行render**。
> render执行 ≠ DOM一定修改。render生成新虚拟DOM，diff发现没变化，commit阶段就不会碰真实DOM。
> 👉 这就是为什么需要 `PureComponent / memo`，阻止不必要的子组件render执行。

### 4️⃣ 类组件接收新的 props

父传props发生变化，子组件触发更新，执行render。

> 补充：不是props对象引用变才触发，父组件render，哪怕props完全一样，子组件依然render。

---

## ❗不会触发render的情况

1. state赋值直接修改，不用setState：`this.state.count = 10`，不会触发render。>

> React感知不到修改，必须setState。

2. shouldComponentUpdate 返回 false → **阻止render执行**
3. PureComponent / React.memo：props和state浅比较相等，跳过render执行。

## 📌 Fiber架构下 render 的执行阶段

`render()` 运行在 **Render阶段（可中断阶段）**

- 也就是协调阶段，构建虚拟DOM、Fiber树；
- **可以被暂停、抢占、重复执行**（并发模式下）
- 此时页面真实DOM完全没有改动。

> 执行顺序：
> setState → 标记需要更新 → Scheduler调度 → 执行组件render()得到虚拟DOM → Fiber diff构建WIP树 → **全部render工作完成后，一次性进入Commit阶段，修改真实DOM**

### 时间线简单梳理

```
setState()
    ↓
标记组件有更新，交给调度器Scheduler
    ↓
【Render阶段（可中断）】
shouldComponentUpdate → render() → getDerivedStateFromProps
生成虚拟DOM，diff，打effect标记
    ↓
【Commit阶段（不可中断，一次性操作DOM）】
getSnapshotBeforeUpdate → 更新真实DOM → componentDidUpdate
```

## 高频面试坑点

1. **render执行 ≠ DOM更新**
   render只是生成虚拟DOM；diff之后发现节点无差异，不会操作真实DOM。render执行是JS计算，DOM修改发生在commit。
2. **父组件render，子组件默认无条件render**
   很多人误以为props不变子组件就不会render，这是错的。memo/PureComponent就是用来解决这个重复render性能开销。
3. render会被并发模式重复调用
   Fiber并发渲染，render阶段可以回滚重跑，**所以render必须是纯函数，绝对不能写副作用**。请求、定时器不能写在render。
4. `forceUpdate`：跳过shouldComponentUpdate，直接执行render。

## 函数组件对应关系

- 类组件：`render()` 方法
- 函数组件：**整个函数体执行 = render过程**
  `useState` 更新触发函数重新执行，等价类组件调用render。
  `React.memo` 等价类的PureComponent。

## 一句话总结

> render() 根据 props+state 计算返回虚拟DOM，**不碰真实DOM**；
> 触发条件：setState、forceUpdate、父组件render、props改变；
> render运行在可中断的Render阶段，必须是纯函数；render执行不等于DOM一定会变化。

如果你需要，我可以讲 shouldComponentUpdate / PureComponent / memo 的对比，讲怎么减少不必要render。
