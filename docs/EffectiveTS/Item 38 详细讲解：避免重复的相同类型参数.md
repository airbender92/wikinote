## Item 38 详细讲解：避免重复的相同类型参数

这一节的核心是：**如果一个函数有多个连续参数且类型相同（例如全都是 `number`），那么调用时很容易混淆参数顺序，而类型系统无法检测这种错误。应该通过引入不同的类型（如 `Point`、`Dimension`）或使用单个对象参数来让参数变得自描述且类型安全。**

书中用 `drawRect` 函数作为例子，展示了这个问题以及两种改进方法。

---

### 1. 问题示例：五个 `number` 参数

```ts
function drawRect(x: number, y: number, w: number, h: number, opacity: number) {
  // ...
}
```

调用代码：
```ts
drawRect(25, 50, 75, 100, 1);
```

**问题**：
- 仅看调用，无法知道 `25, 50` 是左上角坐标还是第一个点的坐标，`75, 100` 是宽度/高度还是第二个点的坐标，`1` 是不透明度还是其他。
- 因为所有参数类型都是 `number`，TypeScript 无法检查顺序是否正确。例如把宽度和高度的位置互换（`drawRect(25, 50, 100, 75, 1)`）仍然通过类型检查，但逻辑错误。
- 可读性差，维护困难，容易引入难以发现的 bug。

**根本原因**：类型相同且缺乏语义标签。参数的含义只存在于文档或开发者的记忆中，没有在类型系统中表达。

---

### 2. 改进方法一：引入不同的类型

定义两个接口 `Point` 和 `Dimension`，分别表示坐标和尺寸：

```ts
interface Point {
  x: number;
  y: number;
}

interface Dimension {
  width: number;
  height: number;
}

function drawRect(topLeft: Point, size: Dimension, opacity: number) {
  // ...
}
```

现在调用方式变为：

```ts
drawRect({ x: 25, y: 50 }, { width: 75, height: 100 }, 1);
```

**优点**：
- 参数的含义一目了然：第一个是左上角坐标，第二个是尺寸，第三个是不透明度。
- 类型系统可以捕获顺序错误。例如，如果错误地传入了两个 `Point`：

  ```ts
  drawRect({ x: 25, y: 50 }, { x: 75, y: 100 }, 1);
  // 错误：类型 '{ x: number; y: number; }' 不能赋给类型 'Dimension'
  ```

- 虽然参数数量仍为三个，但每个参数的类型不同，因此混淆的可能性大大降低。

**注意**：这里 `opacity` 仍然是独立的 `number` 参数。如果将来再添加更多参数，可能需要进一步重构。

---

### 3. 改进方法二：使用单个对象参数

将所有参数合并到一个对象类型中：

```ts
interface DrawRectParams extends Point, Dimension {
  opacity: number;
}

function drawRect(params: DrawRectParams) {
  // ...
}
```

调用方式：

```ts
drawRect({
  x: 25,
  y: 50,
  width: 75,
  height: 100,
  opacity: 1,
});
```

**优点**：
- 所有参数都有名字，完全自文档化。
- 参数顺序无关紧要，因为使用的是命名属性。
- 类型检查确保所有必需属性都存在，且类型正确。
- 将来添加新参数（例如 `strokeWidth`、`fillColor`）不会破坏现有调用（可以设为可选或扩展接口），更容易演化。

**这是更推荐的模式**，尤其适用于参数数量较多（超过 3 个）或未来可能增加参数的函数。

---

### 4. 例外情况

书中也提到，有些情况下重复相同类型的参数是可以接受的：

- **参数是可交换的（commutative）**：例如 `max(a, b)` 或 `isEqual(a, b)`，顺序不影响结果。
- **存在明确的“自然顺序”**：例如数组的 `slice(start, end)`，`start` 在前 `end` 在后很直观；日期 `new Date(year, month, day)` 通常也按时间顺序。但要小心，并非所有人都认同同一自然顺序（例如 `month/day/year` vs `day/month/year`）。

然而，即使在这些例外中，使用对象参数往往也不会更差，有时甚至更清晰（例如 `{ start, end }` 或 `{ year, month, day }`）。

---

### 5. 扩展思考：过多参数的问题

即使参数类型不完全相同，过多的参数（例如 10 个）也容易出错。书中引用了一句名言：“如果你有一个 10 个参数的函数，你可能漏了一些参数。” 意思是参数列表过长暗示函数职责过多，应该拆分或重构。

**工具支持**：`typescript-eslint` 的 `max-params` 规则可以限制函数参数的数量（例如最多 3 或 4 个），超过则报错。

**重构建议**：
- 将相关参数分组为对象。
- 将函数拆分为多个更小的函数。
- 使用建造者（builder）模式或配置对象。

---

### 6. 总结：核心原则

> “Make interfaces easy to use correctly and hard to use incorrectly.” —— Scott Meyers, *Effective C++*

**具体实践**：
- 避免连续出现相同类型的参数。如果两个参数都是 `number`，尽量用不同的接口包装它们（哪怕接口只是 `{ value: number }`）。
- 对于参数超过 3 个的函数，优先使用单个对象参数。
- 利用 TypeScript 的类型系统来编码语义信息，而不是依赖注释或文档。

**最终效果**：调用者不容易犯错，即使犯错，类型检查器也能立即捕获，而不是等到运行时才暴露。