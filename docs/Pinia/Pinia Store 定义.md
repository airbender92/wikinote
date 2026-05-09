## Pinia Store 定义详解：两种方式与核心坑点

Pinia 中定义 Store 有两种风格：**Options Store** 和 **Setup Store**。它们通过 `defineStore(id, ...)` 函数创建，返回一个 hooks 函数（如 `useStore`）。

---

### 一、Options Store（`defineStore(id, options)`）

#### 1. 基本结构
```ts
import { defineStore } from 'pinia'

const useCounterStore = defineStore('counter', {
  state: () => ({
    count: 0,
    name: 'pinia'
  }),
  getters: {
    doubleCount: (state) => state.count * 2,
    // 使用 this（需注意类型）
    computedMsg(): string {
      return `${this.name} - ${this.count}`
    }
  },
  actions: {
    increment() {
      this.count++
    },
    async fetchData() {
      // 异步操作
    }
  }
})
```

#### 2. 关键知识点
- **`id`**：唯一标识符，全局唯一，用于 Devtools 和持久化插件。
- **`state`**：必须是一个**函数**返回对象（避免 SSR 跨请求状态污染）。
- **`getters`**：类似 Vue 的 computed，第一个参数是 `state`，推荐用箭头函数；若要访问其他 getter 或 action，用普通函数（`this`）。
- **`actions`**：支持同步/异步，内部通过 `this` 访问 state、getters、其他 actions。
- **返回值**：调用 `useCounterStore()` 获得响应式 store 对象，直接修改 state 会自动更新（无需 `.value`）。

#### 3. 常见坑点 ⚠️

| 坑点 | 说明 | 正确做法 |
|------|------|----------|
| **state 不是函数** | 写成对象字面量会导致多实例共享数据，尤其在 SSR 中 | 必须 `state: () => ({ ... })` |
| **getter 中使用 this 丢失上下文** | 在箭头函数中使用 `this` 会指向 undefined | 普通函数：`getters: { foo(state) { return this.bar } }` |
| **访问其他 getter** | 在箭头函数中只能用 `state`，无法拿到其他 getter | 用普通函数：`otherGetter(state) { return this.someGetter + 1 }` |
| **actions 中异步更新** | 异步回调内直接修改 `this.xxx` 可以，但注意失去 `this` 绑定 | 使用箭头函数或保存 `this` |
| **解构 store 破坏响应式** | `const { count, doubleCount } = useCounterStore()` 会失去响应式 | 使用 `storeToRefs()` 包裹 |
| **动态添加新属性** | 直接 `store.newProp = 'xx'` 不会触发更新（Pinia 基于 Vue 3 响应式） | 使用 `store.$patch()` 或预先声明 |

---

### 二、Setup Store（`defineStore(id, setup function)`）

#### 1. 基本结构
```ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const useCounterStore = defineStore('counter', () => {
  // state
  const count = ref(0)
  const name = ref('pinia')
  
  // getters
  const doubleCount = computed(() => count.value * 2)
  const computedMsg = computed(() => `${name.value} - ${count.value}`)
  
  // actions
  function increment() {
    count.value++
  }
  
  async function fetchData() { /* ... */ }
  
  // 必须返回所有暴露的内容
  return { count, name, doubleCount, computedMsg, increment, fetchData }
})
```

#### 2. 关键知识点
- **完全组合式 API**：类似 Vue 组件的 `<script setup>`，自由使用 `ref`、`reactive`、`computed`、`watch` 等。
- **返回值**：返回的对象即 store 的公开接口，直接使用 `store.count` 访问（注意 `.value` 已自动剥除）。
- **无需 `actions` 包裹**：任何函数都会自动成为 action。
- **支持生命周期钩子**：可以在 setup 中使用 `onMounted` 等。
- **更好的 TypeScript 推断**：返回值类型自动推导。

#### 3. 常见坑点 ⚠️

