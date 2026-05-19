## Item 44 详细讲解：优先使用比 `any` 更精确的变体

这一节的核心是：**当你必须使用 `any` 时，不要直接写 `any`，而应该使用更具体的形式（例如 `any[]`、`Record<string, any>`、`() => any` 等）**。这些变体能保留一定程度的类型检查，减少 `any` 带来的破坏性。

书中通过几个例子对比了 `any` 与其精确变体的差异，并展示了后者如何捕获更多错误、提供更好的返回值推断。

---

### 1. 参数为数组：`any[]` 优于 `any`

#### 糟糕的版本

```ts
function getLengthBad(array: any) {
  return array.length;
}
```

**问题**：
- 参数 `array` 是 `any`，意味着你可以传入任何值（数字、正则、`null` 等）。
- 即使传入 `RegExp`（有 `length` 属性吗？没有），也不会报错，但运行时 `array.length` 可能返回 `undefined` 或抛出异常。
- 返回值类型被推断为 `any`，会污染调用方。

#### 改进版本

```ts
function getLength(array: any[]) {
  return array.length;
}
```

**优点**：
- 函数体内访问 `array.length` 是类型安全的（`any[]` 肯定有 `length` 属性）。
- 返回值类型被推断为 `number`，而不是 `any`。
- 调用时，TypeScript 会检查参数是否为数组类型（或至少兼容 `any[]`）：

```ts
getLength(/123/);        // 错误：RegExp 不能赋给 any[]
getLength(null);         // 错误：null 不能赋给 any[]
getLength([1, 2, 3]);    // 正确，返回 number
```

**进一步**：如果你需要二维数组，可以用 `any[][]`。

---

### 2. 参数为对象：`Record<string, any>` 或索引签名优于 `any`

#### 需求：检查对象中是否有以 `"z"` 结尾的键，并打印对应的值

**糟糕的版本**：

```ts
function hasAKeyThatEndsWithZ(o: any) {
  for (const key in o) {
    if (key.endsWith('z')) {
      console.log(key, o[key]);
      return true;
    }
  }
  return false;
}
```

这里 `o` 是 `any`，完全没有类型约束。即使传入 `null` 或数字，也会在运行时出错。

**改进版本**：使用 `Record<string, any>`（或 `{ [key: string]: any }`）

```ts
function hasAKeyThatEndsWithZ(o: Record<string, any>) {
  for (const key in o) {
    if (key.endsWith('z')) {
      console.log(key, o[key]);
      return true;
    }
  }
  return false;
}
```

**优点**：
- 明确表示 `o` 是一个对象（有字符串键），而不是数字或 `null`。
- 调用 `hasAKeyThatEndsWithZ(null)` 会报错，因为 `null` 不能赋给 `Record<string, any>`。
- 函数体内仍然可以自由使用 `o[key]`（值为 `any`），但至少确保了 `o` 是可枚举的对象。

**注意**：如果使用 `object` 类型（小写 `o`），虽然能接受所有非原始值，但无法访问属性值（见 Item 60）。所以这里 `Record<string, any>` 更合适。

---

### 3. 参数为函数：使用具体的函数签名变体

当你期望一个函数类型的参数时，不要用 `any`，而应该根据你需要的函数签名使用更精确的类型。

| 变体 | 含义 | 精确度 |
|------|------|--------|
| `() => any` | 无参数的函数，返回任意值 | 比 `any` 精确 |
| `(arg: any) => any` | 一个参数，返回任意值 | 更精确 |
| `(...args: any[]) => any` | 任意数量参数，返回任意值（等价于 `Function` 类型） | 最通用但仍比 `any` 精确 |

#### 对比示例：rest 参数

```ts
const numArgsBad = (...args: any) => args.length;
// 类型：(...args: any) => any
// 返回值 any，参数 args 是 any，完全无检查
```

```ts
const numArgsBetter = (...args: any[]) => args.length;
// 类型：(...args: any[]) => number
// args 被推断为数组，.length 存在，返回 number
```

**效果**：
- 使用 `...args: any[]` 后，`args` 被视为数组，`args.length` 的类型是 `number`，因此返回值推断为 `number`。
- 调用时，TypeScript 会确保你传入的参数可以被收集为数组（任何值都可以，因为 `any[]` 很宽松，但至少不是完全无约束）。

---

