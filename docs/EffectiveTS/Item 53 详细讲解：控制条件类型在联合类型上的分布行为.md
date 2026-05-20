## Item 53 详细讲解：控制条件类型在联合类型上的分布行为

这一节的核心是：**TypeScript 中的条件类型（`T extends U ? X : Y`）在 `T` 是**裸类型参数**时会自动**分布在联合类型**上。这通常很有用（如 Item 52 中的 `double` 函数），但有时会导致错误的结果。你需要知道如何**启用**（默认）和**禁用**（通过将 `T` 包装成 `[T]` 等）分布行为，并注意 `boolean` 和 `never` 的特殊情况。

---

### 1. 条件类型的分布行为（Distributive Conditional Types）

**定义**：当条件类型的检查类型（`T`）是一个**裸类型参数**（即没有用任何其他类型包装，如 `[T]`、`Promise<T>` 等），并且 `T` 是一个联合类型时，条件类型会**自动分布**：对联合的每个成员分别应用条件，最后将结果联合起来。

**示例**：

```ts
type ToArray<T> = T extends any ? T[] : never;
type Result = ToArray<string | number>;  // string[] | number[]
```

等价于：

```ts
(string extends any ? string[] : never) | (number extends any ? number[] : never)
// → string[] | number[]
```

**Item 52 中的 `double` 正是利用了分布**：`T extends string ? string : number` 对 `string | number` 分布后得到 `string | number`。

---

### 2. 何时分布行为不是我们想要的？

书中构造了一个 `isLessThan` 函数，它比较两个值的大小，但允许特殊规则：如果第一个参数是 `Date`，第二个参数可以是 `Date` 或 `number`（时间戳）。

类型定义如下：

```ts
type Comparable<T> =
  T extends Date ? Date | number :
  T extends number ? number :
  T extends string ? string :
  never;

declare function isLessThan<T>(a: T, b: Comparable<T>): boolean;
```

**预期**：
- `isLessThan(new Date(), Date.now())` ✅
- `isLessThan(12, 23)` ✅
- `isLessThan(12, 'B')` ❌（数字与字符串不可比）

**但是**，当 `T` 是 `Date | string` 时，`Comparable<T>` 会**分布**：

```ts
let dateOrStr = Math.random() < 0.5 ? new Date() : 'A';
// T = Date | string
Comparable<Date | string> = 
  (Date extends Date ? Date|number : ...) | (string extends Date ? ... : ...)
  = (Date|number) | (string)
  = Date | number | string
```

因此 `isLessThan(dateOrStr, 'B')` 会通过检查（因为 `'B'` 是 `string`，属于 `Comparable` 的结果）。但这是不合理的：当 `a` 是 `Date` 时，`b` 应该是 `number` 或 `Date`，而不是字符串；当 `a` 是 `string` 时，`b` 应该是 `string`。实际上，我们期望 `Comparable` 对于联合类型给出的是**交集**而不是并集：当 `T = Date | string`，`b` 必须同时满足 `Date` 和 `string` 的约束，即 `never`（没有值能满足）。所以这个调用应该被禁止。

**根本问题**：我们**不想要分布**。我们希望 `Comparable<T>` 对于联合类型 `T1 | T2` 产生 `Comparable<T1> & Comparable<T2>`（交集），而不是 `Comparable<T1> | Comparable<T2>`（并集）。

---

### 3. 如何禁用分布：用 `[T]` 包装

条件类型仅在检查类型是**裸类型参数**时才分布。因此，要禁用分布，只需将 `T` 包装在另一个类型中，例如单元素元组 `[T]`。

```ts
type Comparable<T> =
  [T] extends [Date] ? Date | number :
  [T] extends [number] ? number :
  [T] extends [string] ? string :
  never;
```

现在 `[Date | string] extends [Date]` 不是裸类型，所以不会分布。TypeScript 会检查整个联合类型是否可赋值给 `[Date]`？`Date | string` 不能赋值给 `Date`，所以条件为假；继续检查下一个。最终所有条件都不成立，结果是 `never`。这正是我们想要的：当 `T` 是 `Date | string` 时，`Comparable<T>` 变为 `never`，从而禁止调用。

