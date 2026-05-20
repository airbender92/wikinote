## Item 52 详细讲解：优先使用条件类型而非重载签名

这一节的核心是：**当函数的参数和返回值之间存在类型关系（例如输入 `number` 返回 `number`，输入 `string` 返回 `string`）时，条件类型（conditional type）比重载签名（overload signatures）更安全、更简洁，并且能正确处理联合类型。**

书中通过一个简单的 `double` 函数示例，逐步展示了从联合类型 → 泛型 → 重载 → 条件类型的演进，并指出了每种方式的优缺点。

---

### 1. 问题：`double` 函数的类型

```ts
function double(x) { return x + x; }
```

- 输入 `number` → 输出 `number`（例如 `double(12) === 24`）
- 输入 `string` → 输出 `string`（例如 `double('x') === 'xx'`）
- 输入 `string | number` → 输出 `string | number`

目标是写出准确的类型声明。

---

### 2. 尝试一：使用联合类型（不精确）

```ts
declare function double(x: string | number): string | number;
```

**问题**：丢失了输入与输出之间的具体关系。调用 `double(12)` 得到 `string | number`，而不是 `number`。这迫使调用者进行不必要的类型收窄。

---

### 3. 尝试二：使用泛型（不准确）

```ts
declare function double<T extends string | number>(x: T): T;
```

- 当传入字面量 `12` 时，`T` 被推断为 `12`，返回类型也是 `12` —— 这不对，因为 `double(12)` 应该返回 `24`（`number`），而不是字面量 `12`。
- 当传入 `'x'` 时，返回类型是 `'x'`，但实际应该是 `'xx'`。

这种类型**过于精确**，以至于**不准确**（Item 40 强调不精确优于不准确）。因此是错误的。

---

### 4. 尝试三：使用重载签名（不能处理联合类型）

```ts
declare function double(x: number): number;
declare function double(x: string): string;
```

- 调用 `double(12)` → `number` ✅
- 调用 `double('x')` → `string` ✅
- 但是调用 `double(x)` 其中 `x: string | number` 会出错：

```ts
function f(x: string | number) {
  return double(x);  // 错误：string|number 不能赋给 string
}
```

原因是 TypeScript 按顺序匹配重载：先尝试 `double(x: number)`，不匹配；再尝试 `double(x: string)`，`string|number` 不能赋给 `string`，所以失败。即使第三个重载 `double(x: string|number)` 可以解决，但会导致代码重复且不能自动适应新的联合成员。

---

### 5. 最佳方案：使用条件类型

```ts
declare function double<T extends string | number>(
  x: T
): T extends string ? string : number;
```

**解释**：
- `T` 是输入的类型（可以是 `string`、`number`、字面量 `'x'`、`12` 或联合类型 `string|number`）。
- 返回值是一个**条件类型**：如果 `T` 是 `string` 的子类型，则返回 `string`；否则返回 `number`。

**效果**：
- `double(12)` → `T` 是 `12`，`12 extends string ? ... : number` → 返回 `number` ✅
- `double('x')` → `'x' extends string` → 返回 `string` ✅
- `double(x: string | number)` → 条件类型**分布在联合上**：
  - `(string|number) extends string ? string : number`
  - 等价于 `(string extends string ? string : number) | (number extends string ? string : number)`
  - 结果：`string | number` ✅

**关键特性**：条件类型自动**分布**（distribute）于联合类型。这是重载无法轻易做到的。

---

### 6. 条件类型 vs 重载的总结

| 特性 | 重载 | 条件类型 |
|------|------|----------|
| 支持精确的输入输出关系 | ✅ 可以（需为每个类型写一条） | ✅ 通过条件表达式 |
| 自动处理联合类型 | ❌ 需要额外手动添加联合重载 | ✅ 自动分布 |
| 代码重复 | 多（每个类型一条） | 少（一个泛型） |
| 维护成本 | 高（增加新类型需加新重载） | 低（只需修改条件逻辑） |
| 可读性 | 简单情况直观 | 需要理解条件类型语法 |

---

### 7. 实现条件类型函数的小技巧

TypeScript 不能自动推断条件类型的返回值，因此函数实现中通常需要类型断言或重载技巧。

**推荐模式**：对外使用条件类型签名，对内使用更宽松的实现签名（单重载）。

```ts
// 对外签名（条件类型）
function double<T extends string | number>(
  x: T
): T extends string ? string : number;

// 实现签名（宽松联合类型）
function double(x: string | number): string | number {
  return typeof x === 'string' ? x + x : x + x;
}
```

这样实现内部使用联合类型，避免了复杂的类型断言，同时对外提供了精确的条件类型。TypeScript 会检查两个签名是否兼容。

---

### 8. 何时仍可使用重载？

- 当函数的不同签名之间**没有逻辑上的统一关系**，例如 `readFile` 的回调版和 Promise 版。此时用两个不同名称的函数可能更清晰。
- 当联合类型的情况不现实（例如参数永远不会是联合类型），且重载数量很少。

但大多数情况下，条件类型是更优选择。

---

### 9. 核心要点

- **条件类型可以看作类型空间的 `if` 语句**，非常适合表达输入输出类型之间的依赖关系。
- **条件类型自动分布联合类型**，这是重载难以做到的。
- **优先使用条件类型**，除非函数签名之间完全不同且没有公共逻辑。
- **实现条件类型函数时**，可以使用单重载技巧，在内部使用更宽松的类型，避免断言。

**最终建议**：下次你需要为一个函数写多个重载时，先停下来想一想是否可以用一个泛型 + 条件类型来替代。它通常会更简洁、更强大、更易维护。