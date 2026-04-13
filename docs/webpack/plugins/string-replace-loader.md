**`string-replace-loader`** 是一个 Webpack Loader，用于在**构建打包时**对文件内容进行**文本/正则替换**，适合动态修改代码、注入变量、删除调试语句等场景。

---

### 一、安装
```bash
npm install -D string-replace-loader
# 或
yarn add -D string-replace-loader
# 或
pnpm add -D string-replace-loader
```

### 二、核心配置（3种常用写法）

#### 1. 基础：纯文本替换
```javascript
// webpack.config.js
module.exports = {
  module: {
    rules: [
      {
        test: /\.js$/, // 匹配文件
        loader: 'string-replace-loader',
        options: {
          search: 'API_URL_PLACEHOLDER', // 要替换的文本
          replace: 'https://api.prod.com', // 替换成
          flags: 'g' // 全局匹配（必须加）
        }
      }
    ]
  }
};
```

#### 2. 进阶：正则替换（最常用）
```javascript
{
  test: /\.(js|ts|jsx|tsx)$/,
  loader: 'string-replace-loader',
  options: {
    // 正则：匹配 console.log/info/warn/error
    search: /console\.(log|info|warn|error)\(.*?\);?/g,
    replace: '', // 替换为空 → 删除日志
    // flags: 'g' 已包含在正则内，可省略
  }
}
```

#### 3. 高级：函数动态替换
```javascript
{
  test: /\.js$/,
  loader: 'string-replace-loader',
  options: {
    search: /__VERSION__: '(\d+\.\d+\.\d+)'/g,
    // match: 匹配到的整个字符串
    // p1: 第一个分组 (版本号)
    replace: (match, p1) => {
      const newVersion = p1.replace(/(\d+)$/, n => +n + 1); // 自增版本号
      return `__VERSION__: '${newVersion}'`;
    },
    strict: true // 严格模式：没匹配到就报错
  }
}
```

#### 4. 批量多规则替换
```javascript
{
  test: /\.js$/,
  loader: 'string-replace-loader',
  options: {
    multiple: [
      { search: /foo/g, replace: 'bar' },
      { search: /DEBUG/g, replace: 'false' },
      { search: /@deprecated/g, replace: '' }
    ]
  }
}
```

### 三、完整参数说明
| 参数 | 类型 | 说明 |
|---|---|---|
| `search` | `string|RegExp` | 要查找的内容（文本或正则） |
| `replace` | `string|Function` | 替换文本或替换函数 |
| `flags` | `string` | 正则标志（`g`全局、`i`忽略大小写） |
| `multiple` | `array` | 批量替换规则数组 |
| `strict` | `boolean` | 严格模式：未匹配则抛出错误 |
| `include`/`exclude` | `string|RegExp` | 包含/排除文件路径 |

### 四、典型实战场景

**场景1：构建时注入环境变量（替代DefinePlugin）**
```javascript
// 代码：const API = process.env.API_URL;
{
  test: /\.js$/,
  loader: 'string-replace-loader',
  options: {
    search: 'process.env.API_URL',
    replace: JSON.stringify(process.env.API_URL || 'http://localhost:3000')
  }
}
```

**场景2：开发/生产环境区分**
```javascript
const isProd = process.env.NODE_ENV === 'production';

{
  test: /\.js$/,
  loader: 'string-replace-loader',
  options: {
    multiple: [
      // 生产环境删除日志
      isProd && { search: /console\.log\(.*?\);?/g, replace: '' },
      // 开发环境替换API
      !isProd && { search: 'API_HOST', replace: 'http://dev.api' }
    ].filter(Boolean)
  }
}
```

**场景3：替换文件中的版本号/时间戳**
```javascript
{
  test: /version\.js$/,
  loader: 'string-replace-loader',
  options: {
    search: /BUILD_TIME/g,
    replace: JSON.stringify(new Date().toISOString())
  }
}
```

### 五、Loader顺序（重要）
**替换应在编译前执行**：
```javascript
use: [
  'babel-loader', // 后执行：转译
  'string-replace-loader' // 先执行：替换
]
```

### 六、与 DefinePlugin 区别
- **`string-replace-loader`**：**Loader**，作用于**文件内容字符串**，适合任意文本替换、删除代码。
- **`DefinePlugin`**：**Plugin**，作用于**语法树**，适合定义全局常量、环境变量。

### 七、常见问题
- **正则不生效**：必须加 `flags: 'g'` 或正则内 `/.../g`。
- **特殊字符转义**：`$ ^ * + . ? | ( ) [ ] { } \` 需加 `\` 转义。
- **替换不生效**：检查 `test` 匹配、`include/exclude`、Loader顺序。

---

### 总结
`string-replace-loader` 是**轻量、灵活**的构建时文本替换工具，适合：
- 环境变量注入
- 删除调试代码（`console`、`debugger`）
- 动态修改版本、路径、配置
- 批量文本替换

要不要我把这个 Loader 整合到你之前的 **React + Webpack 完整配置**中，并加上 **环境变量 + 日志删除** 的实战示例？