| 坑点 | 说明 | 正确做法 |
|------|------|----------|
| **忘记返回属性** | setup 函数必须返回一个对象，否则 store 为空 | 明确 `return { state, getters, actions }` |
| **使用 reactive 包裹 state** | `reactive({ count: 0 })` 会丢失结构，且 .value 行为不一致 | 推荐用 `ref`，或 `reactive` 但解构时需用 `toRefs` |
| **解构 store 破坏响应式** | 与 Options Store 相同，直接解构会丢失响应式 | 使用 `storeToRefs(useCounterStore())` 或 `const store = useStore()` 然后 `store.count` |
| **计算属性依赖外部变量** | 如果 computed 依赖了 `props` 或外部 ref，需要确保依赖被追踪 | 正常使用，但注意不要在 action 中修改外部 prop |
| **在 action 中错误使用 .value** | 定义时用 `ref(0)`，在 action 中直接 `count++`（缺少 `.value`） | 必须 `count.value++` |
| **SSR hydration 不一致** | Setup Store 中如果使用 `window` 或随机数，会导致客户端与服务端状态不同 | 用 `onMounted` 或 `$patch` 在客户端注入 |
| **this 不可用** | 设置函数中没有 `this`，不能像 Options 那样用 `this.otherAction` | 直接调用其他函数：`increment()`（作用域内） |

---

### 三、两种方式对比与选择

| 对比项 | Options Store | Setup Store |
|--------|---------------|-------------|
| 语法风格 | 对象字面量，类似 Vuex | 组合式函数，类似 Composition API |
| 代码组织 | 按类型 (state/getters/actions) 分组 | 按逻辑关注点自由分组 |
| TypeScript | 需要额外类型注解 (`state: () => ({...})`) | 自动推断，更友好 |
| 可复用逻辑（hook） | 难复用 | 可抽离为 composable 函数 |
| 依赖注入 | 不支持 | 可接收外部参数（如 `setup(props, context)`） |
| 热更新（HMR） | 需手动 `accept` | 更好的支持 |
| 适用场景 | 简单场景、快速迁移 | 复杂逻辑、高复用需求 |

> **官方推荐**：优先使用 Setup Store（更灵活、更现代）。除非需要快速从 Vuex 迁移或团队偏好对象风格。

---

### 四、通用坑点（无论哪种方式）

1. **Store 只能在 `setup()` 或 `<script setup>` 中调用**  
   不要在普通函数（如 axios 拦截器）中直接调用 `useStore()`，因为 Pinia 依赖 Vue 实例上下文。如果必须用，需传入 `app` 实例：`useStore(undefined, app)`（高级用法）。

2. **跨 store 使用时的循环依赖**  
   Setup Store 中若 store A 引用了 store B，且 store B 又引用 store A，可能导致初始化死循环。使用 `setTimeout` 或提取公共逻辑。

3. **持久化插件与 Setup Store 的兼容性**  
   很多持久化插件（如 `pinia-plugin-persistedstate`）默认只序列化 `state`，Setup Store 中返回的 ref 会被正确识别，但 computed 不会被存储。

4. **在组件外修改 store**  
   虽然可以直接 `store.count = 1`，但建议使用 `store.$patch({ count: 1 })` 或 action，以便 devtools 追踪。

5. **$reset 方法差异**  
   Options Store 自动提供 `$reset()` 方法重置到初始 state；Setup Store 需要手动实现，因为 Pinia 无法知道初始值。

   ```ts
   // Setup Store 手动实现 reset
   const initialState = { count: 0, name: 'pinia' }
   const state = ref(initialState)
   function $reset() { state.value = { ...initialState } }
   ```

---

### 五、快速检查清单

- ✅ state 是否是函数？
- ✅ getter 中如果需要 this，是否用了普通函数？
- ✅ 解构时是否用了 `storeToRefs`？
- ✅ Setup Store 是否返回了所有需要暴露的状态/函数？
- ✅ Setup Store 中 ref 是否写了 `.value`？
- ✅ 异步 action 是否处理了错误和加载状态？
- ✅ 跨 store 引用是否避免了循环依赖？

掌握以上内容，即可自信地在项目中使用 Pinia Store，并避开绝大多数易错点。