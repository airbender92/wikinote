# flex:1 详解

`flex` 是简写属性，由3个子属性合成：

```
flex: flex‑grow flex‑shrink flex‑basis;
```

- `flex‑grow`：**扩展比例**，剩余空间怎么瓜分（默认0）
- `flex‑shrink`：**收缩比例**，空间不足如何压缩（默认1）
- `flex‑basis`：**基准尺寸**，分配剩余空间前的基础大小（默认auto）

> **`flex:1` 等价于 `flex: 1 1 0%`** 🔥这是最关键，很多人会记错。
> 不是 `flex:1 1 auto`！

---

## 三个子属性逐个解释

### 1. flex‑grow 扩展系数

容器有**剩余多余空间**时，子元素按照 `flex‑grow` 的比例瓜分这份剩余空间。

- 默认 `0`：不瓜分剩余空间，保持自身大小。

### 2. flex‑shrink 收缩系数

容器总宽度**不够，空间溢出**，子元素按系数压缩。

- 默认 `1`：空间不足会缩小。
- 设置为 `0`：**禁止缩小**，元素不会被压瘪。

### 3. flex‑basis

分配多余空间**之前**元素的基础尺寸。

- `auto`：取元素本身width/height；
- `0%`：基础尺寸视为0，完全按grow比例分配。

## flex:1 → flex:1 1 0% 含义

1. `flex‑grow:1`：**瓜分父容器剩余空间**；多个flex:1的盒子平分剩余空间。
2. `flex‑shrink:1`：空间不够可以收缩。
3. `flex‑basis:0%`：**计算分配时，把自身基础大小当作0**，只看分配比例。

> 效果：多个设置 `flex:1` 的项目**均分父容器可用空间**，不管内容多少。

### 示例1：两个盒子 flex:1

```
<div style="display:flex;width:400px">
  <div style="flex:1;background:red">aaa</div>
  <div style="flex:1;background:blue">bbbbbbbbbbbb</div>
</div>
```

两个盒子**各占200px，平分400px**，哪怕第二个盒子文字更长。

> 因为 `flex‑basis:0%`，不看内容大小，只按比例分配。

## 容易混淆对比

1. `flex:1 1 auto`（不等于flex:1）
   basis是auto：先按自身内容宽度占位，再瓜分剩下的空间。内容多的盒子会更宽。

```
/* flex:1 真实展开 */
flex: 1 1 0%;

/* 很多人误以为是这个，❌不是 */
flex: 1 1 auto;
```

2. `flex‑grow:1` 只写这一个，不等于 flex:1

```
/* 只写grow，shrink、basis用默认： flex:1 0 auto */
flex‑grow:1;
```

3. `flex:none` → `flex:0 0 auto`；不放大、不缩小，尺寸由自身内容决定。
4. `flex:auto` → `flex:1 1 auto`。

## 经典业务场景

### 场景1：左右固定，中间自适应（最常用）

```
<div style="display:flex">
  <div style="width:80px">左侧固定</div>
  <div style="flex:1">中间自适应，自动占满剩余</div>
  <div style="width:80px">右侧固定</div>
</div>
```

中间 `flex:1` 自动吃掉全部剩余空间。

### 场景2：三个flex:1，三等分

```
<div style="display:flex">
  <div style="flex:1">1</div>
  <div style="flex:1">2</div>
  <div style="flex:1">3</div>
</div>
```

三个宽度完全相等。

## 高频坑

1. 父容器必须是 `display:flex`，`flex:1` 才生效；普通块元素无效。
2. `flex:1` 子元素内部文字很长，会把盒子撑破：
   需要加 `overflow:hidden` 或者 `min‑width:0`。>

> flex子项默认 `min‑width:auto`，不会小于内容最小宽度。

```
.item {
  flex:1;
  min‑width:0; /* 允许被压缩到比内容更小 */
}
```

## 面试一句话答案

> `flex:1` 是简写，等价于 `flex: 1 1 0%`。
>
> - flex‑grow:1：允许瓜分父容器剩余空间；
> - flex‑shrink:1：空间不足允许收缩；
> - flex‑basis:0%：分配空间时基准尺寸视为0；
>   多个flex:1元素会按比例均分父容器可用空间，**不受自身内容大小影响**。

| 写法          | 展开值     | 表现                         |
| ------------- | ---------- | ---------------------------- |
| `flex:1`      | `1 1 0%`   | 按比例分配，忽略自身内容大小 |
| `flex:auto`   | `1 1 auto` | 先占内容大小，再分剩余空间   |
| `flex:none`   | `0 0 auto` | 不放大不收缩，由内容决定尺寸 |
| `flex‑grow:1` | `1 0 auto` | 仅开启扩展，不代表flex:1     |
