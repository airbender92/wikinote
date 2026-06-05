## App.vue 解读

```vue
<template>
  <el-config-provider>
    <router-view />
  </el-config-provider>
</template>
```

---

### 组件结构

```
App.vue
└── <el-config-provider>
    └── <router-view />
```

| 组件 | 作用 |
|------|------|
| `el-config-provider` | Element Plus 全局配置（国际化、主题等） |
| `router-view` | 路由出口，渲染匹配到的页面 |

---

### 为什么需要 el-config-provider？

```vue
<el-config-provider>
  <!-- 内部所有 Element Plus 组件都会使用这个配置 -->
</el-config-provider>
```

**常见配置项：**
```vue
<el-config-provider :locale="zhCn" :size="'default'">
  <router-view />
</el-config-provider>
```

| 属性 | 类型 | 说明 |
|------|------|------|
| `locale` | Locale | 语言（zhCn / en） |
| `size` | 'large'/'default'/'small' | 组件默认尺寸 |
| `button` | ButtonConfig | 按钮配置 |

---

### router-view 的作用

```vue
<router-view />
<!-- 等价于 -->
<RouterView />
```

**渲染匹配到的路由组件：**
```
访问 /login     → 渲染 LoginPage
访问 /dashboard → 渲染 Dashboard
访问 /users     → 渲染 UserList
```

---

### 为什么 App.vue 这么简洁？

| 设计 | 原因 |
|------|------|
| 没有 `<script>` | 不需要额外逻辑 |
| 没有 `<style>` | 全局样式在 global.scss |
| 只做组合 | 布局由 DefaultLayout/BlankLayout 处理 |

---

### 整体渲染层级

```
index.html
  └── <div id="app">
        └── App.vue
              └── el-config-provider
                    └── router-view
                          ├── BlankLayout (登录页等)
                          │     └── router-view
                          │
                          └── DefaultLayout (业务页)
                                ├── Header
                                ├── Sidebar
                                └── Main
                                      └── router-view
```

---

### 与 main.ts 的关系

```typescript
// main.ts
import App from './App.vue'

const app = createApp(App)
app.use(pinia)
app.use(router)
app.mount('#app')
```

```
createApp(App)
    ↓
App.vue 渲染
    ↓
<router-view> 找到匹配路由
    ↓
渲染对应页面组件
```

---

就这么简洁，App.vue 本质上只是一个**根组件容器**。

需要继续了解 **mock/index.ts** 或 **views/login/index.vue** 吗？