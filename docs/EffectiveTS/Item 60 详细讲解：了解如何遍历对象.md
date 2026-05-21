## Item 60 详细讲解：了解如何遍历对象

在 JavaScript 中，使用 `for...in` 循环遍历对象属性是一种常见操作。但在 TypeScript 中，这往往会遇到类型错误。本节解释了为什么会出现这些错误，以及如何安全地遍历对象。

---

### 1. 问题示例：`for...in` 循环的类型错误

```ts
const obj = {
  one: 'uno',
  two: 'dos',
  three: 'tres',
};

for (const k in obj) {
  const v = obj[k];
  // ~~~~~~ 元素隐式具有 "any" 类型，因为类型 ... 没有索引签名
}
```

**错误原因**：  
- `obj` 的类型被推断为 `{ one: string; two: string; three: string; }`。  
- `k` 的类型在 `for...in` 循环中被 TypeScript 推断为 `string`（而不是 `'one' | 'two' | 'three'`）。  
- 使用 `string` 类型的变量去索引一个只有特定键的对象是不安全的，因为 `string` 可能包含 `'four'` 等不存在的键，所以 TypeScript 报错。

**为什么 `k` 的类型是 `string` 而不是字面量联合？**  
因为 TypeScript 考虑到了**结构类型**和**原型链**。一个对象可能包含比声明中更多的属性（例如通过继承或动态添加），因此 TypeScript 只能保守地将 `k` 的类型定为 `string`。

---

### 2. 为什么不能直接推断为 `keyof typeof obj`？

如果 TypeScript 把 `k` 推断为 `'one' | 'two' | 'three'`，那么下面的代码就会错误地允许：

```ts
interface ABC {
  a: string;
  b: string;
  c: number;
}

function foo(abc: ABC) {
  for (const k in abc) {
    // 假设 TypeScript 把 k 推断为 'a' | 'b' | 'c'
    const v = abc[k]; // 可能会遗漏额外属性
  }
}

const x = { a: 'a', b: 'b', c: 2, d: new Date() };
foo(x); // foo 接收了带有额外属性 d 的对象，但类型系统不知道
```

在实际运行中，`abc` 可能包含额外的属性（例如 `d`），而 `for...in` 会枚举出 `'d'`，但如果 `k` 的类型被限制为 `'a'|'b'|'c'`，那么访问 `abc['d']` 就会在类型检查时被错误地拒绝（实际上它应该被允许，因为对象在运行时的确有 `d` 属性，但类型中没有声明）。因此 TypeScript 选择将 `k` 的类型定为 `string`，以允许枚举所有可能的属性，但代价是索引访问需要处理隐式 `any` 的问题。

---

### 3. “修复”方法一：类型断言（有风险）

```ts
for (const kStr in obj) {
  const k = kStr as keyof typeof obj;  // 断言为 "one"|"two"|"three"
  const v = obj[k];                    // 现在类型正确
}
```

**问题**：如果对象实际有额外属性（比如在函数参数中），断言会导致访问不到那些额外属性，或者仍然存在类型不安全。例如上面的 `foo` 函数中，如果使用 `k as keyof ABC`，那么 `k` 只能是 `'a'|'b'|'c'`，但对象可能还有 `'d'`，循环中就会漏掉 `'d'`，或者在访问 `abc[k]` 时，对于 `'d'` 不会进入循环（因为断言后 `k` 不会取到 `'d'`）。更严重的是，如果你错误地断言为 `keyof ABC` 但实际有额外属性，那些属性不会被处理，可能导致逻辑错误。

因此，类型断言只能在你**确切知道对象没有额外属性**（例如字面量创建且不会动态添加属性）的情况下使用。

---

### 4. 更安全的方法：使用 `Object.entries`

```ts
function foo(abc: ABC) {
  for (const [k, v] of Object.entries(abc)) {
    // k 的类型是 string，v 的类型是 any
    console.log(k, v);
  }
}
```

`Object.entries` 返回一个键值对数组。`k` 的类型是 `string`，`v` 的类型是 `any`。虽然这些类型不够精确，但它们是**诚实**的——因为对象确实可能有额外属性，且值可能是任意类型。这是最安全的遍历方式，不会隐藏任何属性，也不会产生类型错误。

**缺点**：`v` 是 `any`，丢失了具体的类型信息。如果你知道对象的结构，你可能需要进一步的类型守卫。

---

### 5. 明确列出键的数组（适用于已知且固定的键）

如果你能确定对象只有一组特定的键，并且没有额外属性，可以显式声明键数组，并使用 `const` 断言来获得字面量类型：

```ts
function foo(abc: ABC) {
  const keys = ['a', 'b', 'c'] as const;
  for (const k of keys) {
    const v = abc[k];  // v 的类型为 string | number
  }
}
```

**优点**：类型精确，`k` 被推断为 `'a'|'b'|'c'`，`v` 的正确类型来自 `ABC`。  
**缺点**：需要手动维护键列表，与类型定义保持同步。如果 `ABC` 后来增加了 `'d'` 属性，但 `keys` 没有更新，就会遗漏。可以使用 `Object.keys(abc) as (keyof ABC)[]` 动态获取，但那样又会回到 `string[]` 的问题。

---

### 6. 考虑使用 `Map` 替代对象

`Map` 在遍历时没有“额外属性”的问题，键的类型是明确的（如 `string`），值类型也是明确的。使用 `Map` 可以避免许多遍历对象的陷阱：

```ts
const m = new Map<string, string>([
  ['one', 'uno'],
  ['two', 'dos'],
  ['three', 'tres'],
]);

for (const [k, v] of m.entries()) {
  // k: string, v: string
  console.log(k, v);
}
```

**优点**：类型清晰，没有原型污染，不会枚举到继承属性。  
**缺点**：如果数据来源是 JSON 对象（例如 API 响应），需要手动转换为 `Map`，可能不太方便。

---

### 7. 总结与建议

| 场景 | 推荐方法 | 说明 |
|------|----------|------|
| 你不知道对象是否有额外属性，只是想安全地遍历所有属性 | `Object.entries(obj)` | 最安全，键为 `string`，值为 `any` |
| 你知道对象只有声明的属性，没有额外属性（例如字面量） | `for...in` + 类型断言 `k as keyof typeof obj` | 快速但需确保无额外属性 |
| 你需要精确的类型，且键集合固定且可枚举 | 显式列出键数组 `as const` | 类型精确，但需手动同步 |
| 你可以控制数据结构 | 使用 `Map` 替代对象 | 最佳类型安全和迭代体验 |
| 你只需要访问已知的属性，而不是枚举所有 | 直接访问属性 `obj.one` | 不涉及遍历 |

**核心要点**：
- 理解 TypeScript 为什么在 `for...in` 中将键推断为 `string`：因为对象在结构类型下可能包含额外属性，且原型链也会带来不可预知的键。
- 不要简单地用类型断言掩盖错误，除非你完全确信对象没有额外键。
- 使用 `Object.entries` 是最稳妥的遍历方式，虽然类型不精确，但不会出错。
- 在可能的情况下，优先使用 `Map` 而不是普通对象，以获得更简单的类型行为。