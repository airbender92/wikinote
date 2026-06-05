## global.scss 全局样式解读

```scss
@import './variables.scss';
@import './mixins.scss';
@import 'tailwindcss/base';
@import 'tailwindcss/components';
@import 'tailwindcss/utilities';

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  width: 100%;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: 14px;
  color: $text-primary;
  background-color: $bg-color;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  width: 100%;
  height: 100%;
}

a {
  color: $primary-color;
  text-decoration: none;

  &:hover {
    opacity: 0.8;
  }
}

// 全局滚动条样式
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-thumb {
  background-color: #C0C4CC;
  border-radius: 4px;
}

::-webkit-scrollbar-track {
  background-color: transparent;
}
```

---

### 1. 导入顺序

```scss
@import './variables.scss';      // 1. 变量（依赖最少）
@import './mixins.scss';         // 2. 混合宏（依赖变量）
@import 'tailwindcss/base';      // 3. Tailwind 基础样式
@import 'tailwindcss/components'; // 4. Tailwind 组件样式
@import 'tailwindcss/utilities';   // 5. Tailwind 工具类
```

**为什么 Tailwind 在 variables 之后？**
- Tailwind 可能在某些配置中使用变量
- 保证变量已定义

---

### 2. CSS Reset（重置样式）

```scss
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
```

| 属性 | 作用 |
|------|------|
| `margin: 0` | 清除默认外边距 |
| `padding: 0` | 清除默认内边距 |
| `box-sizing: border-box` | width/height 包含 border + padding |

---

### 3. html, body 基础样式

```scss
html, body {
  width: 100%;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: 14px;
  color: $text-primary;
  background-color: $bg-color;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

| 属性 | 作用 |
|------|------|
| `width/height: 100%` | 占满视口 |
| `font-family` | 跨平台字体栈 |
| `-webkit-font-smoothing` | Mac Chrome 抗锯齿 |
| `-moz-osx-font-smoothing` | Mac Firefox 抗锯齿 |

**字体栈解释：**
```
-apple-system     → iOS / macOS Safari
BlinkMacSystemFont → macOS Chrome
'Segoe UI'        → Windows
Roboto            → Android
'Helvetica Neue'  → 旧 macOS
Arial             → 通用
```

---

### 4. #app 容器

```scss
#app {
  width: 100%;
  height: 100%;
}
```

**与 body 的区别：**
```
body               → 文档根元素
#app (index.html) → Vue 应用挂载点
```

**为什么需要两层？**
```html
<!-- index.html -->
<body>
  <div id="app"></div>  <!-- Vue 挂载点 -->
</body>
```

---

### 5. 链接样式

```scss
a {
  color: $primary-color;
  text-decoration: none;

  &:hover {
    opacity: 0.8;
  }
}
```

| 状态 | 效果 |
|------|------|
| 默认 | 主题蓝色，无下划线 |
| hover | 透明度 0.8 |

**`&:hover` 语法：**
```scss
// SCSS 嵌套，等价于
a:hover {
  opacity: 0.8;
}
```

---

### 6. 全局滚动条样式

```scss
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-thumb {
  background-color: #C0C4CC;
  border-radius: 4px;
}

::-webkit-scrollbar-track {
  background-color: transparent;
}
```

| 部分 | 作用 |
|------|------|
| `::-webkit-scrollbar` | 滚动条整体 |
| `::-webkit-scrollbar-thumb` | 滑块 |
| `::-webkit-scrollbar-track` | 轨道 |

**为什么全局设置？**
- 浏览器默认滚动条样式不统一
- 提供一致的视觉体验

---

### 7. Tailwind 引入说明

```scss
@import 'tailwindcss/base';      // 基础重置
@import 'tailwindcss/components'; // 组件类
@import 'tailwindcss/utilities';   // 工具类
```

| 模块 | 包含内容 |
|------|---------|
| `base` | 基础重置、typography |
| `components` | 按钮、卡片等组件类 |
| `utilities` | flex、pt-4、text-center 等工具类 |

---

### 8. 文件加载顺序

```
index.html
    ↓
main.ts
    ↓
import './styles/global.scss'
    ↓
global.scss 执行
    ↓
所有样式生效
```

---

### 9. CSS 优先级

```scss
// 全局样式（优先级低）
body { color: $text-primary }

// 组件样式（优先级高）
.my-card { color: red }
```

| 来源 | 优先级 |
|------|--------|
| `global.scss` | 低 |
| 组件 `<style scoped>` | 中 |
| 内联样式 `style=""` | 高 |

---

### 10. 与其他样式文件的关系

```
styles/
├── variables.scss  → SCSS 变量定义
├── mixins.scss     → 混合宏定义
├── global.scss     → 全局样式（导入上面两个）
└── main.ts         → 导入 global.scss
```

**vite.config.ts 全局注入：**
```typescript
additionalData: `@use "@/styles/variables.scss" as *; @use "@/styles/mixins.scss" as *;`
```

**效果：** 每个 .scss 文件都自动注入变量和混合宏，但 global.scss 需要显式导入以确保加载顺序。

---

需要继续了解 **请求封装（request.ts）** 吗？