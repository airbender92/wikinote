## routes.ts 路由表定义解读

```typescript
// src/router/routes.ts

import type { RouteRecordRaw } from 'vue-router'

export const constantRoutes: RouteRecordRaw[] = [
  // ... 静态路由
]

export const asyncRoutes: RouteRecordRaw[] = [
  // ... 动态路由
]
```

---

### 1. RouteRecordRaw 类型

```typescript
type RouteRecordRaw = RouteRecordSingleView | RouteRecordMultipleViews | RouteRecordRaw
```

| 类型 | 用途 |
|------|------|
| `RouteRecordRaw` | 完整的路由记录类型 |
| 包含 | path、name、component、meta 等 |

---

### 2. constantRoutes（静态路由）

```typescript
export const constantRoutes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: {
      title: '登录',
      hidden: true,
      requiresAuth: false,
    },
  },
  {
    path: '/',
    component: () => import('@/layouts/DefaultLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: {
          title: '控制台',
          icon: 'HomeFilled',
          requiresAuth: true,
        },
      },
    ],
  },
]
```

#### 登录路由

```typescript
{
  path: '/login',
  name: 'Login',
  component: () => import('@/views/login/index.vue'),
  meta: {
    title: '登录',           // 页面标题
    hidden: true,           // 不显示在菜单
    requiresAuth: false,    // 不需要登录
  },
}
```

| 属性 | 说明 |
|------|------|
| `path` | 路由路径 |
| `name` | 路由名称（可省略） |
| `component` | 懒加载组件（`() => import()`） |
| `meta` | 元信息（自定义数据） |

#### 首页路由

```typescript
{
  path: '/',
  component: () => import('@/layouts/DefaultLayout.vue'),  // 主布局
  redirect: '/dashboard',                                    // 重定向
  children: [
    {
      path: 'dashboard',
      name: 'Dashboard',
      component: () => import('@/views/dashboard/index.vue'),
      meta: {
        title: '控制台',
        icon: 'HomeFilled',
        requiresAuth: true,
      },
    },
  ],
}
```

| 属性 | 说明 |
|------|------|
| `redirect` | 访问 `/` 时重定向到 `/dashboard` |
| `children` | 嵌套路由（子路由） |

---

### 3. asyncRoutes（动态路由 / 404）

```typescript
export const asyncRoutes: RouteRecordRaw[] = [
  {
    path: '/:pathMatch(.*)*',  // 匹配所有路径
    name: 'NotFound',
    component: () => import('@/layouts/BlankLayout.vue'),
    children: [
      {
        path: '',
        component: () => import('@/views/error/NotFound.vue'),
        meta: {
          title: '404',
          hidden: true,
        },
      },
    ],
  },
]
```

#### 404 路由

```typescript
{
  path: '/:pathMatch(.*)*',  // 正则：匹配任意路径
  name: 'NotFound',
  component: BlankLayout,    // 空白布局
  children: [
    {
      path: '',
      component: NotFoundVue, // 404 页面组件
    },
  ],
}
```

**`:pathMatch(.*)*` 的作用：**
```
访问 /abc     → 匹配 → NotFound
访问 /xyz/123 → 匹配 → NotFound
访问 /login   → 不匹配 → 正常路由
```

---

### 4. 懒加载语法

```typescript
component: () => import('@/views/login/index.vue')
```

| 写法 | 区别 |
|------|------|
| `import('@/views/Login.vue')` | 同步导入（打包时全部 bundle） |
| `() => import('@/views/Login.vue')` | 懒加载（访问时才请求） |

**懒加载优势：**
- 首屏加载更快
- 路由跳转时才加载对应组件
- 减小初始 bundle 体积

---

### 5. 路由表结构图

```
constantRoutes:
├── /login                          → LoginPage (hidden, 无需权限)
└── /                               → DefaultLayout
    └── /dashboard                  → Dashboard (首页)

asyncRoutes:
└── /:pathMatch(.*)*               → BlankLayout
    └── '' (空路径)                 → NotFound (404)
```

---

### 6. 嵌套路由原理

```typescript
{
  path: '/',
  component: DefaultLayout,
  children: [
    { path: 'dashboard', ... }
  ]
}
```

**路由匹配规则：**
```
访问 /dashboard
    ↓
匹配 path: '/' → 渲染 DefaultLayout
    ↓
匹配 children.path: 'dashboard'
    ↓
在 DefaultLayout 的 <router-view> 渲染 Dashboard
```

---

### 7. meta 属性说明

```typescript
meta: {
  title: '控制台',        // 页面标题（用于标签页、面包屑）
  icon: 'HomeFilled',     // 菜单图标
  hidden: true/false,     // 是否在菜单中隐藏
  requiresAuth: true/false // 是否需要登录
}
```

| 属性 | 用途 |
|------|------|
| `title` | 页面标题、菜单名称 |
| `icon` | Element Plus 图标名 |
| `hidden` | 不显示在侧边栏菜单 |
| `requiresAuth` | 是否需要登录 |

---

### 8. 懒加载 vs 同步加载

```typescript
// 同步（所有路由打包到一个文件）
import Login from '@/views/login/index.vue'

// 懒加载（每个路由单独打包）
const Login = () => import('@/views/login/index.vue')
```

**打包效果对比：**
```
同步：app.js (5MB) — 所有页面都在一个文件

懒加载：
  app.js (500KB) — 主框架
  login.js (100KB) — 访问 /login 时加载
  dashboard.js (200KB) — 访问 /dashboard 时加载
```

---

### 9. 完整的路由表配置字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `path` | string | 路由路径 |
| `name` | string | 路由名称 |
| `component` | Component | 页面组件 |
| `components` | Record<string, Component> | 命名视图 |
| `children` | RouteRecordRaw[] | 子路由 |
| `redirect` | string | 重定向路径 |
| `meta` | object | 元信息 |
| `props` | boolean/object/function | 路由传参 |
| `alias` | string | 路由别名 |

---

### 10. 路由表如何被使用

```typescript
// router/index.ts
import { constantRoutes, asyncRoutes } from './routes'

const router = createRouter({
  routes: [...constantRoutes, ...asyncRoutes],
})
```

---

需要继续了解 **路由守卫（guards.ts）** 吗？