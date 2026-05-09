## Pinia Getters 详解：计算属性、缓存与跨访问避坑

Getters 是 Pinia Store 中的**计算属性**，用于**派生状态**（基于 state 计算出新值）。它与 Vue 的 `computed` 行为一致：**基于响应式依赖缓存**，只有依赖变化时才重新计算。

---

### 一、基本知识点

#### 1. 在 Options Store 中定义 Getters

```ts
import { defineStore } from 'pinia'

const useUserStore = defineStore('user', {
  state: () => ({
    firstName: 'John',
    lastName: 'Doe',
    todos: [
      { text: '学习 Pinia', done: true },
      { text: '写文档', done: false }
    ]
  }),
  
  getters: {
    // 1. 普通 getter：接收 state 作为第一个参数
    fullName: (state) => `${state.firstName} ${state.lastName}`,
    
    // 2. 使用 this 访问其他 getter / state（需要普通函数）
    fullNameUppercase(): string {
      return this.fullName.toUpperCase()
    },
    
    // 3. 接收参数的 getter（返回函数）
    getTodoByText: (state) => (text: string) => {
      return state.todos.find(todo => todo.text === text)
    },
    
    // 4. 访问其他 getter 进行计算
    completedCount: (state) => {
      return state.todos.filter(todo => todo.done).length
    },
    progress: (state) => {
      // 可以通过 state 访问，也可以用 this
      const total = state.todos.length
      const completed = this.completedCount  // 使用 this
      return total === 0 ? 0 : (completed / total) * 100
    }
  }
})
```

#### 2. 在 Setup Store 中定义 Getters（更简单）

```ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const useUserStore = defineStore('user', () => {
  const firstName = ref('John')
  const lastName = ref('Doe')
  const todos = ref([
    { text: '学习 Pinia', done: true },
    { text: '写文档', done: false }
  ])
  
  // 使用 computed 实现 getter
  const fullName = computed(() => `${firstName.value} ${lastName.value}`)
  
  const fullNameUppercase = computed(() => fullName.value.toUpperCase())
  
  const completedCount = computed(() => 
    todos.value.filter(todo => todo.done).length
  )
  
  const progress = computed(() => {
    const total = todos.value.length
    return total === 0 ? 0 : (completedCount.value / total) * 100
  })
  
  // 带参数的 getter：返回函数
  const getTodoByText = (text: string) => 
    todos.value.find(todo => todo.text === text)
  
  return { firstName, lastName, todos, fullName, fullNameUppercase, 
           completedCount, progress, getTodoByText }
})
```

#### 3. 在组件中使用 Getters

```vue
<script setup>
import { storeToRefs } from 'pinia'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// 方式1：直接访问（响应式）
console.log(userStore.fullName)      // 'John Doe'
console.log(userStore.progress)       // 50

// 方式2：解构时保持响应式（必须用 storeToRefs）
const { fullName, progress } = storeToRefs(userStore)

// 带参数的 getter 调用
const todo = userStore.getTodoByText('学习 Pinia')
// todo = { text: '学习 Pinia', done: true }
</script>
```

---

### 二、Getters 的核心特性

| 特性 | 说明 |
|------|------|
| **缓存** | 基于计算属性的缓存：只有依赖的 state（或其他 getter）变化时才重新求值。多次访问同一 getter 不会重复计算。 |
| **响应式** | 自动追踪依赖，依赖变化时更新视图。 |
| **通过 this 访问** | Options Store 中可以使用 `this` 访问当前 store 的 state 和其他 getter（注意箭头函数不能使用 this）。 |
| **可传参** | 通过返回函数实现，但这样会**失去缓存**（每次调用都会重新执行）。 |
| **类型推断** | Setup Store 中自动推断；Options Store 中需要为 `this` 标注类型（如果是 TypeScript）。 |

---

### 三、常见坑点与正确做法

#### 坑点1：在 Options Store 的 getter 中使用箭头函数导致无法访问 `this`

```ts
getters: {
  // ❌ 错误：箭头函数不绑定自己的 this，this 指向 undefined
  fullNameUppercase: (state) => {
    return this.fullName.toUpperCase()  // this 是 undefined，报错
  },
  
  // ✅ 正确：使用普通函数（或者完全依赖 state，但不方便）
  fullNameUppercase(state) {
    return this.fullName.toUpperCase()
  }
}
```

