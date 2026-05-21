## Item 59 详细讲解：使用 `never` 类型进行穷尽性检查

这一节的核心是：**利用 `never` 类型（空集）的特性，将“遗漏了某个联合类型成员的处理分支”这种错误从运行时逻辑错误转变为编译时类型错误**。这种技巧称为“穷尽性检查”（exhaustiveness checking），特别适合处理可辨识联合（tagged union）的 `switch` 语句，确保你处理了所有可能的情况。

---

### 1. 问题的由来：遗漏 case 分支

假设你有一个图形绘制程序，使用可辨识联合表示不同的形状：

```ts
type Coord = [x: number, y: number];

interface Box {
  type: 'box';
  topLeft: Coord;
  size: Coord;
}

interface Circle {
  type: 'circle';
  center: Coord;
  radius: number;
}

type Shape = Box | Circle;
```

绘制函数使用 `switch` 根据 `type` 字段处理：

```ts
function drawShape(shape: Shape, context: CanvasRenderingContext2D) {
  switch (shape.type) {
    case 'box':
      context.rect(...shape.topLeft, ...shape.size);
      break;
    case 'circle':
      context.arc(...shape.center, shape.radius, 0, 2 * Math.PI);
      break;
  }
}
```

一切正常。但后来你添加了第三种形状 `Line`：

```ts
interface Line {
  type: 'line';
  start: Coord;
  end: Coord;
}

type Shape = Box | Circle | Line;
```

此时 `drawShape` 仍然通过类型检查，因为 `switch` 只处理了 `'box'` 和 `'circle'`，遇到 `type = 'line'` 时会跳过整个 `switch`，什么都不做。这是一个**错误遗漏**（error of omission），TypeScript 默认不会报错。

---

### 2. `never` 类型与穷尽性检查的原理

TypeScript 的 `never` 类型表示“不可能有值的类型”，即空集。当你对一个可辨识联合进行 `switch` 并覆盖了所有 `type` 字面量后，`default` 分支中 `shape` 的类型会被收窄为 `never`，因为已经没有剩余的可能性了。

例如，一个覆盖了所有 `Shape` 的 `processShape`：

```ts
function processShape(shape: Shape) {
  switch (shape.type) {
    case 'box': break;
    case 'circle': break;
    case 'line': break;
    default:
      shape;  // 类型为 never
  }
}
```

如果遗漏了 `'line'` 分支：

```ts
function processShape(shape: Shape) {
  switch (shape.type) {
    case 'box': break;
    case 'circle': break;
    default:
      shape;  // 类型为 Line（因为还剩下 Line 没有被处理）
  }
}
```

因此，我们可以利用这个特性：在 `default` 分支中，将 `shape` 赋值给一个期望 `never` 类型的变量，或者调用一个只接受 `never` 参数的函数。如果遗漏了任何分支，`shape` 的类型不会是 `never`，从而导致类型错误。

---

### 3. `assertUnreachable` 辅助函数

```ts
function assertUnreachable(value: never): never {
  throw new Error(`Missed a case! ${value}`);
}
```

- 参数类型是 `never`：意味着只有**不可能到达的代码**才能调用它（即 `value` 的类型已经是 `never`）。
- 返回类型也是 `never`：表示该函数永远不会正常返回（抛出异常）。
- 放在 `switch` 的 `default` 分支中：

```ts
function drawShape(shape: Shape, context: CanvasRenderingContext2D) {
  switch (shape.type) {
    case 'box': ... break;
    case 'circle': ... break;
    default:
      assertUnreachable(shape); // 如果遗漏了 'line'，这里 shape 类型是 Line，参数类型不匹配，报错
  }
}
```

当 `Shape` 增加新成员后，`default` 分支中的 `shape` 类型变成新的成员类型，传入 `assertUnreachable` 时报错，强制开发者补全 `case`。

**为什么即使全部覆盖了也要保留 `default`？**  
为了保证未来的扩展性：将来如果再添加新形状，这个 `default` 会立即产生类型错误，提醒你更新 `drawShape`。

---

### 4. 其他实现变体

除了 `assertUnreachable` 函数，你也可以直接在 `default` 分支中赋值给 `never` 变量：

```ts
function processShape(shape: Shape) {
  switch (shape.type) {
    case 'box': break;
    case 'circle': break;
    default:
      const exhaustiveCheck: never = shape; // 如果遗漏，这里的 shape 不是 never，报错
      throw new Error(`Missed case: ${exhaustiveCheck}`);
  }
}
```

