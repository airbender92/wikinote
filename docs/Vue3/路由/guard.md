## router/guards.ts 路由守卫解读

```typescript
// src/router/guards.ts

import type { Router } from 'vue-router'
import { getToken } from '@/utils/auth'
import { useUserStore } from '@/store/modules/user'
import { useMenuStore } from '@/store/modules/menu'

const whiteList = ['/login']

export function setupGuards(router: Router): void {
  router.beforeEach(async (to, from, next) => {
    // ...
  })
}
```

---

### 1. 路由守卫概述

```typescript
router.beforeEach(async (to, from, next) => {
  // to   → 目标路由
  // from → 来源路由
  // next → 放行函数
})
```

| 守卫类型 | 触发时机 |
|---------|---------|
| `beforeEach` | 每次路由切换前 |
| `beforeResolve` | 导航确认前（组件加载后） |
| `afterEach` | 导航完成后 |

---

### 2. 白名单机制

```typescript
const whiteList = ['/login']
```

| 说明 | 含义 |
|------|------|
| `whiteList` | 不需要登录就能访问的页面 |
| `/login` | 登录页本身不需要权限 |

---

### 3. 守卫流程图

```
路由切换
    ↓
检查 Token
    ↓
├─ 有 Token
│   ├─ 访问 /login？ → 重定向到 /
│   └─ 访问其他页面
│       ├─ userInfo 存在？ → 直接放行
│       └─ userInfo 不存在？ → 获取用户信息和菜单
│
└─ 无 Token
    ├─ 在白名单？ → 放行
    └─ 不在白名单？ → 跳转登录页
```

---

### 4. 已登录情况（ token 存在）

```typescript
if (token) {
  // 访问登录页 → 重定向首页
  if (to.path === '/login') {
    next({ path: '/' })
    return
  }

  // 初始化用户信息
  if (!userStore.userInfo) {
    try {
      userStore.initUserInfo()           // 从 localStorage 恢复
      if (!userStore.userInfo) {
        await userStore.fetchUserInfo()  // 从接口获取
      }
      await menuStore.fetchMenus()       // 获取菜单
      if (userStore.userInfo?.permissions) {
        menuStore.setPermissions(userStore.userInfo.permissions)
      }
      next({ ...to, replace: true })     // 重新导航
    } catch {
      userStore.resetState()
      menuStore.resetMenuState()
      next(`/login?redirect=${to.path}`)
    }
  } else {
    next()  // 已初始化，直接放行
  }
}
```

#### 首次访问（userInfo 不存在）

```
1. initUserInfo()     → 从 localStorage 读取
2. fetchUserInfo()    → 从后端获取用户信息
3. fetchMenus()       → 获取菜单权限
4. setPermissions()   → 同步权限到 menuStore
5. next({ ...to })   → 重新进入目标路由
```

#### 刷新页面后（userInfo 存在但可能是旧数据）

```
1. initUserInfo()     → 从 localStorage 恢复
2. 如果恢复成功（userInfo 存在）→ 直接放行
3. 如果恢复失败（userInfo 为空）→ 从接口获取
```

---

### 5. 未登录情况（无 token）

```typescript
if (whiteList.includes(to.path)) {
  next()  // 白名单页面，直接放行
} else {
  next(`/login?redirect=${to.path}`)  // 跳转登录，携带来源路径
}
```

**为什么要带 redirect？**

```typescript
// 登录成功后可以跳回原页面
// 例如：访问 /dashboard → 跳转 /login?redirect=/dashboard
//      登录成功 → 跳回 /dashboard
```

---

### 6. 为什么用 async/await？

```typescript
async (to, from, next) => {
  // ...
  await userStore.fetchUserInfo()  // 异步等待
  await menuStore.fetchMenus()
  next({ ...to, replace: true })
}
```

| 原因 | 说明 |
|------|------|
| 等待数据加载 | 确保权限数据获取完成后再导航 |
| 避免闪屏 | 先拿到菜单再渲染页面 |

---

### 7. `next({ ...to, replace: true })` 解释

```typescript
next({ ...to, replace: true })
```

| 参数 | 含义 |
|------|------|
| `...to` | 复制目标路由的所有信息 |
| `replace: true` | 替换当前历史记录（不会回退到上一步） |

**效果：**
```
浏览器历史：/login → /dashboard
                   ↑
              replace 替换，不是 push
```

---

### 8. 错误处理

```typescript
catch {
  userStore.resetState()      // 清除用户状态
  menuStore.resetMenuState()   // 清除菜单状态
  next(`/login?redirect=${to.path}`)  // 跳转登录
}
```

**什么情况会进入 catch？**
- Token 过期
- 后端接口异常
- 用户信息获取失败

---

### 9. 完整流程时序图

```
用户打开 /dashboard
    ↓
beforeEach 触发
    ↓
有 Token？
    ├─ 是 → userInfo 存在？
    │       ├─ 是 → next() 放行
    │       └─ 否 → initUserInfo()
    │               ├─ localStorage 有 → fetchMenus() → next()
    │               └─ localStorage 无 → fetchUserInfo() → fetchMenus() → next()
    │
    └─ 否 → /login 在白名单？
            ├─ 是 → next() 放行
            └─ 否 → next('/login?redirect=/dashboard')
```

---

### 10. 与其他模块的交互

```
guards.ts
    ├── getToken()          → auth.ts 工具函数
    ├── useUserStore()     → 用户状态管理
    │   ├── initUserInfo()
    │   ├── fetchUserInfo()
    │   └── resetState()
    │
    └── useMenuStore()     → 菜单状态管理
        ├── fetchMenus()
        ├── setPermissions()
        └── resetMenuState()
```

---

### 11. 为什么在 main.ts 中后设置守卫？

```typescript
// main.ts
app.use(pinia)     // 先安装 pinia（守卫中用到 store）
app.use(router)    // 再安装 router
setupGuards(router) // 最后设置守卫
```

**顺序很重要：** 守卫中使用了 `useUserStore()`，所以 pinia 必须先安装。

---

需要继续了解 **请求封装（request.ts）** 吗？