# PostCSS
一句话：**CSS 界的 Babel**，用 JS 插件来**编译、增强、兼容、优化**你的 CSS。
它本身不做任何事，全靠插件生态。

---

## 核心定位
- 不是预处理器（不像 Less/Sass 提供嵌套、变量）
- 是一个**CSS 转换工具**：解析 CSS → 交给插件处理 → 生成新 CSS
- 作用：**兼容性、语法降级、代码优化、自动补全、语法扩展**

---

## 最常用的插件（必背）
### 1. autoprefixer（最常用）
自动加浏览器前缀：`-webkit-`、`-moz-` 等
```css
/* 写的时候 */
.box { display: flex; }

/* 编译后 */
.box {
  display: -webkit-box;
  display: -webkit-flex;
  display: -ms-flexbox;
  display: flex;
}
```

### 2. postcss-preset-env
让你用**未来 CSS 语法**，自动降级兼容现代浏览器
- 嵌套
- 自定义属性
- 颜色函数等

### 3. postcss-nested
让普通 CSS 支持嵌套（类似 Sass）
```css
.box {
  &:hover { color: red; }
}
```

### 4. cssnano
压缩、优化 CSS，去掉空格、重复样式、简化代码

### 5. postcss-px-to-viewport
移动端常用：px 自动转 vw/vh

### 6. stylelint
CSS 代码检查、规范代码风格

---

## 工作流位置
```
Less/Sass
   ↓
PostCSS（autoprefixer、降级、压缩）
   ↓
最终 CSS
```

所以现在项目结构基本都是：
> **预处理器（语法糖） + PostCSS（工程化/兼容）**

---

## 与 Sass/Less、CSS Modules、CSS-in-JS 的区别
- **Sass/Less**：扩展 CSS 语法（变量、嵌套、mixin）
- **PostCSS**：处理 CSS 兼容性、优化、降级
- **CSS Modules**：局部作用域、防冲突
- **CSS-in-JS**：JS 里写样式，强动态

一句话区分：
- 想写更爽的 CSS → Sass/Less
- 想让 CSS 更兼容、更现代 → PostCSS
- 想防命名冲突 → CSS Modules
- 想动态样式、主题 → CSS-in-JS

---

## 面试极简总结
PostCSS 是 CSS 编译工具，通过插件实现：
- 自动加前缀（autoprefixer）
- 兼容未来 CSS 语法
- 压缩、优化 CSS
- 移动端 px 转 vw 等工程化需求
常和 Less/Sass 配合使用，是现代前端工程标配。

需要我帮你整理**这一套（Sass/Less + CSS Modules + CSS-in-JS + PostCSS）的面试背诵版总结**吗？