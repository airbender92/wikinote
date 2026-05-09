## Tailwind CSS 弹性盒子（Flexbox）

Tailwind 提供了一套完整、直观的 Flexbox 工具类，涵盖了容器属性、方向、换行、对齐方式以及子项的控制。这些工具类与响应式前缀组合，可以轻松构建各种弹性布局。

---

### 1. 容器（Container）

要使用 Flexbox，首先需要将父元素定义为弹性容器。

| 类名 | CSS 值 | 说明 |
|------|--------|------|
| `flex` | `display: flex` | 块级弹性容器（占据一整行） |
| `inline-flex` | `display: inline-flex` | 行内弹性容器（宽度由内容撑开） |

```html
<!-- 块级弹性容器，占满父宽度 -->
<div class="flex">
  <div>子项1</div>
  <div>子项2</div>
</div>

<!-- 行内弹性容器，宽度由内容决定 -->
<div class="inline-flex">
  <span>图标</span>
  <span>文字</span>
</div>
```

---

### 2. 方向（Direction）

通过 `flex-direction` 控制主轴的方向。

| 类名 | CSS 值 | 说明 |
|------|--------|------|
| `flex-row` | `flex-direction: row` | 水平方向，从左到右（默认） |
| `flex-row-reverse` | `flex-direction: row-reverse` | 水平方向，从右到左 |
| `flex-col` | `flex-direction: column` | 垂直方向，从上到下 |
| `flex-col-reverse` | `flex-direction: column-reverse` | 垂直方向，从下到上 |

```html
<!-- 水平导航栏 -->
<nav class="flex flex-row gap-4">
  <a href="#">Home</a>
  <a href="#">About</a>
</nav>

<!-- 移动端垂直卡片列表，桌面端水平 -->
<div class="flex flex-col md:flex-row gap-4">
  <div class="card">卡片1</div>
  <div class="card">卡片2</div>
</div>
```

---

### 3. 换行（Wrap）

控制子项是否允许换行。

| 类名 | CSS 值 | 说明 |
|------|--------|------|
| `flex-wrap` | `flex-wrap: wrap` | 允许换行，溢出的子项移到下一行 |
| `flex-wrap-reverse` | `flex-wrap: wrap-reverse` | 换行并反向排列 |
| `flex-nowrap` | `flex-wrap: nowrap` | 不换行（默认），子项会压缩或溢出 |

```html
<!-- 自动换行的标签云 -->
<div class="flex flex-wrap gap-2">
  <span class="badge">JavaScript</span>
  <span class="badge">React</span>
  <span class="badge">Tailwind</span>
  <!-- 更多标签... -->
</div>

<!-- 不换行的水平滚动区 -->
<div class="flex flex-nowrap overflow-x-auto gap-4">
  <div class="w-64 flex-shrink-0">卡片1</div>
  <div class="w-64 flex-shrink-0">卡片2</div>
</div>
```

---

### 4. 对齐（Alignment）

Flexbox 提供了两个轴向的对齐控制：

- **主轴（Main Axis）**：由 `flex-direction` 决定，用 `justify-*` 控制。
- **交叉轴（Cross Axis）**：垂直于主轴，用 `items-*`（单行）或 `align-content-*`（多行）控制。

#### 4.1 主轴对齐（`justify-content`）

| 类名 | CSS 值 | 效果 |
|------|--------|------|
| `justify-start` | `flex-start` | 子项起始对齐（默认） |
| `justify-end` | `flex-end` | 子项末尾对齐 |
| `justify-center` | `center` | 子项居中 |
| `justify-between` | `space-between` | 两端对齐，子项之间间距相等 |
| `justify-around` | `space-around` | 每个子项两侧间距相等 |
| `justify-evenly` | `space-evenly` | 所有间距完全相等 |

```html
<!-- 两端对齐的导航栏 -->
<nav class="flex justify-between">
  <div>Logo</div>
  <div>Links</div>
  <div>Profile</div>
</nav>

<!-- 居中按钮组 -->
<div class="flex justify-center gap-4">
  <button>取消</button>
  <button>确认</button>
</div>
```

#### 4.2 交叉轴单行对齐（`align-items`）

作用于**单行**内子项在交叉轴上的对齐方式。

