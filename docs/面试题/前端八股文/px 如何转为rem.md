# px 转 rem

## 基础概念

`rem`：**相对于根元素 html 的 `font‑size`**。

> `html { font‑size: 16px; }` → `1rem = 16px`

公式：

```
rem = px值 / html根字体大小
```

举例，根字体16px：

- `16px = 1rem`
- `32px = 2rem`
- `8px = 0.5rem`

---

## 方案1：手写换算（不推荐项目使用）

html 设置基准字号：

```css
html {
  font-size: 16px;
}
div {
  width: 200px;
  /* 200 / 16 = 12.5rem */
  width: 12.5rem;
}
```

手写很麻烦，项目一般借助工具自动转换。

## 方案2：postcss‑px‑to‑rem（最常用，webpack/vite）

> CSS写px，编译阶段**自动把px转成rem**，开发依然写px，不用手动算。

### Vite 使用

安装

```bash
npm i postcss-px-to-rem -D
```

`postcss.config.js`

```js
module.exports = {
  plugins: [
    require("postcss-px-to-rem")({
      rootValue: 16, // 基准值：1rem = 16px，和html font‑size保持一致
      unitPrecision: 5, // 小数保留位数
      propList: ["*"], // 哪些属性转换，*全部
      selectorBlackList: [], // 选择器黑名单，不转换
      replace: true,
      mediaQuery: false, // 是否转换媒体查询里px
      minPixelValue: 1, // 小于1px不转换
    }),
  ],
};
```

> 开发写：`width:200px`；编译输出：`width: 12.5rem`

### ⚠️注意：移动端常用750设计稿基准

移动端很多项目基准设置 `rootValue: 37.5`（设计稿750）

- 设计稿 `750px` → `20rem`
  此时 `html font‑size` 要配合JS动态设置。

## 方案3：动态 html font‑size（rem适配移动端）

rem要适配不同屏幕大小，html根字号不能写死。
JS动态设置根字体大小：

```js
// 以750设计稿为例，屏幕宽度 / 10
function setRem() {
  const width = document.documentElement.clientWidth;
  document.documentElement.style.fontSize = width / 10 + "px";
}
setRem();
window.addEventListener("resize", setRem);
```

此时 `postcss‑px‑to‑rem` 的 `rootValue` 设置为 **75**（750/10）。

> 设计稿上拿到 `150px` → 编译为 `2rem`。

## 方案4：VSCode插件，编辑器手动转换

插件：`px to rem`，选中px数值快捷键一键换算，适合少量代码。

## 方案5：Sass/Less 写函数手动换算

```scss
$root‑font‑size: 16px;
@function px2rem($px) {
  @return $px / $root‑font‑size * 1rem;
}

div {
  width: px2rem(200px);
}
```

## px‑to‑rem 重要配置坑

1. `rootValue` 必须和页面实际 `html font‑size` 一致，否则尺寸全部错乱。
2. 不想转换某些属性：`propList: ['width','height','margin','padding']` 指定属性。
3. 某些class不想转：`selectorBlackList: ['.norem']`，带这个类选择器不转换px。
4. 行内样式 `style="width:200px"`，postcss工具**无法转换**！postcss只处理css文件。

> ❗行内style里的px，需要JS自己计算转rem。

行内样式 JS 转换示例：

```js
function pxToRem(px, rootSize = 16) {
  return `${px / rootSize}rem`;
}
// style.width = pxToRem(200)
```

## rem vs em vs vw

- `rem`：相对于 html根字体；全局统一适配，移动端传统方案。
- `em`：相对于**父元素font‑size**，容易嵌套错乱，少用。
- `vw`：视口单位，不需要JS设置根字号，现在移动端更流行。

## 小总结

1. 换算公式：`rem = px / html的font‑size`
2. 业务项目不要手算，用 `postcss‑px‑to‑rem`，写px编译自动转rem。
3. 移动端rem适配，需要JS动态修改html的font‑size。
4. postcss不能处理行内style，行内样式需要JS函数转换。

> 补充：现在很多新项目直接用 **postcss‑px‑to‑viewport**，px直接转vw，省去JS动态设置html字体。

如果你需要，我可以对比 rem、vw 两套移动端适配完整方案。
