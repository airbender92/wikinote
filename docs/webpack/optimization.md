# Webpack Optimization 完整指南
`optimization` 是 Webpack 4+ 核心配置项，**专门用于打包优化**，控制代码分割、压缩、tree shaking、模块复用等，是生产环境打包必配的优化核心。

它内置了默认优化策略，你可以手动配置强化效果，大幅减小打包体积、提升加载速度。

---

## 一、核心作用
1. **代码分割（Code Splitting）**：拆分大 bundle，按需加载
2. **Tree Shaking**：剔除未使用的代码（仅 ES6 模块）
3. **JS/CSS 压缩**：生产环境自动开启
4. **运行时/公共代码抽离**：避免重复打包
5. **模块缓存优化**：让浏览器长期缓存不变的代码

---

## 二、最常用完整配置（可直接复制使用）
```javascript
// webpack.config.js
module.exports = {
  // ...其他配置

  // 优化核心配置
  optimization: {
    // 1. 开发环境不压缩，生产环境自动压缩（默认）
    minimize: true,

    // 2. JS 压缩器（生产默认使用 terser-webpack-plugin）
    minimizer: [
      // 自定义压缩配置（移除注释、压缩代码等）
      require('terser-webpack-plugin')({
        terserOptions: {
          compress: {
            drop_console: true, // 生产环境删除所有 console
          },
          format: {
            comments: false, // 删除注释
          },
        },
        extractComments: false,
      }),
    ],

    // 3. 开启 Tree Shaking（剔除未使用代码，生产默认开启）
    usedExports: true,

    // 4. 代码分割（最关键！）
    splitChunks: {
      chunks: 'all', // 对所有代码（同步+异步）进行分割
      cacheGroups: {
        // 抽离第三方库（vue/react/lodash等）
        vendors: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          priority: -10,
        },
        // 抽离公共业务代码
        common: {
          name: 'common',
          minChunks: 2, // 被引用2次以上就抽离
          priority: -20,
          reuseExistingChunk: true,
        },
      },
    },

    // 5. 抽离运行时代码（优化缓存）
    runtimeChunk: 'single',

    // 6. 模块ID 稳定化（避免缓存失效）
    moduleIds: 'deterministic',
  },
};
```

---

## 三、核心配置详解

### 1. `minimize` & `minimizer`
- `minimize: true`：**生产环境默认开启 JS 压缩**
- `minimizer`：自定义压缩规则
  - 删除 `console`
  - 删除注释
  - 混淆变量名

### 2. `usedExports: true` —— Tree Shaking
**Tree Shaking = 摇树优化**
- 只对 **ES6 模块（import/export）** 生效
- 自动删除**未被使用的代码**
- 生产环境默认开启

### 3. `splitChunks` —— 代码分割（最重要）
默认只分割**异步代码**，配置 `chunks: 'all'` 分割所有代码：
- `vendors`：把 `node_modules` 里的库单独打包（长期缓存）
- `common`：把多个页面共用的业务代码抽离
好处：
- 浏览器缓存第三方库，不用每次重新下载
- 首屏加载更快

### 4. `runtimeChunk: 'single'`
抽离**webpack 运行时代码**，避免业务代码修改导致第三方库缓存失效。

### 5. `moduleIds: 'deterministic'`
生成稳定的模块 ID，**优化长效缓存**，生产环境必配。

---

## 四、默认优化规则（不用配置也生效）
Webpack 在 `mode: production` 下**自动开启**：
1. JS 压缩
2. Tree Shaking
3. 作用域提升（Scope Hoisting）
4. 代码精简优化

---

## 五、最佳实践（生产环境必用）
```javascript
optimization: {
  minimize: true,
  usedExports: true,
  splitChunks: {
    chunks: 'all',
  },
  runtimeChunk: true,
  moduleIds: 'deterministic',
}
```

---

### 总结
1. `optimization` 是 Webpack 打包优化**核心配置**
2. `splitChunks` 拆分代码、`runtimeChunk` 优化缓存、`usedExports` 开启 Tree Shaking
3. 生产环境自动压缩，可自定义删除 `console`
4. 上面的完整配置**直接复制即可用于项目**

需要我帮你根据你的项目（Vue/React/原生）生成**专属优化配置**吗？