## Item 37 详细讲解：限制使用可选属性（Optional Properties）

这一节的核心是：**可选属性虽然方便（尤其是为了向后兼容），但会隐藏许多问题：容易忘记传递、默认值处理分散且容易出错、组合爆炸等。更好的做法是尽量使用必需属性，或者将“未规范化”的输入类型与“规范化”的内部类型分开，在边界处集中处理默认值。**

书中通过一个 UI 组件 `formatValue` 的演化过程，生动地展示了可选属性如何导致难以发现的 bug，并给出了解决方案。

---

### 1. 初始设计：没有可选属性，所有字段必需

```ts
interface FormattedValue {
  value: number;
  units: string;
}

function formatValue(value: FormattedValue) { /* ... */ }
```

用法简单，所有调用都必须提供 `value` 和 `units`，没有歧义。

---

### 2. 需求变化：支持公制/英制单位转换

为了增加单位系统（metric/imperial），开发者想在不破坏现有代码的情况下添加新字段。于是将 `unitSystem` 设为**可选**，并注释说明默认是 `'imperial'`：

```ts
type UnitSystem = 'metric' | 'imperial';

interface FormattedValue {
  value: number;
  units: string;
  /** default is imperial */
  unitSystem?: UnitSystem;
}
```

同时应用配置中也添加了这个可选字段：

```ts
interface AppConfig {
  darkMode: boolean;
  /** default is imperial */
  unitSystem?: UnitSystem;
}
```

---

### 3. Bug 的产生：忘记传递可选属性

在 `formatHike` 函数中，需要将 `unitSystem` 传递给两个 `formatValue` 调用：

```ts
function formatHike({miles, hours}: Hike, config: AppConfig) {
  const { unitSystem } = config;
  const distanceDisplay = formatValue({
    value: miles, units: 'miles', unitSystem   // ✅ 传递了
  });
  const paceDisplay = formatValue({
    value: miles / hours, units: 'mph'         // ❌ 忘记传递 unitSystem
  });
  return `${distanceDisplay} at ${paceDisplay}`;
}
```

结果：距离（distance）会按照用户选择的单位系统显示（例如公制），但速度（pace）始终使用默认的英制（因为 `unitSystem` 为 `undefined`）。用户会看到混合单位：“10 km at 6.2 mph” —— 混乱且可能错误。

**为什么 TypeScript 没有报错？**  
因为 `unitSystem` 是可选的，省略它是合法的。类型检查器无法知道你“本意”要传递它。这个 bug 只能通过运行时发现，或者代码审查时人工察觉。

---

### 4. 可选属性带来的其他问题

#### 4.1 默认值处理分散且容易出错

由于可选属性的默认值 `undefined` 并不符合业务默认值（这里期望 `'imperial'`），你必须在每个使用 `unitSystem` 的地方写类似这样的代码：

```ts
const unitSystem = config.unitSystem ?? 'imperial';
```

- 如果某些地方忘记写，就会使用 `undefined`，导致错误行为。
- 如果不同的开发者对默认值理解不同（例如有人写成 `?? 'metric'`），就会产生不一致。

#### 4.2 可选属性数量一多，组合爆炸

假设一个接口有 10 个可选属性，那么可能的组合数高达 \(2^{10} = 1024\) 种。你不可能测试所有组合，而且很多组合可能根本没有意义（例如 `unitSystem: 'metric'` 和 `useKilometers: false` 同时出现）。这违背了 Item 29 “让类型只能表示有效状态”的原则。

#### 4.3 可选属性可能导致类型系统的不健全（unsoundness）

Item 48 会详细讨论：由于 TypeScript 的结构类型系统，一个具有可选属性的类型可能会被一个具有不兼容属性类型的对象赋值，导致运行时类型与静态类型不匹配。

---

### 5. 解决方案：拆分类型 + 中心化默认值

如果你确实需要支持旧数据（例如从 JSON 文件或数据库中读取的配置可能没有 `unitSystem` 字段），不能直接把它变成必需属性。但你可以创建两个类型：

- **`InputAppConfig`**：表示原始、未规范化的数据，其中 `unitSystem` 是可选的。
- **`AppConfig`**：表示规范化后的、在应用程序内部使用的类型，其中 `unitSystem` 是必需的。

```ts
interface InputAppConfig {
  darkMode: boolean;
  unitSystem?: UnitSystem;   // 可选
}

interface AppConfig extends InputAppConfig {
  unitSystem: UnitSystem;    // 覆盖为必需
}
```

然后编写一个归一化函数，集中处理默认值：

```ts
function normalizeAppConfig(input: InputAppConfig): AppConfig {
  return {
    ...input,
    unitSystem: input.unitSystem ?? 'imperial',
  };
}
```

在应用的入口处（例如读取配置后、启动时），调用 `normalizeAppConfig` 将所有配置转换为 `AppConfig` 类型。之后在整个应用内部，所有地方都使用 `AppConfig`（`unitSystem` 是必需的），这样：

- 类型检查器会强制你必须提供 `unitSystem`，不可能忘记。
- 默认值只在一个地方定义，不会分散。
- 向后兼容性保留：旧数据（缺少 `unitSystem`）仍能通过 `normalizeAppConfig` 被赋予默认值。

**类似的设计也出现在 Item 33 的 `UserPosts` 例子中**：先加载所有数据，然后构造一个完全非空的类。

---

### 6. 什么时候应该使用可选属性？

书中给出了几个合理的场景：

- **描述现有 API 或需要保持向后兼容性**（就像本例中的配置数据）。但即使这样，也应该尽快转换为内部必需类型。
- **某些属性在语义上确实是可选的**：例如人的中间名（middle name），不是每个人都有。这种情况下可选属性是准确的模型。
- **配置对象非常庞大**，如果所有字段都变成必需，调用方需要编写大量 `{ ... }`，可能不现实。但即使如此，也可以考虑使用构建器模式或拆分类型。

**核心原则**：不要因为“将来可能会加字段”就把新字段设成可选。先思考能否让它成为必需，然后通过版本升级或数据迁移来适配。如果必须保持可选，也要通过拆分类型的方式，在内部尽快转换为必需版本。

---

### 7. 总结：何时避免可选属性

| 场景 | 问题 | 推荐做法 |
|------|------|----------|
| 新添加的字段，希望不破坏现有调用 | 容易忘记传递，默认值处理分散 | 拆分为“输入类型”和“内部类型”，在边界处归一化 |
| 多个可选属性同时出现 | 组合爆炸，无效状态增多 | 使用可辨识联合（Item 29）或重新设计 |
| 需要为可选属性提供业务默认值 | 到处写 `?? default`，容易出错 | 归一化函数集中处理一次 |
| 希望类型系统帮忙检查是否遗漏传递 | 可选属性无法强制检查 | 设为必需属性，或使用对象参数（Item 38） |

**最终建议**：**限制使用可选属性。** 每当你想要添加一个 `?` 时，先问自己：这个字段真的可以不存在吗？如果不可以，就把它变成必需的；如果只是因为向后兼容，那么创建两个类型，在边界处转换。这样可以减少 bug，让类型系统更好地为你服务。