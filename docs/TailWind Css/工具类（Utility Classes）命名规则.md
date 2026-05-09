## Tailwind CSS 工具类命名规则

### 1. 属性简写规则

Tailwind 将几乎所有的 CSS 属性映射为**直观的简写前缀**，形成 `{前缀}-{值}` 的模式：

| 前缀 | 含义 | 示例 |
|------|------|------|
| `p-` | padding（内边距） | `p-4` |
| `m-` | margin（外边距） | `m-2` |
| `bg-` | background | `bg-red-500` |
| `text-` | color / 字体大小 | `text-center` / `text-lg` |
| `w-` / `h-` | width / height | `w-full` `h-screen` |
| `border-` | border | `border-2` `border-black` |
| `rounded-` | border-radius | `rounded-md` |
| `flex-` / `grid-` | Flexbox / Grid | `flex-col` `grid-cols-3` |
| `justify-` / `items-` | Flex/Grid 对齐 | `justify-center` `items-end` |
| `font-` | font-weight / 系列 | `font-bold` `font-mono` |
| `gap-` | gap（网格/弹性间距） | `gap-4` |
| `shadow-` | box-shadow | `shadow-lg` |
| `opacity-` | 透明度 | `opacity-50` |

**完全属性**（无简写）也会直接使用 CSS 属性名：`z-10`、`top-0`、`overflow-hidden` 等。

---

### 2. 数值比例尺

Tailwind 使用一套**预定义的语义化比例尺**，而不是直接使用像素值。比例尺基于 **4px 基准**（即 `1` = 4px，`2` = 8px，以此类推）。

#### 标准比例尺（间距、大小等）

| 值 | 对应的 CSS 值 |
|----|---------------|
| `0` | `0px` |
| `px` | `1px`（特殊，用于需要 1px 边框/间距时） |
| `0.5` | `2px` |
| `1` | `4px` |
| `2` | `8px` |
| `3` | `12px` |
| `4` | `16px` |
| `5` | `20px` |
| `6` | `24px` |
| `7` | `28px` |
| `8` | `32px` |
| `9` | `36px` |
| `10` | `40px` |
| … | … |
| `96` | `384px` |

#### 其他属性的特殊比例尺

- **宽度/高度**：`w-1/2`（百分比）、`w-screen`（视口宽度）、`w-full`（父容器 100%）
- **字体大小**：`text-xs`（0.75rem）、`text-sm`（0.875rem）、`text-base`（1rem）、`text-lg`（1.125rem）……`text-9xl`（8rem）
- **颜色**：数值表示亮度等级（如 `bg-blue-500`，`500` 为中亮色）
- **阴影**：`shadow-sm`、`shadow`、`shadow-md`、`shadow-lg`、`shadow-xl`、`shadow-2xl`

#### 任意值（Arbitrary Values）

当预定义比例尺不够用时，可以使用方括号语法**直接写任意 CSS 值**：

```html
<div class="w-[375px] h-[200px] p-[13px] top-[calc(100%+1rem)]">
  <!-- 完全自定义 -->
</div>
```

任意值支持任何 CSS 单位（`px`、`rem`、`em`、`%`、`vw`、`vh`、`calc()` 等），甚至支持 CSS 变量：`bg-[var(--theme-color)]`。

---

### 3. 负值（Negative Values）

Tailwind 允许给部分属性使用**负值**（主要适用于 `margin`、`inset`、`translate`、`space` 等需要定位的地方）。语法为 `-{prefix}-{value}`：

| 示例 | 说明 |
|------|------|
| `-m-2` | margin: -8px |
| `-mt-4` | margin-top: -16px |
| `-translate-x-1` | transform: translateX(-4px) |
| `-inset-0` | top/right/bottom/left: 0px（负零还是零，无意义但语法允许） |

负值同样支持任意值：`-top-[5px]` → `top: -5px`。

**注意**：不是所有属性都支持负值，Tailwind 的负值生成器只针对那些在 CSS 中允许负值的属性。

---

### 4. 自动（`auto`）

`auto` 用于需要浏览器自动计算值的属性，语法为 `{prefix}-auto`：

| 示例 | 说明 |
|------|------|
| `m-auto` | margin: auto（水平居中常用） |
| `ml-auto` | margin-left: auto（将弹性子元素推到右侧） |
| `w-auto` | width: auto（覆盖固定宽度） |
| `h-auto` | height: auto（覆盖固定高度） |
| `top-auto` | top: auto（重置定位） |
| `overflow-auto` | overflow: auto（滚动条按需出现） |
| `cursor-auto` | cursor: auto（默认光标行为） |

`auto` 特别适合**一维布局控制**：例如在 Flexbox 中用 `ml-auto` 将导航栏内的按钮推到右侧，或用 `m-auto` 水平居中块级元素。

---

### 综合示例

```html
<!-- 一个卡片：自定义宽度，负边距偏移，自动边距居中 -->
<div class="w-[320px] mx-auto -mt-3 p-4 bg-white rounded-lg shadow-md">
  <h2 class="text-lg font-bold mb-2">标题</h2>
  <p class="text-gray-600">内容...</p>
  <button class="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 ml-auto block">
    按钮
  </button>
</div>
```

这一套命名规则让你**几乎不需要离开 HTML** 就能完成绝大部分样式定义，同时保持清晰可读。