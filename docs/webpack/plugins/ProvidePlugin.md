# webpack.ProvidePlugin 详解
**webpack.ProvidePlugin** 是 webpack 内置插件，核心作用是**自动加载模块**，无需在每个文件中重复编写 `import/require`，大幅提升开发效率。

## 核心原理
当 webpack 编译时，若检测到代码中出现**配置的标识符**（如 `$`、`_`），会自动引入对应模块，并将模块导出值赋值给该标识符，实现“全局可用”。
- 仅在使用标识符时才会加载模块，避免冗余打包
- 作用范围覆盖所有编译模块，全局生效

## 基础用法
### 1. 引入插件
需先在配置文件中引入 webpack：
```js
const webpack = require('webpack');
```

### 2. 配置插件
在 `plugins` 数组中添加实例，键为标识符，值为模块名或 `[模块名, 导出属性]` 数组：
```js
module.exports = {
  // 其他配置...
  plugins: [
    new webpack.ProvidePlugin({
      // 键：标识符；值：模块名
      $: 'jquery',
      jQuery: 'jquery',
      // 加载 lodash 的 join 方法
      join: ['lodash', 'join'],
      // 加载 Vue 默认导出（ES 模块需指定 default）
      Vue: ['vue/dist/vue.esm.js', 'default'],
      // 加载 Node.js polyfill
      process: 'process/browser',
      Buffer: ['buffer', 'Buffer']
    })
  ]
};
```

### 3. 直接使用
配置后，代码中可直接使用标识符，无需导入：
```js
// 无需 import $ from 'jquery'
$('#app').text('Hello ProvidePlugin');

// 无需 import { join } from 'lodash'
join([1, 2, 3], '-'); // 1-2-3
```

## 常见场景示例
### 1. 加载 jQuery/Lodash
```js
new webpack.ProvidePlugin({
  $: 'jquery',
  jQuery: 'jquery',
  _: 'lodash',
  // 按需加载单个方法（优化打包体积）
  _map: ['lodash', 'map']
});
```

### 2. 加载自定义工具模块
```js
// 加载本地工具函数
new webpack.ProvidePlugin({
  utils: path.resolve(__dirname, 'src/utils/index.js')
});
```

### 3. 全局挂载到 window
```js
new webpack.ProvidePlugin({
  'window.$': 'jquery',
  'window._': 'lodash'
});
```

## 关键注意事项
1. **需先安装依赖**：插件仅负责自动引入，需确保模块已安装（如 `npm install jquery lodash`）
2. **与 ES 模块共存**：若项目同时存在 `import` 和插件提供的标识符，以显式 `import` 优先级更高
3. **React 17+ 无需配置**：React 17 引入新 JSX 转换，无需通过 `ProvidePlugin` 提供 React
4. **谨慎使用**：过度配置可能导致代码可读性下降、模块依赖不清晰，建议仅用于高频使用的第三方库
5. **Tree Shaking 限制**：插件注入的模块可能影响 Tree Shaking，需配合 `sideEffects` 等配置优化

## 与其他方案对比
| 方案 | 优点 | 缺点 |
|------|------|------|
| ProvidePlugin | 自动注入、无需重复导入 | 可能降低代码可读性、影响 Tree Shaking |
| 显式 import | 依赖清晰、可读性高 | 每个文件需手动导入、代码冗余 |
| externals | 适合外部 CDN 资源、减少打包体积 | 需额外配置 CDN 链接、无法按需加载 |

## 总结
**webpack.ProvidePlugin** 是简化模块导入的核心工具，尤其适合高频使用的第三方库（如 jQuery、Lodash）或本地工具模块。合理配置可减少代码冗余，提升开发效率，但需注意平衡可读性与打包性能。

需要我结合你的项目（比如 React + Ant Design 场景）提供可直接复制的完整配置吗？