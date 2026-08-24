# Chrome DevTools Performance 录制面板完整解读

打开 F12 → **Performance**，点击左上角 ● Record（圆形按钮），操作页面，再点停止；得到火焰图，用来分析：**页面加载卡顿、交互卡顿、长任务、渲染慢、脚本耗时、布局抖动**。

> 快捷键：`Ctrl+E` 开始/停止录制。
> 建议录制前勾选：✅ Screenshots（截图）、✅ Memory（内存）。

## 整体面板从上到下分为 5 大块

1. **概览区（Overview）**：时间轴总览（FPS、CPU、NET）
2. **帧条（Frames）**：每一个浏览器帧，看掉帧
3. **主线程火焰图（Main）**：最重要！JS执行、解析、布局、绘制全部在这里
4. **其他线程：Compositor、Raster 等**
5. **详情面板（Bottom）**：选中条目后看详情 Summary / Bottom‑Up / Call Tree / Event Log

---

## 1. 顶部概览区 Overview

### FPS（最上面绿色条）

> FPS：每秒帧数，**60为满帧**，一帧≈16.6ms

- 绿色柱子越高 = FPS越高，体验流畅
- 柱子红色：**掉帧**，发生卡顿
- 红线标记：**Long Task（长任务）**，块大于50ms，主线程阻塞

### CPU（彩色堆叠图）

颜色含义：

- 🟡 **Scripting**：JS执行（解析、编译、运行业务代码）
- 🟣 **Rendering**：渲染（Layout布局、Recalculate Style重算样式）
- 🔵 **Painting**：绘制（Paint）
- 🟤 **Loading**：加载网络、解析HTML
- ⚫ **Idle**：空闲

> CPU占满，代表主线程被打满，必然卡顿。

### NET（网络）

每一条横线代表一个请求，长度=耗时；看是否大量请求串行、大文件加载慢。

---

## 2. Frames 帧轨道

每一小格代表一帧。
鼠标悬浮显示：`Frame time：xx ms`

> 目标：每帧 ≤ **16.6ms**（60fps）
> 一帧超过 50ms → 用户明显感知卡顿。

**红色小三角标记 = 长任务 Long Task**，对应 JS API `longtask`。

---

## 3. Main 主线程火焰图【核心分析区域】

> 浏览器主线程干四件事：**执行JS → 计算样式 → Layout布局 → Paint绘制 → 合成**。
> 火焰图：**横向是时间，纵向是调用栈；方块越宽代表耗时越长**。

展开 Main，可以看到一个个任务块（Task），**宽于50ms的Task就是长任务，块上面有红色小三角⚠️**。

### 常见方块事件名词解释

| 事件名称                      | 含义                           | 问题信号                                                        |
| ----------------------------- | ------------------------------ | --------------------------------------------------------------- |
| `Task`                        | 主线程任务块，包裹内部所有调用 | 方块宽度>50ms = 长任务                                          |
| `Scripting / Evaluate Script` | 执行JS脚本                     | 方块很宽：业务JS计算耗时过大                                    |
| `Recalculate Style`           | 重算CSS样式                    | 大量高频触发：元素太多、频繁修改class/style                     |
| `Layout`                      | **重排（回流）**               | 大块Layout：DOM改动多、循环读写offsetWidth/height，强制同步布局 |
| `Paint`                       | 重绘                           | Paint巨大：大量DOM重绘、阴影、大背景图                          |
| `Composite Layers`            | 合成图层                       | 一般很快，耗时高代表图层太多                                    |
| `Parse HTML`                  | 解析HTML                       | HTML过大                                                        |
| `Compile Code`                | V8编译JS                       | 大量脚本编译耗时                                                |

### 火焰图4种分析视图（底部tab）

选中一个Task/函数块，底部切换：

1. **Summary（摘要）**：各类耗时总占比 Scripting / Rendering / Painting
2. **Bottom‑Up 自底向上（最常用，找耗时代码）**>

> 按**总耗时从大到小排序**，看哪些函数吃掉最多时间。

- `Self Time`：**自身代码执行耗时，不包含子函数调用**，找真正耗时元凶看 Self Time！
- `Total Time`：函数+所有子函数总耗时

3. **Call Tree 调用树**：从上往下看完整调用栈，看是谁调用的耗时代码
4. **Event Log**：按时间顺序看事件流

