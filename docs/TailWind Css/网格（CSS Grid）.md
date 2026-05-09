## Tailwind CSS 网格（CSS Grid）

Tailwind 提供了一套强大且直观的网格工具类，让你无需编写自定义 CSS 就能快速构建基于 CSS Grid 布局的页面。这些工具类涵盖了容器定义、模板列/行、跨列/行、显式定位以及自动排列等所有核心功能。

---

### 1. 容器（Container）

通过 `display: grid` 或 `display: inline-grid` 将元素定义为网格容器。

| 类名 | CSS 值 | 说明 |
|------|--------|------|
| `grid` | `display: grid` | 块级网格容器（占据整行宽度） |
| `inline-grid` | `display: inline-grid` | 行内网格容器（宽度由内容撑开） |

```html
<!-- 块级网格，占满父容器宽度 -->
<div class="grid">
  <div>1</div>
  <div>2</div>
</div>

<!-- 行内网格，宽度由内容决定 -->
<div class="inline-grid grid-cols-2 gap-2">
  <span>A</span>
  <span>B</span>
</div>
```

---

### 2. 模板列/行（Template Columns & Rows）

使用 `grid-cols-{n}` 和 `grid-rows-{n}` 定义网格的列数和行数。Tailwind 提供了从 1 到 12 的预设值，以及 `none`、`subgrid` 等选项。

#### 列模板（`grid-cols-*`）

| 类名 | CSS 值 | 说明 |
|------|--------|------|
| `grid-cols-1` | `grid-template-columns: repeat(1, minmax(0, 1fr))` | 单列（1fr 占满） |
| `grid-cols-2` | `repeat(2, minmax(0, 1fr))` | 两列等宽 |
| `grid-cols-3` | `repeat(3, minmax(0, 1fr))` | 三列等宽 |
| … | … | 最多 `grid-cols-12`（12 列等宽） |
| `grid-cols-none` | `none` | 无显式列模板 |

**注意**：`minmax(0, 1fr)` 与普通 `1fr` 的区别是允许内容溢出时缩小到 0，避免内容撑开网格。

```html
<!-- 三列等宽布局 -->
<div class="grid grid-cols-3 gap-4">
  <div>A</div>
  <div>B</div>
  <div>C</div>
</div>

<!-- 响应式：移动端1列，平板2列，桌面3列 -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  ...
</div>
```

#### 行模板（`grid-rows-*`）

类似地，`grid-rows-{n}` 定义显式行数。

| 类名 | CSS 值 |
|------|--------|
| `grid-rows-1` | `grid-template-rows: repeat(1, minmax(0, 1fr))` |
| `grid-rows-2` | `repeat(2, minmax(0, 1fr))` |
| … | 最多 `grid-rows-6` |

```html
<!-- 固定两行，每行等高分摊高度 -->
<div class="grid grid-rows-2 h-64">
  <div>第一行</div>
  <div>第二行</div>
</div>
```

---

### 3. 跨列/行（Spanning）

通过 `col-span-{n}` 和 `row-span-{n}` 让一个网格项跨越多个列或行。

| 类名 | CSS 值 | 说明 |
|------|--------|------|
| `col-span-1` | `grid-column: span 1 / span 1` | 跨越 1 列（默认） |
| `col-span-2` | `span 2 / span 2` | 跨越 2 列 |
| … | … | 最多 `col-span-12` |
| `col-span-full` | `1 / -1` | 跨越所有列（从第1列到最后一列） |
| `row-span-1` | `grid-row: span 1 / span 1` | 跨越 1 行 |
| `row-span-2` | `span 2 / span 2` | 跨越 2 行 |
| … | … | 最多 `row-span-6` |
| `row-span-full` | `1 / -1` | 跨越所有行 |

```html
<!-- 仪表盘布局：左侧边栏占2行，右侧内容区占满剩余行 -->
<div class="grid grid-cols-4 grid-rows-3 gap-4 h-96">
  <!-- 侧边栏，跨越3行（全部行） -->
  <aside class="col-span-1 row-span-full bg-gray-200">Sidebar</aside>
  
  <!-- 头部，跨越第2~4列（即3列） -->
  <header class="col-span-3 bg-blue-200">Header</header>
  
  <!-- 主要内容，跨越3列，占第2行和第3行 -->
  <main class="col-span-3 row-span-2 bg-white">Main</main>
</div>
```

**常用技巧**：`col-span-full` 相当于 `col-start-1 col-end-[-1]`，用于让元素占据整行。

```html
<div class="grid grid-cols-2 gap-2">
  <div>普通项</div>
  <div>普通项</div>
  <div class="col-span-full">这个元素横跨整行</div>
</div>
```

