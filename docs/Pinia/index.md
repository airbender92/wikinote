## src/store/index.ts 解读

```typescript
// src/store/index.ts

import { createPinia } from 'pinia'

const pinia = createPinia()

export default pinia
```

### 作用

这是 **Pinia 实例的创建和导出文件**。

```
创建 pinia 实例 → 导出 → main.ts 中 app.use(pinia) 安装
```

### 为什么需要单独一个文件？

| 原因 | 说明 |
|------|------|
| 统一管理 | 所有 store 模块集中在一处 |
| 方便扩展 | 后续可以添加中间件、持久化等 |
| 单一职责 | 创建逻辑和使用逻辑分离 |

### 完整 store 目录结构

```
store/
├── index.ts          # 创建 pinia 实例 ⬅️ 这个文件
└── modules/
    ├── user.ts       # 用户状态（登录信息、Token）
    ├── menu.ts       # 菜单权限
    └── app.ts        # 应用配置（侧边栏折叠等）
```

### 后续 store 模块的写法

```typescript
// store/modules/user.ts
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({ name: '张三' }),
  actions: {
    setName(name: string) {
      this.name = name
    },
  },
})
```

### 使用方式

```typescript
// 组件中
import { useUserStore } from '@/store/modules/user'

const userStore = useUserStore()
console.log(userStore.name)  // 张三
```

---

### 流程图

```
store/index.ts
    ↓
export pinia 实例
    ↓
main.ts
    ↓
app.use(pinia)  ← 安装到 Vue 应用
    ↓
所有组件可以通过 useUserStore() 访问状态
```

---

需要继续了解 **user store 模块** 吗？