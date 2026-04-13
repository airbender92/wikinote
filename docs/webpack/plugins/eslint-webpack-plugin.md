# eslint-webpack-plugin 完整教程
`eslint-webpack-plugin` 是把 **ESLint 代码检查集成到 Webpack 构建流程** 的官方插件，让你在开发/打包时自动检查代码语法、风格、错误，提前发现问题，避免上线后报错。

## 一、核心作用
- 在 Webpack 编译时**实时检查 JS/JSX/TS/TSX 代码**
- 控制台直接显示错误/警告，不用单独跑 `eslint` 命令
- 可配置：**检查报错就阻止打包**，强制规范代码
- 配合 React/Vue/TS 完美使用

---

## 二、安装
必须同时安装：`eslint` + `eslint-webpack-plugin`
```bash
npm install -D eslint eslint-webpack-plugin
# 或
yarn add -D eslint eslint-webpack-plugin
# 或
pnpm add -D eslint eslint-webpack-plugin
```

---

## 三、最简可用配置（直接复制）
```javascript
// webpack.config.js
const ESLintPlugin = require('eslint-webpack-plugin');

module.exports = {
  // ...其他配置

  plugins: [
    new ESLintPlugin({
      extensions: ['js', 'jsx', 'ts', 'tsx'], // 要检查的文件
      exclude: 'node_modules', // 排除不检查
      fix: false, // 是否自动修复（建议 false）
      emitError: true, // 显示错误
      emitWarning: true, // 显示警告
    }),
  ],
};
```

---

## 四、完整推荐配置（开发+生产）
```javascript
const ESLintPlugin = require('eslint-webpack-plugin');
const isDev = process.env.NODE_ENV === 'development';

module.exports = {
  plugins: [
    new ESLintPlugin({
      extensions: ['js', 'jsx', 'ts', 'tsx'],
      exclude: ['node_modules', 'dist'],
      fix: false, // 不要自动改代码，避免意外
      cache: true, // 缓存，加快检查速度
      cwd: __dirname, // 根目录
      // 生产环境：报错就打包失败
      failOnError: !isDev,
      // 开发环境：只提示，不打断编译
      failOnWarning: false,
      // 优雅输出格式
      formatter: 'stylish',
    }),
  ],
};
```

---

## 五、关键配置说明
| 配置 | 作用 | 推荐值 |
|---|----|----|
| `extensions` | 检查哪些文件 | `['js','jsx','ts','tsx']` |
| `exclude` | 排除目录 | `node_modules, dist` |
| `fix` | 自动修复代码 | `false`（不安全） |
| `cache` | 缓存加速 | `true` |
| `failOnError` | 代码错误 → 打包失败（生产必开） | `true` |
| `emitWarning` | 控制台显示警告 | `true` |
| `formatter` | 输出格式 | `stylish` |

---

## 六、必须先初始化 ESLint
插件只是**集成**，你必须先有 `.eslintrc.json` 规则文件：

```bash
npx eslint --init
```

跟着提示选择：
- How would you like to use ESLint? → **To check syntax, find problems, and enforce code style**
- What type of modules does your project use? → ES modules
- Which framework? → **React**
- TypeScript? → Yes/No
- 最后生成配置文件

---

## 七、和 React 项目一起使用
如果你用了 **React + React Refresh**，最终插件组合：
```javascript
const ReactRefreshWebpackPlugin = require('@pmmmwh/react-refresh-webpack-plugin');
const ESLintPlugin = require('eslint-webpack-plugin');
const isDev = process.env.NODE_ENV === 'development';

module.exports = {
  plugins: [
    new ESLintPlugin({ /* 配置 */ }),
    isDev && new ReactRefreshWebpackPlugin(),
  ].filter(Boolean),
};
```

---

## 八、常见问题
### 1. 打包时报错但代码没问题？
- 检查 `.eslintrc` 规则是否太严格
- 临时关闭：`failOnError: false`

### 2. 检查速度慢？
开启 `cache: true`，并排除 `node_modules`。

### 3. 不想检查某些文件？
在项目根目录新建 `.eslintignore`：
```
node_modules
dist
build
*.config.js
```

---

### 总结
- `eslint-webpack-plugin` = Webpack + ESLint 代码检查
- **开发提示、生产报错拦截**，保证代码质量
- 配置简单、直接复制即可用
- 必须配合 `.eslintrc` 规则文件使用

需要我把 **ESLint + React Refresh + Optimization** 全部整合，给你一份**最终完整版 Webpack 配置**吗？