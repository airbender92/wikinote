## Item 68 详细讲解：使用 TSDoc 为 API 编写文档

本节的核心是：**对于需要被他人使用的公共 API（函数、类、接口等），应该使用 JSDoc / TSDoc 格式的注释，而不是普通注释**。因为主流的编辑器（VS Code、WebStorm 等）会将这些格式化的注释提取出来，在开发者编写调用代码时以工具提示（tooltip）的形式展示，从而提高开发效率和正确性。而普通注释（`//` 或 `/* ... */`）不会被编辑器以这种形式展示。

---

### 1. 普通注释 vs JSDoc / TSDoc

#### 普通注释（不会被编辑器识别为文档）

```ts
// Generate a greeting. Result is formatted for display.
function greet(name: string, title: string) {
  return `Hello ${title} ${name}`;
}
```

**效果**：当你在代码中调用 `greet` 时，编辑器只会显示基本的函数签名（参数名和类型），不会显示注释内容（图 8-2）。

#### JSDoc 注释（会被编辑器识别并展示）

```ts
/** Generate a greeting. Result is formatted for display. */
function greet(name: string, title: string) {
  return `Hello ${title} ${name}`;
}
```

**效果**：调用时编辑器会弹出提示框，包含该函数描述（图 8-1）。这是因为 TypeScript 语言服务专门解析了 `/** ... */` 形式的注释。

**注意**：JSDoc 原本是 JavaScript 社区的文档标准。在 TypeScript 中，我们通常称这种注释为 **TSDoc**，但语法与 JSDoc 兼容。

---

### 2. 为参数和返回值添加文档

使用 `@param` 和 `@returns` 标签可以为每个参数以及返回值提供独立的说明。在调用函数时，当你正在填写某个参数，编辑器会显示该参数对应的文档（图 8-3）。

```ts
/**
 * Generate a greeting.
 * @param name Name of the person to greet
 * @param title The person's title
 * @returns A greeting formatted for human consumption.
 */
function greetFull(name: string, title: string) {
  return `Hello ${title} ${name}`;
}
```

**好处**：调用 `greetFull(…)` 时，光标在 `name` 参数上会显示 “Name of the person to greet”，在 `title` 上则显示对应的说明。这极大地减少了使用者查阅文档的时间。

---

### 3. 为类型定义（接口、类型别名）添加文档

TSDoc 也适用于类型定义，包括接口本身的描述和每个属性的描述。

```ts
/** A measurement performed at a time and place. */
interface Measurement {
  /** Where was the measurement made? */
  position: Vector3D;
  /** When was the measurement made? In seconds since epoch. */
  time: number;
  /** Observed momentum */
  momentum: Vector3D;
}
```

当你鼠标悬停在 `Measurement` 类型的变量上，或者悬停在某个属性（如 `.position`）上时，对应的注释会显示出来（图 8-4）。这相当于为类型提供了“自文档化”能力。

---

### 4. 文档会通过同态映射类型保留

**同态映射类型**（homomorphic mapped types）如 `Partial<T>`、`Pick<T, K>` 等，会保留原始类型上的 TSDoc 注释。例如，如果你有一个带注释的接口，那么 `Partial<Measurement>` 中的每个属性仍然会显示原来的注释。这是因为 TypeScript 在应用这些映射类型时，将文档也复制过去了（Item 15 中有详细解释）。

这意味着你可以在基础类型上写一次注释，然后在所有派生类型中自动获得相同的文档。

---

### 5. 为泛型类型参数添加文档

使用 `@template` 标签（或 JSDoc 中的 `@typeParam`）来描述泛型参数的含义。

```ts
/**
 * Construct a new object type using a subset of the properties of another one.
 * @template T The original object type
 * @template K The keys to pick, typically a union of string literal types.
 */
type MyPick<T, K extends keyof T> = { [P in K]: T[P] };
```

当用户鼠标悬停在 `MyPick` 上时，会显示这些描述。这有助于理解泛型参数的用途。

---

### 6. 使用 Markdown 格式化

TSDoc 支持 Markdown 语法，因此你可以在注释中使用粗体、斜体、列表、代码块等，使文档更清晰。

```ts
/**
 * This is a **bold** statement.
 * - list item 1
 * - list item 2
 */
```

但注意：不要写冗长的文章，保持简洁。最佳的文档是**简短扼要**的。

---

### 7. 不要在 TSDoc 中重复类型信息

Item 31 强调过：类型信息应该由 TypeScript 的类型系统提供，而不是写在文档中。因此，**不要**使用 JSDoc 的 `@param {string} name` 这种写法，也不要重复描述参数的类型。TSDoc 只负责描述**语义**（“这个参数是什么含义”），而不是类型（“它是字符串”）。类型已经由 TypeScript 保证了。

**错误示例**：

```ts
/**
 * @param {string} name The name of the user  ❌ 重复了类型
 */
```

**正确示例**：

```ts
/** @param name The name of the user */   ✅ 只描述含义
```

---

### 8. 标记废弃的 API

使用 `@deprecated` 标签来标记某个函数、类或接口已经过时，并建议用户使用什么替代方案。编辑器不仅会在悬停提示中显示废弃信息，还会将符号以**删除线**呈现，让用户一眼就能看到（图 8-6）。

```ts
/**
 * @deprecated Use `newMethod` instead.
 */
function oldMethod() {}
```

这种做法有助于平滑地迁移 API，避免用户无意中使用已废弃的功能。

---

### 9. 总结：何时以及如何使用 TSDoc

- **适用范围**：所有**导出的**函数、类、接口、类型别名、枚举等公共 API。
- **格式**：使用 `/** ... */`，内部使用标准的 Markdown 以及 `@param`、`@returns`、`@template`、`@deprecated` 等标签。
- **内容原则**：描述“做什么”、“为什么”、“注意事项”，不要描述类型（类型由 TypeScript 提供）。
- **收益**：用户在使用你的库时，无需翻阅外部文档，直接在编辑器中获得上下文帮助，提高了开发效率和正确性。

**最终建议**：将 TSDoc 作为编写 TypeScript 公共 API 时的默认习惯。这不仅是一种文档实践，更是一种代码质量的体现。