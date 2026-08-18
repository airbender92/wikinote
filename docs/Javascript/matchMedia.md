# `window.matchMedia('(prefers-color-scheme: dark)').matches`

## 作用

读取**系统/浏览器原生配色偏好**：

- 返回 `true` → 系统开启深色模式
- 返回 `false` → 系统浅色模式

> ⚠️ 只会读取**系统设置**，不能直接拿到页面手动切换的主题（页面手动切换主题一般存在 localStorage / state，不会改变 `prefers-color-scheme`）

## 基础示例

```javascript
// 获取当前系统主题
const isDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
console.log(isDark ? "深色模式" : "浅色模式");
```

## 监听系统主题自动变化（重点）

```javascript
const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

// 回调函数
function handleThemeChange(e) {
  if (e.matches) {
    console.log("切换到深色");
  } else {
    console.log("切换到浅色");
  }
}

// 监听变化
mediaQuery.addEventListener("change", handleThemeChange);

// 初始执行一次
handleThemeChange(mediaQuery);

// 取消监听（组件销毁时调用）
// mediaQuery.removeEventListener('change', handleThemeChange);
```

## 常见业务场景封装（自动优先系统，支持用户手动覆盖）

```javascript
/**
 * 获取有效主题
 * @returns 'dark' | 'light'
 */
function getTheme() {
  // 优先读取用户手动保存的设置
  const userTheme = localStorage.getItem("theme");
  if (userTheme) return userTheme;

  // 无手动设置，则跟随系统
  return window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
}
```

## CSS 配套写法

```css
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #111;
    --text: #fff;
  }
}
@media (prefers-color-scheme: light) {
  :root {
    --bg: #fff;
    --text: #222;
  }
}
```

## 注意坑

1. **用户手动切换页面主题 ≠ 修改系统偏好**，`prefers-color-scheme` 不会变；
2. 部分浏览器隐私模式、第三方桌面端浏览器可能不生效；
3. SSR（Vue/React Next/Nuxt）中**不能直接在顶层执行**，必须等到客户端挂载后调用；
4. 旧版 Safari 早期版本事件监听有兼容性问题。

如果你需要，我可以直接给一份 Vue3 / React 可用的完整主题切换 hook。
