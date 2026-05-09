## Pinia 实例 API 详解：`$patch`、`$reset`、`$subscribe`、`$onAction`、`$dispose`

Pinia Store 实例除了 state、getters、actions，还提供几个**内置实例方法**（以 `$` 开头），用于高级操作：批量修改、重置、订阅变化、监听 action 执行、销毁 store。

---

## 一、`$patch` – 批量更新 state

### 用途
同时修改 state 中的多个属性，**只触发一次响应式更新**（性能优于多次单独赋值）。支持两种写法：对象形式或函数形式。

### 语法
```ts
// 对象形式：直接指定要修改的字段
store.$patch({
  count: store.count + 1,
  name: 'new name'
})

// 函数形式：接收当前 state，可以执行复杂逻辑（如数组操作）
store.$patch((state) => {
  state.items.push(newItem)
  state.total += item.price
})
```

### 核心特点
- **批量更新**：无论修改多少个字段，只触发一次视图更新。
- **部分更新**：对象形式中未指定的字段保持原样。
- **函数形式**适合依赖当前 state 的复杂变更（如数组 push、条件修改）。

### 常见坑点 ⚠️

| 坑点 | 说明 | 正确做法 |
|------|------|----------|
| **对象形式覆盖深层嵌套** | `$patch({ user: { age: 30 } })` 会**替换**整个 `user` 对象，而不是合并深层属性 | 如果需要合并深层对象，使用函数形式：`state.user.age = 30` |
| **函数形式中直接替换整个 state** | `(state) => state = newState` 无效，因为参数是响应式代理的引用 | 使用 `Object.assign(state, newState)` 或 `$state = newState` |
| **使用未定义的属性** | `$patch({ newProp: 'value' })` 会动态添加属性，是允许的，但可能破坏类型 | 尽量在 state 初始化时声明所有属性 |
| **多次调用 `$patch` 而非一次** | 连续调用多个 `$patch` 会触发多次更新 | 合并成一个 `$patch` 调用 |
| **在 `$patch` 函数中执行异步操作** | 异步回调中修改 state 不会包含在本次 patch 事件中 | 不要在 `$patch` 函数内写异步代码 |

---

## 二、`$reset` – 重置 state 到初始值

### 用途
将 store 的 state **完全重置**为定义时的初始状态。

### 语法
```ts
store.$reset()
```

### 注意事项
- **仅 Options Store 自动提供**：因为 Pinia 知道初始 state 函数。
- **Setup Store 没有内置 `$reset`**：需要手动实现（因为 Pinia 无法获取初始值）。

### 手动为 Setup Store 实现 `$reset`
```ts
const useSetupStore = defineStore('setup', () => {
  const initialState = { count: 0, name: 'pinia' }
  const state = ref(initialState)
  
  function $reset() {
    state.value = { ...initialState }
  }
  
  return { ...state.value, $reset }
})
```

### 常见坑点 ⚠️

| 坑点 | 说明 | 正确做法 |
|------|------|----------|
| **在 Setup Store 中使用 `$reset` 报错** | `store.$reset is not a function` | 手动实现 `$reset` 方法 |
| **重置后某些引用未被覆盖** | 若初始 state 包含对象/数组，`$reset` 会创建全新对象，旧引用全部断开 | 正常现象，无需担心 |
| **`$reset` 不会触发 `$subscribe` 回调** | 否，它会触发（因为内部通过 `$patch` 实现） | 了解即可 |
| **在 action 中调用 `$reset` 后又修改其他状态** | 可能造成意外覆盖 | 先 `$reset` 再修改，或使用 `$patch` |

---

## 三、`$subscribe` – 监听 state 变化

### 用途
当 store 中的 **任何 state 改变** 时执行回调，类似于 Vue 的 `watch` 但专为 Pinia 设计。

### 语法
```ts
const unsubscribe = store.$subscribe(
  (mutation, state) => {
    // mutation: { storeId, type, events }
    // state: 当前 state（响应式对象）
  },
  options // { detached?: boolean, deep?: boolean, flush?: 'pre'|'post'|'sync' }
)
```

### 关键选项
- `detached: true`：组件卸载后**不自动取消**订阅（默认 `false`，即自动取消）。
- `deep: true`：深度监听嵌套对象变化（默认 `false`）。
- `flush: 'post'`：类似 `watch` 的刷新时机。

### 返回值
一个取消订阅的函数，调用后停止监听。

### 常见坑点 ⚠️

