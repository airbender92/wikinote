## Item 62 详细讲解：使用 Rest 参数和元组类型模拟可变参数函数

本节的核心是：**当一个函数的参数个数或类型依赖于某个参数（例如路由路径）时，可以使用 rest 参数 + 条件类型 + 元组来精确控制函数的签名**。这样，函数可以根据传入的第一个参数（路由）自动决定是否需要第二个参数（查询参数），而且 TypeScript 能够准确推断并检查调用方式。

---

### 1. 问题场景：根据路由决定查询参数

假设有一个 Web 应用，不同的路由接受不同的查询参数：

```ts
interface RouteQueryParams {
  '/': null,                           // 根路径不接受任何查询参数
  '/search': { query: string; language?: string; }  // 搜索页接受 query 和可选 language
  // ... 其他路由
}
```

你需要写一个 `buildURL` 函数，接受一个路由（`route`）和可选的查询参数（`params`），返回完整的 URL。

最初可能会这么写（不安全）：

```ts
function buildURL(route: keyof RouteQueryParams, params?: any) {
  return route + (params ? `?${new URLSearchParams(params)}` : '');
}
```

**问题**：
- `params` 是 `any` 类型，完全失去了类型检查。
- 调用 `buildURL('/', { query: 'recursion' })` 不会报错，但根路径不应该接受任何参数。
- 调用 `buildURL('/search')` 也不会报错，但搜索路径应该至少需要 `query` 参数。

---

### 2. 第一次改进：使用泛型关联参数类型

```ts
function buildURL<Path extends keyof RouteQueryParams>(
  route: Path,
  params: RouteQueryParams[Path]
) {
  return route + (params ? `?${new URLSearchParams(params)}` : '');
}
```

**效果**：
- 调用 `buildURL('/search', { query: '...' })` ✅
- 调用 `buildURL('/search', {})` ❌（缺少 `query` 属性）
- 调用 `buildURL('/', { query: '...' })` ❌（参数类型应为 `null`）

**但问题**：
- 对于根路径 `'/'`，你必须显式传递 `null` 作为第二个参数：`buildURL('/', null)`。
- 你不能省略第二个参数（即使它应该没有参数）。原生的 `URLSearchParams` 设计支持可选的 `params`，这里却强制要求提供 `null`，不太友好。

**目标**：对于 `'/'` 路由，函数应该只接受一个参数；对于 `'/search'` 路由，函数应该接受两个参数（第二个是必需的）。也就是说，函数的参数个数取决于路由的类型。

---

### 3. 使用 rest 参数 + 条件类型 + 元组实现可变参数

TypeScript 允许函数通过 rest 参数（`...args`）接收不定数量的参数，并且可以给 rest 参数一个**元组类型**。元组的长度决定了参数的个数。我们可以利用条件类型根据 `RouteQueryParams[Path]` 的值来选择不同的元组类型：

- 如果 `RouteQueryParams[Path] extends null`（即不需要参数），则 rest 参数类型为空元组 `[]`，函数变成单参数。
- 否则，rest 参数类型为 `[params: RouteQueryParams[Path]]`（一个元素的元组，带标签），函数变成双参数。

**实现**：

```ts
function buildURL<Path extends keyof RouteQueryParams>(
  route: Path,
  ...args: RouteQueryParams[Path] extends null ? [] : [params: RouteQueryParams[Path]]
) {
  const params = args[0];   // 当元组为空时，args[0] 是 undefined
  return route + (params ? `?${new URLSearchParams(params)}` : '');
}
```

**解释**：
- `...args` 的元组类型是一个条件类型。
- 当 `RouteQueryParams[Path]` 是 `null` 时，`...args` 的类型为 `[]`，即没有参数。因此函数签名变为 `(route: Path) => string`。
- 否则，`...args` 的类型为 `[params: RouteQueryParams[Path]]`，即一个包含 `params` 的元组，函数签名变为 `(route: Path, params: RouteQueryParams[Path]) => string`。

**使用效果**：

```ts
buildURL('/');                                // ✅ 一个参数
buildURL('/search', { query: 'hello' });      // ✅ 两个参数
buildURL('/search', {});                      // ❌ 缺少 query
buildURL('/', { query: 'hello' });            // ❌ 期望 1 个参数，但传了 2 个
```

TypeScript 在编辑器中的函数提示也会正确显示参数名（因为元组中用了标签 `params:`）。

---

### 4. 为什么不用重载（overloads）？

理论上你也可以使用重载为每个路由写一个签名：

```ts
function buildURL(route: '/'): string;
function buildURL(route: '/search', params: { query: string; language?: string }): string;
```

**问题**：
- 每个路由都需要单独写一行重载，随着路由增多，代码重复且难以维护。
- 重载不能自动处理新的路由（需要手动添加）。
- 而 rest + 条件类型的方式是**通用**的，只要 `RouteQueryParams` 接口定义正确，任何新增路由都会自动适配。

---

### 5. 关键知识点总结

- **Rest 参数**：`...args: T` 可以将多个参数收集到一个元组中。元组的类型决定了函数接受多少个参数以及每个参数的类型。
- **条件类型**：`RouteQueryParams[Path] extends null ? [] : [params: ...]` 可以根据 `Path` 动态选择不同的元组类型。
- **元组标签**：`[params: Type]` 中的 `params:` 是元组成员的标签，它会影响 IDE 中显示的参数名称，提高可读性。
- **可变参数函数**：这种模式可以模拟 C++/Java 中的函数重载，但更灵活、更易于扩展。

---

### 6. 更广泛的适用场景

这个模式不仅适用于 URL 构建，还适用于：
- **事件处理器**：根据事件类型决定回调参数。
- **SQL 查询构造器**：根据查询类型决定参数个数。
- **命令行参数解析**：根据子命令动态调整选项。
- **任意依赖参数的函数签名**：当函数的行为取决于第一个参数时。

---

### 7. 注意事项

- 函数实现内部需要处理 `args[0]` 可能为 `undefined` 的情况（对应空元组）。可以通过 `const params = args[0]` 获取，如果元组为空，`args[0]` 是 `undefined`。
- 如果希望函数在不需要参数时**不允许**传递额外参数，这种模式已经做到了（空元组）。你无法在不修改函数定义的情况下传递多余参数。
- 标签必须与元组中的元素位置匹配，`[params: Type]` 只影响调用时的参数名称，不影响类型检查。

---

### 8. 总结

通过结合 **泛型**、**条件类型**、**rest 参数**和**元组**，你可以创建出**参数个数和类型依赖于其他参数**的函数签名，并且保持类型安全。这种方法比重载更通用、更易维护，是处理“变参函数”的 TypeScript 惯用法。