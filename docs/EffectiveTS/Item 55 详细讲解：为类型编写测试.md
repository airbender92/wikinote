## Item 55 详细讲解：为类型编写测试

这一节的核心是：**类型声明和类型逻辑也需要测试**。就像你为运行时行为编写单元测试一样，你也应该为你的类型定义、泛型、条件类型等编写测试，以确保它们行为正确、与实现保持同步，并且不会在不经意间引入 `any` 或破坏类型安全。

TypeScript 的类型系统非常强大，允许你在类型层面编写复杂的逻辑（例如条件类型、映射类型、递归类型）。这些逻辑同样可能包含 bug，而且类型声明与运行时实现也可能脱节（尤其是在为 JavaScript 库编写类型声明时）。因此，测试类型是保证类型质量的重要环节。

---

### 1. 为什么需要测试类型？

- **类型中可能存在逻辑错误**：条件类型、泛型约束、递归等都可能出错。
- **类型声明与实现不同步**：对于 JavaScript 库，类型声明是独立编写的，可能与实际 API 行为不一致。
- **回归风险**：当修改类型或重构代码时，可能无意中破坏类型安全，而常规单元测试无法捕捉。

### 2. 两种主要的测试类型的方法

| 方法 | 原理 | 优点 | 缺点 |
|------|------|------|------|
| **内部类型系统测试**（如 `expect-type`、`Type Challenges`） | 利用 TypeScript 的类型系统本身来断言类型是否匹配或相等。 | 无需额外工具，集成在编译过程中，支持重构（自动重命名）。 | 错误信息可能不直观（如 `MISMATCH`）；无法测试类型的显示效果。 |
| **外部工具测试**（如 `dtslint`、`eslint-plugin-expect-type`） | 通过 linter 或单独的工具检查类型注释（如 `$ExpectType`）或 Twoslash 注释。 | 可以测试类型的字符串表示（显示效果）；与编辑器体验一致。 | 需要额外工具；可能对顺序敏感（如 `1\|2` vs `2\|1` 被视为不同）。 |

下面分别介绍这两种方法以及常见陷阱。

---

### 3. 无效/不充分的类型测试方式

#### 3.1 仅调用函数而不检查返回值

```ts
map(['2017','2018','2019'], v => Number(v));
```

这等价于运行时测试中不写断言，只确保不抛出异常。它只能捕获语法错误或参数个数严重不匹配，无法验证返回值类型是否正确。

#### 3.2 用变量声明检查可赋值性

```ts
const lengths: number[] = map(['john','paul'], name => name.length);
```

这需要创建变量，可能触发未使用变量警告。而且它只检查**可赋值性**（assignability），而不是**类型相等**（equality）。可赋值性比相等更宽松：子类型可以赋给父类型。这在很多时候是够用的，但可能隐藏问题：

```ts
assertType<{name: string}[]>(map(beatles, name => ({ name, inYellowSubmarine: name === 'ringo' })));
// 通过，因为 { name, inYellowSubmarine } 可赋值给 { name }，但我们丢失了 inYellowSubmarine 的信息。
```

此外，函数类型可赋值性也有反直觉的行为：`(x: number) => number` 可赋值给 `(a: number, b: number) => number`（因为允许忽略参数）。因此用可赋值性测试可能会误判。

---

### 4. 正确的方式：检查类型相等（type equality）

#### 4.1 使用 `expect-type` 库（推荐）

```ts
import { expectTypeOf } from 'expect-type';

expectTypeOf(map(beatles, name => name.length)).toEqualTypeOf<number[]>();
```

`expectTypeOf` 会检查两个类型是否完全相同（包括 `readonly` 修饰符、元组标签等），而不是仅仅可赋值。它还能检测 `any` 类型：

```ts
const anyVal: any = 1;
expectTypeOf(anyVal).toEqualTypeOf<number>(); // 错误：any 不等于 number
```

#### 4.2 使用 Type Challenges 的 `Equals` 技巧

