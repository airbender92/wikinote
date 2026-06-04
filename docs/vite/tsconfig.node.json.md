## tsconfig.node.json 解读

```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

### 逐项解析

| 配置 | 含义 |
|------|------|
| `composite: true` | **项目引用模式**，允许被 tsconfig.json 的 `references` 字段引用。这是项目分层的关键 |
| `skipLibCheck: true` | **跳过库类型检查**，不检查 `node_modules` 中第三方库的类型，加快编译速度 |
| `module: "ESNext"` | **模块系统**，使用最新的 ES 模块语法（import/export） |
| `moduleResolution: "bundler"` | **模块解析策略**，告诉 TS 按照 Vite/Webpack 等打包工具的方式解析模块 |
| `allowSyntheticDefaultImports: true` | **允许合成默认导入**，如 `import React from 'react'` 即使 React 没有默认导出 |
| `include: ["vite.config.ts"]` | **仅编译 vite.config.ts**，这是 Node.js 运行的文件，不走 Vue 应用的 TS 规则 |

### 为什么需要单独一个 tsconfig？

项目中有两个 tsconfig：

```
tsconfig.json          → 负责 src/ 下的 Vue/TS 代码
tsconfig.node.json     → 负责 vite.config.ts（Node.js 环境）
```

两者通过 `references` 关联：

```json
// tsconfig.json
{
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### moduleResolution 的区别

| 策略 | 解析方式 |
|------|----------|
| `bundler` | 支持 `@/` 路径别名、`exports` 字段，适合 Vite/Webpack |
| `node` | 传统 Node.js 解析方式，`node_modules` 查找 |
| `node16` | Node.js 16+ 的 ESM 解析 |

### 为什么 skipLibCheck 为 true？

`vite.config.ts` 依赖 Vite 自身的类型定义，这些类型可能不完整或包含循环引用，开启此选项可以避免类型检查报错。

---

需要继续了解 **tsconfig.json 主配置** 吗？