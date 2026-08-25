# React setState 同步还是异步

> **核心结论：并不是真正异步，是批量更新策略。**
> `setState` **本身函数调用是同步执行的，但是 state 的更新、组件重新渲染，不一定立刻生效。**

## 1、两种模式（React18 是分水岭，面试重点）

### React17及更早

#### ① 合成事件、生命周期内部 → **批量更新，state不会立刻更新（表现像异步）**

```jsx
handleClick = () => {
  console.log(this.state.num); // 0
  this.setState({ num: 1 });
  console.log(this.state.num); // 还是 0！不会马上拿到1
};
```

- setState 执行了，但是 state 没有马上改变；react 把多个 setState 收集起来，事件结束后**合并批量更新一次**，再渲染。
- 多次setState会合并：

```js
this.setState({ num: this.state.num + 1 });
this.setState({ num: this.state.num + 1 });
// 最终只 +1，不是+2，对象式setState会合并
```

> 如果要依赖上一次state，用函数式setState：

```js
this.setState((prev) => ({ num: prev.num + 1 }));
```

#### ② 原生DOM事件、setTimeout、Promise回调（脱离react合成事件）→ 同步更新，立刻拿到最新state

```js
componentDidMount(){
  document.getElementById('btn').onclick = ()=>{
    console.log(this.state.num) //0
    this.setState({num:1})
    console.log(this.state.num) //1，立刻生效
  }
}
```

定时器里：

```js
setTimeout(() => {
  this.setState({ num: 1 });
  console.log(this.state.num); //拿到最新值
}, 0);
```

> React17：是否批量，看是否处于React合成事件上下文。

---

## ✨React18（包含18之后）行为大变化

> **React18，只要是React可以控制的上下文，全部自动批量更新！**
> 不管是：合成事件、setTimeout、Promise、fetch回调，**全部批量，setState后拿不到最新state**。

```jsx
// React18
const handleClick = () => {
  setTimeout(() => {
    setCount(1);
    console.log(count); // ❗依旧是旧值，不再同步更新！
  });
};
```

React18把批量更新扩大到了所有场景。

### React18如何强制不批量，立刻更新？

`flushSync`，强制同步刷新state、立刻渲染。

```jsx
import { flushSync } from "react-dom";

flushSync(() => {
  setCount(1);
});
console.log(count); // 拿到最新
```

## 函数组件 useState 和 setState行为完全一致

```jsx
const [count, setCount] = useState(0);

const click = () => {
  setCount(1);
  console.log(count); // 旧值，不会立刻变
};
```

> setCount也是一样，**调用同步，state更新渲染延迟**。

## 为什么不是真正异步？

setState**函数本身是同步执行**，你调用它这行代码马上跑完；
只是 React 把状态更新、re‑render 放到后面队列执行，不是 setTimeout 那种异步。

## 多次setState合并规则

1. **对象形式 setState**：会合并，多次调用只生效最后一次

```js
setState({ count: state.count + 1 });
setState({ count: state.count + 1 });
// 只+1
```

2. **函数式 setState**：不会合并，依次执行

```js
setState((prev) => ({ count: prev.count + 1 }));
setState((prev) => ({ count: prev.count + 1 }));
// +2
```

## 怎么拿到更新后的state？

1. 类组件：setState第二个回调

```js
this.setState({ num: 1 }, () => {
  console.log(this.state.num); // 最新值
});
```

2. 函数组件：用 `useEffect` 监听state变化

```js
useEffect(() => {
  // count更新后执行
}, [count]);
```

## 面试背诵精简版

> setState函数调用本身是同步，**状态更新和渲染是异步（批量更新）**。
> React17：合成事件、生命周期内批量更新；定时器、原生DOM事件会同步更新state，可以马上拿到新值。
> React18扩大了自动批量更新范围，即使setTimeout、Promise回调也会批量，set完拿不到最新state；需要强制同步使用flushSync。
> 对象写法多次setState会合并，函数式setState可以基于前一次状态计算；
> 获取更新后状态：类组件用第二个回调；函数组件用useEffect监听。

### 高频追问：为什么要批量更新？

> 避免频繁重复渲染，多个状态修改只触发一次render，提升性能。

如果你需要，我可以顺带讲下合成事件原理。
