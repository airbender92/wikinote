## Pinia Store 使用：`useStore()` 的正确姿势与避坑指南

Pinia 的 Store 通过 `useStore()` 函数（即 `defineStore` 返回的 hooks）在组件、composables 中获取和使用。**最关键的约束：`useStore()` 必须在 `setup()` 或 `<script setup>` 的同步执行中调用，不能在普通函数（如事件回调、异步请求、路由守卫）中直接调用。**

---

### 一、正确用法示例

#### 1. 在 Vue 组件中使用（`<script setup>`）
```vue
<script setup>
import { useCounterStore } from '@/stores/counter'

const counter = useCounterStore()  // ✅ 正确：setup 同步顶层

// 直接访问 state
console.log(counter.count)

// 调用 action
counter.increment()

// 解构时保持响应式（必须用 storeToRefs）
import { storeToRefs } from 'pinia'
const { count, doubleCount } = storeToRefs(counter)
</script>
```

#### 2. 在选项式 API 的 `setup()` 函数中
```vue
<script>
import { defineComponent } from 'vue'
import { useCounterStore } from '@/stores/counter'

export default defineComponent({
  setup() {
    const counter = useCounterStore()  // ✅ 正确
    return { counter }
  }
})
</script>
```

#### 3. 在自定义 Composable 中使用
```ts
// composables/useCart.ts
import { useCartStore } from '@/stores/cart'
import { storeToRefs } from 'pinia'

export function useCart() {
  const cart = useCartStore()  // ✅ 正确：composable 内调用的上下文也是 setup
  const { total, items } = storeToRefs(cart)
  
  const addItem = (item) => cart.addItem(item)
  
  return { total, items, addItem }
}

// 在组件中使用该 composable
<script setup>
const { total, addItem } = useCart()
</script>
```

---

### 二、为什么不能在外面调用？

Pinia 底层依赖 Vue 的**当前活动实例**（`getCurrentInstance()`）。在组件 `setup` 执行期间，Vue 会记录当前正在初始化的组件实例。Pinia 内部通过 `inject()` 获取 root store 容器，这需要 Vue 的依赖注入上下文。

**如果在非 setup 环境下调用 `useStore()`**：
- 没有活跃的组件实例，`inject()` 会失败
- 错误示例：`Uncaught Error: getActivePinia was called with no active Pinia. Did you forget to install pinia?`

> 即使你已经在 `app.use(pinia)` 安装了插件，也不能在 setup 之外调用。

---

### 三、常见陷阱与解决方案

| 坑点 | 错误示例 | 正确做法 |
|------|----------|----------|
| **在异步回调中调用** | `setTimeout(() => { const store = useStore() }, 1000)` | 在 setup 顶层先获取 store，然后在回调中使用它 |
| **在路由守卫中调用** | `router.beforeEach((to) => { const store = useStore() })` | 在守卫中通过 `pinia` 实例访问：`import { pinia } from '@/main'`，然后 `useStore(pinia)` |
| **在 axios 拦截器中调用** | `axios.interceptors.response.use(() => { const store = useStore() })` | 同上，传入 pinia 实例 |
| **在普通 js/ts 文件中** | 直接调用 `useStore()` | 要么把 store 实例作为参数传递，要么导入 pinia 实例并作为参数 |
| **在 watchEffect 的第一次立即执行内** | 如果 watchEffect 在 setup 之外定义，也可能出错 | 确保调用链始终以组件 setup 为起点 |
| **在 computed 或 watch 的回调中直接调用** | 这些回调执行时可能已经离开了同步 setup 阶段 | 在 setup 中获取 store，然后在回调中引用 |
| **在 Vuex 迁移过程中混用** | 旧的 Vuex 模块还在，在 Vuex action 中调用 useStore | 完全迁移后再使用，或注入 pinia 实例 |

---

### 四、在非组件环境下使用 Store 的正确方式

如果你**确实需要**在路由守卫、工具函数、拦截器等地方访问 store，有两种官方推荐方法：

#### 方法一：传入 `pinia` 实例（推荐）

在你的 `main.js` / `main.ts` 中导出 pinia 实例：
```ts
// main.ts
import { createPinia } from 'pinia'

export const pinia = createPinia()
const app = createApp(App)
app.use(pinia)
```

然后在任何地方使用：
```ts
// router/guards.ts
import { pinia } from '@/main'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore(pinia)  // ✅ 传入实例
```

#### 方法二：将 store 实例挂载到全局对象（不推荐）
```ts
// main.ts
import { useAuthStore } from '@/stores/auth'
export const authStore = useAuthStore(pinia)  // 先获取实例，然后导出

// 其他文件中直接 import { authStore } from '@/main'
// 注意：这会导致与组件生命周期隔离，且失去 SSR 支持
```

---

### 五、常见错误与排查

1. **错误信息**：  
   `getActivePinia was called with no active Pinia. Did you forget to install pinia?`  
   **原因**：Pinia 未安装，或在没有活动实例的地方调用了 `useStore()`。  
   **解决**：确认 `app.use(pinia)` 执行，且调用位置在 setup 或传入 pinia 实例。

2. **错误信息**：  
   `Pinia: "🍍" store "xxx" was called without a Pinia instance.`  
   **原因**：同上。

3. **奇怪的现象**：部分组件能访问 store，部分不能？可能因为某些组件是异步组件或动态引入，且父组件未提供 pinia。确保根组件已安装。

---

### 六、最佳实践总结

- ✅ **总是在组件的 `<script setup>` 或 `setup()` 函数中直接调用 `useStore()`**
- ✅ **写 composable 时，在 composable 顶层调用**（因为 composable 也是在 setup 中使用的）
- ✅ **需要跨组件共享的状态，使用 Pinia 而非 provide/inject**
- ✅ **在路由守卫或拦截器中，显式传递 `pinia` 实例**
- ❌ **不要在任何异步回调（Promise、setTimeout、事件监听）内部直接调用 `useStore()`**
- ❌ **不要在 Vue 生命周期钩子（如 `onMounted`）之外的非 setup 上下文调用**

---

### 七、记忆口诀

> **Store 要使用，只把 setup 留；**
> **回调若要用，实例传进去；**
> **一旦解构上，toRefs 来帮忙；**
> **异步别乱调，顶层先拿好。**

遵循这些规则，你就能彻底避免 Pinia 在使用层面的各种坑。