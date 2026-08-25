# React合成事件 vs 原生DOM事件 执行顺序

> 核心前提：React17 之前，**合成事件全部委托到 document**；React17+ 改成委托到 root 容器（#root），不再绑document，但事件冒泡逻辑原理不变。

React 的事件不是原生DOM事件，是**合成事件 SyntheticEvent**。
浏览器原生事件先执行，触发冒泡到容器，React 再执行自己的合成事件回调。

## 执行总顺序（冒泡场景，最常考）

```
1. 子元素【原生捕获事件】
2. 父元素【原生捕获事件】
-------- DOM开始目标阶段 --------
3. 目标元素【原生目标事件】
-------- DOM开始冒泡阶段 --------
4. 子元素【原生冒泡事件】
5. 父元素【原生冒泡事件】
→ 事件冒泡到 React root容器，触发容器上的原生监听
6. React执行【合成事件冒泡】（onClick、onChange...）
```

### 重点结论

**同元素：原生冒泡事件 优先于 React合成事件执行。**

示例代码：

```
<div id="root">
  <button id="btn" onClick={()=>{
    console.log("React合成事件 onClick")
  }}></button>
</div>

// js原生绑定
document.getElementById('btn').addEventListener('click',()=>{
  console.log("btn原生冒泡 click")
},false)
```

点击按钮输出顺序：

```
btn原生冒泡 click
React合成事件 onClick
```

---

## 捕获模式

原生可以开启捕获 `addEventListener(..., true)`
React 的 `onClickCapture` 是**合成捕获事件**。

完整捕获顺序：

1. root容器原生捕获
2. 父元素原生捕获
3. 目标元素原生捕获
4. 【React合成捕获事件 onClickCapture】
5. 目标原生事件
6. 子原生冒泡
7. 父原生冒泡
8. 【React合成冒泡 onClick】

> React的合成捕获，依然是等事件冒泡到root容器之后，React内部模拟捕获、冒泡顺序，**并不是DOM原生捕获**。
> React没有把回调绑定到真实DOM节点上，全部在root代理。

## stopPropagation 的大坑（面试高频）

### 1. 原生事件调用 `e.stopPropagation()`

```
btn.addEventListener('click',(e)=>{
  e.stopPropagation() // 原生阻止冒泡
},false)
```

原生阻止冒泡，事件不会向上冒泡到 #root 容器。
👉 **React合成事件根本不会执行！**

### 2. React合成事件调用 `e.stopPropagation()`

```
<button onClick={(e)=>{
  e.stopPropagation() // 合成事件的stopPropagation
}} />
```

⚠️ **只能阻止 React合成事件 的模拟冒泡，不会阻止浏览器真实DOM事件冒泡。**
也就是说：原生事件依然会继续向上冒泡。

> 原因：SyntheticEvent是React包装的对象，不是浏览器原生event。合成事件的stopPropagation只作用于React内部模拟的事件系统，不影响真实DOM事件流。

如果你要阻止真实DOM冒泡，拿到原生事件：

```
onClick={(e)=>{
  e.nativeEvent.stopImmediatePropagation()
}}
```

- `e.nativeEvent`：浏览器原生Event对象
- `stopImmediatePropagation`：阻止这个元素剩下同类型监听，并且停止冒泡。

## React16 vs React17 事件委托变化

1. React16‑：所有合成事件委托到 `document`
   - 如果你自己在 document 绑定原生click，会比React合成事件更早执行。
2. React17+：委托到应用挂载根节点 `#root`，不再用document。
   - 如果你在#root外层再套div绑定原生事件，顺序会跟着变化，但底层逻辑不变。

## 完整Demo输出顺序汇总

```
<div id="outer">
  <div id="root">
    <button id="innerBtn" onClick={()=>console.log('react子onClick')}>click</button>
  </div>
</div>
```

```
// innerBtn 原生冒泡
innerBtn.addEventListener('click',()=>console.log('innerBtn原生冒泡'),false)
// root 原生冒泡
root.addEventListener('click',()=>console.log('#root原生冒泡'),false)
// outer 原生冒泡
outer.addEventListener('click',()=>console.log('outer原生冒泡'),false)
```

点击按钮输出顺序：

1. innerBtn原生冒泡
2. #root原生冒泡
3. outer原生冒泡
4. react子onClick ✨合成事件在这里执行

> 为什么#root原生冒泡先打印？因为真实DOM冒泡先走到root，root上的原生监听先执行；**然后才触发React内部逻辑，执行合成事件回调**。

## 面试极简记忆口诀

1. **原生事件永远比同层级React合成事件先跑**；React合成事件是冒泡到root容器后才统一执行。
2. `e.stopPropagation()`（合成事件）只管React内部模拟冒泡，拦不住原生DOM冒泡。
3. 原生调用stopPropagation，事件到不了root，React合成事件直接不执行。
4. `e.nativeEvent` 拿到浏览器真实事件对象。

## 容易踩坑业务场景

- 弹窗点击外部关闭：混用原生document监听和React onClick，会出现点击弹窗内部也触发关闭；根源就是事件执行顺序问题。

如果你需要，我可以写一段可复制完整demo，还有讲解 `stopPropagation` / `stopImmediatePropagation` 的区别。