或者使用 `satisfies` 操作符（TypeScript 4.9+）：

```ts
function processShape(shape: Shape) {
  switch (shape.type) {
    case 'box': break;
    case 'circle': break;
    default:
      shape satisfies never; // 如果 shape 不是 never，报错
      throw new Error(`Missed case: ${shape}`);
  }
}
```

三种方式本质相同，选你喜欢的一种即可。

---

### 5. 对于有返回值的函数

如果你的 `switch` 需要返回值，并且你有完整的 `case` 覆盖，可以省略 `default` 且函数会自动推导返回值类型。但如果你遗漏了某个 `case`，TypeScript 会将返回值推断为 `number | undefined`（如果开启了 `strictNullChecks`），这可能导致后续使用时出错。为了提前捕获遗漏，可以显式注解返回类型，并仍然在 `default` 中调用 `assertUnreachable`：

```ts
function getArea(shape: Shape): number {
  switch (shape.type) {
    case 'box': ... return area;
    case 'circle': ... return area;
    default:
      return assertUnreachable(shape);
  }
}
```

由于 `assertUnreachable` 返回 `never`，而 `never` 可以赋值给任何类型（包括 `number`），所以类型检查通过。如果遗漏了任何 `case`，`shape` 不是 `never`，会导致参数类型错误。

---

### 6. 扩展到多类型组合（笛卡尔积）

对于需要处理两个或多个类型的所有可能组合的情况（例如“石头剪刀布”游戏），可以用模板字面量类型生成所有组合的联合，然后同样使用 `switch` + `default` 穷尽性检查。

```ts
type Play = 'rock' | 'paper' | 'scissors';

function shoot(a: Play, b: Play) {
  const pair = `${a},${b}` as `${Play},${Play}`;
  // pair 的类型被断言为 "rock,rock" | "rock,paper" | ... (共9种)
  switch (pair) {
    case 'rock,rock':
    case 'paper,paper':
    case 'scissors,scissors':
      console.log('draw'); break;
    case 'rock,scissors':
    case 'paper,rock':
      console.log('A wins'); break;
    case 'rock,paper':
    case 'paper,scissors':
    case 'scissors,rock':
      console.log('B wins'); break;
    default:
      assertUnreachable(pair); // 如果遗漏了某个组合，会报错
  }
}
```

这里 `pair` 的每个可能值都被枚举，任何遗漏都会导致 `default` 分支中的 `pair` 类型不是 `never`，从而触发类型错误。

---

### 7. 工具支持：ESLint 规则

`typescript-eslint` 提供了规则 `switch-exhaustiveness-check`，可以自动检查 `switch` 语句是否穷尽了联合类型的所有可能。与手动 `assertUnreachable` 相比，该规则是**自动启用**的（opt-out），而 `assertUnreachable` 需要显式写在 `default` 中。两者各有优点，可以结合使用。

---

### 8. 注意事项

- **必须启用 `strictNullChecks`**：否则 `undefined` 可以作为任何类型的成员，可能干扰穷尽性检查。
- **`assertUnreachable` 中的异常**：即使在类型层面确认了不可达，在运行时仍可能因为 `any` 或直接调用而进入，抛出异常可以防御这种意外。
- **适用场景**：主要适用于处理可辨识联合（每个成员有唯一的字面量标签）的 `switch` 语句，也适用于任何通过条件收窄能产生 `never` 的场景。

---

### 9. 总结

- `never` 类型是空集，只有不可能发生的代码分支才能拥有 `never` 类型的值。
- 在 `switch` 的 `default` 分支中调用 `assertUnreachable(shape)`，如果之前没有覆盖所有联合成员，`shape` 的类型不会是 `never`，导致类型错误，从而强制开发者补充分支。
- 这是一种将“遗漏 case”从运行时 bug 转变为编译时错误的技术，提高代码的健壮性和可维护性。
- 对于两个或更多类型的组合，可以用模板字面量类型生成所有组合的联合，同样进行穷尽性检查。

**最终建议**：每当你处理一个可辨识联合（例如状态机、事件类型等），都应该在 `switch` 末尾添加 `default: assertUnreachable(x)`，让 TypeScript 帮你确保未来添加新类型时不会遗漏处理。