### 4. 何时使用 `unknown[]` 代替 `any[]`

如果函数不需要产生 `any` 值（例如只读取数组长度），可以使用 `unknown[]` 代替 `any[]`。`unknown` 是类型安全的，因为在使用元素前必须进行类型收窄。

```ts
function getLengthSafe(arr: unknown[]) {
  return arr.length;          // 仍然可以访问 length
  // arr[0].toFixed();        // 错误：arr[0] 是 unknown
}
```

`unknown` 比 `any` 安全得多，因为它强制你在使用前验证类型。详见 Item 46。

---

### 5. 核心原则总结

| 场景 | 不推荐（裸 `any`） | 推荐（精确变体） |
|------|-------------------|------------------|
| 函数参数为数组 | `array: any` | `array: any[]` 或 `array: unknown[]` |
| 函数参数为对象 | `obj: any` | `obj: Record<string, any>` 或 `{ [key: string]: any }` |
| 函数参数为函数 | `fn: any` | `() => any`、`(arg: any) => any` 或 `(...args: any[]) => any` |
| Rest 参数 | `...args: any` | `...args: any[]` |
| 不确定值的数组 | `any[]` | `unknown[]`（更安全） |

**最终建议**：使用 `any` 时，停下来想一想你实际期望的值的形状。如果能用数组、对象、函数等更具体的类型来描述，就用对应的精确变体。这样做可以：

- 保留一定程度的类型检查（例如确保参数是数组而非正则）。
- 获得更精确的返回值推断（如 `number` 而非 `any`）。
- 减少 `any` 的污染范围，提升代码的可维护性。

**记住**：`any` 是类型系统的“核选项”。如果你不得不使用它，请选择最精确的弹头（`any[]`、`Record<string, any>`、`()=>any` 等），而不是原始核弹（`any`）。

----

你的困惑很合理。让我换一种更清晰的方式解释这个建议。

原话是：

> If you want an array but don’t care about the type of the elements, you may be able to use `unknown[]` instead of `any[]`. This is preferable because it is safer.

**核心意思是**：  
当你的函数参数需要接收一个数组，但你**不关心数组元素的类型**（例如你只读取数组的 `length` 属性，或者只是遍历数组而不对元素做任何需要具体类型的操作），那么你应该使用 `unknown[]` 而不是 `any[]`。

为什么 `unknown[]` 更安全？因为：
- `any[]` 允许你在不进行任何类型检查的情况下访问元素，并且可以对该元素调用任何方法、传递到任何地方，这很容易导致运行时错误。
- `unknown[]` 也会让你访问 `length`、遍历数组等，但如果你试图直接使用某个元素（例如 `arr[0].toFixed()`），TypeScript 会报错，因为你必须先**收窄**（narrow）该元素的类型（比如通过 `typeof` 检查或类型断言）。这迫使你显式处理未知性，从而更安全。

### 举例说明

假设你写一个函数，只想知道数组的长度：

```ts
// 用 any[] 版本
function getLengthAny(arr: any[]) {
  return arr.length;  // 没问题
}

// 用 unknown[] 版本
function getLengthUnknown(arr: unknown[]) {
  return arr.length;  // 同样没问题
}
```

两者都能正常工作。但如果你不小心在函数体内写了：

```ts
function getLengthAny(arr: any[]) {
  console.log(arr[0].toFixed()); // 类型检查通过，但运行时如果 arr[0] 不是数字就崩溃
  return arr.length;
}
```

而 `unknown[]` 版本会直接报错：

```ts
function getLengthUnknown(arr: unknown[]) {
  console.log(arr[0].toFixed()); // ❌ 类型“unknown”上不存在属性“toFixed”
  return arr.length;
}
```

这样你就不会意外地写出危险的代码。如果你真的需要处理元素，就必须先验证类型：

```ts
if (typeof arr[0] === 'number') {
  console.log(arr[0].toFixed()); // 现在安全了
}
```

**所以建议是**：只要你的函数逻辑不依赖元素的具体类型（例如只读 `length`、通过 `for...of` 遍历但不调用元素上的方法，或者把元素传给另一个能处理 `unknown` 的函数），就优先使用 `unknown[]`。只有当你确实需要随意操作元素且愿意放弃类型检查时，才用 `any[]`。

希望这个解释清楚了。如果还有疑问，欢迎继续追问。