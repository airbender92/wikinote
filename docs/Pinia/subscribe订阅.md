## `$subscribe` 的作用：监听 State 变化，执行副作用

`userStore.$subscribe` 是 Pinia 提供的一个**订阅函数**，用来监听当前 Store 中 **state 的任何变化**（无论是通过直接赋值、`$patch` 还是 action 修改）。当 state 改变时，你注册的回调函数就会触发。

---

### 一、典型使用场景

| 场景 | 说明 |
|------|------|
| **持久化存储** | 将 state 自动保存到 `localStorage` 或 `IndexedDB` |
| **日志记录** | 追踪用户操作导致的状态变化，用于调试或埋点 |
| **同步到后端** | 实时同步重要状态到服务器（如草稿自动保存） |
| **触发其他非响应式逻辑** | 当某个数据变化时，更新非 Vue 生态的工具（如更新一个全局变量、调用原生 API 等） |
| **跨 Store 协作** | 监听到某个 Store 变化后，主动更新另一个 Store（不推荐，可能造成循环） |

> **与 `watch` 的区别**：  
> - `watch` 是 Vue 的通用监听器，可以监听任何响应式源（ref、reactive、getter）。  
> - `$subscribe` 是 Pinia 的特有 API，专门用于监听整个 Store 的 state 变化，并且能**在 patch 后统一触发一次**（而 `watch` 对 `$patch` 中的多个变更可能会触发多次）。  
> - `$subscribe` 回调内可以拿到 `mutation` 对象，包含了这次变化的详细元信息（比如是哪个 action 触发的）。

---

### 二、参数详解 (`mutation` 和 `state`)

```ts
store.$subscribe((mutation, state) => {
  // mutation 包含本次变更的详细信息
  // state 是变更后的新 state（响应式对象）
})
```

#### `mutation` 对象的属性：

| 属性 | 类型 | 说明 |
|------|------|------|
| `storeId` | `string` | 发生变化的 store 的 id（即 `defineStore` 的第一个参数） |
| `type` | `'direct'` \| `'patch object'` \| `'patch function'` | 变更方式：直接修改、使用 `$patch` 对象、使用 `$patch` 函数 |
| `events` | `PatchTree[]` | 具体变化列表（每个事件包含旧值、新值、路径等） |
| `payload` | `any` | 如果是通过 action 间接修改，payload 可能是 action 的参数（取决于 pinia 版本和配置） |

**注意**：`mutation` 的内容主要用于调试或高级追踪，日常开发中可能只用到 `storeId` 和 `type`。

#### `state` 参数：
就是当前 store 的最新 state（已经更新完成）。你可以直接读取它。

---

### 三、实际代码示例

```ts
// 1. 自动保存到 localStorage
const useSettingsStore = defineStore('settings', {
  state: () => ({ theme: 'dark', language: 'zh' })
})

const settingsStore = useSettingsStore()
settingsStore.$subscribe((mutation, state) => {
  localStorage.setItem('settings', JSON.stringify(state))
})

// 2. 记录用户行为日志
const userStore = useUserStore()
userStore.$subscribe((mutation, state) => {
  console.log(`Store "${mutation.storeId}" changed via ${mutation.type}`)
  // 发送到分析服务
  analytics.track('store_change', {
    storeId: mutation.storeId,
    state: state
  })
})

// 3. 监听特定变化并执行逻辑（通过条件判断）
cartStore.$subscribe((mutation, state) => {
  if (state.total > 1000) {
    showDiscountTip.value = true
  }
})
```

---

### 四、重要坑点与注意事项

| 坑点 | 说明 | 正确做法 |
|------|------|----------|
| **默认会绑定到当前组件** | `$subscribe` 默认在组件卸载时自动取消订阅 | 如果需要全局持久订阅（比如应用整个生命周期都监听），传递 `{ detached: true }` 选项 |
| **不要在 subscribe 回调中再次修改同一个 store (除非很小心)** | 容易造成无限循环或性能问题 | 如果非要修改，判断条件避免死循环，或使用 nextTick |
| **mutation 对象不是完全可靠** | 某些变更可能无法提供完整的事件树（尤其是嵌套对象变动） | 不要完全依赖 `events` 做业务逻辑，把它当作辅助调试信息 |
| **state 参数是响应式对象** | 不要直接替换它（如 `state = newState`），会丢失响应式 | 只读取，不修改 |
| **多个 subscribe 执行顺序** | 按照注册顺序同步执行，如果某个回调抛出错误会中断后续 | 确保回调内没有未捕获的异常，或使用 `try...catch` |
| **与 `watch` 混用时可能多次触发** | 如果同时用 `watch` 和 `$subscribe` 监听同一变化，会各触发一次 | 按需选择一种：需要变更详情用 `$subscribe`，只需新老值用 `watch` |
| **在 Setup Store 中使用 `$subscribe` 同样有效** | 没有任何区别 | 放心使用 |

---

### 五、如何取消订阅

`$subscribe` 返回一个**取消订阅函数**，调用它即可停止监听。

```ts
const unsubscribe = settingsStore.$subscribe((mutation, state) => {
  // ...
})

// 当不再需要时（如组件卸载、条件满足）
unsubscribe()
```

如果设置了 `{ detached: true }`，取消订阅需要手动调用；否则组件卸载时会自动取消。

---

### 六、记忆口诀

> **订阅监听 state 变，触发副作用很方便；**
> **存本地、记日志、同步后端都能见；**
> **传 detached 保长久，别忘了取消避风险。**

简单说：`$subscribe` 就是 Pinia 版的 “watch state”，专门用来在 state 发生变化时**执行非状态相关的额外逻辑**（如持久化、日志、同步等）。