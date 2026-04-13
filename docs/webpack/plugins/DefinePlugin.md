**`DefinePlugin`** 是 Webpack 内置的核心插件，用于在**编译时**将代码中的全局变量替换为指定的值或表达式，主要用于**环境区分、全局常量注入、代码优化**。

### 一、核心作用
- **编译时替换**：在构建阶段直接替换代码中的变量（非运行时）
- **全局常量**：定义后在所有模块中可直接使用，无需导入
- **环境配置**：最常用于设置 `process.env.NODE_ENV`，区分开发/生产环境
- **死代码剔除**：替换后，压缩工具（如 Terser）可移除永远为 `false` 的分支

### 二、基本用法（webpack.config.js）
```javascript
const webpack = require('webpack');

module.exports = {
  plugins: [
    new webpack.DefinePlugin({
      // 字符串值必须用 JSON.stringify 或 双引号包单引号
      'process.env.NODE_ENV': JSON.stringify('production'),
      VERSION: JSON.stringify('1.0.0'),
      // 布尔/数字会自动转字符串
      IS_DEV: false,
      // 字符串会被当作代码片段执行
      TWO: '1+1',
      // 定义对象
      'process.env.API': JSON.stringify('https://api.example.com'),
    }),
  ],
};
```

### 三、关键规则（易踩坑）
1. **字符串值必须序列化**
   - 错误：`VERSION: '1.0.0'` → 编译后变成 `VERSION = 1.0.0`（语法错误）
   - 正确：`VERSION: JSON.stringify('1.0.0')` → 编译后 `VERSION = '1.0.0'`

2. **非字符串自动转字符串**
   - `IS_DEV: true` → 编译为 `true`（布尔）
   - `TWO: '1+1'` → 编译为 `1+1`（表达式）

3. **支持嵌套键**
   - `'process.env.API': ...` → 代码中用 `process.env.API`

### 四、典型场景
#### 1. 环境分支（生产移除日志）
```javascript
// 源码
if (process.env.NODE_ENV === 'development') {
  console.log('Debug log');
}

// 编译后（production）
if (false) {
  console.log('Debug log');
}
// Terser 会直接删除这段代码
```

#### 2. 全局版本/配置
```javascript
console.log(`App v${VERSION}`);
fetch(`${process.env.API}/users`);
```

#### 3. 替代全局变量（如 SSR 安全）
```javascript
// 浏览器环境定义
new webpack.DefinePlugin({
  'typeof window': JSON.stringify('object'),
});
```

### 五、与 `EnvironmentPlugin` 的区别
- **`DefinePlugin`**：灵活，可定义任意常量，需手动 `JSON.stringify`
- **`EnvironmentPlugin`**：简化版，仅用于 `process.env`，自动处理字符串化
  ```javascript
  // 等价于 DefinePlugin({ 'process.env.NODE_ENV': ... })
  new webpack.EnvironmentPlugin(['NODE_ENV', 'API_URL'])
  ```

### 六、常见误区
- ❌ 不要直接写字符串：`VERSION: '1.0.0'` → 语法错误
- ❌ 不要在运行时修改：编译后是常量，无法动态更新
- ✅ 必须用 `JSON.stringify` 包裹字符串值

### 七、总结
`DefinePlugin` 是 Webpack 最常用的插件之一，核心是**编译时全局常量替换**，用于环境控制、配置注入、代码优化。**字符串必须序列化**是使用关键。

要不要我帮你写一个可直接复制的 **开发/生产双环境 DefinePlugin 配置模板**？