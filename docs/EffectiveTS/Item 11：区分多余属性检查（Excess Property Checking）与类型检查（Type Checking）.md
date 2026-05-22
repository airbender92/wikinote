## Item 11：区分多余属性检查（Excess Property Checking）与类型检查（Type Checking）—— 详细讲解

TypeScript 的类型系统本质上是**结构化的**（structural typing，Item 4），这意味着只要一个值拥有所需的所有属性，即使它还有额外的属性，通常也是允许的。例如，`{ numDoors: 1, ceilingHeightFt: 10, elephant: 'present' }` 按理说可以赋值给 `Room` 类型，因为它至少包含了 `numDoors` 和 `ceilingHeightFt`。

但是，如果 TypeScript 完全按照结构化规则进行赋值检查，就会错过一类常见错误：**属性名拼写错误**或**意外添加了多余属性**。为了解决这个问题，TypeScript 引入了一项特殊的检查机制：**多余属性检查（Excess Property Checking）**。它只发生在**对象字面量**直接赋值给具有预期类型的位置时，会禁止出现未在预期类型中声明的属性。

理解多余属性检查与普通结构化类型检查的区别，是构建正确 TypeScript 心智模型的关键。

---

## 1. 结构化类型检查与多余属性检查的冲突

### 示例：`Room` 接口

```typescript
interface Room {
    numDoors: number;
    ceilingHeightFt: number;
}

// 直接字面量赋值 -> 触发多余属性检查
const r: Room = {
    numDoors: 1,
    ceilingHeightFt: 10,
    elephant: 'present',   // ❌ 错误：'elephant' 不在 Room 中
};
```

TypeScript 报错，提示只能指定已知属性。

**但根据结构化类型系统**，`{ numDoors, ceilingHeightFt, elephant }` 显然拥有 `Room` 所需的所有属性，应该可以赋值。为了证明这一点，我们可以先用一个中间变量：

```typescript
const obj = {
    numDoors: 1,
    ceilingHeightFt: 10,
    elephant: 'present',
};
const r: Room = obj;   // ✅ 完全通过类型检查
```

这里没有错误！为什么？

- 变量 `obj` 的类型被推断为 `{ numDoors: number; ceilingHeightFt: number; elephant: string }`。
- 该类型是 `Room` 的一个子集（它拥有 `numDoors` 和 `ceilingHeightFt`，且额外的 `elephant` 不影响），所以赋值是允许的。
- 关键区别：**第二个赋值语句的右侧不是对象字面量，而是一个已存在的变量**。多余属性检查**只关心对象字面量**。

因此，多余属性检查是一种**额外的、更严格的检查**，它弥补了纯结构化类型检查可能漏掉的错误，但它的作用范围有限。

---

## 2. 多余属性检查的实际价值：捕获拼写错误

考虑一个更实际的例子：

```typescript
interface Options {
    title: string;
    darkMode?: boolean;
}

function createWindow(options: Options) { /* ... */ }

createWindow({
    title: 'Spider Solitaire',
    darkmode: true   // ❌ 错误：属性名拼写错误（darkmode vs darkMode）
});
```

- `darkmode` 不是 `Options` 中声明的属性，但因为 `Options` 允许任意额外属性（结构类型），按理说这个对象字面量应该可以赋值。
- 然而，这显然是开发者的笔误。多余属性检查发现了这个错误，并给出提示：“Did you mean to write 'darkMode'?”
- 这正是多余属性检查的价值所在：**捕获那些从类型角度合法但逻辑上很可能是错误的代码**。

---

## 3. 结构类型的广泛性：为什么需要多余属性检查

`Options` 类型实际上非常宽泛。以下赋值都是合法的：

```typescript
const o1: Options = document;               // document 有 title 属性（字符串）
const o2: Options = new HTMLAnchorElement();// 也有 title 属性
```

`document` 和 `HTMLAnchorElement` 不是对象字面量，所以不会触发多余属性检查。但它们确实满足了 `Options` 所需的最少属性，因此可以赋值。

