## Item 63 详细讲解：使用可选的 `never` 属性模拟“异或”（Exclusive Or）

在自然语言中，“或”通常是指**异或（exclusive or）**：要么 A，要么 B，不能同时两者。但在 TypeScript 的类型系统中，联合类型（`A | B`）是**包含或（inclusive or）**：它允许 A、B，或者**同时具有 A 和 B 的所有属性**（因为结构类型系统允许额外属性）。这可能导致一些意料之外的类型兼容性。本节介绍了一种通过**可选的 `never` 属性**来强制实现互斥（异或）的技巧。

---

### 1. 问题：结构类型导致联合类型包含“两者”

```ts
interface ThingOne {
  shirtColor: string;
}

interface ThingTwo {
  hairColor: string;
}

type Thing = ThingOne | ThingTwo;
```

直观上，我们希望 `Thing` 表示“要么有 `shirtColor`，要么有 `hairColor`，但不能同时有”。但由于 TypeScript 的结构类型：

- `ThingOne` 允许有额外属性（例如 `hairColor`）。
- `ThingTwo` 也允许有额外属性（例如 `shirtColor`）。

所以下面这个同时包含两个属性的对象，可以被同时赋值给 `ThingOne` 和 `ThingTwo`：

```ts
const bothThings = { shirtColor: 'red', hairColor: 'blue' };
const thing1: ThingOne = bothThings;  // ✅ 因为 shirtColor 存在，额外属性 hairColor 被忽略
const thing2: ThingTwo = bothThings;  // ✅ 同理
```

这就是**包含或**：`bothThings` 既可以被当作 `ThingOne`，也可以被当作 `ThingTwo`。但业务上你可能希望禁止这种“既是又是”的情况（例如你不能同时是一个有衬衫颜色的人和有头发颜色的人——虽然现实可以，但这里只是示例）。

---

### 2. 解决方案：使用可选的 `never` 属性禁止额外属性

思路：在每个接口中，显式声明一个**可选属性**，其类型为 `never`，属性名与另一个接口中的独有属性名相同。

```ts
interface OnlyThingOne {
  shirtColor: string;
  hairColor?: never;   // 禁止存在 hairColor 属性
}

interface OnlyThingTwo {
  hairColor: string;
  shirtColor?: never;   // 禁止存在 shirtColor 属性
}

type ExclusiveThing = OnlyThingOne | OnlyThingTwo;
```

**原理**：
- `never` 类型没有值。一个可选属性如果类型是 `never`，那么它**唯一允许的状态就是该属性不存在**（因为不能给它赋任何值，连 `undefined` 也不行？实际上 `?: never` 允许属性缺失，或者值为 `undefined`？注意：在 TypeScript 中，`?` 表示该属性可以不存在；如果存在，它的值必须是 `never` 类型，而没有任何值满足 `never`，因此实际上该属性不能存在。这种微妙的行为使得该技巧有效）。
- 当对象同时有 `shirtColor` 和 `hairColor` 时，它同时违反了 `OnlyThingOne` 和 `OnlyThingTwo` 的约束：
  - 作为 `OnlyThingOne`，它多了一个 `hairColor` 属性（且类型不是 `never`），所以不兼容。
  - 作为 `OnlyThingTwo`，它多了一个 `shirtColor` 属性，也不兼容。
- 因此，`bothThings` 不能赋值给 `ExclusiveThing`。

**效果**：

```ts
const bothThings = { shirtColor: 'red', hairColor: 'blue' };
const thing1: OnlyThingOne = bothThings;     // ❌ hairColor 存在且不是 never
const thing2: OnlyThingTwo = bothThings;     // ❌ shirtColor 存在且不是 never
const allThings: ExclusiveThing = bothThings; // ❌ 同时违反两者
```

只有**恰好只包含一个接口所需属性**的对象才能通过：

```ts
const justShirt = { shirtColor: 'red' };
const justHair = { hairColor: 'blue' };
const a: ExclusiveThing = justShirt;  // ✅
const b: ExclusiveThing = justHair;   // ✅
```

---

