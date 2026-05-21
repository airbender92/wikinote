## Item 4 详细讲解：适应结构类型系统（Structural Typing）

TypeScript 的核心设计理念之一是 **结构类型系统**。这意味着类型兼容性不是基于类型名称或声明位置，而是基于**类型的实际成员结构**。只要两个类型具有相同的成员（或所需成员的子集），它们就被认为是兼容的。这直接反映了 JavaScript 的“鸭子类型”行为。理解结构类型对于写出符合预期、避免陷阱的 TypeScript 代码至关重要。

---

### 一、什么是结构类型？

在 TypeScript 中，只要一个对象具有函数所要求的所有属性，即使它没有显式声明实现了该接口，也可以被传入。

**示例**：

```ts
interface Vector2D {
  x: number;
  y: number;
}

interface NamedVector {
  name: string;
  x: number;
  y: number;
}

function calculateLength(v: Vector2D) {
  return Math.sqrt(v.x ** 2 + v.y ** 2);
}

const v: NamedVector = { x: 3, y: 4, name: 'Pythagoras' };
calculateLength(v); // ✅ 通过，返回 5
```

- `NamedVector` 没有声明继承或实现 `Vector2D`，但由于它拥有 `x` 和 `y` 属性（且类型为 `number`），TypeScript 认为它符合 `Vector2D` 的形状。
- 这符合 JavaScript 的灵活性：函数只需要它需要的属性，不关心对象如何构造。

**优点**：代码复用性高，无需写大量的接口继承或适配器。

---

### 二、结构类型可能带来的问题

#### 2.1 “过多属性”导致逻辑错误

```ts
interface Vector3D {
  x: number;
  y: number;
  z: number;
}

function normalize(v: Vector3D) {
  const length = calculateLength(v); // 错误！calculateLength 只使用 x,y
  return {
    x: v.x / length,
    y: v.y / length,
    z: v.z / length,
  };
}
```

- `calculateLength` 期望 `Vector2D`，但传入 `Vector3D` 时，由于结构上包含 `x` 和 `y`，类型检查通过。
- 实际运行时，`length` 只考虑了 `x` 和 `y`，忽略了 `z`，导致归一化结果错误（返回的向量长度不是 1）。
- **TypeScript 无法捕获此类语义错误**，因为它只检查结构，不检查“意图”。

**结论**：结构类型是“开放的”，函数接受任何拥有所需属性的值，可能包含额外属性。这要求开发者自己注意不要让函数用于不合适的类型。

#### 2.2 遍历对象属性时的类型问题

```ts
function calculateLengthL1(v: Vector3D) {
  let length = 0;
  for (const axis of Object.keys(v)) {
    const coord = v[axis];   // ❌ 错误：元素隐式具有 'any' 类型
    length += Math.abs(coord);
  }
  return length;
}
```

**为什么报错**？
- `Object.keys(v)` 返回 `string[]`，而不是 `("x"|"y"|"z")[]`。
- TypeScript 无法保证 `v[axis]` 是数字，因为 `v` 可能具有额外属性（如 `address`），其值可能是任意类型。
- 尽管在代码中 `v` 被声明为 `Vector3D`，但结构类型允许传入具有更多属性的对象，因此 TypeScript 保守地将 `axis` 视为 `string`，导致索引访问不安全。

**正确做法**：不要遍历对象属性，而是显式访问已知字段：
```ts
function calculateLengthL1(v: Vector3D) {
  return Math.abs(v.x) + Math.abs(v.y) + Math.abs(v.z);
}
```

#### 2.3 类的结构类型行为

```ts
class SmallNumContainer {
  num: number;
  constructor(num: number) {
    if (num < 0 || num >= 10) throw new Error(...);
    this.num = num;
  }
}

const b: SmallNumContainer = { num: 2024 }; // ✅ 通过！
```

- 虽然 `b` 不是通过 `new SmallNumContainer` 构造的，但它的结构（一个 `num` 属性，类型 `number`）与 `SmallNumContainer` 类的实例形状相同，因此赋值被允许。
- 这意味着 `b` 可能绕过了构造函数中的验证逻辑，导致后续代码假设 `num` 在 0-9 范围内时出错。

**启示**：在 TypeScript 中，类也被视为结构类型，不能假设所有实例都经过构造器验证。如果需要确保运行时验证，可以使用私有字段（`#num`）或品牌（Item 64）。

---

### 三、结构类型带来的好处

#### 3.1 简化单元测试

**生产代码**：
```ts
interface Author { first: string; last: string; }

function getAuthors(database: PostgresDB): Author[] {
  const rows = database.runQuery(`SELECT first, last FROM authors`);
  return rows.map(row => ({ first: row[0], last: row[1] }));
}
```

为了测试 `getAuthors`，你通常需要模拟整个 `PostgresDB` 类，这很繁琐。

**改进**：引入一个最小接口 `DB`，只包含需要的方法：
```ts
interface DB {
  runQuery: (sql: string) => any[];
}

function getAuthors(database: DB): Author[] { ... }
```

- 生产环境中，`PostgresDB` 由于拥有 `runQuery` 方法，自动符合 `DB` 接口，无需修改。
- 测试中，你可以直接传入一个简单对象：
  ```ts
  getAuthors({
    runQuery(sql: string) {
      return [['Toni', 'Morrison'], ['Maya', 'Angelou']];
    }
  });
  ```

**优点**：无需创建复杂的模拟对象或使用模拟库，结构类型自动完成类型检查。

#### 3.2 解耦库之间的依赖

通过定义最小接口，你可以避免直接依赖具体实现，从而切断不必要的类型传递（Item 70 有更多讨论）。

---

### 四、如何避免结构类型的陷阱？

- **为函数提供更精确的输入类型**：可以使用“可选 `never` 属性”禁止额外属性（Item 63），或使用品牌（brand）实现名义类型（Item 64）。
- **不要假设类型是封闭的**：始终考虑到对象可能有额外属性，编写健壮的逻辑（例如使用 `in` 操作符检查属性存在性，而不是直接索引）。
- **对于类，如果必须保证构造逻辑，使用私有字段或品牌**，避免仅依靠结构兼容性。

---

### 五、总结要点（Things to Remember）

- **JavaScript 是鸭子类型，TypeScript 通过结构类型模拟这一行为**：只要形状匹配，类型就兼容。值可能包含类型声明中未列出的额外属性。
- **类型不是“封闭”的**：函数接收的参数可能比声明的属性更多。
- **类也遵循结构类型规则**：你可能得到并非通过构造函数创建的实例，因此不能依赖构造器中的验证逻辑。
- **利用结构类型简化测试**：通过定义最小接口，可以使用简单对象模拟复杂依赖，无需模拟库。

通过深入理解结构类型，你可以更好地利用 TypeScript 的灵活性，同时避免常见的意外。在实际编码中，要时刻记住：**“看起来像鸭子，就是鸭子”**，但也要注意“看起来像二维向量的三维向量”可能导致数学错误。