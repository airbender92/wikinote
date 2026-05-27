## Item 19: 为不同类型使用不同的变量 —— 详解与示例

### 核心观点

在 TypeScript 中，**一个变量的类型通常不会改变**（除了通过窄化缩小类型，或 Item 25 提到的“演化类型”）。因此，**不要重复使用同一个变量来存储不同类型的数据**。如果两个值的类型不同，就应该使用两个不同的变量。

这不仅能帮助类型检查器准确追踪类型，也能让代码对人类读者更清晰。

---

### 1. 问题示例：在 JavaScript 中合法，在 TypeScript 中报错

**JavaScript 代码（可以运行）**：
```javascript
let productId = "12-34-56";
fetchProduct(productId);      // 期望 string
productId = 123456;
fetchProductBySerialNumber(productId);   // 期望 number
```

**TypeScript 版本（报错）**：
```typescript
let productId = "12-34-56";
fetchProduct(productId);
productId = 123456;   // ❌ Type 'number' is not assignable to type 'string'
fetchProductBySerialNumber(productId);
// ❌ Argument of type 'string' is not assignable to parameter of type 'number'
```

**原因**：TypeScript 根据初始值 `"12-34-56"` 推断 `productId` 的类型为 `string`。之后赋值为 `number` 就违反了类型系统规则。

---

### 2. 不推荐方案：使用联合类型

可以让 `productId` 的类型为 `string | number`，这样就能接受两种赋值：

```typescript
let productId: string | number = "12-34-56";
fetchProduct(productId);      // 此处 productId 被窄化为 string
productId = 123456;           // 允许
fetchProductBySerialNumber(productId);  // 此处被窄化为 number
```

**为什么不是最佳方案？**
- 联合类型不如单一类型方便：在使用 `productId` 之前，通常需要先进行类型检查（`typeof` 或 `in` 等）。
- 语义不清晰：同一个变量名先后代表两个不同的概念（ID 字符串 和 序列号数字），容易引起混淆。
- 增加了不必要的复杂度。

---

### 3. 推荐方案：使用不同的变量

```typescript
const productId = "12-34-56";      // 类型为 "12-34-56" (字面量)
fetchProduct(productId);

const serial = 123456;             // 类型为 123456 (字面量)
fetchProductBySerialNumber(serial);
```

**优点总结**：
| 方面 | 优势 |
|------|------|
| 语义清晰 | 两个变量名表达不同概念（ID vs 序列号） |
| 类型简单 | `string` 字面量和 `number` 字面量，而非 `string\|number` |
| 无需注解 | 类型推断自动给出精确字面量类型 |
| 可用 `const` | 不变性让代码更容易推理 |
| 易重构 | 改变其中一个变量的类型不会影响另一个 |

---

### 4. 深层原理：变量的类型在 TypeScript 中通常不变

- 在大多数编程语言中，一个变量从声明到销毁只能有一种类型。TypeScript 继承了这一理念。
- **窄化**（narrowing）是唯一的例外：通过条件检查（如 `if (productId === null)`）可以让类型变得更具体（从 `string\|null` 变为 `string`），但**不会扩大**。
- “演化类型”（Item 25）是另一个特例（如空数组 `[]` 变成 `number[]`），但这不是推荐的设计模式。

因此，**不要指望一个变量能够“换类型”**。

---

### 5. 与“变量遮蔽（shadowing）”的区别

变量遮蔽是创建同名变量，但处于不同的作用域。**这不是重新赋值，而是两个完全不同的变量**：

```typescript
const productId = "12-34-56";
fetchProduct(productId);

{
    const productId = 123456;   // 这是新变量，仅在此块内有效
    fetchProductBySerialNumber(productId);
}
// 外层 productId 仍然是 "12-34-56"
```

虽然 TypeScript 不会混淆，但**对人类读者来说仍可能造成困惑**。因此许多团队使用 linter 规则（如 `no-shadow`）禁止这种写法。更好的做法：使用不同的名称。

---

### 6. 扩展到对象和数组

该建议不仅适用于原始类型，也适用于对象和数组。

**❌ 错误：重复使用同一个数组变量**：
```typescript
let data = [1, 2, 3];
data = ['a', 'b', 'c'];   // 类型错误
```

**✅ 正确：使用不同变量**：
```typescript
const numbers = [1, 2, 3];
const strings = ['a', 'b', 'c'];
```

**更复杂的例子（Item 21 会深入）**：
```typescript
// ❌ 避免逐步构建对象
const pt = {};
pt.x = 3;    // 错误
pt.y = 4;

// ✅ 一次性创建
const pt = { x: 3, y: 4 };
```

---

### 7. 核心法则总结

> **变量值可以变，但类型一般不变。如果要变类型，就换一个变量名。**

| 做法 | 是否推荐 | 原因 |
|------|----------|------|
| 重复使用变量，改变类型 | ❌ 不推荐 | 类型检查失败，代码迷惑 |
| 使用联合类型 `string\|number` | ⚠️ 可接受但不佳 | 增加复杂性，语义模糊 |
| 使用不同变量名（`const`） | ✅ 推荐 | 类型安全，代码清晰 |
| 变量遮蔽（同名的嵌套作用域） | ❌ 不推荐 | 对人类读者不友好，linter 通常会禁止 |

---

### 8. 实际编码建议

- **优先使用 `const`**：只要变量不会重新赋值，就用 `const`。这能锁定类型，并让代码更容易理解。
- **如果必须重新赋值，确保类型相同**：例如累加器 `let sum = 0; sum += value;` 类型始终是 `number`，这是可以的。
- **当需要表示“可能是字符串或数字”时**：不要复用同一个变量来切换类型；而是使用不同的变量，或者使用函数将不同数据流分开。
- **使用有意义的名称**：`productId` 和 `serial` 比两个 `productId` 好得多。

---

### 书中示例代码逐行解读

```typescript
// 初始错误版本
let productId = "12-34-56";       // 推断类型为 string
fetchProduct(productId);          // 期望 string，OK
productId = 123456;               // ❌ 不能把 number 赋给 string
fetchProductBySerialNumber(productId); // 即使赋值成功，这里也是 string，不符合参数 number
```

```typescript
// 联合类型的“修复”（不推荐）
let productId: string | number = "12-34-56";
fetchProduct(productId);          // 窄化为 string
productId = 123456;               // 允许
fetchProductBySerialNumber(productId); // 窄化为 number
// 问题：未来所有使用 productId 的地方都可能需要类型守卫
```

```typescript
// 最佳方案
const productId = "12-34-56";     // 字面量类型
fetchProduct(productId);
const serial = 123456;            // 字面量类型
fetchProductBySerialNumber(serial);
// 完美，无需注解，类型精准，语义清晰
```

---

**一句话总结**：**变量名是给人和编译器看的，不要为了让变量“复用”而牺牲类型清晰度。不同类型，不同名字；多用 `const`，少用 `let`。**