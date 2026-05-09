## Pinia Actions 详解：异步、跨调用与直接修改 State

Actions 是 Pinia Store 的**方法集合**，用于封装**业务逻辑**（包括同步和异步操作）。它与 Vuex 的 actions 类似，但**更简单**：可以直接通过 `this` 访问 state、getters 和其他 actions，并且支持 `async/await`。

---

### 一、基本知识点

#### 1. 在 Options Store 中定义 Actions

```ts
import { defineStore } from 'pinia'

const useUserStore = defineStore('user', {
  state: () => ({
    name: 'Alice',
    age: 25,
    posts: []
  }),
  
  actions: {
    // 同步 action：直接修改 state
    setName(newName: string) {
      this.name = newName   // ✅ 直接通过 this 修改 state
    },
    
    // 异步 action：登录 + 获取用户信息
    async login(username: string, password: string) {
      try {
        const { token, user } = await api.login(username, password)
        // 修改多个 state
        this.name = user.name
        this.age = user.age
        // 可以调用其他 action
        this.fetchPosts()
        return token
      } catch (error) {
        console.error('登录失败', error)
        throw error
      }
    },
    
    // 调用其他 action 的示例
    fetchPosts() {
      return api.getPosts().then(posts => {
        this.posts = posts
      })
    },
    
    // 调用另一个 action 并等待结果
    async refreshUserData() {
      await this.fetchPosts()      // 等待其他 action 完成
      this.setName('Alice Updated') // 调用同步 action
    }
  }
})
```

#### 2. 在 Setup Store 中定义 Actions（任何普通函数都是 action）

```ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

const useUserStore = defineStore('user', () => {
  const name = ref('Alice')
  const age = ref(25)
  const posts = ref([])
  
  // 同步 action
  function setName(newName: string) {
    name.value = newName   // 注意 .value
  }
  
  // 异步 action
  async function login(username: string, password: string) {
    const { token, user } = await api.login(username, password)
    name.value = user.name
    age.value = user.age
    await fetchPosts()     // 调用另一个 action
    return token
  }
  
  async function fetchPosts() {
    const data = await api.getPosts()
    posts.value = data
  }
  
  return { name, age, posts, setName, login, fetchPosts }
})
```

#### 3. 在组件中使用 Actions

```vue
<script setup>
const userStore = useUserStore()

// 调用 action，支持 await
const handleLogin = async () => {
  try {
    const token = await userStore.login('alice', '123')
    console.log('登录成功', token)
  } catch (error) {
    // 处理错误
  }
}

// 同步 action 直接调用
userStore.setName('Bob')
</script>
```

---

### 二、Actions 的核心特性

| 特性 | 说明 |
|------|------|
| **支持异步** | 可以使用 `async/await` 或直接返回 Promise，Pinia 能正确追踪异步状态 |
| **调用其他 action** | Options Store 中用 `this.otherAction()`；Setup Store 中直接调用函数（无需 `this`） |
| **直接修改 state** | 无需通过 `$patch`，直接 `this.xxx = value`（Options Store）或 `ref.value = ...`（Setup Store） |
| **任意参数** | 可以接收任何类型的参数，没有特殊限制 |
| **返回值** | 可以返回任何值（Promise、普通值等），组件中可获取返回值 |
| **错误处理** | 推荐在 action 内部捕获并处理错误，或者将错误抛给调用方 |

---

### 三、常见坑点与正确做法

