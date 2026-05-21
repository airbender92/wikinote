在 TypeScript 中，`never` 类型表示**永远不会发生的值**。它用来描述那些“理论上不可能存在”的类型。

---

## 🧠 核心概念

`never` 是 TypeScript 类型层级中的**底部类型**（bottom type），意味着：

- `never` 可以赋值给任何其他类型（`never` 是任何类型的子类型）。
- 但没有一个类型可以赋值给 `never`（除了 `never` 自身）。
- 在运行时，一个值为 `never` 的变量是**不可能**被创建的。

---

## 📍 常见使用场景

### 1. 函数永不返回
比如函数抛出异常或进入无限循环，其返回值类型就是 `never`。

```typescript
function throwError(message: string): never {
    throw new Error(message);
}

function infiniteLoop(): never {
    while (true) {}
}
```

### 2. 条件类型中的过滤
利用 `never` 在条件类型中剔除某些类型。

```typescript
type OnlyStrings<T> = T extends string ? T : never;

type Result = OnlyStrings<string | number | boolean>;  // string
```

原理：联合类型中的 `never` 会自动被消除。

### 3. 穷尽性检查（Exhaustiveness Check）
在 `switch` 或 `if-else` 中，使用 `never` 确保所有可能的分支都被处理。

```typescript
type Shape = 'circle' | 'square';

function area(shape: Shape) {
    switch (shape) {
        case 'circle':
            return Math.PI * 1;
        case 'square':
            return 1 * 1;
        default:
            const _exhaustiveCheck: never = shape; // 如果上面遗漏了某个 case，这里会报错
            return _exhaustiveCheck;
    }
}
```

如果将来 `Shape` 增加了 `'triangle'`，TypeScript 会提示 `default` 分支中不能将 `'triangle'` 赋值给 `never`。

### 4. 泛型约束中表示不可能的类型
有时用于阻止某些类型参数的传入。

---

## 🔁 `never` vs `void`

| 类型 | 含义 | 示例函数 |
|------|------|----------|
| `void` | 函数返回 `undefined` 或没有显式返回值 | `function log(msg: string): void { console.log(msg) }` |
| `never` | 函数永远不会正常结束（抛异常或死循环） | `function error(): never { throw new Error() }` |

**关键区别**：`void` 类型的变量可以被赋值为 `undefined`（或 `null` 在 strictNullChecks 关闭时），但 `never` 类型的变量不能被赋予任何值（包括 `undefined`）。

```typescript
let a: void = undefined; // ✅
let b: never = undefined; // ❌ 不能将类型“undefined”分配给类型“never”
```

---

## 🧩 与 `unknown`、`any` 的关系

- `unknown`：任何值都可以赋值给 `unknown`，但使用前需要类型收窄。
- `any`：关闭类型检查，可以当作任何类型使用。
- `never`：没有任何值可以赋值给 `never`。

在类型层级中：`never` < `void` / `unknown` / `any` < 其他具体类型。

---

## 💡 实用技巧

### 提取联合类型中非 `null`/`undefined` 的部分
```typescript
type NonNullable<T> = T extends null | undefined ? never : T;
// 内置类型就是这样的
```

### 在元组操作中作为占位
```typescript
type First<T extends any[]> = T extends [infer F, ...any[]] ? F : never;
type EmptyFirst = First<[]>; // never
```

---

## ⚠️ 常见误区

- 不要用 `never` 表示“还没有值”或“将来会有值”，那应该是 `undefined` 或 `null`。
- 不要在普通变量声明中写 `let x: never`，因为你无法给它赋任何值，这会导致代码无法使用。

---

希望这个解释能帮你彻底理解 `never`。如果你有特定的使用场景，可以进一步探讨！