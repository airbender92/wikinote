## 深入理解 declare module

### 问题根源

TypeScript 只能理解标准 JS/TS 语法：

```
.ts 文件    → TypeScript 原生认识 ✅
.vue 文件   → TypeScript 完全不认识 ❌
```

`.vue` 文件是 Vue 框架自定义的格式，包含：
- `<template>` HTML 模板
- `<script>` JavaScript/TypeScript
- `<style>` CSS

这些内容对 TS 来说都是"乱码"。

### declare module 的作用

```typescript
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<object, object, unknown>
  export default component
}
```

这段代码的意思是：

```
当遇到 import xxx from '*.vue' 时：
  ↓
TS 不知道 .vue 是什么
  ↓
TS 查找 .d.ts 声明文件
  ↓
找到 declare module '*.vue'
  ↓
TS 理解：.vue 文件导出的是一个 Vue 组件
  ↓
给这个导入加上 DefineComponent<...> 类型
```

### 实际效果对比

**没有 declare 时：**
```typescript
import App from './App.vue'

// TS 报错：
// Cannot find module './App.vue' or its corresponding type declarations.
```

**有 declare 后：**
```typescript
import App from './App.vue'

// TS 知道：App 是一个 Vue 组件
//            ↓
//            有类型提示 ✅
//            不报错 ✅
```

### declare module 是什么语法？

`declare` 是 TypeScript 的**声明语法**，用于告诉 TS"某个东西存在"。

| 语法 | 用途 |
|------|------|
| `declare const` | 声明全局变量 |
| `declare function` | 声明全局函数 |
| `declare module` | 声明模块类型 |

### 通配符 * 的含义

```typescript
declare module '*.vue'  // * 匹配任意文件名
```

所以以下导入都会被匹配：
- `'./App.vue'`
- `'./views/Login.vue'`
- `'@/components/Button.vue'`

### 运行时谁来处理 .vue？

**TypeScript 只负责类型检查**，不负责解析 `.vue` 文件内容。

真正解析 `.vue` 的是 **Vite**：
```
浏览器加载 App.vue
    ↓
Vite 的 vue 插件拦截
    ↓
解析 template/script/style
    ↓
返回可执行的 JS 代码
```

### 完整流程图

```
开发时：
  编写 App.vue
      ↓
  import App from './App.vue'
      ↓
  ┌─────────────────────────────┐
  │ TypeScript (类型检查)         │
  │ 读取 env.d.ts               │
  │ 知道 .vue = Vue 组件         │
  │ 提供类型提示                 │
  └─────────────────────────────┘
      ↓
  ┌─────────────────────────────┐
  │ Vite (实际解析)              │
  │ vue 插件解析 .vue 文件        │
  │ 转换为 JS 代码               │
  │ 返回给浏览器                 │
  └─────────────────────────────┘
```

### 总结

| 谁 | 做什么 |
|----|--------|
| **TypeScript** | 只做类型检查，依赖 `.d.ts` 知道 .vue 的类型 |
| **Vite** | 实际解析 .vue 文件，转换为浏览器可执行代码 |
| **declare module** | 桥接两者，告诉 TS 如何理解 .vue |

---

## 为什么需要 `export default`

### 核心原因

因为你用的是 **默认导入** 语法：

```typescript
import App from './App.vue'  // 默认导入
```

TypeScript 必须知道这个导入的**类型**，而声明文件必须**匹配导入语法**。

### 对比两种导入方式

| 导入语法 | 声明要求 |
|---------|---------|
| `import App from './App.vue'` | `export default` |
| `import { App } from './App.vue'` | `export { App }` |

### 如果不用 export default

```typescript
// 声明文件 - 错误写法
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<object, object, unknown>
  // 没有 export default
}
```

```typescript
// 使用时
import App from './App.vue'  // ❌ 报错！
// TS 提示：模块没有默认导出
```

### 加上 export default 后

```typescript
// 声明文件 - 正确写法
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<object, object, unknown>
  export default component  // ✅ 添加默认导出
}
```

```typescript
// 使用时
import App from './App.vue'  // ✅ 正常
```

### 为什么 Vue 组件用默认导出？

因为 **每个 .vue 文件只导出一个组件**：

```vue
<!-- App.vue -->
<script setup>
const App = { ... }  // 定义了一个组件
</script>
```

一个文件 = 一个组件 → 自然用默认导出。

### 如果你想用命名导入

```typescript
// 如果 Vue 这样写：
export { component }

// 那使用方必须这样用：
import { component } from './App.vue'
```

但 Vue 的设计是每个文件一个默认导出，所以声明文件也对应写 `export default`。

---

### 总结

| 语法 | 作用 |
|------|------|
| `declare module '*.vue'` | 声明 .vue 文件的类型 |
| `const component: DefineComponent<...>` | 定义组件的类型 |
| `export default component` | 匹配 `import App from './App.vue'` 的语法 |

---

需要继续了解 **路由配置** 吗？