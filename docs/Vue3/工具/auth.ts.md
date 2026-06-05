## utils/auth.ts 认证工具函数解读

```typescript
// src/utils/auth.ts

import { getItem, setItem, removeItem } from './storage'

const TOKEN_KEY = 'token'
const REFRESH_TOKEN_KEY = 'refreshToken'
const USER_INFO_KEY = 'userInfo'

/** 获取 token */
export function getToken(): string | null {
  return getItem<string>(TOKEN_KEY)
}

/** 设置 token */
export function setToken(token: string): void {
  setItem(TOKEN_KEY, token)
}

/** 移除 token */
export function removeToken(): void {
  removeItem(TOKEN_KEY)
  removeItem(REFRESH_TOKEN_KEY)
  removeItem(USER_INFO_KEY)
}

/** 获取用户信息 */
export function getUserInfo(): UserInfo | null {
  return getItem<UserInfo>(USER_INFO_KEY)
}

/** 设置用户信息 */
export function setUserInfo(userInfo: UserInfo): void {
  setItem(USER_INFO_KEY, userInfo)
}
```

---

### 1. 存储结构

| Key | 存储内容 |
|-----|---------|
| `token` | 访问令牌 |
| `refreshToken` | 刷新令牌 |
| `userInfo` | 用户信息对象 |

---

### 2. 核心操作

```typescript
getItem<T>(key)     // 从 localStorage 读取
setItem(key, value) // 写入 localStorage
removeItem(key)     // 删除
```

| 函数 | 作用 |
|------|------|
| `getToken()` | 读取 token |
| `setToken()` | 存储 token |
| `removeToken()` | 清除 token + refreshToken + userInfo |
| `getUserInfo()` | 读取用户信息 |
| `setUserInfo()` | 存储用户信息 |

---

### 3. removeToken 的作用

```typescript
export function removeToken(): void {
  removeItem(TOKEN_KEY)
  removeItem(REFRESH_TOKEN_KEY)
  removeItem(USER_INFO_KEY)
}
```

**退出登录时调用：**
```
用户点击退出
    ↓
userStore.logout()
    ↓
removeToken() → 清除所有认证信息
    ↓
跳转登录页
```

---

### 4. 与 userStore 的配合

```typescript
// user.ts 中使用
import { setToken, removeToken, setUserInfo, getUserInfo } from '@/utils/auth'

// 登录
setToken(data.token)
setUserInfo(data)

// 初始化（刷新页面时）
const info = getUserInfo()  // 从 localStorage 恢复

// 退出
removeToken()  // 清除所有
```

---

### 5. 为什么需要泛型？

```typescript
getItem<T>(TOKEN_KEY)  // T = string | UserInfo
```

| 调用 | T 类型 | 返回值 |
|------|--------|--------|
| `getItem<string>(TOKEN_KEY)` | string | `string \| null` |
| `getItem<UserInfo>(USER_INFO_KEY)` | UserInfo | `UserInfo \| null` |

---

### 6. 存储流程图

```
登录成功
    ↓
setToken(token)     → localStorage.setItem('token', token)
    ↓
setUserInfo(info)   → localStorage.setItem('userInfo', JSON.stringify(info))
    ↓
刷新页面
    ↓
getToken()         → localStorage.getItem('token')
getUserInfo()       → localStorage.getItem('userInfo')
    ↓
用户状态恢复
```

---

### 7. 为什么单独封装？

```typescript
// 直接用 localStorage 的问题
localStorage.setItem('token', token)
localStorage.getItem('token')

// 封装后的好处：
// 1. 统一管理 Key
// 2. 类型安全
// 3. 便于后续扩展（如加密、换存储介质）
```

---

### 8. 完整调用链

```
组件调用 userStore.login()
    ↓
loginApi() 返回 token
    ↓
setToken(token)     → auth.ts
    ↓
userStore.fetchUserInfo()
    ↓
setUserInfo(info)   → auth.ts
    ↓
路由跳转
```

---

### 9. storage.ts 是什么？

auth.ts 依赖 storage.ts：

```typescript
import { getItem, setItem, removeItem } from './storage'
```

需要查看 storage.ts 吗？

---

需要继续了解 **request.ts（请求封装）** 吗？