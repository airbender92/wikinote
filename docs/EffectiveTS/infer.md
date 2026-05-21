在 TypeScript 中，`infer` 关键字允许你在条件类型中**动态地推断**某个位置的类型。结合元组（tuple）的 rest 元素，可以轻松提取“第一个”和“剩余部分”。

下面是一个经典的例子——定义一个条件类型 `First<T>` 和 `Rest<T>`：

```typescript
// 提取元组的第一个元素
type First<T extends any[]> = T extends [infer First, ...any[]] ? First : never;

// 提取除第一个元素外的剩余部分
type Rest<T extends any[]> = T extends [any, ...infer Rest] ? Rest : [];
```

### 工作原理
- `T extends [infer First, ...any[]]` 表示：如果 `T` 可以匹配一个“至少有一个元素”的元组，则把**第一个元素的类型**推断为 `First`，`...any[]` 忽略剩余元素。
- `T extends [any, ...infer Rest]` 则把**剩余元素的类型**推断为 `Rest`（返回一个元组）。
- 对于空数组，`First` 返回 `never`，`Rest` 返回 `[]`。

### 使用示例
```typescript
type MyTuple = [string, number, boolean];

type A = First<MyTuple>;  // string
type B = Rest<MyTuple>;   // [number, boolean]

type Empty = [];
type C = First<Empty>;    // never
type D = Rest<Empty>;     // []
```

### 更深入的用法：同时提取 First 和 Rest
你可以用一个条件类型同时捕获两者：

```typescript
type Split<T extends any[]> = T extends [infer First, ...infer Rest]
  ? { first: First; rest: Rest }
  : { first: never; rest: [] };

// 使用
type Result = Split<[1, 'a', true]>;  // { first: 1; rest: ['a', true] }
```

### 注意事项
1. `infer` 只能在条件类型（`extends`）的右侧使用，并且必须写在 `extends` 子句中。
2. 对数组/元组使用 rest 推断时，TypeScript 默认会保留**元组标签**和**可读性修饰符**（`readonly`、可选等）。
3. 如果需要处理 `readonly` 元组，可以添加 `readonly` 约束：
   ```typescript
   type FirstReadonly<T extends readonly any[]> = T extends readonly [infer First, ...any[]] ? First : never;
   ```

掌握 `infer` 和 rest 元素的组合，是编写高阶类型工具（如实现 `Push`、`Pop`、`Reverse` 等）的基础。