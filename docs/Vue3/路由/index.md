## router/index.ts 解读

```typescript
// src/router/index.ts

import { createRouter, createWebHistory } from 'vue-router'
import { constantRoutes, asyncRoutes } from './routes'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [...constantRoutes, ...asyncRoutes],
  scrollBehavior: () => ({ top: 0 }),
})

export default router
```

---

### 1. 创建路由实例

```typescript
const router = createRouter({...})
```

| 选项 | 说明 |
|------|------|
| `history` | 路由模式（History / Hash） |
| `routes` | 路由表（静态 + 动态） |
| `scrollBehavior` | 路由切换时滚动行为 |

---

### 2. History 模式

```typescript
history: createWebHistory(import.meta.env.BASE_URL)
```

| 模式 | 特点 | URL 示例 |
|------|------|---------|
| `createWebHistory` | History API（需要服务器配置） | `/users/123` |
| `createWebHashHistory` | Hash 路由（无需服务器配置） | `/#/users/123` |

**`import.meta.env.BASE_URL`**：来自 vite.config.ts 的 `base` 配置，默认 `/`

---

### 3. 路由表合并

```typescript
routes: [...constantRoutes, ...asyncRoutes]
```

| 路由类型 | 说明 |
|---------|------|
| `constantRoutes` | 常驻路由（登录页、404 等） |
| `asyncRoutes` | 动态路由（权限相关，异步加载） |

---

### 4. 滚动行为

```typescript
scrollBehavior: () => ({ top: 0 })
```

| 值 | 效果 |
|-----|------|
| `{ top: 0 }` | 切换路由时滚动到顶部 |
| `{ left: 0, top: 0 }` | 滚动到左上角 |
| `false` | 不控制滚动 |

---

### 5. scrollBehavior 完整示例

```typescript
scrollBehavior(to, from, savedPosition) {
  // 如果有保存的位置（如浏览器后退），恢复到该位置
  if (savedPosition) {
    return savedPosition
  }
  // 否则滚动到锚点
  if (to.hash) {
    return { el: to.hash }
  }
  // 默认滚动到顶部
  return { top: 0 }
}
```

---

### 6. 路由表结构

```
routes
├── constantRoutes（静态路由，所有人都能访问）
│   ├── /login
│   ├── /404
│   └── /
│
└── asyncRoutes（动态路由，根据权限加载）
    ├── /users（用户管理）
    ├── /orders（订单管理）
    └── /system（系统设置）
```

---

### 7. 与 routes.ts 的关系

```typescript
// routes.ts 导出
export const constantRoutes = [...]
export const asyncRoutes = [...]

// index.ts 导入并合并
import { constantRoutes, asyncRoutes } from './routes'
routes: [...constantRoutes, ...asyncRoutes]
```

---

### 8. 导出后的使用

```typescript
// main.ts
import router from './router'

const app = createApp(App)
app.use(router)  // 安装路由插件

// 组件中
import { useRouter, useRoute } from 'vue-router'
const router = useRouter()
const route = useRoute()
```

---

### 9. 整体流程图

```
main.ts
    ↓
app.use(router)
    ↓
router.install(app)  // 全局注册 $router、$route
    ↓
setupGuards(router)  // 设置路由守卫
    ↓
app.mount('#app')
    ↓
用户访问 /users
    ↓
router.match('/users')  → 找到对应路由 → 渲染组件
```

---

### 10. 路由守卫设置位置

```typescript
// main.ts 中
import { setupGuards } from './router/guards'
setupGuards(router)
```

**顺序很重要：**
```typescript
app.use(pinia)     // 1. 先安装状态管理
app.use(router)    // 2. 再安装路由
setupGuards(router) // 3. 最后设置守卫（依赖 router 实例）
```

---

需要继续了解 **routes.ts** 路由表定义吗？