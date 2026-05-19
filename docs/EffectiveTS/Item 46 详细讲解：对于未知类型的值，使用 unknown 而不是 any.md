## Item 46 详细讲解：对于未知类型的值，使用 `unknown` 而不是 `any`

这一节的核心是：**`unknown` 是 `any` 的类型安全替代品。当你无法确定一个值的具体类型时（例如解析 YAML、JSON、外部 API 响应），应该返回 `unknown` 而不是 `any`。** `unknown` 强制调用者在使用该值之前进行类型检查（类型断言、`instanceof`、类型守卫等），从而避免了 `any` 带来的“传染性”和运行时错误。

书中通过 YAML 解析器、GeoJSON 的 `properties` 字段、数组长度函数等例子，清晰地展示了 `unknown` 的优势。

---

### 1. 问题示例：YAML 解析器返回 `any`

假设我们要写一个 YAML 解析函数。YAML 可以表示任意数据（类似 JSON）。受 `JSON.parse` 的影响，我们可能写成：

```ts
function parseYAML(yaml: string): any {
  // 实际解析逻辑省略
}
```

**问题**：返回 `any` 意味着类型检查完全失效。调用方可以随意访问任何属性、调用任何方法，即使运行时不存在也不会报错。

```ts
const book = parseYAML(`
name: Jane Eyre
author: Charlotte Brontë
`);

console.log(book.title);     // 类型检查通过，运行时打印 undefined
book('read');                // 类型检查通过，运行时抛出 "book is not a function"
```

这里 `book` 被推断为 `any`，后续所有操作都不受类型检查保护。错误被推迟到运行时，而且很难定位。

**根本问题**：`any` 同时是所有类型的子类型和超类型（它既可以赋值给任何类型，也可以接收任何类型）。这破坏了类型系统的集合模型。

---

### 2. 改进：返回 `unknown`

```ts
function safeParseYAML(yaml: string): unknown {
  return parseYAML(yaml);
}

const book = safeParseYAML(`...`);
```

现在 `book` 的类型是 `unknown`。你不能直接访问它的属性或调用它：

```ts
console.log(book.title);     // 错误：'book' 类型为 'unknown'
book('read');                // 错误：'book' 类型为 'unknown'
```

**强制使用者显式处理**：使用者必须通过类型断言或类型收窄来告诉 TypeScript 他们知道的实际类型。

```ts
const book = safeParseYAML(`...`) as Book;  // 类型断言
console.log(book.title);  // 现在安全，但断言可能出错
```

或者更安全的方式：使用类型守卫收窄：

```ts
function isBook(value: unknown): value is Book {
  return typeof value === 'object' && value !== null &&
         'name' in value && 'author' in value;
}

const raw = safeParseYAML(`...`);
if (isBook(raw)) {
  console.log(raw.author);  // 类型安全
}
```

---

### 3. `unknown` 的集合论解释（复习 Item 7）

- `any` 是所有集合的**子集**（可以赋值给任何类型）同时又是所有集合的**超集**（任何类型都可以赋值给它）。这在集合论中是不可能的，所以 `any` 实际上“跳出”了类型系统。
- `unknown` 是**全集**（所有类型都可以赋值给 `unknown`），但它**不是**任何其他类型的子集（你不能把 `unknown` 赋值给 `string` 或 `number`，除非先收窄）。因此它是类型安全的“顶层类型”（top type）。
- `never` 是**空集**（没有任何值可以赋值给 `never`），但它可以赋值给任何类型。它是“底层类型”（bottom type）。

**结论**：`unknown` 是“我知道有这个值，但我现在不知道它具体是什么，你必须先检查再使用”。`any` 是“我放弃所有类型检查，随便你怎么用”。

---

### 4. 其他适合使用 `unknown` 的场景

#### 4.1 GeoJSON 的 `properties` 字段

GeoJSON 规范中，每个要素（Feature）的 `properties` 是一个自由格式的 JSON 对象，没有任何预定义结构。因此应该用 `unknown`：

```ts
interface Feature {
  type: 'Feature';
  geometry: Geometry;
  properties: unknown;  // ✅ 而不是 any
}
```

使用者需要根据实际情况收窄 `properties` 的类型。

