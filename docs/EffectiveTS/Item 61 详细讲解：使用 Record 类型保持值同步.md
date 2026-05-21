## Item 61 详细讲解：使用 `Record` 类型保持值同步

本节的核心是：**当一个接口新增属性时，你需要确保所有依赖该属性的地方（例如 `shouldUpdate` 函数）也随之更新。** 手动维护容易出错，而使用 `Record<keyof T, boolean>` 可以强制 TypeScript 检查必须为每个属性提供一个布尔值，从而在**编译时**强制你为每个新属性决定是否需要更新。这解决了传统的“fail open”（保守重绘）与“fail closed”（可能漏绘）之间的两难选择。

---

### 1. 问题场景：散点图组件（`ScatterProps`）

假设你有一个散点图组件，其属性分为三类：数据、显示设置、事件处理器。

```ts
interface ScatterProps {
  xs: number[];
  ys: number[];
  xRange: [number, number];
  yRange: [number, number];
  color: string;
  onClick?: (x: number, y: number, index: number) => void;
}
```

你需要实现一个 `shouldUpdate` 函数，决定何时重新绘制图表（避免不必要的重绘）。基本规则：
- **数据或显示属性变化** → 需要重绘。
- **事件处理器变化** → 不需要重绘（因为事件处理器的改变不影响图像的显示）。

但未来接口可能增加新属性（例如 `onDoubleClick`、`tooltip` 等）。如何确保每次新增属性时，都有人明确决定这个属性变化是否需要触发重绘？

---

### 2. 两种传统策略及其问题

#### 策略 A：“fail open”（保守重绘）

```ts
function shouldUpdate(oldProps: ScatterProps, newProps: ScatterProps) {
  for (const k in oldProps) {
    const key = k as keyof ScatterProps;
    if (oldProps[key] !== newProps[key]) {
      return true;      // 任何属性变化都重绘
    }
  }
  return false;
}
```

- 优点：永远不会遗漏必要的重绘（安全）。
- 缺点：事件处理器变化也会导致重绘（浪费性能）。新增属性自动被包含，但可能不需要重绘的事件处理器也被包含进去。

#### 策略 B：“fail closed”（仅明确列出的属性触发重绘）

```ts
function shouldUpdate(oldProps: ScatterProps, newProps: ScatterProps) {
  return (
    oldProps.xs !== newProps.xs ||
    oldProps.ys !== newProps.ys ||
    oldProps.xRange !== newProps.xRange ||
    oldProps.yRange !== newProps.yRange ||
    oldProps.color !== newProps.color
    // 注意没有检查 onClick
  );
}
```

- 优点：性能最优（仅必要的属性触发重绘）。
- 缺点：新增属性（如 `onDoubleClick`）时，如果不更新这个列表，就不会触发重绘，但也许那个新属性实际上需要重绘（例如新增了 `tooltip` 属性）。这就可能遗漏必要的重绘，导致 UI 错误。

**困境**：你希望在添加属性时，**强制开发者做出明确选择**（这个属性是否需要触发重绘），而不是自动采用某种策略。

---

### 3. 使用 `Record<keyof ScatterProps, boolean>` 强制同步

解决方案：定义一个**与接口属性一一对应的配置对象**，其中每个属性都是一个布尔值，表示该属性变化时是否需要重绘。使用 `Record<keyof ScatterProps, boolean>` 类型注解，TypeScript 会检查这个对象是否包含了 `ScatterProps` 的所有属性。

```ts
const REQUIRES_UPDATE: Record<keyof ScatterProps, boolean> = {
  xs: true,
  ys: true,
  xRange: true,
  yRange: true,
  color: true,
  onClick: false,      // 事件处理器变化不重绘
};
```

然后 `shouldUpdate` 使用这个配置来决定是否重绘：

```ts
function shouldUpdate(oldProps: ScatterProps, newProps: ScatterProps) {
  for (const k in oldProps) {
    const key = k as keyof ScatterProps;
    if (oldProps[key] !== newProps[key] && REQUIRES_UPDATE[key]) {
      return true;
    }
  }
  return false;
}
```

**关键点**：`Record<keyof ScatterProps, boolean>` 要求 `REQUIRES_UPDATE` 必须为 `ScatterProps` 的**每个属性**提供一个布尔值，不能多也不能少。

---

### 4. 新增属性时的效果

假设后续你在 `ScatterProps` 中添加了 `onDoubleClick` 属性：

```ts
interface ScatterProps {
  // ... 原有属性
  onDoubleClick?: () => void;
}
```

此时 TypeScript 会立即在 `REQUIRES_UPDATE` 定义处报错：

```
Property 'onDoubleClick' is missing in type ...
```

因为 `REQUIRES_UPDATE` 的类型要求包含 `onDoubleClick`。你必须显式添加：

```ts
const REQUIRES_UPDATE: Record<keyof ScatterProps, boolean> = {
  // ... 原有条目
  onDoubleClick: false,   // 或者 true，根据需求决定
};
```

这就**强制开发者**在添加新属性时，必须思考该属性变化是否应触发重绘，并显式记录下来。既不是“fail open”（自动重绘），也不是“fail closed”（可能忽略），而是“just fail”——编译错误，迫使你决策。

---

### 5. 为什么用 `Record` 而不是数组？

如果使用数组：

```ts
const PROPS_REQUIRING_UPDATE: (keyof ScatterProps)[] = ['xs', 'ys', ...];
```

新增属性不会导致编译错误（数组元素可以随意扩展），你仍然需要手动记得添加，容易遗漏。而 `Record` 要求**每个属性都出现且仅出现一次**，完全同步。

---

### 6. 其他应用场景

- **URL 参数同步**：确保应用状态的每个属性都在 URL 查询参数中有对应字段。
- **默认值对象**：为接口的每个属性提供默认值，确保新增属性时不会忘记默认值。
- **验证规则映射**：为表单字段定义验证规则，字段与规则一一对应。

---

### 7. 注意事项

- `Record<keyof T, boolean>` 强制对象包含 `T` 的**所有属性**，包括可选属性。对于可选属性，你仍然需要提供值（可以设为 `false` 或 `true`）。这是合理的，因为即使属性可选，你仍然需要决定它变化时是否触发重绘。
- 如果你希望某些属性绝对不应该出现在 `REQUIRES_UPDATE` 中（例如内部使用），可以考虑拆分接口。
- 该模式适用于**任何需要为每个属性关联一个元数据**的场景。

---

### 8. 总结

- **问题**：维护一个与接口属性同步的配置对象时，手动同步容易遗漏。
- **解决方案**：使用 `Record<keyof T, ValueType>` 类型注解，让 TypeScript 强制该对象必须包含 `T` 的所有属性。
- **效果**：新增接口属性会导致编译错误，迫使开发者立即补充配置，从而保持同步。
- **启示**：利用类型系统自动检查“完整性”，避免运行时遗漏或错误行为。

**最终建议**：当你有这样一个与接口属性一一对应的配置对象时，总是使用 `Record<keyof T, ...>` 来保证完整性。这样你就能享受类型系统带来的“主动同步”好处，而不是依赖注释或人工检查。