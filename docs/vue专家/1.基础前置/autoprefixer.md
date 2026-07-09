# Autoprefixer
一句话：**给 CSS 自动加浏览器私有前缀（-webkit-、-moz-、-ms-）的 PostCSS 插件，不用自己手写兼容。**

---

## 它是干嘛的？
很多新 CSS 属性在旧浏览器里需要加前缀才能生效，比如：
- `display: flex`
- `transform`
- `transition`
- `gradient`
- `animation`

Autoprefixer 会**根据你设置的浏览器范围**，自动补上需要的前缀，不需要你记、也不用你手写。

### 示例
你写：
```css
.box {
  display: flex;
  user-select: none;
}
```

编译后自动变成：
```css
.box {
  display: -webkit-box;
  display: -webkit-flex;
  display: -ms-flexbox;
  display: flex;
  -webkit-user-select: none;
     -moz-user-select: none;
      -ms-user-select: none;
          user-select: none;
}
```

---

## 安装
```bash
npm install autoprefixer -D
```

---

## 配合 PostCSS 配置（最常用）
在项目根目录 `postcss.config.js`：
```js
module.exports = {
  plugins: [
    require('autoprefixer')({
      // 配置要兼容的浏览器范围
      overrideBrowserslist: [
        '> 1%',                  // 市场份额 >1% 的浏览器
        'last 2 versions',       // 每个浏览器最后 2 个版本
        'not dead',              // 排除已停止维护的
        'iOS >= 9',
        'Android >= 5'
      ]
    })
  ]
}
```

---

## 也可以用 .browserslistrc（推荐）
根目录新建 `.browserslistrc`：
```
> 1%
last 2 versions
not dead
iOS >= 9
Android >= 5
```

然后 `postcss.config.js` 里可以简化：
```js
module.exports = {
  plugins: [
    require('autoprefixer')()
  ]
}
```
Autoprefixer 会自动读取 `.browserslistrc`。

---

## 关键特点
1. **智能**
   只加**需要的前缀**，新版本浏览器不需要的就不加，不会冗余。

2. **自动去重/清理**
   你不小心自己写了前缀，它会帮你整理、去重。

3. **和框架天然集成**
   - Vue CLI / Create React App / Vite **默认自带 Autoprefixer**
   - 大部分项目你根本不用装，直接写 CSS 就行

---

## 常见误区
- 不是越兼容越好，兼容太旧浏览器会导致 CSS 体积变大
- 现在移动端一般兼容到 iOS 9+ / Android 5+ 就足够
- 不需要自己记 `-webkit-` 之类，交给工具就行

---

## 极简总结（面试版）
Autoprefixer 是 PostCSS 生态最常用插件，**自动根据目标浏览器范围为 CSS 属性添加浏览器前缀**，解决兼容性问题，现代前端工程化标配。

如果你愿意，我可以把 **PostCSS + Autoprefixer + px转vw** 三合一完整配置直接给你复制即用。