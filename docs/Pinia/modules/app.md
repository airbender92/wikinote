## src/store/modules/app.ts 解读

```typescript
// src/store/modules/app.ts

import { defineStore } from 'pinia'

interface AppState {
  sidebarCollapsed: boolean
  loading: boolean
}

export const useAppStore = defineStore('app', {
  state: (): AppState => ({
    sidebarCollapsed: false,
    loading: false,
  }),

  actions: {
    /** 切换侧边栏 */
    toggleSidebar(): void {
      this.sidebarCollapsed = !this.sidebarCollapsed
    },

    /** 设置侧边栏状态 */
    setSidebarCollapsed(collapsed: boolean): void {
      this.sidebarCollapsed = collapsed
    },

    /** 设置全局加载状态 */
    setLoading(loading: boolean): void {
      this.loading = loading
    },
  },
})
```

### Pinia Store 写法解析

```typescript
defineStore('app', { ... })
//        ↑
//      store 的唯一 ID
```

### 三种定义方式

| 方式 | 示例 |
|------|------|
| 选项式 | `defineStore('app', { state, actions })` |
| 组合式 | `defineStore('app', () => { reactive(...) })` |
| 类型式 | `defineStore('app', { state: () => ({...}) })` |

本项目用的是**类型式选项**，结合了两种优点。

### State 定义

```typescript
state: (): AppState => ({
  sidebarCollapsed: false,  // 侧边栏是否折叠
  loading: false,           // 全局加载状态
})
```

| 状态 | 类型 | 默认值 | 用途 |
|------|------|--------|------|
| `sidebarCollapsed` | boolean | false | 控制侧边栏展开/收起 |
| `loading` | boolean | false | 控制全屏加载遮罩 |

### Actions 定义

```typescript
actions: {
  toggleSidebar(): void {
    this.sidebarCollapsed = !this.sidebarCollapsed
  },
  setSidebarCollapsed(collapsed: boolean): void {
    this.sidebarCollapsed = collapsed
  },
  setLoading(loading: boolean): void {
    this.loading = loading
  },
}
```

| 方法 | 调用场景 |
|------|---------|
| `toggleSidebar()` | 点击侧边栏折叠按钮 |
| `setSidebarCollapsed()` | 根据路由/权限自动设置 |
| `setLoading()` | 接口请求时显示加载状态 |

### 使用示例

```typescript
// 组件中
import { useAppStore } from '@/store/modules/app'

const appStore = useAppStore()

// 读取状态
console.log(appStore.sidebarCollapsed)

// 调用 action
appStore.toggleSidebar()

// 或者同时设置多个
appStore.$patch({
  sidebarCollapsed: true,
  loading: true,
})
```

### 与其他 store 的关系

```
user store  →  登录状态、用户信息
menu store  →  菜单权限数据
app store   →  UI 状态（侧边栏、加载）
                    ↑
            被组件和布局使用
```

---

需要继续了解 **user store** 还是 **menu store**？