### 3. 其他应用：禁止三维向量被当作二维向量

```ts
interface Vector2D {
  x: number;
  y: number;
  z?: never;   // 禁止出现 z 属性
}

function norm(v: Vector2D) { return Math.sqrt(v.x ** 2 + v.y ** 2); }

const v3 = { x: 3, y: 4, z: 5 };
norm(v3);   // ❌ 类型“{ x: number; y: number; z: number; }”的参数不能赋给类型“Vector2D”的参数
```

没有 `z?: never` 时，`v3` 可以传给 `norm` 因为结构类型允许额外属性（`z`），但数学上三维向量的长度计算应该包含 `z`，这会导致错误。加入 `z?: never` 后就禁止了这种误用。

---

### 4. 替代方案：使用可辨识联合（tagged union）

可辨识联合通过一个共同的标签字段来区分，天然是互斥的：

```ts
interface ThingOneTag {
  type: 'one';
  shirtColor: string;
}
interface ThingTwoTag {
  type: 'two';
  hairColor: string;
}
type Thing = ThingOneTag | ThingTwoTag;
```

因为 `type` 字段不能同时是 `'one'` 和 `'two'`，所以不可能存在一个对象同时满足两个接口。这是最推荐的“异或”实现方式。

**何时用可选的 `never`**：当你**无法**或**不想**添加一个显式的标签字段时（例如你需要保持类型与某个外部 API 的 JSON 形状一致，或者你不想在运行时增加一个无意义的字段），可以使用 `never` 技巧。

---

### 5. 通用 `XOR` 辅助类型

如果你经常需要创建两个类型的异或，可以定义一个泛型 `XOR<T1, T2>`：

```ts
type XOR<T1, T2> =
  | (T1 & { [k in Exclude<keyof T2, keyof T1>]?: never })
  | (T2 & { [k in Exclude<keyof T1, keyof T2>]?: never });
```

**解释**：
- `Exclude<keyof T2, keyof T1>`：取 `T2` 中有而 `T1` 中没有的属性名。
- 将这些属性在 `T1` 中定义为可选的 `never`，这样就禁止了 `T1` 同时拥有这些属性。
- 同样对 `T2` 也做对称处理。
- 最终结果是 `T1` 和 `T2` 的联合，但各自排除了对方的独有属性。

使用示例：

```ts
type ExclusiveThing = XOR<ThingOne, ThingTwo>;
// 效果等同于上面的 OnlyThingOne | OnlyThingTwo
```

---

### 6. 注意事项

- `?: never` 并不完全等同于“属性不能存在”，因为 TypeScript 仍然允许显式设置该属性为 `undefined`？实际上，如果你写 `hairColor?: never`，你可以赋值 `undefined` 吗？测试发现 `{ shirtColor: 'red', hairColor: undefined }` 是否满足 `OnlyThingOne`？这取决于 `strictNullChecks`。通常我们假设对象不会有 `undefined` 属性（除非显式设置）。但为了确保严谨，可以改用 `hairColor: never`（非可选），但那样就必须提供 `hairColor` 属性，矛盾。因此该技巧依赖于“对象没有未定义的属性”的常见模式。如果担心，还是推荐使用可辨识联合。

- 这种技巧在 TypeScript 社区中被称为“可选 never 模式”，常用于实现互斥类型。

---

### 7. 总结

- **问题**：联合类型 `A | B` 是包含或（inclusive or），允许同时拥有 A 和 B 的属性。
- **解决方案1（推荐）**：使用可辨识联合（tagged union），通过一个公共标签字段实现互斥。
- **解决方案2（备选）**：在每个接口中添加可选属性，类型为 `never`，属性名为对方接口的独有属性名。这样任何同时包含双方属性的对象都会违反类型约束。
- **通用工具**：可以定义 `XOR<T1, T2>` 来自动生成互斥类型。
- **适用场景**：当你无法或不希望添加标签字段时，使用 `never` 技巧。否则优先使用可辨识联合。

**核心启示**：TypeScript 的类型系统默认是结构性的，联合是包含的。要表达“异或”，你需要显式地添加约束来禁止重叠。