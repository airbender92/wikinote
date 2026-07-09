

# Rollup.js 从入门到精通 · 完整学习路线

## 一、入门：Rollup 是什么？能干啥？
### 1.1 核心定位
- 下一代 **ES Module 打包工具**
- 主打：**快、小、Tree Shaking 极强**
- 适合：**库 / 组件 / SDK 打包**（Vue、React、VueUse 都用它）
- 对比 Webpack：
  - Webpack：大而全，适合**应用**
  - Rollup：轻量高效，适合**库**

### 1.2 核心概念
- **entry**：入口文件
- **output**：输出格式（ESM / CJS / UMD / IIFE）
- **plugins**：扩展功能（处理 TS、CSS、图片等）
- **Tree Shaking**：剔除未使用代码（只支持 ESM）

---

# 二、快速上手（5 分钟跑起来）
## 安装
```bash
npm init -y
npm install rollup --save-dev
```

## 最简单配置 `rollup.config.js`
```js
export default {
  input: 'src/index.js',
  output: {
    file: 'dist/bundle.js',
    format: 'es' // 可选 es | cjs | umd | iife
  }
}
```

## 运行
```bash
rollup -c
```

你就得到一个干净无冗余的打包文件。

---

# 三、进阶：常用插件（必须掌握）
## 1. 处理 CommonJS 模块
```bash
npm install @rollup/plugin-commonjs --save-dev
```

## 2. 处理 node_modules
```bash
npm install @rollup/plugin-node-resolve --save-dev
```

## 3. 替换环境变量
```bash
npm install @rollup/plugin-replace --save-dev
```

## 4. 压缩代码（Terser）
```bash
npm install @rollup/plugin-terser --save-dev
```

## 5. 处理 TypeScript
```bash
npm install @rollup/plugin-typescript --save-dev
```

## 6. 处理 JSON
```bash
npm install @rollup/plugin-json --save-dev
```

---

# 四、中阶：多格式同时打包（库开发必备）
同时输出：
- ESM（`es`）
- CommonJS（`cjs`）
- UMD（浏览器直接用）

```js
export default {
  input: 'src/index.ts',
  output: [
    { file: 'dist/index.esm.js', format: 'es' },
    { file: 'dist/index.cjs.js', format: 'cjs' },
    {
      file: 'dist/index.umd.js',
      format: 'umd',
      name: 'MyLibrary' // UMD 必须有全局变量名
    }
  ],
  plugins: [
    resolve(),
    commonjs(),
    typescript(),
    terser()
  ]
}
```

---

# 五、高阶：实战技巧（精通必备）
## 1. Tree Shaking 优化
- 只支持 **ESM**
- 代码必须是**纯函数、无副作用**
- package.json 加：
  ```json
  "sideEffects": false
  ```

## 2. 外部依赖（不打包进库）
```js
external: ['vue', 'react']
```

## 3. 代码分割（code splitting）
```js
output: {
  dir: 'dist',
  format: 'es',
  manualChunks: id => {
    if (id.includes('node_modules')) return 'vendor'
  }
}
```

## 4. 监听模式（开发用）
```bash
rollup -c -w
```

## 5. 处理 CSS / 样式
```bash
npm install rollup-plugin-styles --save-dev
```

## 6. 处理图片
```bash
npm install @rollup/plugin-image --save-dev
```

---

# 六、实战：完整企业级库打包配置
直接复制可用：

```js
import resolve from '@rollup/plugin-node-resolve'
import commonjs from '@rollup/plugin-commonjs'
import typescript from '@rollup/plugin-typescript'
import terser from '@rollup/plugin-terser'
import json from '@rollup/plugin-json'
import styles from 'rollup-plugin-styles'

export default {
  input: 'src/index.ts',
  external: ['vue'],
  output: [
    {
      file: 'dist/index.esm.js',
      format: 'es',
      sourcemap: true
    },
    {
      file: 'dist/index.cjs.js',
      format: 'cjs',
      sourcemap: true
    },
    {
      file: 'dist/index.umd.min.js',
      format: 'umd',
      name: 'MyUI',
      globals: { vue: 'Vue' },
      plugins: [terser()]
    }
  ],
  plugins: [
    resolve(),
    commonjs(),
    typescript({ tsconfig: './tsconfig.json' }),
    json(),
    styles({ inject: true, minimize: true })
  ]
}
```

---

# 七、精通：原理 & 工程化深度
1. **Rollup 打包流程**
   - 解析入口 → 构建依赖图 → 遍历模块 → Tree Shaking → 生成代码
2. **为什么 Tree Shaking 比 Webpack 强**
   - 原生 ESM 设计，无冗余兼容代码
3. **Rollup 插件机制**
   - 基于 AST 遍历
   - 钩子：`buildStart`、`resolveId`、`load`、`transform`、`generateBundle`
4. **与 Vite 的关系**
   - Vite 开发环境：esbuild
   - Vite 生产环境：**Rollup**
5. **最佳实践**
   - 库：Rollup
   - 应用：Webpack / Vite
   - 微内核、多产物、SDK 必选 Rollup

---

# 八、学习路径（最快精通路线）
1. 基础：安装、配置、多格式输出
2. 插件：resolve、commonjs、typescript、terser
3. 实战：写一个自己的 npm 库并打包发布
4. 进阶：code splitting、external、globals、sideEffects
5. 精通：插件开发、AST、Rollup 原理、Vite 集成

---

如果你想，我可以直接带你**一步步实战：从零搭建一个可发布到 npm 的 TypeScript 库 + Rollup 完整配置**，包教包会。