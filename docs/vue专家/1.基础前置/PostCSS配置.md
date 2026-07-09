下面给你一套**最实用、能直接复制到项目里**的 PostCSS 安装 + 配置教程，以 **Webpack + Vite** 两种最常见环境为例。

# 一、通用安装（不管 Webpack 还是 Vite 都先装这个）

```bash
npm install postcss autoprefixer postcss-preset-env -D
```
```bash
npm install postcss autoprefixer postcss-preset-env -D
```

常用插件解释：
- `postcss`：核心
- `autoprefixer`：自动加浏览器前缀
- `postcss-preset-env`：支持现代 CSS 语法并降级兼容

---

# 二、配置文件（项目根目录新建）
## 新建：`postcss.config.js`
```js
module.exports = {
  plugins: [
    // 使用现代 CSS 语法并自动兼容
    require('postcss-preset-env')({
      stage: 0, // 支持最新 CSS 特性
    }),
    // 自动加浏览器前缀
    require('autoprefixer')({
      overrideBrowserslist: [
        '> 1%',
        'last 2 versions',
        'not dead'
      ]
    }),
    // 如需压缩 CSS（生产环境）
    // require('cssnano')()
  ]
}
```

---

# 三、在 Webpack 项目中配置（vue-cli / cra 通用）
## 安装 loader

```bash
npm install css-loader postcss-loader less-loader less -D
```
```bash
npm install css-loader postcss-loader less-loader less -D
```

## webpack.config.js 配置
```js
module.exports = {
  module: {
    rules: [
      {
        test: /\.less$/i,
        use: [
          'style-loader', // 或 mini-css-extract-plugin
          'css-loader',
          'postcss-loader', // 关键：自动读取 postcss.config.js
          'less-loader'
        ]
      }
    ]
  }
}
```

顺序很重要：
```
less-loader → postcss-loader → css-loader → style-loader
```

---

# 四、在 Vite 项目中配置（最简单）
**Vite 内置 PostCSS，不需要额外配置 loader！**

只需要：
1. 项目根目录创建 `postcss.config.js`（上面那段）
2. 正常写 `xxx.less` / `xxx.css`

Vite 会**自动识别并应用 PostCSS 插件**。

---

# 五、常用插件扩展（按需安装）
## 1. px 自动转 vw（移动端必备）

```bash
npm install postcss-px-to-viewport -D
```
```bash
npm install postcss-px-to-viewport -D
```

配置：
```js
require('postcss-px-to-viewport')({
  viewportWidth: 750,
  unitPrecision: 5,
  viewportUnit: 'vw',
  selectorBlackList: ['.ignore'],
  minPixelValue: 1,
  mediaQuery: false
})
```

## 2. CSS 压缩
```bash
npm install cssnano -D
```

```js
require('cssnano')()
```

---

# 六、完整流程总结（面试也能说）
1. 安装 `postcss` + 插件
2. 写 `postcss.config.js` 启用插件
3. Webpack 中加入 `postcss-loader`
4. Vite 自动集成，无需配置 loader
5. 最终效果：
   - 自动加前缀
   - 支持最新 CSS 语法
   - 降级兼容低版本浏览器
   - 可做 px → vw、压缩、代码检查等

---

# 七、一句话记住
**PostCSS = CSS 的编译工具，靠插件干活，和 Less/Sass 不冲突，是现代项目标配。**

需要我给你一份**可直接复制到项目的完整配置模板**吗？