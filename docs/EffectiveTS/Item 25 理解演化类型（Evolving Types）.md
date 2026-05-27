## Item 25: 理解演化类型（Evolving Types）—— 详解与示例

### 核心概念

在 TypeScript 中，通常情况下一个变量的类型在声明时就确定了，之后只能通过**窄化**（narrowing，如 `if (x !== null)`）使其变得更具体，但**不能扩展**（即不能从一种类型变成另一种完全不相关的类型）。然而有一个显著的例外：**演化类型**。

演化类型是指：当一个变量被初始化为 `[]`（空数组）、`null` 或 `undefined` 时，TypeScript 允许它的类型随着后续的赋值操作而**逐步演化**。这可以避免不必要的类型注解，但理解其行为至关重要。

---

### 1. 数组的演化：从 `any[]` 到更具体的数组类型

先看一个常见的 `range` 函数：

```typescript
function range(start: number, limit: number) {
    const nums = [];            // ① 初始类型：any[]
    for (let i = start; i < limit; i++) {
        nums.push(i);           // ② 推入 number 后，类型演化为 number[]
    }
    return nums;                // ③ 返回类型：number[]
}
```

**逐步分析**：

- 第 ① 行：`const nums = []`  
  通常情况下，空数组会被推断为 `any[]`（一种未分化、可容纳任何类型的数组）。但 TypeScript 并没有立即报错，因为它允许演化。

- 第 ② 行：在循环中 `nums.push(i)`，其中 `i` 是 `number`。此时 TypeScript 观察到数组中只被推入了 `number` 类型的值，于是将 `nums` 的类型从 `any[]` 演化为 `number[]`。

- 第 ③ 行：函数返回 `nums`，其类型已经是 `number[]`。

**关键点**：演化与窄化不同。窄化是使类型变小（如 `string | null` → `string`），而演化是让类型从 `any[]` 变成更具体的数组类型，甚至可以是联合类型数组。

---

### 2. 推入不同类型：演化出联合类型数组

```typescript
const result = [];        // any[]
result.push('a');         // 推入 string → 演化为 string[]
result.push(1);           // 推入 number → 演化为 (string | number)[]
```

最终 `result` 的类型是 `(string | number)[]`。TypeScript 会根据所有推入值的类型，计算出一个最合适的联合类型。

---

### 3. 标量值的演化：条件分支中的类型合并

演化不仅发生在数组上，也发生在普通变量上（初始化为 `null`、`undefined` 或未初始化时）。

```typescript
let value;                // 类型为 any（未初始化，隐式 any）
if (Math.random() < 0.5) {
    value = /hello/;      // 分支内演化为 RegExp
} else {
    value = 12;           // 分支内演化为 number
}
value;                    // 最终类型：number | RegExp
```

- 初始化时未赋值，TypeScript 将其视为 `any`（但这不是危险的 `any`，后面会解释）。
- 在两个分支中分别赋值为 `RegExp` 和 `number`。
- 最终合并为联合类型 `number | RegExp`。

这种行为同样适用于初始化为 `null` 或 `undefined` 的情况。

---

### 4. 初始化为 `null` 或 `undefined` 的演化

常见于 `try/catch` 块中：

```typescript
let value = null;         // 初始 any（不是危险的 any）
try {
    value = doSomethingRiskyAndReturnANumber();   // 演化为 number
} catch (e) {
    console.warn('alas!');
}
value;                    // 最终类型：number | null
```

---

### 5. 演化类型的限制与陷阱

#### 5.1 读取尚未演化的变量会报错

```typescript
function range(start: number, limit: number) {
    const nums = [];                // any[]
    if (start === limit) {
        return nums;                // ❌ 错误：nums 隐式具有 any[] 类型
    }
    for (let i = start; i < limit; i++) {
        nums.push(i);
    }
    return nums;                    // OK
}
```

如果在数组被填充之前就尝试读取（或返回），TypeScript 会报错，因为此时类型仍是 `any[]`，而 `any[]` 被认为是“不安全的隐式 any”。

**演化类型只在“写操作”（赋值、push 等）后才会改变类型**。尚未写入时，它仍然是 `any` 或 `any[]`，但**读取时会触发错误**。这不同于普通的 `any`（Item 5），因为演化类型的 `any` 不会像普通 `any` 一样悄悄传播到整个代码库。

#### 5.2 函数调用不会触发演化

```typescript
function makeSquares(start: number, limit: number) {
    const nums = [];            // any[]
    range(start, limit).forEach(i => {
        nums.push(i * i);       // ❌ 错误：nums 仍是 any[]，因为 forEach 回调中的赋值无法触发演化
    });
    return nums;                // ❌ 错误：隐式 any[]
}
```

TypeScript 的演化分析是基于局部控制流的，它无法跨函数边界进行。因此在回调函数内部推入元素，不会让外部数组的类型演化。

**解决方案**：
- 使用 `for-of` 循环（而非 `forEach`），因为 `for-of` 在同一作用域内，演化可以正常工作。
- 更好的做法：使用函数式方法如 `map`，一次性生成数组，从而完全避免演化：

```typescript
function makeSquares(start: number, limit: number) {
    return range(start, limit).map(i => i * i);   // 直接返回 number[]
}
```

这正是 Item 26 所提倡的：使用函数式构造让类型自动流动。

---

### 6. 演化类型的优缺点

**优点**：
- 减少冗余的类型注解，使代码更简洁。
- 对于常见的“构建数组”模式非常方便。

**缺点**：
- 可能导致意外：如果你错误地推入了不同类型，数组类型会变成宽泛的联合类型，这可能不是你想要的。
- 演化分析有限制（不能跨函数调用）。
- 容易让人误以为 `any` 是安全的，但其实演化类型的 `any` 只存在于“未赋值”阶段，一旦读取就会报错。

**建议**：
- 对于简单、局部的数组构建，可以使用演化类型。
- 如果数组最终类型应该是明确的（例如 `number[]`），可以考虑显式注解：`const nums: number[] = [];` 这样任何错误推入都会立即被捕获。
- 至少在函数返回类型上加上注解（Item 18），确保实现错误不会泄露到签名中。

---

### 7. Things to Remember（书中总结）

- TypeScript 的类型通常只能窄化，但初始化为 `null`、`undefined` 或 `[]` 的值允许**演化**。
- 识别并理解这种模式，在适当的时候使用它来减少类型注解。
- 为了更好的错误检查，可以考虑使用显式类型注解来代替演化类型。

---

### 8. 补充说明：与“危险的 any”的区别

Item 5 描述的 `any` 会禁用类型检查并污染整个代码库。而演化类型中的“临时 `any`”只在变量尚未被赋值时存在。一旦你尝试读取它，TypeScript 就会报错，防止它悄悄传播。因此，演化类型是相对安全的。

---

**一句话总结**：**当变量初始化为 `[]`、`null` 或 `undefined` 时，TypeScript 允许其类型随着后续赋值逐步演化（如 `any[]` → `number[]`），这能减少注解，但要小心跨函数调用时演化失效，且最好在返回值上加上类型注解以保证安全。**