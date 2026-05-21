## Item 64 详细讲解：考虑使用品牌（Brands）实现名义类型

TypeScript 是**结构类型**（structural typing）语言：只要两个类型具有相同的成员结构，它们就被认为是兼容的，即使它们来自不同的地方或具有不同的语义含义。这在很多场景下非常灵活，但有时也会带来问题——例如，你可能希望区分“绝对路径”和“相对路径”，或者区分“米”和“秒”，尽管它们底层都是 `string` 或 `number`。这时可以使用**品牌（brands）** 来模拟**名义类型**（nominal typing），即通过一个唯一的“标记”让类型系统认为它们是不同的类型，即使它们的结构相同。

---

### 1. 问题：结构类型导致的语义混淆

```ts
interface Vector2D { x: number; y: number; }

function calculateNorm(p: Vector2D) {
  return Math.sqrt(p.x ** 2 + p.y ** 2);
}

const vec3D = { x: 3, y: 4, z: 1 };
calculateNorm(vec3D); // ✅ 类型检查通过，但数学上错误（忽略了 z）
```

尽管 `vec3D` 多了一个 `z` 属性，但因为结构上包含 `x` 和 `y`，TypeScript 认为它是 `Vector2D` 的合法值。这可能导致逻辑错误。

**可能的解决方案**：
- **可选的 `never` 属性**（Item 63）：`z?: never` 可以禁止 `z` 属性，但需要修改接口，且不能用于原始类型（如 `string`、`number`）。
- **运行时标签**：例如 `type: '2d'`，但会带来运行时开销，且只能用于对象类型。
- **品牌（brands）**：纯类型层面的标记，零运行时成本，且可以用于原始类型。

---

### 2. 品牌的概念

品牌就是在类型上附加一个**类型层面的假属性**，使得 TypeScript 认为该类型与其他结构相同的类型不兼容。这个假属性在运行时不存在，它只存在于类型系统中。

**基本语法**：使用交叉类型（`&`）与一个包含唯一标记的对象类型相交。

```ts
type AbsolutePath = string & { _brand: 'abs' };
```

- `string & { _brand: 'abs' }` 表示：这是一个字符串，但它还有一个类型层面的标记 `_brand`，其字面量为 `'abs'`。
- 你无法在运行时真的给一个字符串添加 `_brand` 属性（Item 10 解释过字符串是原始类型，不能添加属性）。但这没关系，因为品牌只存在于类型检查阶段。

**关键**：你不能直接创建 `AbsolutePath` 类型的值，必须通过类型断言或类型守卫来“标记”一个普通字符串为 `AbsolutePath`。

---

### 3. 实际应用示例

#### 3.1 绝对路径 vs 相对路径

```ts
type AbsolutePath = string & { _brand: 'abs' };
type RelativePath = string & { _brand: 'rel' };

function listAbsolutePath(path: AbsolutePath) { /* ... */ }
function listRelativePath(path: RelativePath) { /* ... */ }

// 类型守卫：检查是否为绝对路径
function isAbsolutePath(path: string): path is AbsolutePath {
  return path.startsWith('/');
}

// 类型守卫：检查是否为相对路径
function isRelativePath(path: string): path is RelativePath {
  return !path.startsWith('/');
}

function processPath(path: string) {
  if (isAbsolutePath(path)) {
    listAbsolutePath(path);   // ✅ path 被收窄为 AbsolutePath
  } else {
    listRelativePath(path);   // ✅ path 被收窄为 RelativePath
  }
}
```

**效果**：
- 函数 `listAbsolutePath` 只接受经过验证的绝对路径。直接传入普通字符串会报错。
- 通过类型守卫，你可以将普通字符串转换为品牌类型。
- 品牌在编译时提供了额外的类型安全，而运行时没有任何额外开销。

---

#### 3.2 数值单位：米和秒