| 坑点 | 说明 | 正确做法 |
|------|------|----------|
| **默认在组件卸载时会自动取消** | 若希望全局持久订阅（如持久化到 localStorage），需设置 `{ detached: true }` | 根据需求决定是否 detached |
| **在 `$subscribe` 回调中修改同一个 store 的 state** | 容易造成无限循环 | 如果需要修改，先判断条件（如 `if(condition) store.$patch({...})`） |
| **`mutation.events` 并非总是完整** | 嵌套对象的深层变更可能没有详细路径 | 不要依赖 `events` 做业务逻辑，只用它调试 |
| **多次订阅的执行顺序** | 按注册顺序同步执行，一个报错会中断后续 | 确保回调内无异常，或用 `try...catch` |
| **订阅未取消导致内存泄漏** | 若设置了 `detached: true` 却忘记调用返回的 `unsubscribe` | 在 `onUnmounted` 或适当时机取消 |

---

## 四、`$onAction` – 监听 action 的执行

### 用途
监听 **action 开始、成功、失败** 等生命周期。常用于日志、埋点、全局 loading 管理等。

### 语法
```ts
const unsubscribe = store.$onAction(
  ({
    name,    // action 名称
    store,   // store 实例
    args,    // action 参数数组
    after,   // 成功后回调（接收返回值）
    onError, // 失败后回调（接收错误）
  }) => {
    // 同步执行（action 执行前）
    console.log(`Action ${name} called with`, args)
    
    after((result) => {
      console.log(`Action ${name} succeeded with`, result)
    })
    
    onError((error) => {
      console.error(`Action ${name} failed`, error)
    })
  },
  options // { detached?: boolean }
)
```

### 典型应用
- 全局请求 loading 管理（监听所有异步 action）
- 错误上报（捕获 action 抛出的异常）
- 性能监控（记录 action 执行耗时）

### 常见坑点 ⚠️

| 坑点 | 说明 | 正确做法 |
|------|------|----------|
| **`after` 和 `onError` 在 action 返回 Promise 时** | 对于异步 action，`after` 在 Promise resolve 后执行，`onError` 在 reject 时执行 | 正确，无需额外处理 |
| **在回调中修改 state 可能引发副作用** | 虽然允许，但不建议（违反单一职责） | 只做监听，不改变状态 |
| **默认自动取消订阅** | 类似 `$subscribe`，默认组件卸载时取消 | 需要全局监听则设置 `detached: true` |
| **无法获取 action 内部的中间状态** | 只能拿到最终结果或错误 | 若要追踪中间过程，在 action 内部手动触发事件 |
| **监听所有 action 导致性能问题** | 如果 store 有大量高频 action，回调中的逻辑应尽量轻量 | 避免在回调中执行重计算或 DOM 操作 |

---

## 五、`$dispose` – 销毁 store 实例

### 用途
**停止 store 的响应式效果**，清理内部订阅和监听器。通常用于**服务端渲染（SSR）**或**动态卸载 store** 的场景。

### 语法
```ts
store.$dispose()
```

### 行为
- 移除所有 `$subscribe` 和 `$onAction` 订阅。
- 停止 store 内部的响应式依赖追踪。
- 调用后 store 不再是响应式，再修改 state 不会触发视图更新。

### 常见坑点 ⚠️

| 坑点 | 说明 | 正确做法 |
|------|------|----------|
| **销毁后无法恢复** | 必须重新创建 store 实例（通过 `useStore()` 重新获取） | 销毁前确保不再需要 |
| **在组件中随意调用 `$dispose`** | 可能导致其他组件依赖此 store 的地方失效 | 几乎不需要在组件中手动调用，除非特殊场景 |
| **SSR 中未正确销毁导致内存泄漏** | 每个请求结束后应调用 `$dispose` 清理状态 | 在 `onServerPrefetch` 或请求处理完毕后调用 |
| **与 `store.$reset` 混淆** | `$reset` 重置数据但保留响应性；`$dispose` 销毁整个 store | 明确需求择一使用 |

---

## 六、API 对比总结

| API | 主要用途 | 是否影响响应式 | 是否可恢复 | 推荐使用场景 |
|-----|----------|----------------|------------|--------------|
| `$patch` | 批量更新 state | 会触发更新 | - | 一次性修改多个字段 |
| `$reset` | 重置为初始 state | 会触发更新 | 是（再次修改） | 清空表单、登出重置 |
| `$subscribe` | 监听 state 变化 | 仅监听 | 可取消/重订阅 | 持久化、日志 |
| `$onAction` | 监听 action 生命周期 | 仅监听 | 可取消/重订阅 | 埋点、全局 Loading |
| `$dispose` | 彻底销毁 store | 移除所有响应性 | 否（需重新获取 store） | SSR 清理、动态 store 卸载 |

---

## 七、记忆口诀

> **批量修改用 $patch，重置归位 $reset；**
> **变化订阅 $subscribe，动作监听 $onAction；**
> **销毁实例 $dispose，场景分清别用岔。**

掌握这些实例 API，你能更灵活地控制 Pinia Store 的行为，实现日志、持久化、重置等高级需求。