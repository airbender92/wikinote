
`contentBase` 是 **Webpack 4** 及以前版本中 `devServer` 的配置项，用于告诉开发服务器从**哪个目录读取静态文件**（如图片、CSS、HTML）。在 **Webpack 5 / webpack-dev-server v4** 中已被 **`static`** 完全替代。

### 一、核心作用（Webpack 4）
**`contentBase` = 静态资源的“根目录”**
- 作用：指定 `webpack-dev-server` 服务器**对外提供静态文件的物理路径**。
- 区别：
    - `output.path`：打包文件**输出到硬盘**的位置。
    - `devServer.contentBase`：开发服务器**读取静态文件**的位置（内存中）。
- 典型场景：项目根目录有 `public/` 文件夹，存放 `favicon.ico`、`robots.txt` 等**不经 Webpack 打包**的文件。

### 二、Webpack 4 标准写法
```javascript
// Webpack 4 配置
const path = require('path');

module.exports = {
  // ...其他配置
  devServer: {
    // 告诉服务器：静态文件从项目根目录的 public 文件夹找
    contentBase: path.join(__dirname, 'public'), // ✅ 推荐绝对路径
    // 监听 contentBase 目录下的文件变化，变化则刷新页面
    watchContentBase: true,
    // 访问地址
    publicPath: '/',
    port: 3000,
    open: true
  }
};
```

### 三、Webpack 5 重大变更：`static` 替代 `contentBase`
从 **webpack-dev-server v4** 开始（配合 Webpack 5），**`contentBase` 被废弃（Deprecated）**，必须改用 `devServer.static`。

#### 1. 新写法（Webpack 5）
```javascript
// Webpack 5 最新写法
const path = require('path');

module.exports = {
  // ...其他配置
  devServer: {
    // 静态资源配置（替代旧的 contentBase）
    static: {
      // 核心：指定静态文件目录
      directory: path.join(__dirname, 'public'),
      // 访问路径（可选，默认 /）
      publicPath: '/',
      // 监听文件变化（默认 true）
      watch: true,
    },
    port: 3000,
    open: true
  }
};
```

#### 2. 升级对照表
| 功能 (Webpack 4) | 写法 (Webpack 4) | 写法 (Webpack 5) |
| :--- | :--- | :--- |
| **指定静态目录** | `contentBase: './public'` | `static: { directory: './public' }` |
| **监听静态文件** | `watchContentBase: true` | `static: { watch: true }` |
| **静态文件URL前缀** | `contentBasePublicPath: '/assets'` | `static: { publicPath: '/assets' }` |

### 三、`contentBase` / `static` 与 `publicPath` 的区别
**最容易混淆的两个概念：**
- **`static.directory` (原 contentBase)**：**服务器从哪读文件**。
  - 例：`directory: path.join(__dirname, 'public')`
  - 含义：访问 `http://localhost:3000/logo.png` 时，服务器去读 **`项目/public/logo.png`**。
- **`output.publicPath`**：**打包文件的URL前缀**。
  - 例：`publicPath: '/assets/'`
  - 含义：打包后的 JS/CSS 文件，在 HTML 里引用路径是 `/assets/main.js`。

### 四、常见问题
1. **报错：`options has an unknown property 'contentBase'`**
    - **原因**：使用了 Webpack 5，但配置还是 Webpack 4 的 `contentBase`。
    - **解决**：替换为 `static: { directory: ... }`。
2. **图片/字体 404 Not Found**
    - **原因**：静态文件（如 `src/assets/img.png`）没放在 `static` 指定的目录下。
    - **解决**：确保路径配置正确，或将资源放入 `public/` 目录。

### 总结
- **Webpack 4**：用 `devServer.contentBase` 指定静态文件目录。
- **Webpack 5**：**必须**用 `devServer.static.directory` 替代。
- **核心原则**：**不经 Webpack 打包**的静态资源（如 `index.html`、图片），都由 `static` 管理。

需要我帮你把项目中 **Webpack 4 的 `contentBase` 配置，升级为 Webpack 5 兼容的 `static` 写法**吗？