如果没有多余属性检查，像 `darkmode` 这样的拼写错误就会被忽略，导致运行时 `darkMode` 永远为 `undefined`，行为不符合预期。

---

## 4. 多余属性检查的触发条件

多余属性检查仅在以下情况发生：

- **对象字面量**（`{ ... }`）直接出现在需要特定类型的位置：
  - 赋值给一个带类型注解的变量。
  - 作为函数实参。
  - 作为函数返回值（且函数有显式返回类型注解）。
- 对象字面量中出现了**目标类型中未定义的属性**。

一旦对象字面量被赋值给一个中间变量（如前面 `obj`），就不再是“新鲜”的对象字面量，多余属性检查就不会触发。

因此，如果你想保留多余属性检查的益处，就应该**避免将对象字面量赋值给无类型注解的中间变量**。

---

## 5. 类型断言也会绕过多余属性检查

```typescript
const o = { darkmode: true, title: 'MS Hearts' } as Options;   // ✅ 无错误
```

`as Options` 断言关闭了多余属性检查，这进一步说明**类型注解（`: Options`）比类型断言更安全**（Item 9）。

---

## 6. 如何有目的地允许额外属性

如果你确实希望一个接口能够接受任意额外属性，可以使用**索引签名**：

```typescript
interface Options {
    darkMode?: boolean;
    [otherOptions: string]: unknown;   // 允许任意字符串键，值类型为 unknown
}

const o: Options = { darkmode: true };   // ✅ 现在 "darkmode" 被索引签名捕获
```

但注意：索引签名会放宽类型检查，应谨慎使用（Item 16）。

---

## 7. 弱类型（Weak Types）的特殊检查

如果一个接口**所有属性都是可选的**，那么它被称为**弱类型（weak type）**。

```typescript
interface LineChartOptions {
    logscale?: boolean;
    invertedYAxis?: boolean;
    areaChart?: boolean;
}

const opts = { logScale: true };
setOptions(opts);   // ❌ 错误：两个类型之间没有任何共同属性
```

- 从结构类型看，任何对象都可以赋值给 `LineChartOptions`（因为所有属性可选）。
- 但这样会导致严重的错误：`logScale` 与 `logscale` 拼写不同，但 TypeScript 无法在类型中体现出错误。
- 因此，TypeScript 对弱类型增加了一条规则：**赋值的目标类型与源类型必须至少有一个共同的属性**。
- 这个检查**不限于对象字面量**，对所有赋值都有效，也不受中间变量影响。

> 注意：“弱类型”是 TypeScript 的专门术语，只指“所有属性均为可选”的接口类型，与一般意义上的“弱类型/强类型”无关。

---

## 8. 总结与核心要点

| 检查类型 | 适用场景 | 目的 | 是否受中间变量影响 |
|---------|----------|------|-------------------|
| 结构化类型检查（普通） | 所有赋值 | 确保最少属性存在 | 是（始终基于最终类型） |
| 多余属性检查 | **对象字面量**直接赋值给已知类型 | 捕获未声明的属性和拼写错误 | 是（绕过） |
| 弱类型检查 | 接口所有属性均为可选 | 确保至少有一个属性匹配 | 否 |

### Things to Remember（中文）

1. **对象字面量**直接赋值给已知类型时，会触发**多余属性检查**，禁止出现未声明的属性。这是为了捕获常见的拼写和误用错误。
2. 多余属性检查**不等于**普通的结构化类型兼容性检查。将两者混为一谈会导致对 TypeScript 类型系统理解混乱。
3. 通过引入一个**中间变量**（无类型注解），可以绕过多余属性检查，但也会失去其保护。
4. 类型断言（`as T`）同样会绕过多余属性检查，这也正是优先使用类型注解的理由之一。
5. **弱类型**（所有属性可选）会额外要求源类型与目标类型**至少有一个共同属性**，以避免空对象匹配一切。
6. 如果你想允许任意额外属性，可以使用**索引签名**（`[prop: string]: unknown`）。

---

希望这个详细讲解能帮助你清晰理解多余属性检查与普通类型检查的区别。如果你继续学习 Item 12（将类型应用于整个函数表达式），我可以为你继续讲解。