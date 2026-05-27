## Item 14 详细解读：使用 `readonly` 避免与修改相关的错误

在 JavaScript 中，对象和数组默认是可变的，这常常导致难以追踪的 bug。TypeScript 提供了 `readonly` 修饰符，帮助我们明确声明“只读”语义，并在类型层面防止意外的修改。

---

### 1. 问题示例：意外修改数组

```typescript
function arraySum(arr: number[]) {
  let sum = 0, num;
  while ((num = arr.pop()) !== undefined) {
    sum += num;
  }
  return sum;
}

function printTriangles(n: number) {
  const nums = [];
  for (let i = 0; i < n; i++) {
    nums.push(i);
    console.log(arraySum(nums));
  }
}

printTriangles(5);
// 输出：0, 1, 2, 3, 4 （而不是三角数 0, 1, 3, 6, 10）
```

**原因**：`arraySum` 通过 `pop()` 修改了传入的数组，导致原数组被清空。`printTriangles` 假设 `arraySum` 不会修改参数，但这个假设被违反了。TypeScript 默认并不阻止这种修改。

---

### 2. `readonly` 的基本用法

#### 2.1 对象属性 `readonly`

```typescript
interface PartlyMutableName {
  readonly first: string;  // 只读
  last: string;            // 可写
}

const jackie: PartlyMutableName = { first: 'Jacqueline', last: 'Kennedy' };
jackie.last = 'Onassis';   // ✅ OK
jackie.first = 'Jacky';    // ❌ 错误：只读属性不可赋值
```

#### 2.2 `Readonly<T>` 工具类型

将对象的所有属性变为只读：

```typescript
interface FullyMutableName {
  first: string;
  last: string;
}
type FullyImmutableName = Readonly<FullyMutableName>;
// 等价于：{ readonly first: string; readonly last: string; }
```

**适用场景**：函数接收一个对象参数且不修改它时，用 `Readonly<T>` 包装参数类型，既能文档化意图，又能让编译器强制执行。

---

### 3. `readonly` 的局限性

#### 3.1 浅层性 (Shallow)

`readonly` 和 `Readonly<T>` 只作用于**直接属性**，不会递归到嵌套对象。

```typescript
interface Outer {
  inner: { x: number; };
}
const obj: Readonly<Outer> = { inner: { x: 0 } };
obj.inner = { x: 1 };      // ❌ 错误：inner 是只读属性
obj.inner.x = 1;           // ✅ 允许！inner.x 没有被标记为只读
```

如果需要深层只读，可以使用社区库（如 `ts-essentials` 中的 `DeepReadonly`）。

#### 3.2 对方法无效

`Readonly<Date>` 不会移除 `Date` 对象的变异方法（如 `setFullYear`）。

```typescript
const date: Readonly<Date> = new Date();
date.setFullYear(2037);   // ✅ 类型检查通过，但实际会修改 date！
```

这是因为 `Readonly` 只影响属性，不影响方法。对于类，需要自行设计可变/不可变版本。

---

### 4. 数组的 `readonly`：`readonly T[]`

TypeScript 为数组提供了专门的只读变体：`readonly T[]`，对应标准库中的 `ReadonlyArray<T>` 接口。

对比 `Array<T>` 和 `ReadonlyArray<T>`：

- `ReadonlyArray<T>` 移除了所有变异方法（`pop`, `push`, `shift`, `unshift`, `splice` 等）。
- 将 `length` 属性和索引签名标记为 `readonly`。

**语法糖**：`readonly T[]` 等价于 `ReadonlyArray<T>`。

**赋值规则**：
- 可变数组可以赋值给只读数组（向下兼容）。
- 只读数组**不能**赋值给可变数组（防止丢失只读保护）。

```typescript
const a: number[] = [1, 2, 3];
const b: readonly number[] = a;   // ✅ OK
const c: number[] = b;            // ❌ 错误
```

---

### 5. 修复示例：使用 `readonly` 捕获错误

#### 5.1 尝试传递只读视图（失败，因为目标函数期望可变数组）

```typescript
function printTriangles(n: number) {
  const nums = [];
  for (let i = 0; i < n; i++) {
    nums.push(i);
    console.log(arraySum(nums as readonly number[]));
    // ❌ 错误：readonly number[] 不能赋值给 mutable number[]
  }
}
```

#### 5.2 修改 `arraySum` 接受只读数组

```typescript
function arraySum(arr: readonly number[]) {
  let sum = 0;
  for (const num of arr) {   // 只读迭代，不修改
    sum += num;
  }
  return sum;
}

// 现在 printTriangles 可以正确调用，无需类型断言
function printTriangles(n: number) {
  const nums: number[] = [];
  for (let i = 0; i < n; i++) {
    nums.push(i);
    console.log(arraySum(nums));   // ✅ 自动兼容，nums 被当作只读视图
  }
}
// 输出三角数：0, 1, 3, 6, 10
```

---

### 6. `const` vs `readonly`

| 特性 | `const` | `readonly` |
|------|---------|------------|
| 作用层面 | 变量**引用**不可重新赋值 | 对象**属性**不可修改 |
| 可变性 | 不能改变引用的对象，但对象本身可变 | 属性值不能直接赋值，但嵌套属性可能仍可变 |
| 适用对象 | 变量声明 | 属性或类型声明 |

```typescript
const obj = { x: 1 };
obj.x = 2;   // ✅ 对象本身可变
obj = {};    // ❌ 引用不可变

interface WithReadonly {
  readonly y: number;
}
const ro: WithReadonly = { y: 1 };
ro.y = 2;    // ❌ 属性不可变
```

---

### 7. `readonly` 的传染性与协作

- 如果一个函数声明参数为 `readonly`，它调用的其他函数如果也需要该参数，那些函数也应该声明 `readonly`。这会使只读约束在代码中传播，从而提高整体安全性。
- 若遇到无法修改的第三方库函数（期望可变数组），可以用类型断言临时绕过，或通过模块 augmentation 修补类型声明。

---

### 8. 总结要点

| 实践建议 | 原因 |
|----------|------|
| 函数不修改参数时，参数类型声明为 `readonly`（数组）或 `Readonly<T>`（对象） | 明确契约，防止意外修改 |
| 优先使用 `readonly T[]` 而不是 `T[]` 作为函数参数类型 | 增强安全性，允许更多调用方（可变和只读数组均可传入） |
| 警惕浅层只读：需要深度只读时使用专门工具 | 避免嵌套对象被意外修改 |
| 理解 `const` 与 `readonly` 的区别 | 避免混淆引用不可变与属性不可变 |

**最终效果**：`readonly` 让意图在类型系统中显式表达，帮助捕捉像 `arraySum` 那样无意的修改，将运行时的错误提前到编译阶段。