## 代码作用

```js
document.documentElement.setAttribute("data-theme", theme);
```

- `document.documentElement` = `<html>` 根元素
- 给 html 标签添加属性：`data-theme="dark"` / `data-theme="light"`

```html
<html data-theme="dark"></html>
```

配合 CSS 属性选择器实现全局主题切换，是前端最通用的主题方案。

## 完整配套示例

### JS 逻辑（结合系统偏好 + 本地存储）

```js
// 获取主题
function getTheme() {
  const save = localStorage.getItem("theme");
  if (save) return save;
  return window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
}

// 应用主题到 html
function setTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("theme", theme);
}

// 初始化
const theme = getTheme();
setTheme(theme);
```

### CSS 写法（推荐 CSS 变量）

```css
/* 浅色默认 */
:root {
  --color-bg: #ffffff;
  --color-text: #222222;
}

/* html[data-theme="dark"] 深色模式 */
html[data-theme="dark"] {
  --color-bg: #121212;
  --color-text: #eeeeee;
}

body {
  background: var(--color-bg);
  color: var(--color-text);
}
```

## 监听系统自动切换（用户未手动选择时）

```js
const media = window.matchMedia("(prefers-color-scheme: dark)");
media.addEventListener("change", (e) => {
  // 只有用户没有手动设置主题时，才跟随系统
  if (!localStorage.getItem("theme")) {
    const newTheme = e.matches ? "dark" : "light";
    setTheme(newTheme);
  }
});
```

## 常见坑

1. **SSR 项目（Nuxt/Next/VitePress）**
   不能直接在顶层执行，必须等到客户端渲染；最好在 `onMounted` / `useEffect` 里执行，否则服务端没有 `document`。

2. 页面刷新闪烁问题
   解决方案：**把主题初始化代码内嵌到 `<head>` 最顶部**，优先执行，避免白屏闪。

```html
<head>
  <script>
    (function () {
      const t =
        localStorage.getItem("theme") ||
        (window.matchMedia("(prefers-color-scheme: dark)").matches
          ? "dark"
          : "light");
      document.documentElement.setAttribute("data-theme", t);
    })();
  </script>
</head>
```

3. 区分两套逻辑

- `prefers-color-scheme`：操作系统原生设置
- `data-theme`：页面自身主题标记，优先级更高（用户手动切换）

如果你用 Vue3 / React，我可以直接封装成 Hook。
