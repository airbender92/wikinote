这是 **unplugin-auto-import** 的完整中文精简使用指南，直接照着配就能用。

# unplugin-auto-import
**自动按需导入 API**，支持 Vite / Webpack / Rspack / Rollup / esbuild，自带 TypeScript 支持。

---

## 效果对比
### Vue
```ts
// 之前
import { computed, ref } from 'vue'
const count = ref(0)
const doubled = computed(() => count.value * 2)

// 之后（自动导入）
const count = ref(0)
const doubled = computed(() => count.value * 2)
```

### React
```tsx
// 之前
import { useState } from 'react'
export function Counter() {
  const [count, setCount] = useState(0)
  return <div>{ count }</div>
}

// 之后
export function Counter() {
  const [count, setCount] = useState(0)
  return <div>{ count }</div>
}
```

---

## 安装
```bash
npm i -D unplugin-auto-import
```

---

## 常用配置（Vite 示例）
```ts
// vite.config.ts
import AutoImport from 'unplugin-auto-import/vite'

export default defineConfig({
  plugins: [
    AutoImport({
      // 自动导入的库
      imports: [
        'vue',
        'vue-router',
        '@vueuse/core',
      ],

      // 自动导入本地目录下的方法
      dirs: [
        './composables/**',
        './hooks/**',
      ],

      // 自动生成 .d.ts 类型声明
      dts: true,

      // 自动生成 eslint 全局变量配置
      eslintrc: {
        enabled: true,
      },

      // Vue 模板内也自动导入
      vueTemplate: true,
    }),
  ],
})
```

---

## 核心配置项
- **`imports`**：预设自动导入的库，如 `vue`、`vue-router`、`react` 等
- **`dirs`**：自动扫描并导入指定目录下的所有导出
- **`dts`**：生成 `auto-imports.d.ts` 让 TS 识别类型
- **`eslintrc`**：生成 ESLint 全局变量配置，解决 `no-undef` 报错
- **`vueTemplate`**：在 Vue 模板中也启用自动导入
- **`resolvers`**：配合 UI 库（Element Plus、Naive UI 等）自动导入组件

---

## ESLint 配置
1. 开启 `eslintrc.enabled: true`
2. 在 `.eslintrc.js` 中引入生成的文件：
```js
module.exports = {
  extends: [
    './.eslintrc-auto-import.json',
  ],
}
```

---

## TypeScript
确保 `tsconfig.json` 包含自动生成的 `.d.ts`：
```json
{
  "include": ["auto-imports.d.ts"]
}
```

---

## 支持的构建工具
- Vite
- Rollup / Rolldown
- Webpack / Rspack
- esbuild
- Nuxt
- Quasar
- Astro

---

## 与其他工具关系
- **unimport**：底层核心库，本插件基于它封装
- **vue-global-api**：前身，本插件更通用、可 Tree-shaking、支持更多框架

需要我给你一份**Vue3 + Element Plus 完整版可直接复制的配置**吗？