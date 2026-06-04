## tailwind.config.js 解读

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#409EFF',
        success: '#67C23A',
        warning: '#E6A23C',
        danger: '#F56C6C',
      },
    },
  },
  plugins: [],
}
```

### 配置解析

| 配置 | 含义 |
|------|------|
| `content` | **内容扫描路径**，Tailwind 会在这些文件中查找类名，只生成用到的 CSS |
| `theme.extend` | **扩展主题**，在默认主题上添加自定义颜色（不覆盖默认值） |
| `theme.extend.colors` | **自定义颜色**，与 Element Plus 主题色保持一致 |
| `plugins` | **插件列表**，可扩展功能（如表单、多列等） |

### 颜色主题

项目自定义了 4 个企业级颜色：

| 颜色名 | 色值 | 用途 |
|--------|------|------|
| `primary` | #409EFF | 主色调（蓝） |
| `success` | #67C23A | 成功状态（绿） |
| `warning` | #E6A23C | 警告状态（橙） |
| `danger` | #F56C6C | 危险状态（红） |

### 使用方式

```vue
<template>
  <!-- 使用 Tailwind 类 -->
  <button class="bg-primary text-white px-4 py-2 rounded">
    主要按钮
  </button>
  
  <!-- 使用自定义颜色 -->
  <div class="bg-success text-white">
    成功
  </div>
</template>
```

### 与 SCSS 的关系

| 方案 | 用途 | 示例 |
|------|------|------|
| **Tailwind** | 快速布局、间距、响应式 | `class="flex justify-between p-4"` |
| **SCSS** | 复杂组件样式、变量复用 | `color: $primary-color` |

两者互补：Tailwind 处理通用布局，SCSS 处理组件细节。

---

### 为什么 content 路径要包含 index.html？

因为 `index.html` 中可能写了内联样式或类名，Tailwind 需要扫描它来生成对应的 CSS。

---

需要继续了解 **PostCSS 配置** 还是 **路由配置**？