# CSS 翻牌效果（卡片翻转 3D flip）

核心原理：

1. CSS 3D 空间：`transform‑style: preserve‑3d` 开启3D空间；`perspective` 透视，产生近大远小立体感
2. 卡片分**正面(front)**、**背面(back)**两个子层
3. 背面默认 `transform: rotateY(180deg)` 翻转隐藏
4. `backface‑visibility: hidden` 隐藏元素背面，防止两面同时看见
5. hover / class 控制外层容器 `rotateY(180deg)`，实现正反面切换

> 翻转是沿 Y 轴左右翻；X轴是上下翻转。

## 完整可运行示例（hover触发翻牌）

```
<!DOCTYPE html>
<html lang="zh‑CN">
<head>
<meta charset="UTF‑8">
<style>
.flip-card {
  width: 260px;
  height: 360px;
  perspective: 800px; /* 透视距离，越大3D效果越弱 */
  cursor: pointer;
}

.flip-card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.6s ease;
  transform‑style: preserve‑3d; /* 开启3D子元素空间 */
}

/* hover 翻转整个卡片 */
.flip-card:hover .flip-card-inner {
  transform: rotateY(180deg);
}

.flip-front,
.flip-back {
  position: absolute;
  width: 100%;
  height: 100%;
  border‑radius: 12px;
  display: flex;
  align‑items: center;
  justify‑content: center;
  font‑size: 28px;
  /* 隐藏背面，非常关键 */
  backface‑visibility: hidden;
}

.flip-front {
  background‑color: #409eff;
  color: #fff;
}

.flip-back {
  background‑color: #f56c6c;
  color: #fff;
  /* 背面初始旋转180度 */
  transform: rotateY(180deg);
}
</style>
</head>
<body>

<div class="flip-card">
  <div class="flip-card-inner">
    <div class="flip-front">正面</div>
    <div class="flip-back">背面内容</div>
  </div>
</div>

</body>
</html>
```

## 关键属性解释

1. `perspective: 800px`
   加在父容器，设置观察者距离平面的距离；**控制3D立体感**，只对后代生效。
2. `transform‑style: preserve‑3d`
   必须加在**直接父容器**（flip‑card‑inner），让子元素可以处在3D空间；不设置，3D失效，变成平面拉伸。
3. `backface‑visibility: hidden;`

> 重中之重！元素旋转之后，**把元素的背面隐藏**。不加，旋转时正反面会同时透出来。

4. `rotateY(180deg)`

- Y轴翻转：左右翻牌（最常用）
- `rotateX(180deg)`：上下翻牌

## JS控制版本（点击翻牌，Vue也可以直接套用样式）

通过 class 控制翻转，而不是hover：

```
<div class="flip-card">
  <div class="flip-card-inner" id="card">
    <div class="flip-front">正面</div>
    <div class="flip-back">背面</div>
  </div>
</div>

<script>
const card = document.getElementById('card')
card.parentElement.addEventListener('click', ()=>{
  card.classList.toggle('flipped')
})
</script>
<style>
.flip-card-inner.flipped {
  transform: rotateY(180deg);
}
</style>
```

## Vue3简易组件

```
<template>
  <div class="flip-card" @click="flipped = !flipped">
    <div class="flip-card-inner" :class="{flipped}">
      <div class="flip-front">
        <slot name="front"></slot>
      </div>
      <div class="flip-back">
        <slot name="back"></slot>
      </div>
    </div>
  </div>
</template>
<script setup>
import {ref} from 'vue'
const flipped = ref(false)
</script>
<style scoped>
.flip-card {
  width:240px;
  height:320px;
  perspective: 800px;
  cursor: pointer;
}
.flip-card-inner {
  position: relative;
  width:100%;
  height:100%;
  transition: transform 0.6s ease;
  transform‑style: preserve‑3d;
}
.flip-card-inner.flipped {
  transform: rotateY(180deg);
}
.flip-front,.flip-back{
  position:absolute;
  width:100%;
  height:100%;
  backface‑visibility:hidden;
  display:flex;
  align‑items:center;
  justify‑content:center;
}
.flip-front{ background:#409eff; color:#fff; }
.flip-back{ background:#f56c6c; color:#fff; transform:rotateY(180deg); }
</style>
```

## 高频踩坑

1. ❌没有写 `transform‑style: preserve‑3d`：3D效果消失，只是平面拉伸。必须放在正反面的直接父元素。
2. ❌忘记 `backface‑visibility: hidden`：旋转的时候两面重叠都能看见。
3. ❌`perspective` 写在inner上面：perspective要写在外层父容器。
4. 正反面必须 `position:absolute`，叠在一起；否则两个盒子会上下排列。
5. 移动端部分旧浏览器，3D可以加 `transform: translateZ(0)` 开启硬件加速，优化动画卡顿。

## 拓展参数

- 修改 `transition` 可以调整翻牌快慢，例如 `transition: transform 0.8s cubic‑bezier(0.25,0.46,0.45,0.94)`
- `rotateX(180deg)` 实现上下翻牌。
- 想要翻转之后有缩放效果，可以复合 transform：`transform: rotateY(180deg) scale(1.02)`

## 面试简答

> CSS翻牌利用CSS3 3D变换实现：
>
> 1. 外层设置 `perspective` 透视；
> 2. 中间容器开启 `transform‑style:preserve‑3d` 开启3D空间；
> 3. 正反面绝对定位重叠，设置 `backface‑visibility:hidden` 隐藏背面；
> 4. 背面初始 `rotateY(180deg)`；hover/class 控制中间容器旋转 `rotateY(180deg)`，完成翻转动画。

如果你需要，我可以写一个**扑克牌翻牌，多张卡片列表**的demo。
