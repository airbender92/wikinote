# React Portals

**Portals（传送门）**：把 React 组件的 DOM 节点，**渲染到父组件 DOM 层级之外的地方**，但是组件依然保留原有的 React 上下文、props、事件冒泡。

```
ReactDOM.createPortal(child, container)
```

- `child`：要渲染的 React 元素（JSX）
- `container`：真实 DOM 容器（`document.getElementById('xxx')`）

---

## 解决什么问题（核心用途）

### 1. 弹窗、模态框、抽屉、Tooltip 最常用

普通组件会受父元素 CSS 限制：

- 父元素设置 `overflow: hidden` → 弹窗被裁剪看不见
- 父元素设置 `z‑index` 堆叠上下文 → 弹窗层级被压住，怎么调 zIndex 都盖不住别的元素

Portal 将 DOM 直接挂载到 `body` 下，跳出父容器的样式限制，完美解决弹窗层级、裁剪问题。

示例：

```
function Modal({ children }) {
  const dom = document.getElementById('modal-root');
  if (!dom) return null;
  return ReactDOM.createPortal(
    <div className="modal">{children}</div>,
    dom
  )
}
```

> html 需要提前写 `<div id="modal-root"></div>`

### 2. 事件冒泡依然遵守 React 组件树，不是 DOM 树

👉 **重点坑点**：
DOM 上 Portal 子元素挂在 body，但**事件冒泡向 React 组件父组件传播，而不是 DOM 的父节点(body)**。

```
<Parent onClick={()=>console.log('父组件')}>
  {createPortal(<Child onClick={()=>console.log('子')}, document.body)}
</Parent>
```

点击 Child：会先打印子，再打印父。
虽然 Child DOM 在 body，但事件冒泡走 React 组件树，不是 DOM 树。
这是 Portal 非常关键的特性。

### 3. 保留 Context、Ref、生命周期

虽然 DOM 挪走了：

- Context 可以正常消费
- ref 可以正常拿到内部 DOM
- state、effect 生命周期完全和原来组件一致

只是物理 DOM 位置变了，逻辑归属不变。

---

## 什么时候不要用 Portal

1. 只是普通局部 UI，不需要跳出父容器，没必要；
2. 需要 CSS 继承（父的 font、color 等）：DOM 移到 body，**CSS 继承会失效**，因为 DOM 不在原来父元素下；>

> 解决方案：css‑variables，不要依赖继承。

## 常见坑总结

1. 需要提前准备真实 DOM 容器，不要直接 `document.body`（容易和其他第三方库冲突，建议单独 div）
2. `SSR` 环境不能直接访问 `document`，要 `useEffect` 里再创建 portal

```
// SSR兼容写法
const [container, setContainer] = useState(null);
useEffect(()=>{
  setContainer(document.getElementById('modal-root'))
},[])
if(!container) return null;
return createPortal(<></>, container)
```

3. 事件冒泡是**组件树**不是 DOM 树，容易踩事件捕获/冒泡的预期偏差
4. 会丢失父元素 CSS 继承

## 简单记忆

> Portal = **逻辑还在当前 React 组件，DOM 扔到页面别的地方**。
> 主要用于：Modal、Drawer、Tooltip、悬浮菜单这类需要跳出父容器的组件。

如果你需要，我可以给你一份完整可直接复制的 Modal 最简封装。
