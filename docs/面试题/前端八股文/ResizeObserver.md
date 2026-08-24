# ResizeObserver

**作用：监听 DOM 元素的尺寸变化（width / height），元素大小改变时触发回调**。

> 对比旧方案：以前监听窗口大小只能用 `window.resize`，**只能监听浏览器视口，不能监听普通DOM元素**；元素因为内容变化、css变换、弹窗展开、flex布局导致尺寸改变，`window.resize` 完全感知不到。
> ResizeObserver 可以监听**任意DOM元素**，不是只监听窗口。

## 触发时机

以下情况元素宽高变化都会触发回调：

1. 浏览器窗口缩放，导致元素被挤压改变大小
2. 动态修改元素 width / height
3. 内容变化：文本增多、图片加载完成撑开容器
4. display 从 none → block，元素出现
5. flex / grid 布局变化、弹窗展开收起
6. 动画改变元素尺寸

> ❗不监听：元素位置变化（left/top）；**只监听盒子尺寸宽高**。

## 基础语法示例

```js
// 创建观察器
const resizeObserver = new ResizeObserver((entries) => {
  // entries：被监听元素数组，一个observer可以监听多个dom
  for (const entry of entries) {
    // 元素
    const dom = entry.target;
    // 内容盒尺寸（content‑box，不含border、padding）
    const { width, height } = entry.contentRect;
    console.log("元素尺寸变化：", width, height);
  }
});

// 开始监听某个DOM
resizeObserver.observe(document.querySelector("#box"));

// 停止监听单个元素
resizeObserver.unobserve(document.querySelector("#box"));

// 全部停止监听，销毁实例
resizeObserver.disconnect();
```

### entry 常用属性

- `entry.target`：发生变化的DOM元素
- `entry.contentRect`：`{width,height,top,left}`，**内容盒大小（不含padding、border）**
- `entry.borderBoxSize`：边框盒尺寸（包含border+padding）
- `entry.contentBoxSize`：内容盒

## 典型业务场景

1. **自适应图表**：ECharts、G2图表容器大小变化，自动执行 `chart.resize()`，不用监听window.resize

```js
// echarts示例
const chartDom = document.getElementById("chart");
const chart = echarts.init(chartDom);
const ro = new ResizeObserver((entries) => {
  chart.resize();
});
ro.observe(chartDom);
// 组件销毁一定要 disconnect！防止内存泄漏
```

2. 弹窗、抽屉展开收起，内部容器尺寸动态变化
3. 富文本编辑器，内容自动增高，监听高度变化
4. 拖拽调整面板大小（分割面板 split‑pane）
5. 响应式组件：组件内部根据自身宽高做布局，而不是依赖屏幕断点

## ⚠️非常重要的坑

1. **内存泄漏**
   组件/弹窗销毁时，**必须调用 `unobserve()` 或者 `disconnect()`**。
   DOM销毁但ResizeObserver实例还在，会持有DOM引用，内存泄露。

> Vue3示例

```js
import { onUnmounted } from "vue";
let ro = null;
ro = new ResizeObserver(() => {});
ro.observe(domRef.value);

onUnmounted(() => {
  ro?.disconnect(); // 销毁
});
```

2. 回调会在浏览器重排前执行，**不要在回调内部修改被监听元素宽高**，否则会无限循环触发ResizeObserver（死循环）。

3. 监听 `display:none` 的元素：不会触发；元素从none变为可见，尺寸从0变成正常值会触发一次。

4. 兼容性：现代浏览器全部支持；IE不支持。

## ResizeObserver vs window.resize

|          | ResizeObserver           | window.resize        |
| -------- | ------------------------ | -------------------- |
| 监听对象 | 任意DOM元素              | 仅浏览器窗口视口     |
| 触发条件 | DOM自身宽高改变          | 浏览器窗口缩放       |
| 多个元素 | 支持同时监听多个dom      | 需要自己循环遍历     |
| 性能     | 性能好，元素不变不会触发 | 窗口缩放高频大量触发 |

## 补充：和 MutationObserver 的区别

- `ResizeObserver`：**专门监听尺寸大小**
- `MutationObserver`：监听 dom 属性、子节点增删改，**不监听宽高变化**。修改style.width，MutationObserver默认感知不到尺寸改变。

如果你需要，我可以写一份Vue3封装好的useResizeObserver hook，可以直接复制项目使用。
