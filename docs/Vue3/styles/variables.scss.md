## variables.scss 全局样式变量解读

```scss
// src/styles/variables.scss

// 主题色
$primary-color: #409EFF;
$success-color: #67C23A;
$warning-color: #E6A23C;
$danger-color: #F56C6C;
$info-color: #909399;

// 文字颜色
$text-primary: #303133;
$text-regular: #606266;
$text-secondary: #909399;
$text-placeholder: #C0C4CC;

// 边框颜色
$border-color: #DCDFE6;
$border-color-light: #E4E7ED;

// 背景色
$bg-color: #F5F7FA;
$bg-white: #FFFFFF;

// 间距
$spacing-xs: 4px;
$spacing-sm: 8px;
$spacing-md: 16px;
$spacing-lg: 24px;
$spacing-xl: 32px;

// 侧边栏
$sidebar-width: 220px;
$sidebar-collapsed-width: 64px;
$header-height: 56px;

// 圆角
$border-radius-sm: 4px;
$border-radius-md: 8px;
$border-radius-lg: 12px;

// 阴影
$shadow-light: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
$shadow-medium: 0 4px 16px 0 rgba(0, 0, 0, 0.15);
```

---

### 1. 主题色（Element Plus 风格）

| 变量 | 色值 | Element Plus 变量 | 用途 |
|------|------|------------------|------|
| `$primary-color` | #409EFF | `--el-color-primary` | 主色调（蓝） |
| `$success-color` | #67C23A | `--el-color-success` | 成功（绿） |
| `$warning-color` | #E6A23C | `--el-color-warning` | 警告（橙） |
| `$danger-color` | #F56C6C | `--el-color-danger` | 危险（红） |
| `$info-color` | #909399 | `--el-color-info` | 信息（灰） |

---

### 2. 文字颜色层级

| 变量 | 色值 | 用途 |
|------|------|------|
| `$text-primary` | #303133 | 主要文字（标题、正文） |
| `$text-regular` | #606266 | 常规文字（正文） |
| `$text-secondary` | #909399 | 次要文字（辅助说明） |
| `$text-placeholder` | #C0C4CC | 占位文字（输入框提示） |

---

### 3. 间距系统

| 变量 | 值 | 用途 |
|------|-----|------|
| `$spacing-xs` | 4px | 紧凑间距 |
| `$spacing-sm` | 8px | 小间距 |
| `$spacing-md` | 16px | 标准间距 |
| `$spacing-lg` | 24px | 大间距 |
| `$spacing-xl` | 32px | 特大间距 |

---

### 4. 侧边栏与头部

| 变量 | 值 | 用途 |
|------|-----|------|
| `$sidebar-width` | 220px | 侧边栏展开宽度 |
| `$sidebar-collapsed-width` | 64px | 侧边栏折叠宽度 |
| `$header-height` | 56px | 顶部导航高度 |

---

### 5. 全局注入机制

```typescript
// vite.config.ts
css: {
  preprocessorOptions: {
    scss: {
      additionalData: `@use "@/styles/variables.scss" as *;`,
    },
  },
}
```

**效果：** 所有 `.scss` 文件自动注入变量，无需 `@use` 或 `@import`。

---

### 6. 使用示例

```scss
// 在组件中直接使用
.default-layout {
  height: 100vh;
  
  .header {
    height: $header-height;           // 56px
    padding: $spacing-md;              // 16px
    background: $bg-white;
    border-radius: $border-radius-md; // 8px
    box-shadow: $shadow-light;         // 0 2px 12px 0 rgba(0, 0, 0, 0.1)
  }
}
```

---

### 7. 与 Tailwind 的对比

| 方面 | SCSS 变量 | Tailwind |
|------|----------|---------|
| 定义 | `$primary-color` | `colors: { primary: '#409EFF' }` |
| 使用 | `color: $primary-color` | `text-primary` |
| 编译 | 运行时替换 | 构建时生成 CSS 类 |
| 场景 | 组件内部样式 | 快速工具类 |

---

### 8. SCSS 变量与 CSS 变量

| SCSS 变量 | CSS 变量 |
|-----------|---------|
| `$primary-color: #409EFF` | `--el-color-primary: #409EFF` |
| 编译时替换 | 运行时替换 |
| 不能动态修改 | 可以通过 JS 动态修改 |

**推荐做法：** Element Plus 使用 CSS 变量，SCSS 变量用于项目自定义样式。

---

### 9. 变量分类

```
variables.scss
├── 颜色类
│   ├── 主题色 (primary/success/warning/danger/info)
│   ├── 文字色 (text-primary/regular/secondary/placeholder)
│   └── 背景色 (bg-color/bg-white)
│
├── 间距类
│   └── spacing-xs/sm/md/lg/xl
│
├── 布局类
│   └── sidebar/header 尺寸
│
└── 效果类
    └── border-radius/shadow
```

---

需要继续了解 **请求封装（request.ts）** 吗？