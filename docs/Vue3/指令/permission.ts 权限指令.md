## permission.ts 权限指令解读

```typescript
// src/directives/permission.ts

import type { Directive } from 'vue'
import { useUserStore } from '@/store/modules/user'

/**
 * 权限指令
 * v-permission="'user:add'"
 * v-permission="['user:add', 'user:edit']"
 */
export const permission: Directive<HTMLElement, string | string[]> = {
  mounted(el: HTMLElement, binding) {
    const userStore = useUserStore()
    const value = binding.value

    if (!value) return

    const permissions = userStore.permissions
    if (permissions.includes('*')) return

    const hasPermission = typeof value === 'string'
      ? permissions.includes(value)
      : value.some((p) => permissions.includes(p))

    if (!hasPermission) {
      el.parentNode?.removeChild(el)
    }
  },
}
```

---

### 1. Vue 自定义指令

```typescript
Directive<HTMLElement, string | string[]>
//     ↑
// 指令类型泛型
// 第一个参数：指令绑定的元素类型
// 第二个参数：binding 值的类型
```

**Vue 指令生命周期钩子：**

| 钩子 | 触发时机 |
|------|---------|
| `beforeMount` | 元素挂载前 |
| `mounted` | 元素挂载后 ⬅️ 使用这个 |
| `beforeUpdate` | 更新前 |
| `updated` | 更新后 |
| `beforeUnmount` | 卸载前 |
| `unmounted` | 卸载后 |

---

### 2. mounted 钩子参数

```typescript
mounted(el: HTMLElement, binding) {
  // el    → 指令绑定的 DOM 元素
  // binding → 指令的绑定值
}
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `el` | `HTMLElement` | 指令绑定的 DOM 元素 |
| `binding.value` | `string \| string[]` | 指令的值（权限标识） |

---

### 3. 权限判断逻辑

```typescript
// 1. 没有传值，直接返回（不处理）
if (!value) return

// 2. 如果有 '*' 超级权限，直接通过
if (permissions.includes('*')) return

// 3. 判断权限
const hasPermission = typeof value === 'string'
  ? permissions.includes(value)           // 字符串：直接检查
  : value.some((p) => permissions.includes(p))  // 数组：任一有权限即可
```

---

### 4. 权限判断详解

```typescript
typeof value === 'string'
  ? permissions.includes(value)
  : value.some((p) => permissions.includes(p))
```

**情况一：字符串**
```typescript
v-permission="'user:add'"
// value = 'user:add'
// permissions = ['user:add', 'user:edit']
// includes('user:add') → true ✅ 有权限
```

**情况二：数组**
```typescript
v-permission="['user:add', 'user:delete']"
// value = ['user:add', 'user:delete']
// permissions = ['user:add']
// value.some(p => permissions.includes(p))
//   → p='user:add', includes('user:add') → true ✅ 有权限
//   → p='user:delete', includes('user:delete') → false
//   → some() 只要有一个 true 就返回 true
```

---

### 5. 无权限时移除元素

```typescript
if (!hasPermission) {
  el.parentNode?.removeChild(el)
}
```

```
无权限
    ↓
el.parentNode?.removeChild(el)
    ↓
从 DOM 中移除当前元素
    ↓
按钮/菜单项不再显示
```

**为什么用 `?.` 可选链？**
- 确保 `parentNode` 存在才执行移除

---

### 6. 使用示例

```vue
<template>
  <!-- 单个权限 -->
  <button v-permission="'user:add'">新增用户</button>
  
  <!-- 多个权限（满足任一即可） -->
  <button v-permission="['user:edit', 'user:delete']">操作</button>
  
  <!-- 超级管理员（*）能看到所有 -->
  <button v-permission="'*'">管理员按钮</button>
</template>
```

---

### 7. 指令注册

```typescript
// main.ts
app.directive('permission', permission)
```

**注册后**：项目任意 `.vue` 文件都可以使用 `v-permission`

---

### 8. 与路由守卫的区别

| 对比 | 路由守卫 | 指令 |
|------|---------|------|
| 控制粒度 | 整个页面 | 单个按钮/元素 |
| 使用位置 | router/index.ts | 组件模板 |
| 场景 | 页面级权限 | 按钮级权限 |

```
路由守卫 → 控制用户能访问哪些页面
指令 → 控制用户能看到哪些按钮
```

---

### 9. TS 类型解析

```typescript
Directive<HTMLElement, string | string[]>
       ↑
       泛型参数
       第一个：el 的类型
       第二个：binding.value 的类型
```

**完整泛型签名：**
```typescript
Directive<
  HTMLElement,           // el 类型
  string | string[],     // binding.value 类型
  unknown,               // binding.arg 类型
  unknown                // modifiers 类型
>
```

---

### 10. 执行流程图

```
按钮渲染到页面
    ↓
v-permission="'user:delete'" 触发
    ↓
mounted(el, binding) 执行
    ↓
├─ value = 'user:delete'
├─ userStore.permissions = ['user:add', 'user:edit']
├─ !'*' 权限
├─ typeof 'string' → true
└─ permissions.includes('user:delete') → false
    ↓
无权限 → removeChild(el) → 按钮不显示
```

---

需要继续了解 **路由配置** 吗？