## Item 50 详细讲解：将泛型视为类型之间的函数

这一节的核心是：**泛型（generic types）就是类型层面的“函数”**。就像值层面的函数接收值参数并返回值，类型层面的泛型接收类型参数并返回一个新的类型。理解这种类比，可以帮助你更好地设计、约束和文档化泛型，并避免常见的错误。

---

### 1. 泛型即类型函数

在值空间（value-land）中，函数封装了逻辑，接收输入（参数）并产生输出（返回值）：

```ts
function add(x: number, y: number): number {
  return x + y;
}
```

在类型空间（type-land）中，**泛型**做类似的事情：接收一个或多个**类型参数**，产生一个**具体类型**。

```ts
type MyPartial<T> = { [K in keyof T]?: T[K] };
```

这里 `T` 是类型参数，`MyPartial<T>` 是一个泛型类型。当你“实例化”它（即 `MyPartial<Person>`），就得到了一个具体类型（`{ name?: string; age?: number }`）。

**类比**：
- 调用函数：`add(1, 2)` → 值 `3`
- 实例化泛型：`MyPartial<Person>` → 类型 `{ name?: string; age?: number }`

封装的好处：使用者不需要知道内部实现（`{ [K in keyof T]?: T[K] }`），只要知道它会将全部属性变为可选即可，就像你不需要知道 `Math.cos` 的实现细节也能使用它。

---

### 2. 定义泛型时遇到的常见错误及解决方法

书中以自己实现 `Pick<T, K>` 为例，演示了从错误到正确的过程。

#### 错误版本 1：没有约束（导致内部错误）

```ts
type MyPick<T, K> = { [P in K]: T[P] };
// Type 'K' is not assignable to type 'string | number | symbol'
// Type 'P' cannot be used to index type 'T'
```

**问题**：
- TypeScript 不知道 `K` 必须是 `string | number | symbol` 的子类型（才能作为映射类型的键）。
- TypeScript 不知道 `P` 可用来索引 `T`。

#### 错误版本 2：忽略错误（不推荐）

```ts
// @ts-expect-error  // 不要这样做！
type MyPick<T, K> = { [P in K]: T[P] };
```

尽管编译器报错，但仍然可以使用（类似于类型错误不阻止代码生成）。但这很危险：`MyPick<Person, 'firstName'>` 会得到 `{ firstName: unknown }`，`MyPick<'age', Person>` 会得到 `{}`。没有类型错误，但结果错误——这比报错更糟糕。

#### 错误版本 3：用交集强制通过（不推荐）

```ts
type MyPick<T, K> = { [P in K & PropertyKey]: T[P & keyof T] };
```

这里 `PropertyKey = string | number | symbol`。`K & PropertyKey` 强制 `K` 成为合法键类型，`P & keyof T` 强制 `P` 能索引 `T`。这类似于类型层面的 `as any`：它压制了实现中的错误，但语义混乱，且当 `K` 不是 `keyof T` 的子集时，`T[P & keyof T]` 会变成 `never`，不是合理的错误信息。

#### 正确版本：使用 `extends` 约束

```ts
type MyPick<T extends object, K extends keyof T> = {
  [P in K]: T[P];
};
```

**解释**：
- `T extends object`：`T` 必须是对象类型（不能是 `'age'` 或 `Person[]`）。
- `K extends keyof T`：`K` 必须是 `T` 的键的子集（即合法的属性名联合）。

现在：
- 实现内部没有错误：`K` 保证是 `string | number | symbol` 的子类型，`P in K` 合法；`T[P]` 合法。
- 错误用法会在**使用处**报出有意义的错误：
  - `MyPick<Person, 'firstName'>`：`'firstName'` 不满足 `keyof Person`（因为 `Person` 只有 `'name'|'age'`）。
  - `MyPick<'age', Person>`：`'age'` 不满足 `object` 约束。

**结论**：为泛型参数添加约束（`extends`）既能消除实现内部的错误，又能为用户提供更好的错误消息。这与值层面为函数参数添加类型注解（例如 `function add(x: number, y: number)`）是同样的道理。

---

### 3. 命名和文档化泛型

- **命名规则**：短作用域用短名（`T`, `K`），长作用域（例如跨多个方法的泛型类）用有意义的名称（`Key`, `Value`）。
- **TSDoc**：使用 `@template` 标签描述类型参数，以便在编辑器中显示提示（图 6-1）。

```ts
/**
 * 从对象类型中选取一组属性
 * @template T 原始对象类型
 * @template K 要选取的键（通常是字符串字面量联合）
 */
type MyPick<T extends object, K extends keyof T> = ...
```

---

### 4. 泛型与集合

TypeScript 的类型是值的集合（Item 7）。泛型则是**集合之间的函数**。例如 `MyPartial<T>` 接收一个集合 `T`（例如 `Person` 的所有可能值），并返回一个新的集合（所有 `Person` 值中每个属性都可选的值的集合）。

由于输入可能是联合类型，泛型必须正确处理联合分布（Item 53）。例如 `Partial<number | string>` 的结果是 `Partial<number> | Partial<string>`，即 `number | string`（因为 `Partial<number>` 仍然是 `number`）。理解这一点有助于避免意外。

---

### 5. 泛型函数与泛型类的优势

- **泛型函数**：参数类型可以被**推断**，调用更简洁。例如 `pick(p, 'age')` 自动推断 `T = Person`，`K = 'age'`，无需显式写出 `<Person, 'age'>`。这是类型推断的一大便利。

- **泛型类**：类型参数在构造时绑定，后续方法可以共享该类型，而无需重复传递。例如 `Box<T>` 实例化后，其 `value` 属性类型固定为 `T`。

