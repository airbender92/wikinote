## Item 34 详细讲解：优先使用接口的联合，而不是联合类型的接口

这一节的核心是：**如果你的接口中有多个属性是联合类型（union types），并且这些属性之间存在配对关系（例如 `layout` 为 `FillLayout` 时 `paint` 也必须是 `FillPaint`），那么这样的接口设计就是有问题的**。它允许无效的状态（例如 `FillLayout` 搭配 `LinePaint`）。更好的做法是将每种有效组合定义为一个独立的接口，然后取这些接口的联合（union of interfaces）。最常见的实现方式就是**可辨识联合（tagged union）**。

---

### 例子一：矢量绘图程序的图层（Layer）

#### 糟糕的设计：接口中的属性都是联合类型

```ts
interface Layer {
  layout: FillLayout | LineLayout | PointLayout;
  paint: FillPaint | LinePaint | PointPaint;
}
```

**问题**：  
- 理论上，一个图层应该由匹配的布局和绘制样式组成。例如，一个填充图层（FillLayer）应该使用 `FillLayout` 和 `FillPaint`；线条图层应使用 `LineLayout` 和 `LinePaint`。  
- 但上述接口允许 `layout: FillLayout` 同时 `paint: LinePaint` 这种无意义的组合。  
- 当其他代码处理 `Layer` 时，不得不考虑这种无效组合，要么写出大量的类型断言，要么在运行时检查是否匹配，违背了“让非法状态不可表示”的原则。

#### 改进方案：接口的联合

```ts
interface FillLayer {
  layout: FillLayout;
  paint: FillPaint;
}
interface LineLayer {
  layout: LineLayout;
  paint: LinePaint;
}
interface PointLayer {
  layout: PointLayout;
  paint: PointPaint;
}
type Layer = FillLayer | LineLayer | PointLayer;
```

现在，`Layer` 类型的值只能是三种具体接口之一，不可能出现混合搭配。类型系统精确地描述了有效状态。

---

### 加入可辨识标签（tagged union）

有时候，你需要根据图层的类型来编写条件逻辑。上述的 `FillLayer`、`LineLayer`、`PointLayer` 没有共同的字段可以用来区分它们。TypeScript 无法通过简单的 `if` 或 `switch` 来收窄类型。为此，我们加入一个 **标签字段**（通常命名为 `type`）：

```ts
interface FillLayer {
  type: 'fill';
  layout: FillLayout;
  paint: FillPaint;
}
interface LineLayer {
  type: 'line';
  layout: LineLayout;
  paint: LinePaint;
}
interface PointLayer {
  type: 'point';
  layout: PointLayout;
  paint: PointPaint;
}
type Layer = FillLayer | LineLayer | PointLayer;
```

现在 TypeScript 可以根据 `layer.type` 的值精确收窄 `layer` 的具体类型：

```ts
function drawLayer(layer: Layer) {
  if (layer.type === 'fill') {
    // 这里 layer 被收窄为 FillLayer
    const { layout, paint } = layer; // 类型正确
  } else if (layer.type === 'line') {
    // layer 是 LineLayer
  } else {
    // layer 是 PointLayer (穷尽性检查)
  }
}
```

这种可辨识联合（discriminated union）在 TypeScript 中极其常见，因为它让类型收窄变得简单可靠。

---

### 例子二：可选字段的隐式关系

考虑一个 `Person` 接口，其中 `placeOfBirth` 和 `dateOfBirth` 要么同时存在，要么同时不存在：

```ts
interface Person {
  name: string;
  placeOfBirth?: string;   // 可选
  dateOfBirth?: Date;      // 可选
}
```

**问题**：  
- 类型允许 `{ name: 'A', placeOfBirth: 'London' }` 而缺少 `dateOfBirth`，或者反过来。  
- 这两者之间的关系没有在类型系统中表达，需要开发者在代码中记住并手动检查，容易出错。

#### 改进方案1：将相关字段分组到一个可选对象中

```ts
interface Person {
  name: string;
  birth?: {
    place: string;
    date: Date;
  };
}
```

现在，要么 `birth` 整个对象不存在（没有出生信息），要么它同时包含 `place` 和 `date`。调用方只需一次检查 `if (person.birth)` 即可安全访问两者。

#### 改进方案2：使用接口的联合（当无法更改数据结构时）

如果数据结构来自外部 API，你不能修改为嵌套对象，仍然可以用联合类型来表达关系：

```ts
interface Name {
  name: string;
}
interface PersonWithBirth extends Name {
  placeOfBirth: string;
  dateOfBirth: Date;
}
type Person = Name | PersonWithBirth;
```

这样，`Person` 要么只有 `name`（没有出生信息），要么同时有 `placeOfBirth` 和 `dateOfBirth`。使用类型守卫 `'placeOfBirth' in person` 来收窄：

```ts
function eulogize(person: Person) {
  if ('placeOfBirth' in person) {
    // person 被收窄为 PersonWithBirth
    console.log(person.dateOfBirth);
  }
}
```

---

### 核心原理总结

| 模式 | 描述 | 优点 |
|------|------|------|
| **接口中的联合类型属性** | `interface Layer { a: A1\|A2; b: B1\|B2 }` | 简洁，但允许无效组合 |
| **接口的联合** | `type Layer = Layer1 \| Layer2` | 精确，不允许无效组合 |
| **可辨识联合** | 每个接口包含共同的标签字段（如 `type`） | 支持类型收窄，易于使用 `switch` |
| **分组可选字段** | 将多个相关可选字段放入一个可选对象 | 一次检查，所有字段安全访问 |

**最终建议**：
- 当你发现自己写的接口中有多个联合类型的属性，并且它们之间存在“配对”关系时，立刻重构为接口的联合。
- 加上一个字符串字面量类型的标签字段，成为可辨识联合，以获得最佳的类型收窄体验。
- 对于多个可选字段，考虑将它们合并为一个可选对象，从而表达“要么全有，要么全无”的关系。

这完全遵循了 Item 29 的原则：**让你的类型只能表示有效的状态**。虽然类型定义会变长一些，但换来的安全性和可读性是值得的。