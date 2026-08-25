# Fiber：为什么把递归改成链表

## 旧版React（Stack Reconciler 栈协调器）

React15及更早，diff是**递归树**。虚拟DOM是树形结构，深度优先递归遍历。

```
div
├─ h1
└─ p
   └─ span
```

伪代码：

```js
function reconcile(oldVdom, newVdom) {
  diffNode(oldVdom, newVdom);
  // 递归子节点
  for (const child of newVdom.children) {
    reconcile(oldChild, newChild);
  }
}
```

**问题：JS递归调用栈，一旦开始，不能暂停。**
一旦组件树很大，递归执行时间很长（比如几百ms），浏览器主线程被占死：

- 浏览器没法处理点击、输入事件
- 没法做动画渲染
  👉 **页面卡顿，丢帧**，这就是Stack Reconciler最大痛点。

> JS是单线程，递归一旦启动，必须一口气跑完，没有机会交还主线程给浏览器。

---

## Fiber的核心思路：把递归树 → 链表

把原来的**树结构**，拆解成一个个**Fiber工作单元**，用链表串联。

每个Fiber节点代表一个UI单元（组件/标签），维护3个指针：

```
child   → 第一个子Fiber
sibling → 下一个兄弟Fiber
return  → 父Fiber（指向父节点）
```

### 链表关系示意图

```
div(Fiber)
 child → h1(Fiber)
          return → div
          sibling → p(Fiber)
                        return → div
                        child → span(Fiber)
```

遍历顺序不再是函数递归调用栈，而是**循环遍历链表**，while循环，不是递归。
伪代码：

```js
let workInProgress = currentRootFiber;

// 循环处理每一个fiber单元，可以随时暂停
while (workInProgress !== null) {
  workInProgress = performUnitOfWork(workInProgress);
}
```

`performUnitOfWork` 返回下一个要处理的fiber：

1. 优先走 `child`：先处理子节点
2. 没有child，走 `sibling`：处理兄弟
3. 没有sibling，向上找 `return` 的sibling

> 这就是深度优先遍历，但是**不用函数递归，用循环+链表指针实现**。

### 关键收益：可中断

`performUnitOfWork`处理完一个Fiber单元之后，可以**退出循环，交还主线程给浏览器**。
浏览器做完渲染、用户事件，有空了再回来从刚才中断的`workInProgress`继续往下执行。

> ✅ 时间切片：每一帧浏览器留给JS大概16ms，超过时间就暂停，下一帧继续。

原来递归：**一旦开始，不能停，全部做完才归还主线程**
Fiber链表循环：**做完一个单元就可以停，保存当前workInProgress，下次继续**。

---

## 两个Fiber树：current树 vs workInProgress树（双缓存）

- `current`：页面上已经渲染完成的Fiber树（旧树）
- `workInProgress`：正在后台构建、diff的新Fiber树

每次更新，不是修改current，而是复制一份生成workInProgress。
diff在 workInProgress 和 current之间对比。

构建完整个workInProgress树之后，**一次性把root指针切换**，commit阶段统一更新DOM。

> 双缓存避免构建新树的时候污染正在显示的旧树。

### alternate 属性

每个fiber有`alternate`，互相指向对方：
`current.alternate = workInProgress`
`workInProgress.alternate = current`

复用对象，不是每次全部新建，提升性能。

---

## 完整工作流程（render阶段）

1. 触发更新(setState)，标记需要更新的根，开启调度
2. `workInProgress`指向根Fiber
3. `while(workInProgress)`循环，逐个处理Fiber单元
   - beginWork：处理当前fiber，计算props，diff，生成子fiber（构建child/sibling链表）
   - completeWork：当前节点处理完毕，收集DOM副作用（增删改、生命周期）
4. 每处理完一个单元，检查时间是否耗尽；时间到，直接暂停循环，保存当前`workInProgress`，让出主线程。
5. 浏览器空闲，再从保存的`workInProgress`位置继续执行。
6. 全部fiber单元处理完成，得到完整workInProgress树，进入commit阶段，不可中断，执行DOM操作。

> beginWork 向下走child；completeWork向上return。

---

## 重点区分：虚拟DOM ReactElement vs Fiber

- **ReactElement**：JSX编译出来的普通JS对象，描述UI，静态数据。
- **Fiber**：运行时链表节点，是**工作单元**，保存状态、effect副作用、链表指针。

render阶段，把ReactElement转成Fiber链表，做diff。

## 递归树 VS Fiber链表对比

| 项目     | Stack Reconciler(React15) | Fiber Reconciler(React16+)               |
| -------- | ------------------------- | ---------------------------------------- |
| 遍历方式 | 函数递归                  | while循环 + child/sibling/return链表指针 |
| 中断能力 | ❌不可中断，一口气跑完    | ✅处理完一个fiber单元就可以暂停          |
| 调度     | 无时间切片                | 时间切片，高优先级任务可插队             |
| 数据结构 | 树                        | 链表（工作单元）                         |
| 更新阶段 | 全部同步                  | render(可中断) + commit(同步不可中断)    |

## 容易踩坑理解

1. Fiber**没有改变diff算法的同层比较、type规则、key逻辑**，只是把遍历方式从递归改成链表循环。diff策略还是那一套。
2. 可中断只发生在**render阶段（计算fiber树，不碰DOM）**；commit阶段DOM操作是同步不可打断，防止页面中间状态。
3. 中断不是抛弃已经算好的fiber，只是暂停，下一帧继续接着算。

## 极简一句话总结

> 旧版递归：函数调用栈，一旦跑起来停不住，大组件树造成卡顿。
> Fiber把树拆成一个个小工作单元，用child/sibling/return链表，while循环遍历，处理完一个单元就可以暂停交还主线程，实现时间切片。

如果你需要，我可以写一段极简模拟fiber链表遍历的小JS代码，直观看到beginWork / completeWork的执行顺序。