```ts
class Box<T> {
  constructor(public value: T) {}
}
const dateBox = new Box(new Date());  // Box<Date>
```

这与 Item 28 中用类创建新的推断站点的思想一致。

---

### 6. 高级话题：高阶类型（Higher-Kinded Types）

值空间有高阶函数（`map`, `filter`），它们接收函数作为参数。类型空间目前没有直接的高阶类型（即“接收泛型类型作为参数的泛型”），这被称为“更高阶类型”。TypeScript 不支持它们，但你可以通过映射类型等模式绕过。

例如，你想写一个 `MapValues`，将对象所有属性值类型应用某个泛型 `F`：

```ts
type MapValues<T extends object, F> = {
  [K in keyof T]: F<T[K]>;  // 错误：F 不是泛型
};
```

由于不能将 `F` 声明为“泛型类型”，无法直接实现。但你可以内联具体转换（例如使用 `Promise<T[K]>` 而不是 `F<T[K]>`）。所以，缺少高阶类型限制了表达的灵活性，但不限制你能实现的功能——只是更啰嗦。

---

### 7. 实践建议

| 做法 | 说明 |
|------|------|
| 为泛型参数添加 `extends` 约束 | 提高安全性和错误信息质量 |
| 为重要泛型写 TSDoc（`@template`） | 改善编辑器体验 |
| 命名合理（短作用域用短名，长作用域用长名） | 提高可读性 |
| 记住泛型是类型层面的函数 | 有助于思考输入输出关系 |
| 测试泛型（Item 55） | 确保行为正确 |

---

### 8. 总结

- 泛型就是类型空间的函数：输入类型参数，输出具体类型。
- 使用 `extends` 约束参数，类似函数参数的类型注解。
- 命名和文档化与值层面同等重要。
- 泛型函数和类能够利用类型推断，让使用者无需关心底层类型操作。
- 虽然缺少高阶类型，但通过映射类型等依然能实现几乎所有需要。

**最终建议**：每当你定义一个泛型，停下来想一想：“这是一个接受什么输入、产生什么输出的类型函数？” 然后添加恰当的约束和文档，就像你对待一个普通函数那样认真。

----

你提到的这个代码片段是 TypeScript 中一个常见的高级诉求：**想要将某个泛型类型（如 `Promise`、`Array`、`Partial` 等）应用到另一个类型的属性上**，但 TypeScript 目前不支持这种“高阶类型参数”（higher-kinded types）。

### 为什么 `F<T[K]>` 是错误的？

当你写：

```ts
type MapValues<T extends object, F> = {
  [K in keyof T]: F<T[K]>;
};
```

- `F` 是一个类型参数，它代表**一个具体的类型**，例如 `string`、`number`、`Promise<Date>` 等。
- `F<T[K]>` 试图将 `F` 当作一个**泛型类型**来调用，即把 `T[K]` 作为类型参数传给 `F`。
- 但 `F` 本身不是泛型——它只是一个类型，不能被参数化。TypeScript 不知道 `F` 是否接受类型参数，也不知道它接受几个参数。

**类比值空间**：这就像你写了一个函数，它接受一个参数 `f`，然后尝试调用 `f(42)`。如果 `f` 是 `Math.sqrt`（一个函数），那么没问题。但如果调用者传入的是数字 `5`，那么 `5(42)` 就是错误的。TypeScript 无法静态保证 `F` 是一个泛型类型，因此禁止这种写法。

### 期望的行为 vs 实际限制

你可能希望这样使用 `MapValues`：

```ts
type Original = { a: number; b: boolean };
type Mapped = MapValues<Original, Promise>;  // 期望 { a: Promise<number>; b: Promise<boolean> }
```

但在 TypeScript 中，**不能将 `Promise` 本身作为类型参数传递**，因为 `Promise` 是一个泛型类型（它需要类型参数）。你可以传递 `Promise<number>`，但那是一个具体类型，不能保留“泛型”的性质。

**实际上，你只能这样使用**：

```ts
type Mapped = MapValues<Original, Promise<number>>;
// 结果：{ a: Promise<number>; b: Promise<number> }
```

但这显然不是你想要的 —— 它把属性的原类型都丢掉了，全换成了 `Promise<number>`。

### 如何实现类似的功能？

如果你确实需要将某个泛型（如 `Promise`、`Partial`、`Readonly`）应用到对象的所有属性上，可以**硬编码**这个转换，而不是使用一个抽象的 `F`：

```ts
type MapValuesToPromise<T extends object> = {
  [K in keyof T]: Promise<T[K]>;
};
```

这就是一个具体的、可工作的类型。如果你想让 `F` 可配置，在 TypeScript 目前的能力范围内，你只能通过**映射类型 + 硬编码已知的泛型**，或者使用**条件类型 + 高阶类型模拟**（但极其复杂且有限）。例如，你可以定义一个类型，从 `"Promise"` 字符串映射到 `Promise` 类型，但依然无法做到完全通用。

### 书中的说法

作者说：

> At the time of this writing, the answer is no. These would be “functions on functions on types” or “higher-kinded types” as they’re usually known.

意思是 TypeScript **不支持高阶类型**。所以你不能写一个像 `MapValues` 这样接受另一个泛型作为参数的泛型。这是 TypeScript 类型系统的一个已知限制。好消息是，大多数情况下你可以通过写具体的映射类型来绕过，虽然重复但可控。

### 总结

- **错误原因**：`F` 是一个类型，不是泛型，不能接受类型参数。
- **本质**：TypeScript 不支持高阶类型（higher-kinded types）。
- **替代方案**：直接写具体的映射类型，例如 `Promise<T[K]>`、`Partial<T[K]>` 等，而不是试图抽象 `F`。

希望这个解释澄清了你的疑惑。