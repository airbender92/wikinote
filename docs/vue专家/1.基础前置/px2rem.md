
我给你讲**最清晰、工程里最常用**的 rem ↔ px 转换逻辑，直接背、直接用。

# 一、核心公式
rem 是**相对于根元素 `<html>` 的 font-size** 来计算的。

默认浏览器：
`html { font-size: 16px; }`

所以：
```text
1rem = 16px
```

通用公式：
```text
px = rem × html的font-size
rem = px ÷ html的font-size
```

---

# 二、最常用的两种基准

## 1）默认基准：1rem = 16px
- 1rem = 16px
- 2rem = 32px
- 24px = 24 / 16 = 1.5rem
- 30px = 30 / 16 = 1.875rem
- px → rem：直接 ÷16

## 2）开发常用基准：1rem = 10px（好算）
手动设置：
```css
html { font-size: 10px; }
```

转换就变成：
- 12px = 1.2rem
- 16px = 1.6rem
- 20px = 2rem
- 30px = 3rem
- 40px = 4rem
- px → rem：直接 ÷10

**这是前端最常用、最好心算的方案。**

---

# 三、移动端常用：1rem = 100px（方便）
```css
html { font-size: 100px; }
```

- 12px = 0.12rem
- 14px = 0.14rem
- 16px = 0.16rem
- 24px = 0.24rem
- 36px = 0.36rem

直接**小数点左移两位**，口算无敌。

---

# 四、响应式 rem 适配（动态 html font-size）
为了让页面在不同手机上等比缩放，一般这样写（JS 版）：

```js
// 设计稿宽度 750px
// 希望 1rem = 100px（方便换算）
document.documentElement.style.fontSize = 
  document.documentElement.clientWidth / 7.5 + 'px'
```

在 375px 宽手机上：
```text
html font-size = 375 / 7.5 = 50px
1rem = 50px
```

设计稿 100px → 100 / 100 = 1rem → 实际 50px

---

# 五、快速换算表（直接背）
## 1rem = 16px（默认）
- 12px = 0.75rem
- 14px = 0.875rem
- 16px = 1rem
- 18px = 1.125rem
- 20px = 1.25rem
- 24px = 1.5rem
- 32px = 2rem

## 1rem = 10px（开发常用）
- 12px = 1.2rem
- 14px = 1.4rem
- 16px = 1.6rem
- 20px = 2rem
- 24px = 2.4rem
- 30px = 3rem

---

# 六、一句话总结
- **rem = px ÷ html的font-size**
- 想简单就设 `html{font-size:10px}`，直接 ÷10
- 移动端适配一般用**动态 html 字体**实现等比缩放

你要我给你写一个**完整可运行的 rem 响应式页面模板**吗？直接复制就能用。

**Less / Scss 里都会写一个函数（mixin）或方法，直接 `px2rem(16)` 就自动转 rem，不用自己算。**

我直接给你**最常用、项目里直接复制就能用**的版本，包含原理 + 完整代码。

---

# 一、先定一个基准（固定死）
通常移动端设计稿以 **750px** 为宽度，我们规定：
```
1rem = 100px
```
也就是：
- 100px → 1rem
- 12px → 0.12rem
- 14px → 0.14rem
- 16px → 0.16rem
- 24px → 0.24rem
- 30px → 0.30rem

公式：
```
rem = px / 100
```

---

# 二、Less 版 px → rem 方法
```less
// 定义转换函数
.px2rem(@px) {
  @rem: @px / 100rem;
}

// 使用
.box {
  width: 100px;
  height: 100px;
  font-size: .px2rem(14); // 直接调用
}
```

编译后：
```css
.box {
  width: 100px;
  height: 100px;
  font-size: 0.14rem;
}
```

更简洁的写法（推荐）：
```less
.px2rem(@px) {
  font-size: @px / 100rem;
}
```

---

# 三、Scss (Sass) 版 px → rem 方法
Scss 用 **function**，更标准：
```scss
// 定义函数
@function px2rem($px) {
  @return $px / 100 + rem;
}

// 使用
.box {
  font-size: px2rem(16);
  width: px2rem(300);
}
```

编译后：
```css
.box {
  font-size: 0.16rem;
  width: 3rem;
}
```

---

# 四、如果你想用浏览器默认 16px 基准（1rem=16px）
只需要改除数：

## Less
```less
.px2rem(@px) {
  @rem: @px / 16rem;
}
```

## Scss
```scss
@function px2rem($px) {
  @return $px / 16 + rem;
}
```

---

# 五、项目里最标准、最通用的完整版（可直接复制）
## 1. Less 完整版
```less
@baseFontSize: 100; // 基准 1rem=100px

.px2rem(@px) {
  font-size: @px / @baseFontSize * 1rem;
}

// 使用
.title {
  .px2rem(18);
  line-height: .px2rem(36);
}
```

## 2. Scss 完整版
```scss
$baseFontSize: 100;

@function px2rem($px) {
  @return $px / $baseFontSize + rem;
}

// 使用
.content {
  padding: px2rem(20) px2rem(15);
  font-size: px2rem(14);
}
```

---

# 六、为什么要这么写？
- 不用自己心算
- 设计稿多少 px，直接填进去
- 后期改基准只改一个数字
- 团队统一规范，不会乱

---

# 七、配套 JS 动态设置 html 根字体（必配）
```js
function setRem() {
  const html = document.documentElement
  const uiWidth = 750 // 设计稿宽度
  html.style.fontSize = html.clientWidth / uiWidth * 100 + 'px'
}
setRem()
window.addEventListener('resize', setRem)
```

这样：
- 750px 设计稿 → 1rem=100px
- 375px 手机 → 1rem=50px
- 自动等比缩放

---

你要我顺便给你配一个 **vite / webpack 的自动 px2rem 插件配置** 吗？不用写函数，直接写 px 自动转 rem。