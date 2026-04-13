 **Webpack + html-webpack-plugin** 里**最经典的注入全局配置写法**，我给你用**最简单、最直白**的方式讲透，你一看就懂！

# 代码原文
```html
<script>
  window.APP_CONFIG_DATA = <%= htmlWebpackPlugin.options.initCfg %>
</script>
```

# 逐行解释（超级通俗）

## 1. `window.APP_CONFIG_DATA`
- 在**浏览器全局对象 window 上**挂载一个变量
- 作用：让项目里**所有 JS 文件都能直接访问**这个配置
- 相当于：
  ```js
  window.APP_CONFIG_DATA = 某个配置对象
  ```

## 2. `<%= %>`
这是 **EJS 模板语法**
- Webpack 打包时会**自动替换**这里的内容
- 不是前端运行时执行，是**打包编译时注入**

## 3. `htmlWebpackPlugin.options.initCfg`
- `htmlWebpackPlugin`：Webpack 用来生成 HTML 的插件
- `options.initCfg`：**你在 webpack.config.js 里传给插件的自定义配置**

---

# 整段代码的真实作用
## **打包时，把 Webpack 配置里的 initCfg 对象，直接注入到前端全局变量 window.APP_CONFIG_DATA 里。**

大白话：
**前端页面一打开，就能直接拿到后端/构建时传过来的配置！**

---

# 真实运行效果
假如你在 webpack.config.js 里写：
```js
new HtmlWebpackPlugin({
  template: 'index.html',
  initCfg: {
    env: 'prod',
    baseUrl: 'https://api.xxx.com',
    version: '1.0.0'
  }
})
```

那么打包后，前端页面会变成：
```html
<script>
  window.APP_CONFIG_DATA = {"env":"prod","baseUrl":"https://api.xxx.com","version":"1.0.0"}
</script>
```

---

# 前端怎么用？
任何 JS 文件里直接用：
```js
console.log(window.APP_CONFIG_DATA.env) // prod
console.log(window.APP_CONFIG_DATA.baseUrl) // https://api.xxx.com
```

---

# 总结（一句话记住）
## **<%= htmlWebpackPlugin.options.initCfg %>
= 打包时把构建配置注入到前端全局变量。**

---

如果你愿意，我可以帮你看看：
**这个 APP_CONFIG_DATA 到底包含了什么配置，项目为什么要这么写？**