| 坑点 | 错误示例 | 后果 | 正确做法 |
|------|----------|------|----------|
| **在 action 中使用箭头函数** | `actions: { increment: () => { this.count++ } }` | `this` 不指向 store，而是外部作用域（undefined），无法修改 state | 使用普通函数：`increment() { this.count++ }` |
| **在异步回调中使用 `this` 但没有提前保存** | `setTimeout(function() { this.count++ }, 1000)` | 回调中的 `this` 指向 window/undefined | 使用箭头函数：`setTimeout(() => { this.count++ }, 1000)` 或保存 `const store = this` |
| **忘记 `await` 异步 action 的调用** | `userStore.login(); console.log('done')` | 异步操作尚未完成，后续代码可能依赖错误的状态 | 使用 `await userStore.login()` |
| **在 Setup Store 的 action 中忘记 `.value`** | `name = 'Bob'`（应为 `name.value = 'Bob'`） | 直接赋值会丢失响应性，修改无效 | 牢记：`ref` 需要 `.value`；但可以通过返回 `name` 让外部使用 `store.name` 自动解包，内部仍需 `.value` |
| **直接修改 state 而非通过 action（在组件中）** | `userStore.name = 'Bob'`（虽然允许，但分散逻辑） | 逻辑分散，难以维护，调试困难 | 统一通过 action 修改（除非是极简单场景） |
| **action 中调用其他 action 但不处理返回值** | `this.login(); console.log('logged in')` | 如果 login 是异步，不会等待完成 | `await this.login()` |
| **在 action 内部抛出错误但不处理** | `async action() { throw new Error('fail') }` | 外部调用若没有 try/catch 会导致未捕获的 promise rejection | 在 action 内部 `try/catch` 并妥善处理，或者抛出错误让调用者捕获 |
| **超大 action 未拆分** | 一个 action 包含几百行业务逻辑 | 难以测试和维护 | 拆分为多个小 action，组合使用 |
| **Action 中并发请求的错误处理不完整** | `Promise.all([this.fetchA(), this.fetchB()])` | 一个请求失败会导致整个失败，但可能只想部分失败 | 使用 `Promise.allSettled` 或单独处理每个请求 |
| **滥用 `this` 导致 Options Store 与 Setup Store 混用时的困惑** | 在 Options Store 中调用 Setup Store 的 action 时错误使用 `this` | 代码混乱 | 统一风格；或者跨 store 调用时直接导入其他 store：`const other = useOtherStore(); other.someAction()` |
| **在 action 中修改 getter 计算结果（误以为可写）** | `this.fullName = 'New Name'` | `fullName` 是 getter，没有 setter，修改无效（严格模式下报错） | 修改 getter 依赖的原始 state |
| **Action 中修改数组/对象但未触发更新（极少见）** | 直接 `this.arr[0] = newVal`（实际上 Pinia 基于 reactive，会触发更新） | 其实没问题，但如果替换整个数组：`this.arr = newArr` 也是响应式的 | 放心操作，但注意如果用 `reactive` 包裹的嵌套对象替换整个对象时，可能需要 `Object.assign` 保持引用？Pinia 的 state 会自动处理 |

---

### 四、高级技巧与最佳实践

#### 1. 跨 Store 调用 Action

```ts
// store/user.ts
const useUserStore = defineStore('user', {
  actions: {
    async logout() {
      const cartStore = useCartStore()   // 导入其他 store
      await cartStore.clearCart()
      this.resetUser()
    }
  }
})
```

> **注意**：在 action 内部调用其他 store 的 action 是安全的，但要小心循环依赖（例如 store A 调用 store B，而 B 又调用 A）。

#### 2. Action 中合理使用 `$patch` 或直接修改

- 单个字段修改：直接赋值更清晰。
- 批量修改：使用 `this.$patch({ ... })` 性能更好（一次更新触发一次响应式通知）。
- 复杂逻辑（如数组 push/pop）：直接修改或 `$patch` 函数形式均可。

```ts
// 批量更新推荐
updateProfile(name: string, age: number) {
  this.$patch({ name, age })
}
```

#### 3. 错误处理的统一模式

```ts
async fetchData() {
  this.loading = true
  try {
    const data = await api.getData()
    this.data = data
  } catch (error) {
    this.error = error.message
    // 可以重新抛出，让组件决定如何处理
    throw error
  } finally {
    this.loading = false
  }
}
```

#### 4. 在组件中调用 action 并显示加载状态

```vue
<script setup>
const store = useStore()

async function handleSubmit() {
  try {
    await store.submitForm(formData)
    // 成功后的 UI 反馈
  } catch (err) {
    // 显示错误提示
  }
}
</script>
```

---

### 五、记忆口诀

> **Action 封装业务，异步同步都容易；**
> **Options 用 this 改，Setup 要用 .value；**
> **调用其他直接点，await 别忘了加；**
> **错误处理 try catch，维护逻辑不混乱。**

掌握以上内容，你就能熟练使用 Pinia Actions 编写清晰、可维护的业务代码。