| 类名 | CSS 值 | 效果 |
|------|--------|------|
| `items-stretch` | `stretch` | 拉伸到容器高度（默认） |
| `items-start` | `flex-start` | 交叉轴起点对齐 |
| `items-end` | `flex-end` | 交叉轴终点对齐 |
| `items-center` | `center` | 交叉轴居中对齐 |
| `items-baseline` | `baseline` | 按文字基线对齐 |

```html
<!-- 垂直居中的按钮组 -->
<div class="flex items-center h-16">
  <span>标签</span>
  <input type="text" class="border">
  <button>提交</button>
</div>

<!-- 基线对齐（让不同字体大小的文字底部对齐） -->
<div class="flex items-baseline gap-2">
  <span class="text-2xl">大标题</span>
  <span class="text-sm">副标题</span>
</div>
```

#### 4.3 多行交叉轴对齐（`align-content`）

当 `flex-wrap: wrap` 产生多行时，控制多行在容器内的分布。

| 类名 | CSS 值 | 说明 |
|------|--------|------|
| `content-start` | `flex-start` | 行组起始对齐 |
| `content-end` | `flex-end` | 行组末尾对齐 |
| `content-center` | `center` | 行组居中 |
| `content-between` | `space-between` | 行组两端对齐 |
| `content-around` | `space-around` | 行组周围间距相等 |
| `content-evenly` | `space-evenly` | 完全均匀分布 |
| `content-stretch` | `stretch` | 拉伸行组填充容器（默认） |

```html
<!-- 等高网格，多行内容在容器中垂直居中 -->
<div class="flex flex-wrap content-center h-96">
  <div class="w-1/3">项目1</div>
  <div class="w-1/3">项目2</div>
  <div class="w-1/3">项目3</div>
  <div class="w-1/3">项目4</div>
</div>
```

---

### 5. 子项（Items）

以下类直接作用于**弹性子项**，控制其大小、增长、收缩和顺序。

#### 5.1 弹性增长（`flex-grow`）

| 类名 | CSS 值 | 效果 |
|------|--------|------|
| `flex-grow` | `flex-grow: 1` | 子项可增长，占据剩余空间 |
| `flex-grow-0` | `flex-grow: 0` | 不增长（默认） |

```html
<div class="flex">
  <div>固定宽度</div>
  <div class="flex-grow">自动占满剩余宽度</div>
  <div>固定宽度</div>
</div>
```

#### 5.2 弹性收缩（`flex-shrink`）

| 类名 | CSS 值 | 效果 |
|------|--------|------|
| `flex-shrink` | `flex-shrink: 1` | 允许收缩（默认） |
| `flex-shrink-0` | `flex-shrink: 0` | 不允许收缩 |

```html
<!-- 防止头像被压缩 -->
<div class="flex w-64">
  <img class="w-12 h-12 flex-shrink-0" src="avatar.jpg">
  <div class="truncate">很长的用户名很长的用户名...</div>
</div>
```

#### 5.3 简写属性（`flex`）

`flex-{value}` 是 `flex-grow`、`flex-shrink`、`flex-basis` 的简写。

| 类名 | CSS 值 | 说明 |
|------|--------|------|
| `flex-1` | `flex: 1 1 0%` | 可增长可收缩，基础宽度为 0，完全占据剩余空间 |
| `flex-auto` | `flex: 1 1 auto` | 基于内容宽度增长/收缩 |
| `flex-initial` | `flex: 0 1 auto` | 默认值，不增长但可收缩 |
| `flex-none` | `flex: none` | 不增长不收缩（固定尺寸） |

```html
<!-- 三栏自适应布局，左右固定，中间自适应 -->
<div class="flex">
  <div class="w-32 flex-none">侧边栏</div>
  <div class="flex-1">主要内容区，撑满剩余宽度</div>
  <div class="w-40 flex-none">右侧边栏</div>
</div>

<!-- 等宽弹性子项（所有子项均分宽度） -->
<div class="flex">
  <div class="flex-1">1/3</div>
  <div class="flex-1">1/3</div>
  <div class="flex-1">1/3</div>
</div>
```

#### 5.4 顺序（`order`）

控制子项的排列顺序（数值越小越靠前）。

