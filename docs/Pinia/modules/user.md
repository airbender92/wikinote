## user.ts 完整解读

### 1. 导入依赖

```typescript
import { login as loginApi, getUserInfo as getUserInfoApi, logout as logoutApi } from '@/api/modules/auth'
import { setToken, removeToken, setUserInfo, getUserInfo } from '@/utils/auth'
import router from '@/router'
```

| 导入 | 用途 |
|------|------|
| `loginApi` | 登录接口 |
| `getUserInfoApi` | 获取用户信息 |
| `logoutApi` | 退出接口 |
| `setToken/removeToken` | Token 持久化 |
| `setUserInfo/getUserInfo` | 用户信息持久化 |
| `router` | 路由实例，用于跳转 |

---

### 2. State 定义

```typescript
interface UserState {
  token: string | null       // JWT 令牌
  userInfo: UserInfo | null  // 用户信息对象
}
```

---

### 3. Getters（计算属性）

```typescript
getters: {
  isLoggedIn: (state) => !!state.token,           // 是否登录
  username: (state) => state.userInfo?.nickname || state.userInfo?.username || '',
  roles: (state) => state.userInfo?.roles || [],
  permissions: (state) => state.userInfo?.permissions || [],
}
```

| Getter | 作用 |
|--------|------|
| `isLoggedIn` | `!!token` 双取反转布尔，判断登录状态 |
| `username` | 优先取 nickname，没有则取 username |
| `roles` | 用户角色数组 |
| `permissions` | 用户权限字符串数组 |

---

### 4. Actions（核心业务逻辑）

```typescript
actions: {
  /** 初始化 - 刷新页面时恢复登录状态 */
  initUserInfo(): void {
    const userInfo = getUserInfo()  // 从 localStorage 读取
    if (userInfo) {
      this.userInfo = userInfo
    }
  },

  /** 登录流程 */
  async login(credentials: Credentials): Promise<void> {
    const { data } = await loginApi(credentials)
    this.token = data.token
    setToken(data.token)           // 持久化到 localStorage
    await this.fetchUserInfo()    // 获取用户信息
  },

  /** 获取用户信息 */
  async fetchUserInfo(): Promise<void> {
    const { data } = await getUserInfoApi()
    this.userInfo = data
    setUserInfo(data)             // 持久化到 localStorage
  },

  /** 退出登录 */
  async logout(): Promise<void> {
    try {
      await logoutApi()
    } catch {
      // 忽略接口错误，确保退出流程完成
    } finally {
      this.resetState()
      if (router.currentRoute.value.path !== '/login') {
        router.push('/login')
      }
    }
  },

  /** 重置状态 */
  resetState(): void {
    this.token = null
    this.userInfo = null
    removeToken()  // 清除 localStorage
  },
}
```

---

### 5. 登录流程图

```
用户点击登录
    ↓
login(credentials)
    ↓
调用 loginApi(credentials)
    ↓
获取 token，存入 state 和 localStorage
    ↓
调用 fetchUserInfo()
    ↓
获取用户信息，存入 state 和 localStorage
    ↓
登录完成，路由跳转首页
```

---

### 6. 退出流程图

```
用户点击退出
    ↓
logout()
    ↓
┌─────────────────────────┐
│ 调用 logoutApi（可选）    │
│ 即使接口失败也继续执行     │
└─────────────────────────┘
    ↓
resetState()  →  清除 token 和 userInfo
    ↓
router.push('/login')  →  跳转登录页
```

---

### 7. 刷新页面时如何恢复登录状态？

```
用户刷新页面 (F5)
    ↓
Vue 应用重新初始化
    ↓
initUserInfo() 被调用
    ↓
从 localStorage 读取 userInfo
    ↓
恢复到 this.userInfo
    ↓
页面状态保持登录
```

---

### 8. 与其他 store 的关系

```
user store
├── token          → 路由守卫判断是否登录
├── userInfo       → 提供用户信息
├── roles          → 权限判断
└── logout()       → 触发 menuStore.resetMenuState()

menu store
└── fetchMenus()   → 依赖 userStore.token
```

---

### 9. 关键设计点

| 设计 | 说明 |
|------|------|
| `finally` 块 | 确保即使 logoutApi 失败也能跳转登录页 |
| `!!state.token` | 双取反确保返回布尔值（防止 null 转 false） |
| 可选链 `?.` | userInfo 可能为 null，安全访问 |
| `|| ''` | 提供默认值，避免 undefined |

---

### 10. 与 menu store 的数据流

```
登录成功
    ↓
user.login()
    ↓
user.fetchUserInfo() → userInfo 设置完成
    ↓
menu.fetchMenus() → 菜单加载完成
    ↓
路由跳转首页
```

---

### 三个 store 对比

| Store | 管理内容 | 持久化 |
|-------|---------|--------|
| user | token、用户信息 | ✅ localStorage |
| menu | 菜单、权限 | ❌ 仅内存 |
| app | 侧边栏、加载状态 | ❌ 仅内存 |

---

需要继续了解 **路由配置** 吗？