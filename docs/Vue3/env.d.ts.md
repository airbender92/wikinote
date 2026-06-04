## env.d.ts 解读

```typescript
/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<object, object, unknown>
  export default component
}
```

### 两部分解析

### 1. `/// <reference types="vite/client" />`

**三斜线引用**，告诉 TypeScript 引入 Vite 的类型声明。

| 类型 | 提供的声明 |
|------|-----------|
| `import.meta.env` | 环境变量 `VITE_*` |
| `import.meta.glob` | 动态导入 glob |
| `import.meta.hot` | HMR 热更新 API |

**效果：**
```typescript
// 使用环境变量时不会报错
const apiUrl = import.meta.env.VITE_API_BASE_URL
```

### 2. `declare module '*.vue'`

声明 **Vue 单文件组件**的类型。

| 声明内容 | 含义 |
|---------|------|
| `import type { DefineComponent }` | 引入 Vue 组件类型 |
| `DefineComponent<object, object, unknown>` | 泛型参数：props、emits、setup 返回值 |
| `export default component` | 默认导出为 Vue 组件 |

**效果：**
```typescript
// 导入 .vue 文件时有类型提示
import App from './App.vue'
//         ↑ 类型为 DefineComponent<...>
```

### 为什么需要 declare？

`.vue` 文件不是标准 JS/TS，TypeScript 原生不认识它。声明文件告诉 TS："以这种类型来理解 .vue 文件"。

### 文件命名规范

`env.d.ts` 不是固定名字，可以叫任意名字（如 `vite-env.d.ts`），只要在 tsconfig.json 的 `include` 中声明即可。

---

### 总结

| 行 | 作用 |
|----|------|
| 第 1 行 | 引入 Vite 类型（环境变量等） |
| 第 3-7 行 | 声明 .vue 文件的类型 |

---

配置层全部解读完成。接下来进入 **核心业务层**：

- **路由配置** — 路由表 + 守卫
- **状态管理** — Pinia store
- **请求封装** — Axios 拦截器