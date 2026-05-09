## 在组件中使用 Pinia：完整指南与避坑

Pinia Store 需要在组件中通过 `useStore()` 获取实例后才能访问。以下是六种核心用法的详细讲解，包括正确姿势、代码示例和常见坑点。

---

### 一、直接访问 store 实例

#### 基本用法
```vue
<script setup>
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// 读取 state
console.log(userStore.name)

// 调用 action
userStore.setName('Bob')

// 直接修改 state（不推荐，但允许）
userStore.age = 30
</script>

<template>
  <!-- 模板中直接使用 -->
  <p>{{ userStore.name }} - {{ userStore.age }}</p>
  <button @click="userStore.increment">+1</button>
</template>
```

#### 注意点
- 整个 `store` 实例是一个 **reactive 对象**，对其属性的访问会自动触发响应式更新。
- **直接修改 state 是允许的**，但为了可维护性，建议通过 action 修改。
- 如果使用 Options API，可以在 `computed` 中返回 `store.xxx` 来保持响应式。

#### 常见坑点 ⚠️

| 坑点 | 错误示例 | 后果 | 正确做法 |
|------|----------|------|----------|
| **直接解构 store** | `const { name, age } = userStore` | `name` 和 `age` 变成普通值，不再响应式 | 使用 `storeToRefs` 解构 |
| **在异步回调中再次调用 useStore** | `setTimeout(() => { const store = useStore() }, 1000)` | 可能报错（无 active pinia 实例） | 在 setup 顶层获取 store，回调中直接使用该变量 |
| **将 store 实例作为参数传递但破坏了响应式** | `function foo(store) { store.name = 'x' }` | 可以修改，但类型可能丢失 | 正常传递即可，store 仍然是响应式 |
| **模板中频繁调用方法导致性能问题** | `<div>{{ userStore.fullName() }}</div>`（如果 fullName 是方法） | 每次渲染都重新计算，无缓存 | 使用 getter（计算属性）而非方法 |

---

### 二、响应式解构（`storeToRefs`）

#### 基本用法
```vue
<script setup>
import { storeToRefs } from 'pinia'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// 解构 state 和 getters（必须用 storeToRefs）
const { name, age, fullName } = storeToRefs(userStore)

// 解构 actions（直接解构即可）
const { setName, increment } = userStore

// 使用：需要 .value 吗？不需要，name 是 ref，模板中自动解包
// 但在 JS 中访问：name.value
console.log(name.value)   // 'Alice'

function update() {
  setName('Bob')
}
</script>

<template>
  <!-- 模板中直接使用，无需 .value -->
  <p>{{ name }} - {{ age }} - {{ fullName }}</p>
  <button @click="increment">+1</button>
</template>
```

#### 核心原理
- `storeToRefs` 为每个响应式属性（state 和 getter）创建一个 **ref**，并保持连接（类似 `toRefs`）。
- 对于非响应式属性（如 actions、普通方法），直接解构即可，无需包装。

#### 常见坑点 ⚠️

| 坑点 | 错误示例 | 后果 | 正确做法 |
|------|----------|------|----------|
| **对 actions 使用 storeToRefs** | `const { increment } = storeToRefs(store)` | `increment` 变成 ref，无法调用 | actions 直接解构：`const { increment } = store` |
| **忘记使用 storeToRefs 导致响应式丢失** | `const { name } = userStore` | 修改 store.name 后，变量 name 不会更新 | 始终用 `storeToRefs` 包裹需要解构的响应式属性 |
| **在 JS 中忘记 `.value`** | `if (name === 'Alice')`（name 是 ref 对象） | 永远为 false，因为比较的是 ref 对象 | `if (name.value === 'Alice')` |
| **对嵌套 store 的解构** | 如果 store 中包含另一个 store 的实例，对其解构也会丢失响应 | 需要使用 `storeToRefs` 处理嵌套 | 保持 store 扁平，或对子 store 单独调用 `useStore()` |

