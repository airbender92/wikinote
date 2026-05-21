## Item 71 详细讲解：使用模块扩充（Module Augmentation）改善类型

TypeScript 有一些历史遗留的不完美类型定义（例如 `JSON.parse` 返回 `any`，`Set` 构造函数可以接受字符串等）。这些行为是出于兼容性考虑，但你可以在自己的项目中使用**声明合并（declaration merging）** 来覆盖或扩充这些类型，使它们更严格、更安全，甚至禁止某些不安全的用法。

---

### 1. 问题示例：`JSON.parse` 返回 `any`

```ts
const response = JSON.parse('{"lastModified": 12345}');
const cacheExpirationTime = response.lastModified + 3600; // any
```

`JSON.parse` 的返回类型是 `any`，导致 `response` 及其所有属性都失去类型检查，`any` 会污染整个代码流。

**为什么 TypeScript 不改成 `unknown`？**  
因为 `unknown` 类型是在 TypeScript 3.0 才引入的，而大量现有代码依赖于 `any` 行为。为了不破坏现有项目，官方保留了 `any`。

**解决方案**：利用**声明合并**，在自己的项目中为 `JSON` 接口添加一个新的 `parse` 方法签名，返回 `unknown`。

```ts
// 在你的项目中，例如 declarations/safe-json.d.ts
interface JSON {
  parse(
    text: string,
    reviver?: (this: any, key: string, value: any) => any
  ): unknown;
}
```

由于接口可以重复声明并合并，这个新的 `parse` 签名会与原有的 `lib.es5.d.ts` 中的签名合并，相当于添加了一个重载。由于你的声明在项目编译时后加载，它实际上会“胜出”，使得 `JSON.parse` 的返回类型变为 `unknown`。

**效果**：

```ts
const response = JSON.parse('{}');        // unknown
const x = response.foo;                   // 错误：'response' 类型为 unknown
const data = JSON.parse('{}') as MyType;  // 必须显式断言
```

这迫使开发者在使用 `JSON.parse` 时进行类型断言或收窄，提高了类型安全性。

---

### 2. 类似改进：`Response.json()` 返回 `unknown`

`fetch` API 的 `response.json()` 同样返回 `any`。你可以对 `Body` 接口进行扩充：

```ts
// declarations/safe-response.d.ts
interface Body {
  json(): Promise<unknown>;
}
```

此后 `response.json()` 返回 `Promise<unknown>`，也需要断言。

---

### 3. 禁止不安全的用法：`new Set(string)`

JavaScript 允许 `new Set('abc')`，它会将字符串拆分为字符数组，生成一个包含 `'a'`、`'b'`、`'c'` 的集合，而不是一个包含字符串 `'abc'` 的集合。这常常是 bug 的来源。

TypeScript 无法直接禁止这种用法，因为类型签名允许。但你可以通过声明合并**覆盖 `SetConstructor` 接口**，添加一个返回 `void`（或错误字符串字面量）的构造函数重载，从而“废掉”这个用法。

```ts
// declarations/ban-set-string-constructor.d.ts
interface SetConstructor {
  /** @deprecated */
  new (str: string): void;
}
```

**效果**：

```ts
const s = new Set('abc');
// ^? const s: void
s.has('abc');      // 错误：类型“void”上不存在属性“has”
```

现在 `new Set(string)` 返回 `void`，无法作为集合使用。你甚至可以让它返回一个字符串字面量错误信息：

```ts
interface SetConstructor {
  /** @deprecated */
  new (str: string): 'Error: new Set(string) is banned.';
}
```

这样 IDE 会显示该构造函数已废弃，并且返回值类型是错误信息，迫使开发者修正代码。

**注意**：这只能在**类型层面**禁止。运行时 `new Set('abc')` 仍然会创建一个集合，但因为你无法使用它（返回值类型是 `void` 或字面量），你会立即发现错误。这是一种权衡。

---

### 4. 适用范围和注意事项

- **仅影响类型检查**：运行时行为不变。`JSON.parse` 仍然返回对象，`Set` 仍然接受字符串。你只是让 TypeScript 强迫你写出更安全的代码。
- **不要脱离现实**：如果添加的类型声明与实际运行时不符（例如声称 `JSON.parse` 返回 `number`），会导致更严重的混淆。遵循 Item 40 的原则：宁可类型不精确，也不能不准确。
- **对第三方库同样有效**：你可以为 `@types` 中的接口进行扩充，修正错误或补充缺失的类型。
- **社区方案**：`ts-reset` 这个 npm 包就收集了许多对内置类型的改进（包括 `JSON.parse` 返回 `unknown`、`Set` 构造函数禁止字符串等），可以直接使用。

---

### 5. 总结

- **声明合并**（declaration merging）允许你扩充或覆盖全局的接口、模块声明。
- 使用它可以将不安全的 `any` 返回值改为 `unknown`，强制调用者进行断言。
- 也可以用来**禁用**不安全的构造函数或方法（通过返回 `void` 或错误字面量），并标记 `@deprecated`。
- 这种技巧适合在自己的项目或团队内部使用，用于提高类型安全性；但在发布公共库时要谨慎，避免破坏用户的类型环境。

**最终建议**：如果你受够了 `JSON.parse` 的 `any` 或 `Set(string)` 的诡异行为，大胆使用声明合并来修复它。你的团队会感谢你。