## Item 43 详细讲解：将 `any` 类型的使用范围限制到最小

这一节的核心是：**如果你必须使用 `any`（例如为了绕过类型检查器的一个错误判断），请将它的影响范围限制到最小——无论是时间上（只在一个表达式内）还是空间上（只在一个属性上）。** 这样可以避免 `any` 的“传染性”破坏代码其他部分的类型安全。

书中通过几个对比示例，展示了宽范围 `any` 的危害和窄范围 `any` 的好处，并介绍了 `@ts-expect-error` 等替代方案。

---

### 1. 问题情境：一个类型不匹配但你知道是正确的调用

假设有以下代码：

```ts
declare function getPizza(): Pizza;
function eatSalad(salad: Salad) { /* ... */ }

function eatDinner() {
  const pizza = getPizza();
  eatSalad(pizza);  // 类型错误：Pizza 不能赋给 Salad
  pizza.slice();    // 后续还要使用 pizza
}
```

TypeScript 报错，因为 `Pizza` 不能赋给 `Salad`。但你可能知道，在这种情况下，`Pizza` 其实可以被当作 `Salad` 处理（例如一种特殊的披萨沙拉）。最佳做法是修正类型定义，让 `Pizza` 可赋值给 `Salad`。但如果暂时无法修改类型（例如第三方库），你可能会想用 `any` 来绕过错误。

有两种使用 `any` 的方式，它们的后果截然不同。

---

### 2. 糟糕的方式：将整个变量声明为 `any`

```ts
function eatDinner1() {
  const pizza: any = getPizza();   // ❌ 将 pizza 标记为 any
  eatSalad(pizza);                 // 类型错误被压制
  pizza.slice();                   // 这一行也完全失去类型检查
}
```

**问题**：
- `pizza` 的类型从 `getPizza()` 返回的 `Pizza` 变成了 `any`。
- **从这一行开始，直到函数结束**，`pizza` 始终是 `any` 类型。
- 后续的 `pizza.slice()` 调用完全不受类型检查，任何拼写错误（例如 `pizza.sliec()`）都不会报错，运行时才会崩溃。
- 如果函数返回 `pizza`，那么调用方也会收到一个 `any`，破坏更广范围的类型安全。

**示例**：返回 `any` 的传染性

```ts
function eatDinner1() {
  const pizza: any = getPizza();
  eatSalad(pizza);
  return pizza;   // 返回 any
}

function spiceItUp() {
  const pizza = eatDinner1();   // pizza 类型是 any
  pizza.addRedPepperFlakes();  // 完全不受检查，可能运行时崩溃
}
```

`any` 像病毒一样扩散到调用链。

---

### 3. 更好的方式：仅在调用时使用类型断言 `as any`

```ts
function eatDinner2() {
  const pizza = getPizza();               // pizza 类型仍然是 Pizza
  eatSalad(pizza as any);                // 仅在这一处断言为 any
  pizza.slice();                         // 这里 pizza 仍然是 Pizza，类型检查有效
}
```

**优点**：
- `as any` 的作用域仅限于**单个表达式**（函数参数）。它不影响 `pizza` 变量的原始类型。
- 后续代码（`pizza.slice()`）仍然享受完整的类型检查。
- 如果函数返回 `pizza`，返回类型仍然是 `Pizza`，不会污染调用方。

**结论**：**总是优先使用 `as any` 或 `as unknown as T` 这种局部断言，而不是将整个变量声明为 `any`。**

---

### 4. 更安全的替代方案：`@ts-expect-error`

除了 `any`，TypeScript 还提供了注释指令来忽略某一行上的类型错误：

```ts
function eatDinner() {
  const pizza = getPizza();
  // @ts-expect-error
  eatSalad(pizza);
  pizza.slice();
}
```

**与 `as any` 对比**：
- `@ts-expect-error` 只忽略**紧接着的下一行**的错误，不会改变任何变量的类型。
- 如果未来代码变更（例如 `eatSalad` 的参数类型改为接受 `Pizza`），这一行的错误消失，TypeScript 会**提示**你该指令不再需要，从而可以删除它。
- `@ts-ignore` 类似，但不会在错误消失时提醒，因此 `@ts-expect-error` 更优。

**注意**：不要滥用这些指令。它们也会隐藏同一行上的其他错误（如果有多个错误），而且如果错误类型改变，你可能错过重要警告。

---

### 5. 空间上的窄范围：只对对象的某个属性使用 `as any`

当你有一个较大的对象字面量，其中只有一个属性有类型错误时，不要对整个对象使用 `as any`：

```ts
const config: Config = {
  a: 1,
  b: 2,
  c: {
    key: value   // 这里报错，例如缺少某个必需属性
  }
} as any;  // ❌ 这样做会让 a 和 b 也失去类型检查
```

更好的做法：**只对出问题的属性使用 `as any`**：

```ts
const config: Config = {
  a: 1,
  b: 2,           // 这两个属性仍然被类型检查
  c: {
    key: value as any   // ✅ 仅绕过这一处
  }
};
```

这保持了其他属性的类型安全，将 `any` 的污染限制在最小的“空间”范围内。

---

### 6. 核心原则总结

| 原则 | 说明 |
|------|------|
| **时间上窄范围** | 使用 `as any` 或 `as unknown as T`，而不是将变量声明为 `any`。 |
| **空间上窄范围** | 只对对象中出问题的属性使用 `as any`，不要对整个对象断言。 |
| **永不返回 `any`** | 函数的返回类型不应是 `any`（除非显式标记），否则会污染调用方。 |
| **优先使用 `@ts-expect-error`** | 如果只是要忽略某一行错误，且不改变类型，用注释指令比 `any` 更安全。 |
| **工具辅助** | 使用 `typescript-eslint` 的 `recommended-type-checked` 预设，其中的 `no-unsafe-assignment`、`no-unsafe-return` 等规则会帮你发现 `any` 的扩散。 |

**最终建议**：`any` 是 TypeScript 类型系统的一扇后门，使用它时要像处理核废料一样小心——**限制在最小的容器里，并确保它不会泄漏到其他地方**。尽量通过修正类型定义来解决问题，只有在万不得已时才使用窄范围的 `any` 或 `@ts-expect-error`。