---

### 4. 起始与结束（Start & End）

如果需要精确控制网格项的位置，可以使用 `col-start-{n}`、`col-end-{n}`、`row-start-{n}`、`row-end-{n}` 类。

#### 列起始/结束

| 类名 | CSS 值 |
|------|--------|
| `col-start-1` | `grid-column-start: 1` |
| `col-start-2` | `grid-column-start: 2` |
| … | 最多 `col-start-13`（因为最多12列，网格线编号从1到13） |
| `col-start-auto` | `auto` |
| `col-end-1` … `col-end-13` | `grid-column-end` 对应值 |
| `col-end-auto` | `auto` |

#### 行起始/结束

| 类名 | CSS 值 |
|------|--------|
| `row-start-1` … `row-start-7` | `grid-row-start: n` |
| `row-end-1` … `row-end-7` | `grid-row-end: n` |

**组合使用**：

```html
<!-- 自定义位置：将某个元素放到第2列起始，到第4列结束（跨越2列） -->
<div class="grid grid-cols-4 gap-2">
  <div class="col-start-2 col-end-4 bg-red-200">
    我从第2列网格线开始，到第4列网格线结束
  </div>
</div>

<!-- 更简洁的方式：col-start-2 + col-span-2 等价于上面的效果 -->
<div class="grid grid-cols-4 gap-2">
  <div class="col-start-2 col-span-2 bg-blue-200">
    同样跨越2列，从第2列开始
  </div>
</div>
```

**特殊值**：使用 `col-start-[-1]` 或 `col-end-[-1]` 可以通过任意值实现，例如 `col-start-[13]` 对于12列网格。

---

### 5. 自动填充与流（Auto Placement & Flow）

当没有显式指定每个网格项的位置时，浏览器会自动放置它们。Tailwind 提供了控制自动放置行为的工具类。

#### 网格流（`grid-flow-*`）

控制自动放置的方向（行优先还是列优先）。

| 类名 | CSS 值 | 说明 |
|------|--------|------|
| `grid-flow-row` | `grid-auto-flow: row` | 行优先（默认），先填满第一行的列，再换行 |
| `grid-flow-col` | `grid-auto-flow: column` | 列优先，先填满第一列的行，再换列 |
| `grid-flow-row-dense` | `row dense` | 行优先并尝试填补空缺 |
| `grid-flow-col-dense` | `column dense` | 列优先并尝试填补空缺 |

```html
<!-- 默认行优先，自动换行生成多行 -->
<div class="grid grid-cols-3 grid-flow-row gap-2">
  <div>1</div> <div>2</div> <div>3</div>
  <div>4</div> <div>5</div> <div>6</div>
  <!-- 最终形成3列多行的网格 -->
</div>

<!-- 列优先，先向下填充再向右 -->
<div class="grid grid-rows-3 grid-flow-col gap-2 h-48">
  <div>1</div> <div>2</div> <div>3</div>
  <div>4</div> <div>5</div> <div>6</div>
  <!-- 形成3行多列的网格，垂直方向先填满 -->
</div>
```

#### 自动列/行大小（`auto-cols-*`, `auto-rows-*`）

当自动创建的隐式网格（超出显式模板的部分）出现时，可以通过 `auto-cols-*` 和 `auto-rows-*` 控制它们的大小。

| 类名 | CSS 值 | 说明 |
|------|--------|------|
| `auto-cols-auto` | `grid-auto-columns: auto` | 根据内容决定列宽 |
| `auto-cols-min` | `min-content` | 列宽为内容最小宽度 |
| `auto-cols-max` | `max-content` | 列宽为内容最大宽度 |
| `auto-cols-fr` | `minmax(0, 1fr)` | 等比例分配剩余空间 |
| `auto-rows-auto` | `grid-auto-rows: auto` | 行高根据内容 |
| `auto-rows-min` | `min-content` | |
| `auto-rows-max` | `max-content` | |
| `auto-rows-fr` | `minmax(0, 1fr)` | |

```html
<!-- 显式只有2列，但自动放置时可能会创建第3列，使用 auto-cols-fr 使新增列也等宽 -->
<div class="grid grid-cols-2 auto-cols-fr gap-2">
  <div>1</div> <div>2</div> <div>3</div> <div>4</div>
  <!-- 第3、4个元素会自动进入第2行？不对，因为 grid-flow-row 会换行增加行，而不是增加列 -->
  <!-- 更合适的例子：grid-flow-col 时，显式只有2行，但自动填充会新增列 -->
</div>

<!-- 更清晰示例：限制行数为2，列数动态增加，新列宽度设为 min-content -->
<div class="grid grid-rows-2 grid-flow-col auto-cols-min gap-2">
  <div>短</div> <div>很长很长很长</div> <div>更宽</div>
  <!-- 每列宽度由该列最宽内容决定 -->
</div>
```