---

### 三、批量修改（`$patch`）

#### 基本用法
```vue
<script setup>
const store = useUserStore()

// 对象形式：一次修改多个字段
function updateUser() {
  store.$patch({
    name: 'NewName',
    age: 30,
    profile: { avatar: 'new.jpg' }  // ⚠️ 这会替换整个 profile 对象！
  })
}

// 函数形式：执行复杂逻辑
function addTodo(text) {
  store.$patch((state) => {
    state.todos.push({ text, done: false })
    state.total++
  })
}
</script>
```

#### 优势
- 只触发**一次**响应式更新（性能优于多次单独赋值）。
- 函数形式可以轻松操作数组、条件修改等。

#### 常见坑点 ⚠️

| 坑点 | 错误示例 | 后果 | 正确做法 |
|------|----------|------|----------|
| **对象形式的浅合并导致嵌套数据丢失** | `$patch({ user: { name: 'Bob' } })`，原本 `user` 有 `age` 字段 | `age` 被删除 | 使用函数形式：`state.user.name = 'Bob'` |
| **动态添加未声明的属性** | `$patch({ newProp: 'value' })`，但 state 初始无 `newProp` | TypeScript 报错，但不影响运行 | 预先在 state 中声明，或使用索引签名 |
| **在 `$patch` 函数中异步修改** | `$patch((state) => { setTimeout(() => { state.count++ }, 100) })` | 异步回调不在 patch 上下文中，会单独触发更新 | 不要在 `$patch` 中异步操作，改用 action |
| **多次调用 `$patch` 而非一次合并** | 连续两次 `$patch({ a:1 })` 和 `$patch({ b:2 })` | 触发两次更新，效率低 | 合并为一次 `$patch({ a:1, b:2 })` |

---

### 四、重置状态（`$reset`）

#### Options Store（自动支持）
```vue
<script setup>
const store = useUserStore() // Options Store

function reset() {
  store.$reset()  // 恢复到 state 函数返回的初始状态
}
</script>
```

#### Setup Store（需手动实现）
```ts
// 定义 Setup Store 时手动添加 $reset
const useSetupStore = defineStore('setup', () => {
  const count = ref(0)
  const name = ref('pinia')
  
  function $reset() {
    count.value = 0
    name.value = 'pinia'
  }
  
  return { count, name, $reset }
})
```

```vue
<script setup>
const store = useSetupStore()
store.$reset()  // 可用
</script>
```

#### 常见坑点 ⚠️

| 坑点 | 说明 | 解决 |
|------|------|------|
| **Setup Store 中调用 `$reset` 报错** | `store.$reset is not a function` | 手动实现 `$reset` 方法 |
| **重置后旧引用仍然持有旧数据** | 如果在组件中缓存了某个 state 对象，`$reset` 后该对象未被替换 | 使用 `storeToRefs` 保持引用，或重置后重新获取 |
| **`$reset` 不会触发 `$subscribe`** | 会触发，因为内部使用 `$patch` | 无需担心 |
| **只重置部分字段** | `$reset` 会重置所有字段，无法选择 | 手动使用 `$patch` 重置特定字段 |

---

### 五、订阅 state（`$subscribe`）

#### 基本用法
```vue
<script setup>
import { onUnmounted } from 'vue'
const store = useUserStore()

// 订阅 state 变化
const unsubscribe = store.$subscribe((mutation, state) => {
  console.log('State changed:', mutation.type, state)
  
  // 比如保存到 localStorage
  localStorage.setItem('user', JSON.stringify(state))
})

// 组件卸载时自动取消订阅（默认行为，无需手动）
// 但如果设置了 { detached: true }，则需要手动取消
onUnmounted(() => {
  unsubscribe() // 可选，默认也会自动清理
})
</script>
```

#### 选项说明
- `mutation.type`: `'direct'` / `'patch object'` / `'patch function'`
- `mutation.storeId`: store 的 id
- `options`: `{ detached: false, deep: false, flush: 'pre' }`

