## Item 24: 理解类型推断中如何使用上下文 —— 详解与示例

### 核心概念

TypeScript 的类型推断不仅基于值本身，还会考虑**值出现的上下文**（如函数参数类型、返回值类型等）。这通常能让代码更简洁安全，但当我们将一个值从它的上下文中提取出来（例如提取到单独的变量）时，可能会丢失关键的类型信息，导致类型错误。

**根本问题**：TypeScript 在推断一个独立变量的类型时，仅根据其初始值（通过拓宽规则，见 Item 20），而不会“向前看”到它将来如何使用。这与一些能基于后续用法推断类型的语言不同（Anders Hejlsberg 称之为“幽灵般的远距离作用”）。

---

## 1. 基础示例：字符串字面量类型丢失

```typescript
type Language = 'JavaScript' | 'TypeScript' | 'Python';

function setLanguage(language: Language) { /* ... */ }

// ✅ 内联形式：上下文已知
setLanguage('JavaScript');

// ❌ 提取变量后：类型丢失
let language = 'JavaScript';   // 推断为 string，而不是 'JavaScript'
setLanguage(language);         // 错误：string 不能赋给 Language
```

**为什么？**
- 内联时，TypeScript 看到 `setLanguage('JavaScript')`，知道参数必须是 `Language`，而字面量 `'JavaScript'` 可赋值给 `Language`，因此通过。
- 提取变量后，`let language = 'JavaScript'` 独立存在。根据拓宽规则，`let` 声明的字符串字面量被拓宽为 `string`。此时 `language` 的类型是宽泛的 `string`，而 `setLanguage` 期望精确的 `Language` 联合类型，因此不匹配。

**解决方案**：

### 方案一：类型注解
```typescript
let language: Language = 'JavaScript';
setLanguage(language);   // OK
```

### 方案二：使用 `const`
```typescript
const language = 'JavaScript';   // 推断为 "JavaScript"，不拓宽
setLanguage(language);           // OK
```

`const` 阻止了拓宽，保留了字面量类型。但如果需要重新赋值，则必须使用注解。

---

## 2. 元组类型问题

```typescript
function panTo(where: [number, number]) { /* ... */ }

panTo([10, 20]);          // ✅ 内联，推断为 [number, number]

const loc = [10, 20];     // ❌ 推断为 number[]（长度未知）
panTo(loc);               // 错误：number[] 不能赋给 [number, number]
```

**为什么？** `[10, 20]` 作为独立数组时，TypeScript 推断为 `number[]` 而不是元组，因为它不知道你期望固定长度。

**修复方法**：

### 2.1 类型注解
```typescript
const loc: [number, number] = [10, 20];
panTo(loc);
```

### 2.2 常量断言 `as const`
```typescript
const loc = [10, 20] as const;   // 推断为 readonly [10, 20]
panTo(loc);
// ❌ 错误：readonly 不能赋给可变元组
```

如果函数参数声明为 `readonly [number, number]`，则可接受：
```typescript
function panTo(where: readonly [number, number]) { /* ... */ }
const loc = [10, 20] as const;
panTo(loc);   // ✅ OK
```

**注意**：`as const` 的问题在于错误可能出现在调用处而非定义处。比如添加第三个元素：
```typescript
const loc = [10, 20, 30] as const;   // 错误实际在这里
panTo(loc);   // 错误信息指向这里，但根源在上一行
```
因此，更推荐使用类型注解或内联形式。

---

## 3. 对象字面量类型丢失

```typescript
type Language = 'JavaScript' | 'TypeScript' | 'Python';
interface GovernedLanguage {
    language: Language;
    organization: string;
}
function complain(language: GovernedLanguage) { /* ... */ }

// ✅ 内联：上下文推断
complain({ language: 'TypeScript', organization: 'Microsoft' });

// ❌ 提取变量
const ts = {
    language: 'TypeScript',   // 推断为 string
    organization: 'Microsoft'
};
complain(ts);   // 错误：language 类型不匹配
```

**修复**：
- 类型注解：`const ts: GovernedLanguage = { ... }`
- 常量断言：`const ts = { language: 'TypeScript', organization: 'Microsoft' } as const`（注意这会使得整个对象只读，属性类型变为字面量）
- 使用 `satisfies`（Item 20）：`const ts = { language: 'TypeScript', ... } satisfies GovernedLanguage`（保留精确推断但验证类型）

---

## 4. 回调函数中的上下文丢失

```typescript
function callWithRandomNumbers(fn: (n1: number, n2: number) => void) {
    fn(Math.random(), Math.random());
}

// ✅ 内联回调：参数 a, b 自动推断为 number
callWithRandomNumbers((a, b) => {
    console.log(a + b);
});

// ❌ 提取回调函数到变量
const fn = (a, b) => {   // 参数隐式 any，因为失去上下文
    console.log(a + b);
};
callWithRandomNumbers(fn);   // 错误
```

**修复**：
- 显式注解参数：`(a: number, b: number) => ...`
- 为整个函数表达式添加类型（如果可用）：`const fn: (n1: number, n2: number) => void = (a, b) => ...`（见 Item 12）

**经验法则**：如果函数只在一个地方使用，最好保持内联形式，这样最简洁且无需类型注解。

---

## 5. 总结与应对策略

| 场景 | 问题 | 解决方案 |
|------|------|----------|
| 提取字符串字面量 | 拓宽为 `string` | 用 `const` 或类型注解 |
| 提取数组 | 推断为 `number[]` 而非元组 | 用类型注解或调整函数参数为 `readonly` |
| 提取对象 | 属性拓宽为基类型 | 用类型注解、`as const` 或 `satisfies` |
| 提取回调函数 | 参数类型丢失 | 保持内联，或显式注解参数/函数类型 |

**核心要点**：
- TypeScript 在推断独立变量时**不依赖后续使用**，只依赖初始值和拓宽规则。
- 将值从上下文中提取出来（重构为变量）可能会丢失类型信息，导致错误。
- 解决方案通常是在提取时提供类型注解，或使用 `const` / `as const` / `satisfies`。
- 如果值只在一个地方使用，**优先内联**，避免不必要的提取。

---

## 6. Things to Remember（书中总结）

- 了解上下文在类型推断中的作用。
- 如果提取变量引入类型错误，尝试添加类型注解。
- 如果变量是真正的常量，可以使用常量断言（`as const`），但要注意错误可能出现在使用处而非定义处。
- 在实际可行的范围内，优先内联值，以减少对类型注解的需求。