#### 4.2 检查数组长度的函数

如果你只关心数组长度，不关心元素类型：

```ts
function isSmallArray(arr: readonly unknown[]): boolean {
  return arr.length < 10;
}
```

使用 `unknown[]` 比 `any[]` 安全，因为你不会意外地访问元素的方法（例如 `arr[0].toFixed()`）而不先检查类型。

---

### 5. 如何收窄 `unknown` 类型

除了直接使用 `as T` 断言，还可以使用 JavaScript 运行时检查：

- `instanceof`：

```ts
function processValue(value: unknown) {
  if (value instanceof Date) {
    value;  // 类型收窄为 Date
  }
}
```

- `typeof` + 属性检查（用户定义类型守卫）：

```ts
function isBook(value: unknown): value is Book {
  return typeof value === 'object' && value !== null &&
         'name' in value && 'author' in value;
}
```

注意：TypeScript 要求先证明 `value` 是非空对象，才能使用 `in` 操作符。

---

### 6. 避免“只返回泛型”的假安全

有时人们会写：

```ts
function safeParseYAML<T>(yaml: string): T {
  return parseYAML(yaml);
}
```

调用时 `const book = safeParseYAML<Book>(yaml)`。这看起来比 `as Book` 更“优雅”，但实际上**没有任何类型检查**——如果 YAML 内容不是 `Book`，程序仍然会在运行时出错，而 TypeScript 不会警告。这种“返回泛型”的模式和直接断言一样不安全，却给人一种虚假的安全感。Item 51 会详细讨论这种不必要的泛型。

**正确做法**：返回 `unknown`，让调用者显式断言或收窄。

---

### 7. `unknown` 与 `{}`、`object` 的区别

你可能见过用 `{}` 或 `object` 表示“任何非空值”，但它们和 `unknown` 不同：

| 类型 | 包含的值 | 不包含的值 | 可赋值性 |
|------|----------|------------|----------|
| `unknown` | 所有值 | 无 | 任何类型可赋值给 `unknown`，但 `unknown` 只能赋值给 `unknown`（和 `any`） |
| `{}` | 除了 `null` 和 `undefined` 以外的所有值 | `null`, `undefined` | 任何非空值可赋值给 `{}`，`{}` 可赋值给 `object`（受限） |
| `object` | 所有非原始类型（对象、数组、函数） | `null`, `undefined`, `string`, `number`, `boolean`, `symbol`, `bigint` | 只能赋值给 `object` 或更窄的类型 |

**建议**：除非你有意排除 `null` 和 `undefined`，否则 `unknown` 通常比 `{}` 或 `object` 更合适，因为它是真正的全集，不需要担心空值问题。

---

### 8. 双断言中使用 `unknown` 代替 `any`

当你需要将一个类型强制转换为另一个完全不相关的类型时（例如 `Foo` 到 `Bar`），通常写：

```ts
const bar = foo as any as Bar;
```

这种“双断言”可以换成更温和的 `unknown`：

```ts
const bar = foo as unknown as Bar;
```

语义相同，但 `as unknown` 不会像 `as any` 那样引起恐惧反应，而且意图更清晰：先转成“未知”，再转成目标类型。

---

### 9. 核心原则总结

| 场景 | 错误做法 | 正确做法 |
|------|----------|----------|
| 解析未知格式的数据（YAML、JSON 等） | 返回 `any` | 返回 `unknown` |
| 函数参数是“任意值但不需要具体操作” | `value: any` | `value: unknown` |
| 需要遍历但不操作元素的数组 | `arr: any[]` | `arr: unknown[]` |
| 希望强制调用者进行类型检查 | 使用 `any` 并依赖文档 | 使用 `unknown`，让类型系统强制收窄 |
| 双断言转换 | `foo as any as Bar` | `foo as unknown as Bar` |

**最终建议**：每当你想写 `any` 时，先问自己：是否可以用 `unknown`？如果能，就用 `unknown`；如果不能用（例如需要直接访问属性且无法收窄），再考虑更具体的 `any[]` 或 `Record<string, any>` 等（Item 44）。`unknown` 是 `any` 的“软约束”版本，它能帮你保留类型检查的习惯，而不是完全放弃。