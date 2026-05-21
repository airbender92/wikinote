## Item 56 详细讲解：关注类型的显示方式

这一节的核心是：**作为库的作者，你不仅需要保证类型的正确性（assignability），还要关注类型在编辑器中的显示效果**。一个类型可能有多种等价的显示方式，其中一些比另一些更清晰、更易读。TypeScript 提供了一些技巧（如 `Resolve` 类型）来“展平”复杂的类型别名，隐藏实现细节，让用户看到更直观的类型。同时，你可能需要处理特殊情况（如 `K extends never`）来进一步改善显示。最后，还应该为类型的显示编写测试，防止回归。

---

### 1. 为什么类型显示很重要？

- 当你使用一个库时，鼠标悬停在某个类型上看到的信息直接影响你的开发体验。
- 复杂的类型（如 `Partial<Pick<T, K>> & Omit<T, K>`）虽然正确，但难以理解。
- 用户更希望看到直观的、展开后的类型（如 `{ title?: string; commentId: number; content: string }`）。

书中通过两个例子展示了同一类型的不同显示方式：
- 联合类型中成员顺序可能不同（`'1' | '2' | '3'` vs `'2' | '1' | '3'`），但可读性差异不大。
- 自定义泛型 `PartiallyPartial` 显示为 `Partial<Pick<...>> & Omit<...>`，非常“实现化”，用户无法直接看出哪些字段可选、哪些字段存在。

---

### 2. 问题示例：`PartiallyPartial` 的糟糕显示

```ts
type PartiallyPartial<T, K extends keyof T> = Partial<Pick<T, K>> & Omit<T, K>;

interface BlogComment {
  commentId: number;
  title: string;
  content: string;
}

type PartComment = PartiallyPartial<BlogComment, 'title'>;
// 鼠标悬停显示：
// type PartComment = Partial<Pick<BlogComment, "title">> & Omit<BlogComment, "title">
```

用户看到这个显示，无法快速知道最终类型中有哪些字段，`title` 是否可选。他们需要手动展开 `Partial<Pick<...>>` 和 `Omit`，这很糟糕。

---

### 3. 解决方案：`Resolve` 辅助类型

```ts
type Resolve<T> = T extends Function ? T : { [K in keyof T]: T[K] };
```

#### 工作原理

- 如果 `T` 是函数类型，直接返回 `T`（不对函数做映射，因为映射函数类型会得到空对象 `{}`，如 `{ [K in keyof T]: T[K] }` 对函数类型会得到 `{}`，这不对）。
- 否则，对于对象类型，使用同态映射类型 `{ [K in keyof T]: T[K] }` 将 `T` 的每个属性显式列出来。这会强制 TypeScript 展开所有别名、交叉类型等，得到最终的属性列表。

**为什么它有效？**  
同态映射类型（`{ [K in keyof T]: T[K] }`）会保留 `readonly` 和可选修饰符，并展开所有属性。这相当于“计算”出 `T` 的具体结构。对于基本类型（`string`, `number` 等），映射后仍是自身。对于函数类型，映射后会变成 `{}`，所以需要条件类型保护。

#### 使用 `Resolve`

```ts
type PartiallyPartial<T, K extends keyof T> =
  Resolve<Partial<Pick<T, K>> & Omit<T, K>>;

type PartComment = PartiallyPartial<BlogComment, 'title'>;
// 现在显示为：
// type PartComment = {
//   title?: string | undefined;
//   commentId: number;
//   content: string;
// }
```

显示清晰，一目了然。

---

### 4. `Resolve` 的其他用途

#### 4.1 内联 `keyof` 表达式

```ts
type Chan = keyof Color;   // 显示为 keyof Color
type ChanInline = Resolve<keyof Color>;  // 显示为 "r" | "g" | "b" | "a"
```

#### 4.2 不要对类（如 `Date`）使用 `Resolve`

因为 `Resolve` 会展开类的所有属性和方法，导致显示极其冗长（甚至上百行）。对于类，直接保留原类型更好。

---

### 5. 处理特殊情况改善显示

当 `K` 为 `never` 时，`PartiallyPartial<T, never>` 应该等价于 `T`（没有属性变为可选）。原来的定义会显示为展开后的 `T`，但更简洁的显示是直接显示 `T`。

添加特殊分支：

```ts
type PartiallyPartial<T extends object, K extends keyof T> =
  [K] extends [never]
    ? T
    : T extends unknown
      ? Resolve<Partial<Pick<T, K>> & Omit<T, K>>
      : never;
```

注意：
- 使用 `[K] extends [never]` 而不是 `K extends never`，因为条件类型对 `never` 会空联合，导致分布后永远不进入该分支（Item 53）。
- 额外添加 `T extends unknown` 是为了保持分布性（如果原来有分布需求，但这里其实不需要，不过添加无害）。

现在 `PartiallyPartial<BlogComment, never>` 直接显示为 `BlogComment`，更简洁。

---

### 6. 其他调整显示的技术（不推荐）

- `Exclude<keyof T, never>` 可以内联 `keyof`，但不如 `Resolve<keyof T>` 直观。
- `unknown & T` 或 `{} & T` 也可以展平对象类型，但不如 `Resolve` 通用。

书中推荐统一使用 `Resolve` 模式。

---

### 7. 测试类型显示

由于类型显示可能随 TypeScript 版本变化或因微小重构而改变，且 `Resolve` 不影响可赋值性，因此容易产生回归。你应该为类型的显示编写测试（Item 55 提供了方法）。可以使用 `eslint-plugin-expect-type` 的 Twoslash 注释或 `dtslint` 来断言类型的字符串表示。

---

### 8. 总结关键点

- **类型显示是用户体验的一部分**：清晰的类型显示让库更易用。
- **`Resolve` 技巧**：通过同态映射类型强制展开类型，隐藏实现细节。
- **注意保护函数类型和类**：不对它们使用映射。
- **处理特殊情况**：如 `never`，可以返回更简洁的表示。
- **测试类型显示**：防止回归。

**记住**：一个正确但难以理解类型的类型，会给用户带来困扰。花点心思调整显示，会让你的库更受欢迎。