| 类名 | CSS 值 |
|------|--------|
| `order-1` | `order: 1` |
| `order-2` | `order: 2` |
| … 支持到 `order-12`，以及 `order-first`（`order: -9999`）、`order-last`（`order: 9999`）、`order-none`（默认，`order: 0`） |

```html
<div class="flex">
  <div class="order-2">第二个显示</div>
  <div class="order-1">第一个显示</div>
  <div class="order-3">第三个显示</div>
</div>

<!-- 响应式：移动端将某个元素提到最前 -->
<div class="flex flex-col md:flex-row">
  <div class="md:order-last">移动端在最下，桌面端在最右</div>
  <div>主要内容</div>
</div>
```

#### 5.5 单个子项交叉轴对齐（`self-*`）

覆盖父容器 `items-*` 的设置，仅对单个子项生效。

| 类名 | CSS 值 |
|------|--------|
| `self-auto` | `align-self: auto` |
| `self-start` | `align-self: flex-start` |
| `self-end` | `align-self: flex-end` |
| `self-center` | `align-self: center` |
| `self-stretch` | `align-self: stretch` |
| `self-baseline` | `align-self: baseline` |

```html
<div class="flex items-start h-32">
  <div class="self-center">这个子项垂直居中</div>
  <div>其他在顶部对齐</div>
</div>
```

---

### 6. 常见实用组合示例

#### 6.1 经典圣杯布局（页眉 + 内容 + 页脚）

```html
<div class="flex flex-col min-h-screen">
  <header class="h-16 bg-gray-800">Header</header>
  <main class="flex-1 flex">
    <aside class="w-64 bg-gray-200">Sidebar</aside>
    <article class="flex-1 p-4">Content</article>
  </main>
  <footer class="h-12 bg-gray-900">Footer</footer>
</div>
```

#### 6.2 水平滚动卡片列表（不换行 + 防压缩）

```html
<div class="flex flex-nowrap overflow-x-auto gap-4 p-4">
  <div class="w-80 flex-shrink-0 rounded-lg shadow">卡片1</div>
  <div class="w-80 flex-shrink-0 rounded-lg shadow">卡片2</div>
  <div class="w-80 flex-shrink-0 rounded-lg shadow">卡片3</div>
</div>
```

#### 6.3 响应式工具栏（桌面端左中右，移动端垂直堆叠）

```html
<div class="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
  <div class="flex gap-2">
    <button>编辑</button>
    <button>删除</button>
  </div>
  <div class="text-center">标题</div>
  <div class="flex gap-2">
    <input type="search" placeholder="搜索">
    <button>搜索</button>
  </div>
</div>
```

#### 6.4 订单确认页（金额右对齐）

```html
<div class="flex justify-between">
  <span>商品小计</span>
  <span>¥199</span>
</div>
<div class="flex justify-between font-bold">
  <span>总计</span>
  <span>¥199</span>
</div>
```

---

### 总结

| 分类 | 关键类 | 记忆要点 |
|------|--------|----------|
| **容器** | `flex`, `inline-flex` | 定义弹性上下文 |
| **方向** | `flex-row`, `flex-col` | 主轴方向，响应式常用 |
| **换行** | `flex-wrap` | 结合 `gap-*` 实现间距 |
| **主轴对齐** | `justify-start/end/center/between/around/evenly` | 控制子项在主轴上的分布 |
| **交叉轴对齐（单行）** | `items-start/end/center/baseline/stretch` | 垂直居中常用 `items-center` |
| **交叉轴对齐（多行）** | `content-start/end/center/between/around` | 多行时控制行组整体位置 |
| **子项增长/收缩** | `flex-1`, `flex-none`, `flex-grow`, `flex-shrink-0` | `flex-1` 最常用（占满剩余空间） |
| **子项顺序** | `order-*`, `order-first`, `order-last` | 不改变 DOM 结构，只改变视觉顺序 |
| **单子项对齐** | `self-*` | 覆盖父级 `items-*` |

Tailwind 的 Flexbox 工具类几乎覆盖了原生 CSS 的所有 Flex 属性，并且通过响应式前缀可以轻松适配不同屏幕尺寸，让复杂布局变得简单直观。