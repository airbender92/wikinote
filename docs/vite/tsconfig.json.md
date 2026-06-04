## tsconfig.json 完整解读

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",

    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,

    /* Path Alias */
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    },
    "types": ["vite/client", "element-plus/global"]
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue", "./env.d.ts"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### 编译目标

| 配置 | 值 | 含义 |
|------|-----|------|
| `target` | ES2020 | 编译到 ES2020 语法，兼容现代浏览器 |
| `useDefineForClassFields` | true | 使用 `defineProperty` 定义类字段，符合 ES 标准 |
| `module` | ESNext | 使用最新模块语法 |
| `lib` | ES2020, DOM, DOM.Iterable | 运行时环境支持 |

### Bundler Mode（Vite 专用）

| 配置 | 含义 |
|------|------|
| `moduleResolution: "bundler"` | TS 跟随 Vite 解析模块 |
| `allowImportingTsExtensions` | 允许 `import ... from './App.vue'` 带扩展名 |
| `resolveJsonModule` | 允许 `import data from './data.json'` |
| `isolatedModules` | 每个文件独立编译，Vite 快速 HMR 必需 |
| `noEmit` | 不生成 `.js` 文件，Vite 自己处理编译 |
| `jsx: "preserve"` | 保留 JSX，由 Vite 的 esbuild 处理 |

### 严格检查（Strict Linting）

| 配置 | 含义 |
|------|------|
| `strict: true` | 开启所有严格类型检查（相当于启用 8 个子选项） |
| `noUnusedLocals` | 禁止未使用的局部变量 |
| `noUnusedParameters` | 禁止未使用的函数参数 |
| `noFallthroughCasesInSwitch` | switch 必须有 break/return |

### 路径别名

```json
"baseUrl": ".",
"paths": {
  "@/*": ["src/*"]
}
```
配置后可以直接使用：
```typescript
import { useUserStore } from '@/store/modules/user'
// 相当于
import { useUserStore } from 'src/store/modules/user'
```

### 全局类型声明

```json
"types": ["vite/client", "element-plus/global"]
```
自动注入以下类型：
- `vite/client` — `import.meta.env` 环境变量
- `element-plus/global` — Element Plus 组件实例类型

### 包含范围

```json
"include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue", "./env.d.ts"]
```

### 项目引用

```json
"references": [{ "path": "./tsconfig.node.json" }]
```
引用 tsconfig.node.json，解析 vite.config.ts 的类型

---

### 与 tsconfig.node.json 对比

| 配置 | tsconfig.json（应用层） | tsconfig.node.json（Node 层） |
|------|------------------------|------------------------------|
| 目标文件 | src/ | vite.config.ts |
| composite | ❌ | ✅ |
| moduleResolution | bundler | bundler |
| 严格模式 | strict ✅ | ❌ |

---

需要继续了解 **路由配置** 还是 **状态管理**？