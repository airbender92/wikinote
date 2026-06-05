## mixins.scss 公共样式混合宏解读

```scss
// src/styles/mixins.scss

// 文本省略
@mixin text-ellipsis($lines: 1) {
  @if $lines == 1 {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  } @else {
    display: -webkit-box;
    -webkit-line-clamp: $lines;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
}

// 居中
@mixin flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

// 水平居中
@mixin flex-x-center {
  display: flex;
  justify-content: center;
}

// 垂直居中
@mixin flex-y-center {
  display: flex;
  align-items: center;
}

// 清除浮动
@mixin clearfix {
  &::after {
    content: '';
    display: table;
    clear: both;
  }
}

// 滚动条样式
@mixin custom-scrollbar($width: 6px, $color: #C0C4CC) {
  &::-webkit-scrollbar {
    width: $width;
    height: $width;
  }

  &::-webkit-scrollbar-thumb {
    background-color: $color;
    border-radius: $border-radius-sm;
  }

  &::-webkit-scrollbar-track {
    background-color: transparent;
  }
}
```

---

### 1. @mixin 是什么？

```scss
@mixin 名称($参数) {
  // 样式代码
}
```

**使用方式：**
```scss
.card {
  @include flex-center;  // 使用混合宏
}
```

---

### 2. text-ellipsis 文本省略

```scss
@mixin text-ellipsis($lines: 1) {
  @if $lines == 1 {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  } @else {
    display: -webkit-box;
    -webkit-line-clamp: $lines;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
}
```

| 参数 | 说明 |
|------|------|
| `$lines: 1` | 默认单行省略 |

**单行省略（$lines = 1）：**
```scss
overflow: hidden;           // 超出隐藏
text-overflow: ellipsis;     // 显示省略号
white-space: nowrap;         // 不换行
```

**多行省略（$lines > 1）：**
```scss
display: -webkit-box;        // 弹性盒
-webkit-line-clamp: 3;       // 最多3行
-webkit-box-orient: vertical; // 垂直排列
overflow: hidden;            // 超出隐藏
```

---

### 3. Flex 居中系列

```scss
@mixin flex-center {
  display: flex;
  align-items: center;       // 垂直居中
  justify-content: center;   // 水平居中
}

@mixin flex-x-center {
  display: flex;
  justify-content: center;   // 仅水平居中
}

@mixin flex-y-center {
  display: flex;
  align-items: center;       // 仅垂直居中
}
```

| 混合宏 | 效果 |
|--------|------|
| `flex-center` | 完全居中 |
| `flex-x-center` | 水平居中 |
| `flex-y-center` | 垂直居中 |

---

### 4. clearfix 清除浮动

```scss
@mixin clearfix {
  &::after {
    content: '';
    display: table;
    clear: both;
  }
}
```

**为什么需要清除浮动？**
```scss
// 子元素浮动后，父元素高度塌陷
.parent {
  .child {
    float: left;  // 脱离文档流
  }
  // parent 高度为 0
}
```

**使用 clearfix：**
```scss
.parent {
  @include clearfix;
}
```

---

### 5. custom-scrollbar 自定义滚动条

```scss
@mixin custom-scrollbar($width: 6px, $color: #C0C4CC) {
  &::-webkit-scrollbar {
    width: $width;
    height: $width;
  }
  &::-webkit-scrollbar-thumb {
    background-color: $color;
    border-radius: $border-radius-sm;
  }
  &::-webkit-scrollbar-track {
    background-color: transparent;
  }
}
```

| 部分 | 说明 |
|------|------|
| `&::-webkit-scrollbar` | 滚动条整体尺寸 |
| `&::-webkit-scrollbar-thumb` | 滚动条滑块 |
| `&::-webkit-scrollbar-track` | 滚动条轨道 |

**使用示例：**
```scss
.content {
  height: 300px;
  overflow-y: auto;
  @include custom-scrollbar(8px, #409EFF);
}
```

---

### 6. 使用示例

```scss
// 卡片组件
.card {
  @include flex-center;        // 居中
  @include text-ellipsis;     // 单行省略
  @include custom-scrollbar;   // 自定义滚动条
}

// 多行文本
.article-content {
  @include text-ellipsis(3);  // 3行省略
}

// 清除浮动
.list-wrapper {
  @include clearfix;
}
```

---

### 7. 混合宏 vs 普通 CSS 类

| 对比 | 混合宏 | 普通类 |
|------|--------|--------|
| 封装 | 样式组合复用 | 无法组合 |
| 参数 | 可传参数 | 固定样式 |
| 编译 | 内联到使用处 | 单独存在 |
| 维护 | 一处修改 | 需改多处 |

---

### 8. 全局注入机制

```typescript
// vite.config.ts
css: {
  preprocessorOptions: {
    scss: {
      additionalData: `@use "@/styles/variables.scss" as *; @use "@/styles/mixins.scss" as *;`,
    },
  },
}
```

**效果：** 所有 `.scss` 文件自动注入，无需手动 `@use`。

---

需要继续了解 **请求封装（request.ts）** 吗？