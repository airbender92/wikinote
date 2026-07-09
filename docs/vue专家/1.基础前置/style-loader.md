# style-loader & css-loader 核心讲解（Webpack 必考点）

一句话总结：
- **css-loader**：让 Webpack 能**读懂、解析 CSS 文件**，处理 `@import`、`url()` 等
- **style-loader**：把解析后的 CSS **以 <style> 标签插入到页面 DOM** 里

它们**必须配合使用**，缺一不可。

---

# 1. css-loader 干什么？
作用：**解析 CSS 语法，把 CSS 转成 Webpack 能识别的模块**

主要处理：
- 识别 `@import './other.css'`
- 识别 `url(./bg.png)` 图片/字体路径
- 配合 CSS Modules 时，**把类名转成对象**（`styles.btn`）

它**只负责解析，不负责插入页面**。

---

# 2. style-loader 干什么？
作用：**把 CSS 字符串创建成 <style> 标签，插到 HTML 的 head 里**

结果：
```html
<head>
  <style>
    .box { color: red; }
  </style>
</head>
```

特点：
- 开发环境极快（热更新快）
- 不会生成独立 `.css` 文件
- 生产环境一般不用它，改用 `mini-css-extract-plugin`

---

# 3. 最经典配置
```js
{
  test: /\.css$/,
  use: [
    'style-loader',   // 第二步：插入DOM
    'css-loader'      // 第一步：解析CSS
  ]
}
```

⚠️ **顺序非常重要：从右往左执行**
1. 先 `css-loader` 读 CSS
2. 再 `style-loader` 插入页面

---

# 4. 配合 less / sass / postcss
```js
{
  test: /\.less$/,
  use: [
    'style-loader',
    'css-loader',
    'postcss-loader',
    'less-loader'
  ]
}
```

执行顺序：
```
less-loader → postcss-loader → css-loader → style-loader
```

---

# 5. css-loader 开启 CSS Modules
```js
{
  loader: 'css-loader',
  options: {
    modules: true, // 开启 CSS Modules
    localIdentName: '[name]__[local]__[hash:5]'
  }
}
```

开启后才能：
```js
import styles from './index.css'
// styles.box → 哈希类名
```

---

# 6. 生产环境为什么不用 style-loader？
style-loader 是**运行时动态插入样式**：
- 会有**闪屏**
- 不利于缓存
- 无法单独压缩、分离 CSS 文件

所以生产环境用：
**mini-css-extract-plugin** 代替 style-loader
把 CSS 抽成独立的 `.css` 文件。

---

# 7. 极简面试背诵版
- **css-loader**：解析 CSS，处理 @import、url，支持 CSS Modules
- **style-loader**：把 CSS 转为 <style> 注入 DOM
- 顺序：use 数组 **从右到左执行**
- 开发环境用 style-loader，生产环境用 mini-css-extract-plugin

---

需要我给你整理一份 **style-loader + css-loader + less + postcss + 生产环境抽离CSS** 的完整可复制 Webpack 配置吗？