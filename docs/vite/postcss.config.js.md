## postcss.config.js 解读

```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

### 配置解析

| 插件 | 作用 |
|------|------|
| `tailwindcss` | 将 Tailwind 工具类转换为标准 CSS |
| `autoprefixer` | 自动添加 CSS 浏览器前缀（如 `-webkit-`、`-moz-`） |

### 执行顺序

PostCSS 会**按顺序**处理 CSS：

```
源代码 CSS
    ↓
1. tailwindcss  → 解析 @tailwind 指令，生成工具类
    ↓
2. autoprefixer → 添加浏览器前缀
    ↓
最终 CSS
```

### autoprefixer 示例

```css
/* 源代码 */
display: flex;
justify-content: center;

/* 转换后 */
display: -webkit-box;
display: -webkit-flex;
display: flex;
-webkit-box-pack: center;
-webkit-justify-content: center;
justify-content: center;
```

### 为什么需要这两个插件？

| 工具 | 解决的问题 |
|------|-----------|
| Tailwind | 类名太多，手写太慢 |
| autoprefixer | 手动写 `-webkit-` 太繁琐 |

### 工作流程图

```
.vue 文件
    ↓
Vite 构建时
    ↓
postcss.config.js
    ├── tailwindcss    → 生成 .bg-primary { background-color: #409EFF }
    └── autoprefixer   → 添加 -webkit-background-clip: text 等前缀
    ↓
最终 CSS 文件
```

### 注意

`tailwindcss: {}` 和 `autoprefixer: {}` 中的空对象表示使用默认配置。如果需要自定义：

```javascript
autoprefixer: {
  flexbox: 'no-2009',  // 不添加 2009 版本的 flexbox 前缀
  grid: true,          // 开启 Grid 布局前缀
}
```

---

### CSS 处理流程完整链路

```
src/styles/global.scss
    ↓
vite.config.ts (preprocessorOptions: scss)
    ↓
postcss.config.js (tailwindcss + autoprefixer)
    ↓
浏览器可用的 CSS
```

---

配置层面已经全部解读完毕。需要进入 **核心业务层** 吗？

- **路由配置** — 路由表 + 守卫
- **状态管理** — Pinia store
- **请求封装** — Axios 拦截器