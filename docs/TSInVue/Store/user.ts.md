## user.ts 中的 TypeScript 语法详解

### 1. 类型导入 vs 值导入

```typescript
import { login as loginApi, ... } from '@/api/modules/auth'
import router from '@/router'
```

| 写法 | 含义 |
|------|------|
| `import { login as loginApi }` | 值导入（从模块导入函数） |
| `import router from '@/router'` | 默认导入（导入默认导出） |

---

### 2. 接口继承与联合类型

```typescript
interface UserState {
  token: string | null      // 联合类型：字符串或 null
  userInfo: UserInfo | null // 自定义类型或 null
}
```

| 类型 | 含义 |
|------|------|
| `string \| null` | 可以是字符串，也可以是 null |
| `UserInfo \| null` | UserInfo 类型或 null |

---

### 3. Getter 的类型推断

```typescript
getters: {
  isLoggedIn: (state) => !!state.token,
  username: (state) => state.userInfo?.nickname || state.userInfo?.username || '',
}
```

**逐个解析：**

```typescript
// isLoggedIn
(state) => !!state.token
// 推断为: (state: UserState) => boolean

// username
(state) => state.userInfo?.nickname || state.userInfo?.username || ''
// 推断为: (state: UserState) => string
```

---

### 4. 可选链操作符 `?.`

```typescript
state.userInfo?.nickname
```

| 写法 | userInfo 为 null 时 |
|------|---------------------|
| `state.userInfo.nickname` | ❌ 报错 `Cannot read property...` |
| `state.userInfo?.nickname` | ✅ 返回 undefined |

---

### 5. 空值合并运算符 `||`

```typescript
state.userInfo?.nickname || state.userInfo?.username || ''
```

```
userInfo = null
    ↓
nickname = undefined
    ↓
username = undefined
    ↓
最终返回 ''（默认值）
```

| 运算符 | 区别 |
|--------|------|
| `\|\|` | 假值（0, '', false, null, undefined）都用默认值 |
| `??` | 仅 null 和 undefined 用默认值 |

---

### 6. 双取反 `!!` 转布尔

```typescript
isLoggedIn: (state) => !!state.token
```

| token 值 | `!!token` |
|----------|-----------|
| `'abc'` | `true` |
| `''` | `false` |
| `null` | `false` |
| `undefined` | `false` |

**为什么用 `!!`？**

```typescript
// 不用 !! 的问题
const isLoggedIn = (state) => state.token
// 返回类型: string | null

// 用 !! 
const isLoggedIn = (state) => !!state.token
// 返回类型: boolean
```

---

### 7. 异步函数返回类型

```typescript
async login(credentials: Credentials): Promise<void> {
  const { data } = await loginApi(credentials)
  // ...
}
```

| 部分 | 含义 |
|------|------|
| `async` | 声明这是一个异步函数 |
| `: Promise<void>` | 返回 Promise，不返回值 |

---

### 8. 参数类型约束

```typescript
async login(credentials: Credentials): Promise<void>
```

`Credentials` 是自定义类型，来自 `@/types/user.d.ts` 或其他类型定义。

---

### 9. 解构赋值的类型

```typescript
const { data } = await loginApi(credentials)
```

**为什么能解构？**

```typescript
// loginApi 返回的是 AxiosResponse
{
  data: { token: 'xxx', ... },
  status: 200,
  message: 'success'
}

// 解构后 data 类型为 { token: string, ... }
```

---

### 10. TypeScript 如何推断 this 类型

```typescript
actions: {
  login(credentials: Credentials): void {
    this.token = credentials  // this 是 UserState
  }
}
```

**Pinia 的类型推断：**

```typescript
defineStore('user', { ... })
//        ↓
// Pinia 根据 state 推断 this 类型
//        ↓
// this 自动变成 Store<{ token: ..., userInfo: ... }>
```

---

### 11. 类型守卫（try-catch）

```typescript
async logout(): Promise<void> {
  try {
    await logoutApi()
  } catch {
    // 忽略接口错误
  }
}
```

| 语法 | 说明 |
|------|------|
| `catch { }` | TS 4.0+ 语法，无需 `(error)` |
| 接口错误时 | 不会中断 finally 块执行 |

---

### 12. 完整类型推导图

```typescript
// 1. State 接口
interface UserState {
  token: string | null
  userInfo: UserInfo | null
}

// 2. state 返回类型
state: (): UserState => ({...})

// 3. getters 类型推导
getters: {
  isLoggedIn: (state) => !!state.token
  // → (state: UserState) => boolean
  
  username: (state) => state.userInfo?.nickname || ''
  // → (state: UserState) => string
}

// 4. actions 中 this 类型
actions: {
  login(credentials: Credentials): Promise<void> {
    this.token  // → string | null
    this.userInfo  // → UserInfo | null
  }
}
```

---

### 13. 与 app.ts、menu.ts 的 TS 对比

| 特性 | user.ts | menu.ts | app.ts |
|------|---------|---------|--------|
| 接口定义 | ✅ UserState | ✅ MenuState | ✅ AppState |
| Getter | ✅ 4个 | ✅ 1个 | ❌ |
| 异步 Action | ✅ login/logout/fetchUserInfo | ✅ fetchMenus | ❌ |
| 解构赋值 | ✅ `{ data }` | ✅ `{ data }` | ❌ |
| 可选链 | ✅ `?.` | ✅ `?.` | ❌ |
| 联合类型 | ✅ `\| null` | ❌ | ❌ |

---

需要继续了解 **路由配置** 吗？