**注意**：`[A] extends [B]` 等价于 `A extends B`（元组类型是协变的），但前者**不会触发分布**。

---

### 4. 相反的情况：想要分布但当前没有分布

有时你写的条件类型不会自动分布（因为检查类型不是裸类型参数），但你希望它对联合分布。书中用 `NTuple<T, N>` 示例说明。

`NTuple<T, N>` 目标是生成一个包含 `N` 个 `T` 的元组类型。实现使用递归累加器：

```ts
type NTupleHelp<T, N extends number, Acc extends T[]> =
  Acc['length'] extends N ? Acc : NTupleHelp<T, N, [T, ...Acc]>;
type NTuple<T, N extends number> = NTupleHelp<T, N, []>;
```

当 `N` 是单个数字时正常工作（例如 `NTuple<bigint, 2>` 得到 `[bigint, bigint]`）。但当 `N` 是联合 `2 | 3` 时，期望得到 `[bigint, bigint] | [bigint, bigint, bigint]`，但实际上只得到 `[bigint, bigint]`。

原因：`Acc['length'] extends N` 中的 `N` 是联合类型，但条件类型的分布要求检查类型是**裸类型参数**，而这里 `Acc['length']` 不是类型参数，因此不会分布。结果就是 `Acc['length']` 与 `2 | 3` 的比较被视为一次整体比较，而不是分别对 `2` 和 `3`。

**修复**：在外层添加一个**总是为真的分布条件**，强制分布：

```ts
type NTuple<T, N extends number> =
  N extends number          // 这会在 N 是联合时分布
    ? NTupleHelp<T, N, []>
    : never;
```

因为 `N extends number` 总是真（`N` 被约束为 `number`），但因为它是一个**裸类型参数**的检查，所以当 `N` 是联合时，它会分布：先对 `2` 求 `NTupleHelp`，再对 `3` 求 `NTupleHelp`，然后联合结果。这样就能得到正确的元组联合。

**关键**：即使条件总是真，这个额外的条件层也能“激活”分布。

---

### 5. `boolean` 的分布陷阱

`boolean` 在 TypeScript 内部是 `true | false` 的联合。因此：

```ts
type CelebrateIfTrue<V> = V extends true ? 'Huzzah!' : never;
type Surprise = CelebrateIfTrue<boolean>;
```

展开：

```ts
CelebrateIfTrue<true> | CelebrateIfTrue<false> = 'Huzzah!' | never = 'Huzzah!'
```

结果竟然是 `'Huzzah!'`，这通常不是期望的（你可能希望 `never` 或 `'Huzzah!' | '…'`）。要禁用分布，同样用 `[V] extends [true]`。

---

### 6. `never` 的分布陷阱

当条件类型检查一个空的联合（即 `never`）时，由于没有成员可分布，结果就是 `never`，无论条件如何。

```ts
type AllowIn<T> = T extends {password: "open-sesame"} ? "Yes" : "No";
type N = AllowIn<never>; // never
```

这可以理解为：`F<never> = never` 是所有分布式条件类型的性质，因为 `never` 是空联合。如果你不希望这样，同样可以用 `[T]` 包装禁用分布。

---

### 7. 总结：控制分布的方法

| 需求 | 实现 | 示例 |
|------|------|------|
| 启用分布（默认） | 使用裸类型参数作为检查类型 | `T extends U ? ...` |
| 禁用分布 | 将类型参数包装在元组中 | `[T] extends [U] ? ...` |
| 强制分布（即使原本不分布） | 在最外层添加一个总是真的裸类型条件 | `N extends number ? F<N> : never` |

**实践建议**：
- 编写条件类型时，先思考：我希望联合输入得到并集（分布）还是交集（或整体判断）？
- 如果希望整体判断（如 `Comparable<T>` 需要交集），就用 `[T]` 禁用分布。
- 如果希望联合输入分别处理再组合（如 `NTuple`），但实现中无法直接分布，就套一层分布条件。
- 注意 `boolean` 和 `never` 在分布下的特殊行为，必要时用 `[T]` 避免意外。

**最终原则**：分布是强大但需要显式控制的工具。理解它，你就能写出既简洁又准确的高级类型。