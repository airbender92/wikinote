## Pinia State 详解：定义、读写方式与避坑指南

State 是 Pinia Store 的数据核心，它就像组件里的 `data()`，但**跨组件共享且响应式**。

---

### 一、基本知识点

#### 1. 在 Options Store 中定义 state
```ts
import { defineStore } from 'pinia'

const useUserStore = defineStore('user', {
  state: () => ({
    name: 'Alice',
    age: 25,
    tags: ['developer', 'pinia']
  })
})
```
- `state` **必须是一个函数**，返回一个普通对象。
- 函数形式保证每个请求（SSR）或每个组件实例（如果 store 被多次使用）都有独立的状态副本。

#### 2. 在 Setup Store 中定义 state
```ts
import { ref, reactive } from 'vue'

const useUserStore = defineStore('user', () => {
  const name = ref('Alice')
  const age = ref(25)
  const tags = reactive(['developer', 'pinia'])
  return { name, age, tags }
})
```
- 使用 `ref` 或 `reactive` 创建响应式状态。
- 最终返回的对象中，ref 会被自动“解包”，在模板和 store 实例上使用时无需 `.value`。

#### 3. 访问和修改 state（核心）
无论哪种定义方式，**得到的 store 实例直接暴露 state 属性**：
```vue
<script setup>
const userStore = useUserStore()

// 读取
console.log(userStore.name)   // 'Alice'

// 直接修改（支持响应式更新）
userStore.name = 'Bob'        // ✅ 视图立即更新
userStore.age++               // ✅ 可以

// 批量修改
userStore.$patch({
  name: 'Charlie',
  age: 30
})

// 或者用 $patch 接收一个函数（适合复杂逻辑）
userStore.$patch((state) => {
  state.name = 'David'
  state.tags.push('vue')
})

// 替换整个 state（除了少数保留属性）
userStore.$state = { name: 'Eve', age: 28, tags: ['new'] }
</script>
```

#### 4. 重置 state
- **Options Store** 自带 `$reset()` 方法，恢复到初始 state。
- **Setup Store** 需要手动实现 `$reset`（Pinia 不知道初始值），例如：
  ```ts
  const initialState = { name: 'Alice', age: 25, tags: ['developer', 'pinia'] }
  const state = ref(initialState)
  function $reset() { state.value = { ...initialState } }
  return { ...state.value, $reset }  // 注意展开
  ```

---

### 二、常见坑点与正确做法

| 坑点 | 错误示例 | 后果 | 正确做法 |
|------|----------|------|----------|
| **state 写成普通对象** | `state: { count: 0 }` | SSR 时多个请求共享同一份状态，导致数据污染；热更新异常 | `state: () => ({ count: 0 })` |
| **直接解构 store 失去响应式** | `const { name, age } = userStore` | `name`、`age` 变为普通值，不再响应更新 | 使用 `storeToRefs(userStore)` 解构响应式属性 |
| **在 action 外部替换整个 state** | `userStore.$state = newObj` | 可用，但可能丢失响应式（如果 newObj 不是普通对象） | 确保 newObj 是纯对象，或使用 `$patch` |
| **忘记 `.value`（仅 Setup Store + ref）** | `const count = ref(0); return { count }` 然后在 action 中写 `count++` | 没有 `.value` 会直接修改 ref 对象，而非内部值 | 写法：`count.value++`；或者在组件/store 外部通过 `store.count` 访问（自动解包） |
| **直接修改非 `ref/reactive` 的嵌套属性** | `store.user.profile.city = 'BJ'` | 若 `user` 是普通对象且未包装，可能丢失响应式（但 Pinia 会对 state 深度响应式，一般没问题） | Pinia 内部使用 Vue 的 `reactive`，深层次修改也能触发更新。但最好保持数据扁平或使用 `$patch` |
| **在 getter 中修改 state** | `getters: { doubleAndInc(state) { state.count++; return state.count*2 } }` | 违反单向数据流，调试困难，可能造成无限循环 | getter 只读；修改应放到 action |
| **异步修改 state 时未处理竞态** | 多个异步 action 先后修改同一数组，顺序不确定 | 最终状态可能不符合预期（例如分页加载） | 使用请求取消令牌（AbortController）或标记最新请求 |
| **在组件中直接修改嵌套对象但不触发更新** | `store.nested.obj.prop = val` | 实际上会触发更新，因为 Pinia 基于 `reactive`。但有例外：如果嵌套对象最初不存在，动态添加属性可能非响应式 | 使用 `$patch` 或确保初始结构完整；或使用 `ref({})` |
| **使用 `reactive` 包裹整个 state（Setup Store）** | `const state = reactive({ count:0 }); return { state }` | 访问时必须写 `store.state.count`，增加一层嵌套 | 直接返回 `reactive` 内部的属性：`return { ...state }` 或分别返回 `ref` |
| **忘记在 SSR 中重置 state** | 服务端渲染后 state 残留 | 可能泄漏用户数据 | 在 `onServerPrefetch` 或入口处重置 store |


### 三、进阶：`$patch` vs 直接赋值 vs `$state`

| 方式 | 语法 | 适用场景 |
|------|------|----------|
| 直接赋值 | `store.name = 'new'` | 单字段更新，简单直接 |
| `$patch` 对象 | `store.$patch({ name, age })` | 批量更新，性能较好（只触发一次更新） |
| `$patch` 函数 | `store.$patch(state => { state.items.push(x) })` | 复杂逻辑（如数组操作、条件修改） |
| `$state` 替换 | `store.$state = newState` | 完全重置或替换（需保证结构一致） |

> **坑点**：直接修改数组或对象内部（如 `store.items.push(item)`）是允许的，但可能造成较大的变更范围；`$patch` 函数方式可以更好地追踪变化。

---

### 四、响应式解构的正确姿势（最重要！）

```vue
<script setup>
import { storeToRefs } from 'pinia'
const userStore = useUserStore()

// ❌ 错误：解构后失去响应式
const { name, age } = userStore
watchEffect(() => {
  console.log(name)  // 只会打印一次，后续变化不会触发
})

// ✅ 正确：使用 storeToRefs 包装
const { name, age } = storeToRefs(userStore)
// 现在 name, age 都是 ref，可以解构、传递、在 watch 中使用

// 如果要解构 action 或非响应式属性，可以直接取
const { updateUser } = userStore  // 方法不需要 storeToRefs
</script>
```

**原理**：`storeToRefs` 会为每个 state/getter 创建一个 ref，保持响应式连接。`store` 本身是一个 `reactive` 对象，直接解构会丢失代理。

---

### 五、监控 State 的变化

```ts
// 监听整个 store（深度）
watch(
  () => userStore,
  (newVal, oldVal) => { /* ... */ },
  { deep: true }
)

// 监听某个属性（推荐）
watch(() => userStore.name, (newName) => { /* ... */ })

// 使用 $subscribe（类似 Vuex 的 subscribe）
userStore.$subscribe((mutation, state) => {
  // mutation 包含 storeId, type, events 等信息
  console.log('state changed', mutation)
})
// $subscribe 默认在组件卸载时自动取消订阅，可传第二个参数 { detached: true } 保持订阅
```

---

### 六、记忆口诀

> **State 函数返对象，直接读写真方便；**
> **解构记得 toRefs，批量更新用 patch；**
> **异步改值防竞态，重置 state 看 Store 型。**

掌握这些，你就能安全、高效地操作 Pinia 的 State，避开所有常见的响应式陷阱。