> ✅ 定位卡顿优先用：**Bottom‑Up，按 Self Time 降序排序**。

### 重要概念：Self Time vs Total Time

举例子：A函数调用B函数，B执行80ms

- A：TotalTime=80ms，SelfTime=0ms（A只是调用，自己没干活）
- B：TotalTime=80ms，SelfTime=80ms
  👉 **找性能问题，看 Self Time，不要只看 TotalTime**。

---

## 4. 典型卡顿场景识别（看火焰图现象）

### 场景1：JS长任务卡顿

现象：Main 里面有很宽黄色 `Task`，带红色三角；大量 `Evaluate Script`。

- Bottom‑Up看到业务JS函数 Self Time很高。
  原因：大循环、复杂JSON解析、大列表同步渲染、复杂计算。
  解决：任务分片，setTimeout / requestIdleCallback / WebWorker。

### 场景2：Layout 重排（回流）风暴

现象：出现连续大量紫色 `Layout`，一块叠一块。

> 经典坑：循环里**先读DOM尺寸，立刻写DOM**，触发强制同步布局 Forced synchronous layout。
> DevTools会警告提示：⚠️ Forced reflow。

坏代码示例：

```
for(let i=0;i<list.length;i++){
  divs[i].offsetWidth; // 读
  divs[i].style.width = '100px'; // 写，强制触发Layout
}
```

优化：**先批量读完所有DOM值，再批量写DOM**。

### 场景3：Recalculate Style 耗时高

大量元素频繁修改className/style，选择器过于复杂。
优化：减少频繁样式修改，使用css class，减少DOM节点。

### 场景4：Paint绘制耗时高

蓝色Paint块巨大。
原因：频繁修改背景、box‑shadow、大渐变，大面积重绘。
优化：使用 `transform` / `opacity`，走合成线程，跳过Layout&Paint。

### 场景5：网络拖慢加载

NET轨道看到资源串行加载；大JS文件下载解析编译耗时久。
优化：代码分割，懒加载，压缩JS。

## 5. 几个重要小技巧

1. **放大时间轴**：鼠标滚轮滚动，或者拖拽上方标尺，放大局部时间片段，看清细节。
2. 点击方块，可以直接跳转到**源码行号**，定位业务代码。
3. 录制注意事项：
   - 录制时关闭浏览器扩展，扩展JS会干扰结果；最好用无痕窗口录制。
   - 模拟真实性能：CPU Throttling（CPU节流）下拉，设置 **4x slowdown**，模拟中低端手机。
   - Network Throttling：网络节流，模拟3G。
4. 不要只看电脑高性能下的录制，**一定要CPU降速看效果**，PC很快的代码在手机就是长任务。

## 6. 和 PerformanceObserver 线上指标对应关系

- Performance 录制看到的红色三角 Task → 就是 JS `longtask` 捕获的长任务(duration>50ms)
- LCP、FCP、CLS、INP 在Performance面板也有对应标记，线上通过PerformanceObserver采集。>

> DevTools是线下调试定位根源；PerformanceObserver是线上埋点采集统计。

## 7. 标准排查步骤（实操流程）

1. 无痕模式，CPU节流4x，网络节流
2. 点击录制，复现卡顿操作（页面加载 / 点击交互），停止录制
3. 看概览：FPS是否掉帧，CPU哪一块占比最高（Scripting / Rendering / Painting）
4. 放大卡顿时间段，找到 Main 主线程宽的Task块（红色三角长任务）
5. 选中耗时任务，切换到 Bottom‑Up，按 `Self Time` 降序
6. 定位耗时代码函数，查看源码，分析是JS计算 / Layout / Paint问题
7. 修改代码，再次录制对比优化前后火焰图。

## 8. 常见误区

1. ❌只看 Total Time，忽略 Self Time，误把调用函数当成元凶。
2. ❌在本机高性能电脑直接录制，不做CPU节流，看不出移动端卡顿。
3. ❌录制开一堆浏览器插件，插件JS产生大量干扰Task。
4. ❌看到Layout就认为一定是bug，少量Layout是浏览器正常行为，**高频大量连续Layout才是问题**。

如果你需要，我可以拿一个模拟卡顿火焰图案例，告诉你怎么一眼分辨是JS问题还是渲染问题。
