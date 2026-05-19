## Item 29 详细讲解：优先设计只能表示有效状态的类型

这一节的核心原则是：**用类型系统强制排除无效状态，让“非法状态不可表示”。** 如果类型允许无效的组合（比如同时 `isLoading` 和 `error` 都为真），你的代码就会充满歧义、条件判断和潜在 bug。相反，通过精确建模状态（例如使用可辨识联合），可以使代码逻辑变得清晰且易于维护。

---

### 第一个例子：页面加载状态

#### 糟糕的设计

```ts
interface State {
  pageText: string;
  isLoading: boolean;
  error?: string;
}
```

这里的问题：
- `isLoading` 和 `error` 可以**同时为真**（例如 `{ isLoading: true, error: '404' }`）。这种状态在现实中不存在，但类型却允许它。
- 渲染函数 `renderPage` 必须先检查 `error`，再检查 `isLoading`，否则会错误地显示加载中（即使出错了）。
- 更新函数 `changePage` 很难正确实现：忘记重置 `error`、忘记将 `isLoading` 设为 `false`，并且无法处理并发请求。

根本原因：**类型允许的取值组合多于实际可能的状态**。

#### 更好的设计：可辨识联合（tagged union）

```ts
interface RequestPending { state: 'pending'; }
interface RequestError   { state: 'error'; error: string; }
interface RequestSuccess { state: 'ok'; pageText: string; }

type RequestState = RequestPending | RequestError | RequestSuccess;

interface State {
  currentPage: string;
  requests: { [page: string]: RequestState };
}
```

这里：
- 每个请求的状态只能是 `'pending'`、`'error'` 或 `'ok'` 三者之一，**互斥**。
- 渲染时，根据 `requestState.state` 用 `switch` 分别处理，无需担心无效组合。
- 更新时，直接设置对应的状态对象，不会丢失或错误覆盖字段。

**优点**：即使类型定义变长，但逻辑变得直白，并且 TypeScript 会强制你处理所有情况（配合 Item 59 的穷尽性检查）。

---

### 第二个例子：法航447航班（真实悲剧）

这是一个极富冲击力的案例，说明**错误的状态设计可能导致灾难**。

#### 糟糕的设计（空客的真实逻辑）

```ts
interface CockpitControls {
  leftSideStick: number;   // 左座驾驶杆角度，0=中立，正=推杆（俯冲）
  rightSideStick: number;  // 右座驾驶杆角度
}
```

这里允许的状态包括：
- 左杆推前，右杆拉后
- 两杆同时拉后
- 等等

在实际飞行中，左右杆可以**独立运动**，没有任何机械联动。而飞机计算最终指令的算法是：

```ts
function getStickSetting(controls: CockpitControls) {
  return (controls.leftSideStick + controls.rightSideStick) / 2;
}
```

**后果**：当副驾驶持续拉杆（负值），机长拼命推杆（正值），两者平均后接近零 → 飞机既不俯冲也不爬升，最终失速坠毁。228人遇难。

#### 为什么类型系统没阻止？

因为类型 `CockpitControls` 允许左右杆独立任意取值。从数学上看，任何一对 `(left, right)` 都是合法输入，但现实世界中，**一个合理的驾驶杆系统应该只有一个统一的控制指令**。

#### 正确的设计

```ts
interface CockpitControls {
  stickAngle: number;   // 单一驾驶杆角度
}
```

这样根本不需要 `getStickSetting` 函数 —— 直接使用 `controls.stickAngle` 即可。**设计好的类型，让错误的调用方式在编译期就不可能写出**。

---

### 核心教训

1. **避免让无效组合成为可表示的状态**  
   例如同时设置 `isLoading` 和 `error`，或者左右杆独立。

2. **使用可辨识联合（tagged union）来精确建模互斥状态**  
   每个成员只包含与该状态相关的字段，不包含无关字段。

3. **类型设计会影响整个系统的正确性**  
   如果类型允许非法状态，那么任何使用该类型的函数都必须处理这些非法状态，或者隐含地假设它们不会出现 —— 这种假设往往会导致 bug。

4. **好的类型设计即使更冗长，也值得**  
   多写几行类型定义，可以节省无数调试时间，甚至（在极端情况下）挽救生命。

---

### 实践建议

- 每次定义 `interface` 或 `type` 时，问自己：**这个类型允许哪些值的组合？这些组合在现实中都会发生吗？**  
- 如果某些组合不应该同时出现，就用联合类型拆分。  
- 对于网络请求、UI 状态、用户输入等，优先使用可辨识联合。

**记住 Fred Brooks 的话（本章开篇的引述）**：  
> 给我看你的数据表（类型），我就不需要你的流程图了。  
> —— 好的类型本身就是最好的文档。