```ts
type Equals<X, Y> = (<T>() => T extends X ? 1 : 2) extends (<T>() => T extends Y ? 1 : 2) ? true : false;
type Expect<T extends true> = T;

type Test = Expect<Equals<typeof double, (x: number) => number>>;
```

这个技巧利用函数类型的协变性和条件类型，强制 TypeScript 比较两个类型的“真实”相等性。但错误信息不友好，且对某些结构（如交叉类型 `{x:1}&{y:2}` vs `{x:1,y:2}`）可能误判。

---

### 5. 测试回调参数和 `this` 类型

对于像 `map` 这样的函数，需要测试回调的参数类型和 `this` 上下文。使用函数表达式（非箭头函数）可以捕获 `this`。

```ts
expectTypeOf(map(beatles, function(name, i, array) {
  expectTypeOf(name).toEqualTypeOf<string>();
  expectTypeOf(i).toEqualTypeOf<number>();
  expectTypeOf(array).toEqualTypeOf<string[]>();
  expectTypeOf(this).toEqualTypeOf<string[]>();
  return name.length;
})).toEqualTypeOf<number[]>();
```

这要求类型声明中包含正确的 `this` 类型：

```ts
declare function map<U, V>(
  array: U[],
  fn: (this: U[], u: U, i: number, array: U[]) => V
): V[];
```

---

### 6. 处理 `any` 类型的污染

即使通过上述测试，一个 `declare module 'foo';` 这样的通配符模块声明会让整个模块变成 `any`，从而让所有测试都虚假通过。为了检测这种情况，需要**负向测试**（预期某个用法会报错）。

使用 `@ts-expect-error` 注释：

```ts
// @ts-expect-error only takes two parameters
map([1,2,3], x => x*x, 'third parameter');
```

如果这一行没有类型错误，TypeScript 会报错，从而确保我们期望的错误确实存在。这有助于发现意外的 `any` 类型（因为 `any` 会允许额外的参数）。

但 `@ts-expect-error` 是粗糙的：它不能指定具体错误类型，且可能被同一行的其他错误干扰。更好的做法是使用专门的类型测试库，它们可以检测 `any`。

---

### 7. 测试类型显示（display）

有时候，类型的**显示方式**（例如在编辑器悬停时展示的内容）也很重要。例如，你可能希望自定义类型显示为 `{ fooBar: number }` 而不是 `Pick<..., ...> & Omit<...>`。外部工具如 `eslint-plugin-expect-type` 可以通过 Twoslash 注释来测试显示的字符串：

```ts
const spiceGirls = ['scary', 'sporty', 'baby', 'ginger', 'posh'];
// ^? const spiceGirls: string[]
```

它比较的是类型在编辑器中的实际字符串表示，因此可以检测显示问题。

---

### 8. 工具选择建议

| 场景 | 推荐工具 |
|------|----------|
| 为 DefinitelyTyped 贡献类型 | `dtslint`（标准） |
| 为自己的项目测试类型结构和相等性 | `expect-type` + `vitest` 或 `tsd` |
| 需要测试类型的显示字符串 | `eslint-plugin-expect-type` |
| 喜欢挑战类型级编程 | Type Challenges 风格的 `Expect<Equals<...>>` |

---

### 9. 关键总结（Things to Remember）

- **区分可赋值性和相等性**：函数类型、对象类型中，可赋值性比相等更宽松，可能导致误判。
- **测试回调参数和 `this`**：确保回调签名完整。
- **不要自己造轮子**：使用现成的类型测试库。
- **注意负向测试**：使用 `@ts-expect-error` 或库内置功能来检测不应该通过的情况（如 `any`）。
- **对类型显示敏感时**：使用基于字符串比较的工具（如 ESLint 插件）。
- **定期运行类型测试**：像单元测试一样，集成到 CI 中。

测试类型可能比测试运行时行为更棘手，但它能显著提高类型安全的可靠性。借助社区工具，你可以轻松地为你的类型系统编写全面、可维护的测试。