```ts
type Meters = number & { _brand: 'meters' };
type Seconds = number & { _brand: 'seconds' };

function toMeters(value: number): Meters {
  return value as Meters;
}

function toSeconds(value: number): Seconds {
  return value as Seconds;
}

function addMeters(a: Meters, b: Meters): Meters {
  return (a + b) as Meters;
}

const distance = toMeters(100);
const time = toSeconds(10);
const sum = addMeters(distance, time);   // ❌ 类型错误：Seconds 不能赋给 Meters
```

**注意**：算术运算（如 `distance * 2`）会丢失品牌，结果变成 `number`，需要重新断言。这在某些场景下不太方便，但仍然可以帮助捕获单位混淆的错误。

---

#### 3.3 排序列表（`SortedList<T>`）

结构上，排序列表与普通数组完全相同，但语义上要求元素已排序。你可以创建一个品牌来区分：

```ts
type SortedList<T> = T[] & { _brand: 'sorted' };

function isSorted<T>(xs: T[]): xs is SortedList<T> {
  for (let i = 0; i < xs.length - 1; i++) {
    if (xs[i] > xs[i + 1]) return false;
  }
  return true;
}

function binarySearch<T>(xs: SortedList<T>, x: T): boolean {
  // 二分查找实现，假设 xs 已排序
  // ...
}

const arr = [1, 3, 2];
if (isSorted(arr)) {
  binarySearch(arr, 2);   // ✅ arr 被收窄为 SortedList<number>
} else {
  // 不能调用 binarySearch，需要先排序
}
```

**好处**：二进制搜索函数 `binarySearch` 只能接收 `SortedList`，这迫使调用者必须先确保数组已排序（通过 `isSorted` 检查或手动排序后使用类型断言）。这类似于运行时检查，但通过类型系统强制。

---

### 4. 品牌的技术变体

#### 4.1 对象属性品牌（最常用）

```ts
type Branded<T, B> = T & { __brand: B };
type AbsolutePath = Branded<string, 'abs'>;
```

#### 4.2 使用 `unique symbol` 避免冲突

```ts
declare const absBrand: unique symbol;
type AbsolutePath = string & { [absBrand]: 'abs' };
```

- `unique symbol` 保证品牌标识符是唯一的，不会被其他模块意外使用。
- 通常不导出 `absBrand`，这样外部无法伪造 `AbsolutePath`（除非使用类型断言）。

#### 4.3 私有字段品牌（用于类）

```ts
class BrandedPath {
  private _brand: 'abs' = 'abs';
  constructor(public path: string) {}
}
type AbsolutePath = BrandedPath & { path: string };
```

这种方法有运行时开销（实例化对象），一般不推荐用于原始类型。

---

### 5. 品牌的局限性

- **需要显式转换**：每次从普通值转换为品牌类型时，必须使用类型断言（`as AbsolutePath`）或类型守卫。这增加了少量样板代码。
- **算术运算会丢失品牌**：对于 `number` 品牌，`a + b` 的结果是 `number`，需要重新断言为品牌类型。
- **不是完全安全的**：任何地方都可以用 `as AbsolutePath` 强行转换，绕过检查。因此品牌依赖团队约定和代码审查，而不是绝对保证。

---

### 6. 总结

- **何时使用品牌**：当你需要区分两个**结构相同但语义不同**的类型，并且不想引入运行时标签（例如为了性能或因为类型是原始类型）时，品牌是一个轻量级的选择。
- **品牌本质**：通过交叉类型添加一个假的、运行时不存在的属性，使类型系统认为它是不同的类型。
- **典型场景**：绝对/相对路径、带单位的数值、已排序数组、已验证的电子邮件地址等。
- **与其他方案对比**：
  - **可选的 `never` 属性**：适用于对象类型，禁止额外属性。
  - **可辨识联合**：需要显式的标签字段，是互斥类型的首选。
  - **品牌**：更灵活，可用于原始类型，且无运行时开销。

**最终建议**：品牌是一种“类型层面的约定”。它不提供绝对的安全性（因为断言可以绕过），但结合类型守卫和良好的编码规范，可以显著提高类型安全性，并让代码意图更清晰。当你觉得结构类型太宽松，需要更强的类型区分时，考虑引入品牌。