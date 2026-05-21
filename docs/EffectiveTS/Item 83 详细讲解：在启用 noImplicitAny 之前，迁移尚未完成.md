## Item 83 详细讲解：在启用 `noImplicitAny` 之前，迁移尚未完成

将整个代码库从 JavaScript 转换为 TypeScript（即所有文件都是 `.ts` 或 `.tsx`）是一项巨大的成就，但这**不是迁移的终点**。下一个关键里程碑是启用 `noImplicitAny` 编译选项。没有 `noImplicitAny` 的 TypeScript 代码本质上仍是“过渡状态”，因为隐式的 `any` 会掩盖类型声明中的真实错误，让你误以为类型安全已经实现。

---

### 1. 为什么 `noImplicitAny` 如此重要？

- **隐式 `any` 是危险的**：当 TypeScript 无法推断一个变量的类型时，如果 `noImplicitAny` 为 `false`（默认关闭），它会将该变量视为 `any`。这相当于放弃了类型检查。
- **`any` 会传播**：一个 `any` 值可以赋值给任何其他类型，导致类型污染，使周围代码也失去类型安全。
- **错误的类型假设不会被发现**：你可能会像例子中的 `Chart` 类一样，错误地将 `indices` 声明为 `number[]`，但实际上它是 `number[][]`。没有 `noImplicitAny` 时，后续代码 `r[0]` 访问 `number` 属性不会报错（因为 `number` 上可以有任何属性，TypeScript 允许对 `any` 做任何操作）。但启用 `noImplicitAny` 后，TypeScript 会捕获这种“元素隐式具有 `any` 类型”的错误，迫使你纠正类型。

**结论**：`noImplicitAny` 是 TypeScript 提供的最重要的严格检查之一，它确保了每个变量、参数和属性都有明确的、非 `any` 的类型。

---

### 2. 如何逐步启用 `noImplicitAny`

建议采用渐进方式，而不是一次性打开并面对数千个错误。

#### 2.1 本地启用，逐步修复

- 在你的本地开发环境中，修改 `tsconfig.json`，设置 `"noImplicitAny": true`。
- 运行类型检查（`tsc --noEmit`），查看错误数量。
- 从错误最少的模块开始修复，或者按照依赖图自底向上修复（Item 82）。

#### 2.2 配合类型覆盖率工具

使用 `type-coverage`（Item 49）来跟踪非 `any` 符号的比例。当覆盖率达到 100% 时，就意味着所有隐式和显式 `any` 都被消除了。

#### 2.3 提交策略

- 在修复过程中，可以频繁提交**类型修正**的代码，但暂时**不要提交** `tsconfig.json` 的更改（即不把 `noImplicitAny: true` 推送到共享仓库）。
- 当本地错误数量归零后，再将 `tsconfig.json` 的变更提交并合并到主分支。

这样做可以避免在修复过程中打断团队其他成员的工作。

#### 2.4 分模块启用（使用项目引用）

如果你的项目分为多个子项目（例如 `src` 和 `test`，或者 `client` 和 `server`），可以分别设置不同的 `tsconfig.json`，先为生产代码启用 `noImplicitAny`，测试代码稍后处理。

---

### 3. 常见错误示例及其修复

#### 3.1 隐式 `any` 参数

```ts
function add(a, b) { return a + b; }
// 错误：参数 'a', 'b' 隐式具有 any 类型
```

**修复**：显式添加类型注解。

```ts
function add(a: number, b: number) { return a + b; }
```

#### 3.2 未注解的回调参数

```ts
items.forEach(item => console.log(item.length));
// 如果 items 是 any[]，则 item 隐式 any
```

**修复**：为数组指定具体类型，或显式注解回调参数。

#### 3.3 类属性的隐式 `any`

通过快速修复添加的属性可能被标记为 `any`，需要根据实际使用赋予正确类型。

```ts
class Chart {
  indices: any; // 应改为 number[][] 或 [number, number][]
}
```

#### 3.4 动态属性访问

```ts
const obj = {};
obj.name = 'Alice'; // 错误：{} 没有 name 属性
```

**修复**：一次性定义对象形状，或使用索引签名、Record 类型。

---

### 4. 启用 `noImplicitAny` 后的其他好处

- **更好的编辑器支持**：自动补全、重命名、跳转定义等功能更加准确。
- **文档价值**：每个变量和参数的类型都显式可见，代码自文档化。
- **为更严格的检查铺路**：`noImplicitAny` 是 `strict` 模式的一部分。启用它之后，再考虑开启 `strictNullChecks`、`strictFunctionTypes` 等。

---

### 5. 给团队适应的时间

- **不要一次性要求所有成员适应严格模式**。可以先在 `noImplicitAny` 修复期间让大家学习如何添加类型注解。
- 当所有错误清零后，再合并配置变更，并作为代码审查的强制要求（例如在 CI 中运行 `tsc --noEmit` 并禁止隐式 `any`）。
- 之后可以逐步引入 `strictNullChecks` 等其他严格选项。

---

### 6. 总结

- **完成 TypeScript 迁移的标志是启用了 `noImplicitAny`**。在此之前，代码仍然处于“带类型的 JavaScript”而非“类型安全的 TypeScript”。
- 启用 `noImplicitAny` 会暴露许多潜在的类型错误，必须逐一修复。这会显著提升代码质量。
- 采用渐进策略：本地开启、逐步修复、利用类型覆盖率工具，最后才提交配置变更。
- 完成 `noImplicitAny` 后，再考虑更严格的检查（如 `strict` 模式）。

**最终建议**：不要满足于只把文件后缀改成 `.ts`。只有当你不再有隐式 `any`，并且每个变量都有明确类型时，才能真正享受 TypeScript 带来的安全感和开发效率。所以，`noImplicitAny` 才是你迁移的终点线。