---

### 6. 显式与隐式网格的最佳实践

- **显式网格**：通过 `grid-cols-*` 和 `grid-rows-*` 定义的列/行。
- **隐式网格**：当放置的元素超出显式范围时，浏览器自动添加的列/行。
- **控制隐式网格大小**：使用 `auto-cols-*` 和 `auto-rows-*`。
- **控制自动放置方向**：使用 `grid-flow-*`。

```html
<!-- 组合示例：一个动态添加标签的容器 -->
<div class="grid grid-cols-4 auto-rows-min gap-2">
  <!-- 显式4列，隐式行高由内容最小高度决定 -->
  <div class="col-span-1">标签1</div>
  <div class="col-span-1">标签2</div>
  <div class="col-span-2">长标签3</div>
  <!-- 更多元素会自动换行，新行高度 auto -->
</div>
```

---

### 7. 完整示例：常见页面布局

#### 示例 1：经典卡片网格（响应式）

```html
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 p-4">
  <div class="bg-white rounded-lg shadow p-4">卡片1</div>
  <div class="bg-white rounded-lg shadow p-4">卡片2</div>
  <div class="bg-white rounded-lg shadow p-4">卡片3</div>
  <!-- ...更多卡片 -->
</div>
```

#### 示例 2：博客文章页（左侧边栏 + 右侧内容）

```html
<div class="grid grid-cols-12 gap-6 max-w-7xl mx-auto">
  <!-- 侧边栏占3列 -->
  <aside class="col-span-3 bg-gray-100 p-4">
    侧边栏
  </aside>
  <!-- 主内容占9列 -->
  <main class="col-span-9">
    <article class="prose">
      <h1>文章标题</h1>
      <p>内容...</p>
    </article>
  </main>
</div>
```

#### 示例 3：瀑布流布局（使用 dense 填补空隙）

```html
<div class="grid grid-cols-3 gap-4 grid-flow-row-dense">
  <div class="col-span-1 h-24 bg-red-200">1</div>
  <div class="col-span-2 h-32 bg-blue-200">2（跨越2列）</div>
  <div class="col-span-1 h-48 bg-green-200">3（高）</div>
  <div class="col-span-1 h-24 bg-yellow-200">4</div>
  <div class="col-span-1 h-32 bg-purple-200">5</div>
  <!-- dense 会让后续小项填充前面的空隙 -->
</div>
```

#### 示例 4：自定义起始位置（杂志风格）

```html
<div class="grid grid-cols-4 grid-rows-3 gap-2 h-96">
  <div class="col-span-2 row-span-2 bg-gray-800 text-white p-4">大块内容</div>
  <div class="col-start-3 col-span-2 bg-gray-300 p-2">小图1</div>
  <div class="row-start-2 col-start-3 bg-gray-300 p-2">小图2</div>
  <div class="row-start-2 col-start-4 bg-gray-300 p-2">小图3</div>
  <div class="col-span-4 row-start-3 bg-gray-200 p-2">页脚</div>
</div>
```

---

### 总结

| 分类 | 关键类 | 说明 |
|------|--------|------|
| **容器** | `grid`, `inline-grid` | 启用网格布局 |
| **列模板** | `grid-cols-1` ~ `grid-cols-12` | 定义列数，使用 1fr 等宽 |
| **行模板** | `grid-rows-1` ~ `grid-rows-6` | 定义行数 |
| **跨列** | `col-span-{n}`, `col-span-full` | 让元素跨越 n 列或全部列 |
| **跨行** | `row-span-{n}`, `row-span-full` | 跨越 n 行或全部行 |
| **起始/结束** | `col-start-{n}`, `col-end-{n}`, `row-start-{n}`, `row-end-{n}` | 精确控制网格线的起止位置 |
| **自动流** | `grid-flow-row`, `grid-flow-col`, `-dense` 变体 | 控制自动放置的方向和密集填充 |
| **隐式网格大小** | `auto-cols-*`, `auto-rows-*` | 定义自动生成的列/行的大小策略（auto/min/max/fr） |

Tailwind 的网格工具类与响应式前缀结合极佳，可以轻松实现不同屏幕尺寸下的复杂布局变化。例如 `md:grid-cols-2 lg:grid-cols-4`。掌握这些类后，你可以在不写 CSS 的情况下构建任何网格布局。