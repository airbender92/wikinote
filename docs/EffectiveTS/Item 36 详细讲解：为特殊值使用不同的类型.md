## Item 36 详细讲解：为特殊值使用不同的类型

这一节的核心是：**不要使用与正常值属于同一类型但含义特殊的值（例如用 `-1` 表示“未找到”），因为 TypeScript 无法区分它们，会隐藏逻辑错误。应该使用 `null` 或 `undefined`，或者使用可辨识联合（tagged union）来显式表示特殊状态。**

书中通过两个例子来说明：一个是数组版的 `splitAround` 函数，另一个是商品价格字段。

---

### 例子一：`splitAround` 函数（数组分割）

#### 初始实现（有 bug）

```ts
function splitAround<T>(vals: readonly T[], val: T): [T[], T[]] {
  const index = vals.indexOf(val);
  return [vals.slice(0, index), vals.slice(index+1)];
}
```

这个函数期望在数组中找到 `val`，然后返回 `[val 之前的元素, val 之后的元素]`。例如：

```ts
splitAround([1,2,3,4,5], 3)  // 返回 [[1,2], [4,5]]
```

**问题**：如果 `val` 不在数组中，`indexOf` 返回 `-1`。`slice(0, -1)` 会截取到倒数第二个元素（即去掉最后一个元素），`slice(-1+1)` = `slice(0)` 返回整个数组的副本。因此：

```ts
splitAround([1,2,3,4,5], 6)  // 返回 [[1,2,3,4], [1,2,3,4,5]]
```

这显然不是预期的行为（也许应该返回整个数组和一个空数组？或者抛出错误？）。更严重的是，**TypeScript 没有报任何错**，因为 `indexOf` 的返回类型是 `number`，`-1` 是合法的数字，`slice` 也能处理负数。这个 bug 完全被类型系统忽略了。

#### 根本原因

`indexOf` 用了一个**特殊值**（`-1`）来表示“未找到”，但这个特殊值与正常索引值的类型相同（都是 `number`）。TypeScript 无法区分 `-1` 和 `3`，因此不能提醒开发者处理未找到的情况。

#### 改进方案：用 `null` 表示“未找到”

我们可以封装一个 `safeIndexOf`，返回 `number | null`，其中 `null` 表示未找到：

```ts
function safeIndexOf<T>(vals: readonly T[], val: T): number | null {
  const index = vals.indexOf(val);
  return index === -1 ? null : index;
}
```

然后修改 `splitAround` 使用这个新函数：

```ts
function splitAround<T>(vals: readonly T[], val: T): [T[], T[]] {
  const index = safeIndexOf(vals, val);
  return [vals.slice(0, index), vals.slice(index+1)];
  // ~~~~~ ~~~~~ 错误：'index' 可能为 'null'
}
```

现在 TypeScript 报错了！它提醒我们 `index` 可能是 `null`，我们没有处理这种情况。这正是我们想要的 —— 类型系统强制我们考虑“未找到”的分支。

**修复**：显式处理 `null` 情况

```ts
function splitAround<T>(vals: readonly T[], val: T): [T[], T[]] {
  const index = safeIndexOf(vals, val);
  if (index === null) {
    return [[...vals], []];   // 约定：未找到时，返回原数组和一个空数组
  }
  return [vals.slice(0, index), vals.slice(index+1)];
}
```

现在，无论选择什么行为（抛出异常、返回原数组+空数组等），开发者都必须明确决定。TypeScript 迫使你思考边界情况，而不是默默产生错误结果。

---

### 例子二：商品价格中的特殊值

#### 糟糕的设计：用 `-1` 表示“价格未知”

```ts
interface Product {
  title: string;
  /** Price in dollars, or -1 if unknown */
  priceDollars: number;
}
```

**问题**：
- `priceDollars` 是 `number` 类型，所以 `-1` 是合法值。但业务逻辑中，`-1` 不是一个价格，而是“未知”的标记。
- 任何处理价格的函数（比如计算总价、应用折扣）都必须记得检查 `priceDollars === -1`，否则就会把 `-1` 当作实际价格进行算术运算，导致错误（例如给顾客退款 `-1` 美元）。
- TypeScript 无法帮助你，因为 `-1` 和 `42` 都是 `number`。

**后果**：某天你忘记检查 `-1`，把未知价格的商品的 `priceDollars` 当作实际价格加到订单中，就会造成财务错误。

#### 正确做法：使用 `null` 或 `undefined` 表示缺失

```ts
interface Product {
  title: string;
  priceDollars: number | null;  // null 表示价格未知
}
```

现在 `priceDollars` 的类型明确包含 `null`，任何使用价格的地方都必须先检查是否为 `null`，否则 TypeScript 会报错。

```ts
function applyDiscount(product: Product, discountPercent: number) {
  if (product.priceDollars === null) {
    return null;  // 或抛出异常，或跳过
  }
  return product.priceDollars * (1 - discountPercent / 100);
}
```

#### 什么时候不能用 `null`/`undefined`？

如果特殊状态不止一种（例如“加载中”、“错误”、“数据为空”），那么 `null` 或 `undefined` 就不够表达了。此时应使用**可辨识联合**（见 Item 29）：

```ts
type PriceState =
  | { status: 'loading' }
  | { status: 'error'; error: string }
  | { status: 'ready'; priceDollars: number };

interface Product {
  title: string;
  price: PriceState;
}
```

这样状态是显式的，TypeScript 会强制你处理所有情况。

---

### 核心原则总结

| 做法 | 问题 | 推荐替代 |
|------|------|----------|
| 用 `-1`、`0`、`""` 等表示特殊含义 | 与正常值类型相同，无法区分，容易遗漏检查 | 使用 `null` 或 `undefined` |
| 用 `null` 或 `undefined` 表示多种特殊状态 | 含义模糊，无法区分“错误”与“加载中” | 使用可辨识联合（tagged union） |
| 使用 `strictNullChecks: false` | `null` 被允许赋值给任何类型，类似特殊值问题 | 开启 `strictNullChecks`，用 `\| null` 显式标记 |

**最终建议**：
- 永远不要用 `-1`、`0`、`""` 这类与正常值同类型的值作为特殊标记。**使用 `null` 或 `undefined`**，让类型系统强制检查。
- 如果有多个不同的特殊状态，使用**可辨识联合**，每个状态有唯一的标签字段。
- 始终开启 `strictNullChecks`，让 `null` 和 `undefined` 成为显式的类型成员。

这其实和 Item 29 一脉相承：**让类型只能表示有效的状态**。特殊值 `-1` 是一个无效的状态（因为它不是一个价格），但类型却允许它存在。用 `null` 或 `undefined` 就把这种无效性显式化了，类型系统就能帮助你防止错误。