#### 常见坑点 ⚠️

| 坑点 | 说明 | 正确做法 |
|------|------|----------|
| **在 subscribe 回调中再次修改同一个 store** | 可能造成无限循环 | 添加判断条件避免循环，或用 `nextTick` |
| **默认组件卸载时自动取消，但若需要全局永久监听** | 默认 `detached: false`，组件卸载后回调不再执行 | 设置 `{ detached: true }` |
| **深度监听嵌套对象变化** | 默认 `deep: false`，嵌套对象修改可能不触发（取决于 Pinia 版本） | 需要时显式设置 `deep: true` |
| **回调中执行异步操作** | 可以，但注意不要擅自修改 state | 允许异步，但需确保不造成竞态 |
| **忘记处理 unsubscribe 的内存泄漏（detached: true 时）** | 全局订阅未手动取消，导致 store 销毁后回调仍执行 | 在组件 `onUnmounted` 或合适的生命周期调用 `unsubscribe()` |

---

### 六、订阅 action（`$onAction`）

#### 基本用法
```vue
<script setup>
import { onUnmounted } from 'vue'
const store = useUserStore()

const unsubscribe = store.$onAction(({
  name,      // action 名称
  store,     // store 实例
  args,      // 参数数组
  after,     // 成功后回调
  onError    // 失败后回调
}) => {
  console.log(`Action ${name} started with`, args)
  
  after((result) => {
    console.log(`Action ${name} succeeded with`, result)
  })
  
  onError((error) => {
    console.error(`Action ${name} failed`, error)
  })
})

// 可选：手动取消（默认组件卸载时自动取消，但 detached 时需手动）
onUnmounted(() => {
  unsubscribe()
})
</script>
```

#### 典型场景
- **全局 Loading 管理**：监听异步 action，自动显示/隐藏 loading。
- **日志与埋点**：记录用户操作。
- **错误上报**：捕获 action 抛出的异常并发送到监控平台。

#### 常见坑点 ⚠️

| 坑点 | 说明 | 正确做法 |
|------|------|----------|
| **对异步 action，`after` 在 Promise resolve 后执行** | 正确行为，但注意异步 action 中抛出的错误会进入 `onError` | 放心使用 |
| **在 `after` 中修改 state** | 可以，但不推荐，容易导致难以追踪的副作用 | 尽量不修改，只做日志/上报 |
| **默认自动取消订阅** | 组件卸载时自动取消，如果需要在全局范围监听（如埋点），需设置 `{ detached: true }` | 需要时设置 `detached: true` |
| **监听不到 action 内部的子 action** | 如果 action A 调用 action B，只会触发 A 的回调，B 不会单独触发 | 需要为每个 action 单独订阅，或统一监听所有 |
| **多次订阅的执行顺序** | 按注册顺序同步执行，一个回调抛出错误会中断后续 | 确保回调内无异常 |

---

### 七、总结对比表

| 用法 | API | 响应式保留 | 主要坑点 |
|------|-----|------------|----------|
| 直接访问 | `store.xxx` | ✅ | 错误解构会丢失响应式 |
| 响应式解构 | `storeToRefs(store)` | ✅（ref） | 对 actions 误用 |
| 批量修改 | `store.$patch()` | ✅ | 嵌套对象替换、函数中异步 |
| 重置状态 | `store.$reset()` | ✅ | Setup Store 需手动实现 |
| 订阅 state | `store.$subscribe()` | 只读监听 | 无限循环、内存泄漏 |
| 订阅 action | `store.$onAction()` | 只读监听 | 异步回调时机、手动取消 |

### 记忆口诀

> **直接访问用 store，解构带上 toRefs；**
> **批量修改用 patch，重置注意 type；**
> **订阅切记清监听，action 回调分前后。**

掌握以上六种用法，你就能在组件中灵活驾驭 Pinia，同时避开所有常见陷阱。