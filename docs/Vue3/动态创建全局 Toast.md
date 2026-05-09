在 Vue 3 中，`createApp` 用于创建一个新的应用实例，它的基本用法是：

```javascript
const app = createApp(根组件, 可选的 props 对象)
```

你给出的代码：

```javascript
const app = createApp(ToastComponent, { message, type })
toastInstance = app.mount(div)
```

具体解释如下：

---

## 1. `createApp` 的两个参数

- **第一个参数 `ToastComponent`**  
  是一个 Vue 单文件组件（或选项对象），作为整个应用的**根组件**。

- **第二个参数 `{ message, type }`**  
  是传递给根组件的 **props**。  
  相当于在模板中直接使用 `<ToastComponent :message="message" :type="type" />`，只不过这里是通过编程方式创建并传入。

因此，`ToastComponent` 内部可以通过 `defineProps`（或 `props` 选项）接收 `message` 和 `type` 这两个属性。

---

## 2. `app.mount(div)`

- `mount` 方法将应用实例挂载到真实的 DOM 元素上。  
- 参数 `div` 通常是一个 **DOM 元素**（例如 `document.createElement('div')` 或某个已存在的元素 `document.querySelector('#toast')`）。  
- `mount` 会渲染根组件，并将生成的 DOM 替换或插入到该容器中。  
- **返回值**是**根组件实例**，赋值给 `toastInstance`。通过这个实例可以访问组件的方法、数据等（例如用于后续手动更新或销毁）。

---

## 3. 常见使用场景：动态创建全局 Toast / 弹窗

这种写法经常用于创建命令式的轻提示（Toast）或对话框。例如：

```javascript
// 创建一个 div 容器
const div = document.createElement('div')
document.body.appendChild(div)

// 动态挂载 Toast 组件，并传入属性
const toastInstance = createApp(ToastComponent, {
  message: '操作成功',
  type: 'success'
}).mount(div)

// 3 秒后卸载组件并移除 DOM
setTimeout(() => {
  toastInstance.unmount()   // Vue 3 组件实例提供了 unmount 方法
  div.remove()
}, 3000)
```

---

## 4. 与 Vue 2 的区别

- Vue 2 中使用 `new Vue({ ... }).$mount(el)`，并且全局配置（如插件、指令）会影响每一个实例。  
- Vue 3 的 `createApp` 返回一个**隔离的应用实例**，多个应用实例之间互不干扰，更利于组合和复用。

---

## 总结

| 步骤 | 作用 |
|------|------|
| `createApp(Comp, props)` | 创建一个以 `Comp` 为根组件、传入 `props` 的应用 |
| `app.mount(div)` | 将应用渲染到 DOM 元素 `div` 中，并返回根组件实例 |
| `toastInstance` | 可用来调用组件方法、访问数据或执行 `unmount()` 销毁组件 |

这种方式非常适合在非模板环境下（如纯 JS 逻辑中）临时渲染一个 Vue 组件，实现轻提示、加载中、模态框等需求。