**原理**：箭头函数的 `this` 是词法作用域，指向定义时的上下文（通常是模块作用域）而不是 store 实例。普通函数中 `this` 会被 Pinia 绑定到当前 store。

#### 坑点2：误解缓存的边界——带参数的 getter 没有缓存

```ts
getters: {
  // 返回函数的形式
  getTodoById: (state) => (id: number) => {
    console.log('执行了')  // 每次调用都会打印
    return state.todos.find(t => t.id === id)
  }
}
```

- 每次调用 `userStore.getTodoById(123)` 都会重新执行内部函数，**不会缓存结果**。
- 如果需要基于参数的缓存，可以考虑使用 `computed` + `Map` 或外部库（如 `lodash.memoize`）。

**改进方案**：如果参数范围有限，可以在组件中用 `computed` 包装：

```vue
<script setup>
const selectedId = ref(1)
const currentTodo = computed(() => userStore.getTodoById(selectedId.value))
</script>
```

#### 坑点3：在 getter 内部修改 state

```ts
getters: {
  // ❌ 千万不要这么做
  badGetter(state) {
    state.count++  // 修改了 state
    return state.count * 2
  }
}
```

- **永远不要**在 getter 中修改 state。getter 应该是纯函数，只读。
- 修改 state 请放到 `actions` 中。

#### 坑点4：解构 store 时未使用 `storeToRefs`，导致 getter 失去响应式

```vue
<script setup>
const userStore = useUserStore()
// ❌ 错误：解构后 fullName 变成普通值，不再响应更新
const { fullName } = userStore

// ✅ 正确
const { fullName } = storeToRefs(userStore)  // fullName 是 ref
</script>
```

#### 坑点5：在 Options Store 的 getter 中多次使用 `this` 导致类型错误（TypeScript）

```ts
getters: {
  // TypeScript 中会报错：隐式 any 类型
  computedMsg() {
    return this.someState + this.someGetter
  }
}
```

**解决方案**：显式标注 `this` 类型

```ts
import { defineStore } from 'pinia'

const useStore = defineStore('main', {
  state: () => ({ count: 0 }),
  getters: {
    // 方式1：标注 this 为 store 实例类型（通常用推断）
    doubleCount(this: any) {  // 或者定义接口
      return this.count * 2
    },
    // 方式2：使用参数 + this 混合（官方推荐）
    tripleCount(state) {
      // 这里 this 自动推断正确
      return state.count * 3
    }
  }
})
```

#### 坑点6：滥用 getter 导致不必要的计算结果

- 如果一个 getter 依赖的 state 很少变化，但它进行了高开销计算（如遍历大数组），没问题，因为缓存。
- 但**带参数的 getter** 每次调用都重新计算，如果频繁调用且计算开销大，会影响性能。此时考虑将计算结果存储在 state 中，手动更新。

#### 坑点7：在 Setup Store 中将 getter 错写成普通函数（失去缓存）

```ts
// ❌ 错误：这里 fullName 是普通函数，不是计算属性
const fullName = () => `${firstName.value} ${lastName.value}`

// ✅ 正确：使用 computed
const fullName = computed(() => `${firstName.value} ${lastName.value}`)
```

#### 坑点8：依赖其他 getter 时形成循环依赖

```ts
getters: {
  a(state) { return this.b + 1 },  // a 依赖 b
  b(state) { return this.a + 1 }   // b 依赖 a → 循环
}
```

- 循环依赖会导致栈溢出或无限递归。
- 解决方法：拆分逻辑或使用 action 计算并存储结果。

---

### 四、最佳实践总结

| 推荐 | 反对 |
|------|------|
| 使用普通函数定义 getter（Options Store） | 使用箭头函数（除非不需要 this） |
| 在模板/组件中通过 `store.xxx` 直接访问 | 直接解构 getter 而不使用 `storeToRefs` |
| 纯函数，只派生，不修改 state | 在 getter 中修改 state 或执行副作用 |
| 利用缓存提高性能 | 滥用带参数的 getter 并频繁调用 |
| 在 Setup Store 中使用 `computed` | 把普通函数当成 getter 用 |

### 五、记忆口诀

> **Getter 就像计算属性，依赖缓存纯函数；**
> **Options 用 this 须普通，Setup 使用 computed；**
> **解构记得 toRefs，参数返回丢缓存；**
> **只读不改守本分，派生状态最稳当。**

掌握这些，你就能安全、高效地使用 Pinia Getters，避开所有常见陷阱。