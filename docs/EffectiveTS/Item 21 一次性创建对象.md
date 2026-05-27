## Item 21: 一次性创建对象 —— 详解与示例

### 核心观点

在 TypeScript 中，**变量的类型通常不会改变**（Item 19）。因此，**应该优先选择一次性创建对象，而不是分步逐步添加属性**。分步构建对象会导致类型错误，因为 TypeScript 在每一步都只看到当前已有的属性，无法预知后续会添加什么。

---

## 1. 问题演示：分步构建对象的错误

### 错误写法 1：从空对象开始，逐步添加属性

```typescript
const pt = {};
pt.x = 3;   // ❌ Property 'x' does not exist on type '{}'
pt.y = 4;   // ❌ Property 'y' does not exist on type '{}'
```

**原因**：`pt` 初始化为 `{}`，TypeScript 推断其类型为 `{}`（没有任何属性）。之后给 `pt.x` 赋值时，`{}` 类型中并没有 `x` 属性，因此报错。

### 错误写法 2：声明类型为空对象，再分步添加

```typescript
interface Point { x: number; y: number; }
const pt: Point = {};
// ❌ Type '{}' is missing the following properties from type 'Point': x, y
pt.x = 3;
pt.y = 4;
```

**原因**：你声明 `pt` 的类型是 `Point`，但初始化时给了一个空对象 `{}`，不满足 `Point` 的完整结构，所以立即报错。

### 错误解法：使用类型断言（不推荐）

```typescript
const pt = {} as Point;   // 类型断言，欺骗编译器
pt.x = 3;
pt.y = 4;                 // 没有错误
```

**问题**：TypeScript 不会检查你是否真的设置了所有属性。如果忘记设置 `pt.y`，代码仍会通过类型检查，但在运行时可能导致 `NaN` 或其他异常。如 Item 9 所说，类型断言不应该是首选工具。

---

## 2. 最佳实践：一次性创建完整对象

```typescript
const pt: Point = {
    x: 3,
    y: 4,
};
```

✅ 类型安全，无冗余，不需要断言，一次性完成。

---

## 3. 从多个小对象构建大对象：使用对象展开语法（`...`）

### 错误做法：分步合并

```typescript
const pt = { x: 3, y: 4 };
const id = { name: 'Pythagoras' };
const namedPoint = {};
Object.assign(namedPoint, pt, id);
namedPoint.name;   // ❌ Property 'name' does not exist on type '{}'
```

**原因**：`namedPoint` 初始化为 `{}`，`Object.assign` 虽然运行时添加了属性，但 TypeScript 的类型推断无法从 `Object.assign` 中提取出新属性类型。

### 正确做法：使用对象展开一次性创建

```typescript
const namedPoint = { ...pt, ...id };
// ^? const namedPoint: { name: string; x: number; y: number; }
namedPoint.name;   // ✅ OK
```

**原理**：对象展开语法 `{...a, ...b}` 会在类型系统中产生一个新的对象类型，包含所有源对象的属性，类型完全正确。

---

## 4. 渐进式构建对象（安全但繁琐）

如果你确实需要逐步添加属性（例如在循环或条件中），可以每次使用对象展开创建一个新的对象，从而每次都获得新的类型：

```typescript
const pt0 = {};
const pt1 = { ...pt0, x: 3 };   // 类型: { x: number }
const pt: Point = { ...pt1, y: 4 };   // 最终满足 Point
```

**关键**：每次展开都生成一个新对象，类型逐步丰富，最后用类型注解验证完整性。这虽然比一次性创建啰嗦，但比类型断言安全得多。

---

## 5. 条件添加属性：使用展开与空对象 / 假值

如果你想根据条件决定是否添加某个属性，可以使用对象展开和三元表达式或逻辑与短路。

### 示例：有条件的中间名

```typescript
declare let hasMiddle: boolean;
const firstLast = { first: 'Harry', last: 'Truman' };
const president = {
    ...firstLast,
    ...(hasMiddle ? { middle: 'S' } : {})
};
// ^? const president: { middle?: string; first: string; last: string; }
```

- 当 `hasMiddle` 为 `true` 时，展开 `{ middle: 'S' }`，添加 `middle` 属性。
- 当 `hasMiddle` 为 `false` 时，展开空对象 `{}`，不添加任何属性。
- 最终推断的类型中，`middle` 成为可选属性。

等价写法（利用 `&&` 短路）：
```typescript
const president = { ...firstLast, ...(hasMiddle && { middle: 'S' }) };
```
因为 `false && 对象` 结果为 `false`，而展开 `false` 不会添加任何属性。

### 示例：条件添加多个属性

```typescript
declare let hasDates: boolean;
const nameTitle = { name: 'Khufu', title: 'Pharaoh' };
const pharaoh = {
    ...nameTitle,
    ...(hasDates && { start: -2589, end: -2566 })
};
// ^? const pharaoh: { start?: number; end?: number; name: string; title: string; }
```

`start` 和 `end` 都变成了可选属性，使用时可能为 `undefined`。

---

## 6. 扩展：转换对象或数组时的替代方案

如果你需要从一个现有对象或数组构建另一个，可以使用函数式方法（`map`、`filter`、`reduce` 等）或 Lodash 等库，而不是用循环逐步修改。这符合“一次性创建”的精神，也让类型更容易流动（Item 26）。

---

## 7. 总结：Things to Remember

| 做法 | 安全性 | 推荐度 |
|------|--------|--------|
| 分步赋值（`const pt = {}; pt.x=3;`） | ❌ 类型错误 | 不推荐 |
| 类型断言（`{} as Point`） | ⚠️ 可能遗漏属性 | 不推荐 |
| 一次性创建完整对象 | ✅ 完全安全 | ✅ 首选 |
| 使用对象展开合并多个对象 | ✅ 类型正确 | ✅ 推荐 |
| 展开 + 空对象条件添加属性 | ✅ 安全，得到可选属性 | ✅ 推荐 |
| 每次展开产生新对象（渐进式） | ✅ 安全但繁琐 | 可接受 |

---

## 8. 书中示例完整回顾

```typescript
// ❌ 分步构建
const pt = {};
pt.x = 3;   // 错误

// ❌ 声明类型但初始化为空
const pt: Point = {};   // 错误

// ⚠️ 类型断言（不推荐）
const pt = {} as Point;
pt.x = 3;
pt.y = 4;   // 通过但容易遗漏

// ✅ 一次性创建
const pt: Point = { x: 3, y: 4 };

// ✅ 使用展开合并对象
const namedPoint = { ...pt, ...id };

// ✅ 条件添加属性
const president = { ...firstLast, ...(hasMiddle && { middle: 'S' }) };
```

---

**一句话总结**：**在 TypeScript 中，应该一次性创建完整的对象，而不是分步添加属性。使用对象展开语法可以安全地合并多个对象，并且可以条件性地添加属性，同时保持类型准确。**