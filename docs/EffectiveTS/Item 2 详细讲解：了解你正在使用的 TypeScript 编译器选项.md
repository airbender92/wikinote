## Item 2 详细讲解：了解你正在使用的 TypeScript 编译器选项

TypeScript 编译器（`tsc`）有超过一百个配置选项。同样的代码在不同选项下可能会通过类型检查，也可能报错。因此，**了解你正在使用的选项**是有效使用 TypeScript 的基础。本节重点介绍两个最重要的选项：`noImplicitAny` 和 `strictNullChecks`，以及如何通过 `tsconfig.json` 统一管理配置。

---

### 一、为什么需要配置文件而不是命令行参数？

命令行示例：
```bash
tsc --noImplicitAny program.ts
```

问题：
- 团队成员可能使用不同的命令行参数，导致类型检查结果不一致。
- 难以共享和复现。

**推荐做法**：使用 `tsconfig.json`。
```json
{
  "compilerOptions": {
    "noImplicitAny": true
  }
}
```
- 执行 `tsc --init` 可生成默认配置文件。
- 确保所有工具（编辑器、CI、打包工具）使用相同的配置。

---

### 二、`noImplicitAny`：控制隐式 `any` 的行为

#### 2.1 关闭 `noImplicitAny` 时（默认）

```ts
function add(a, b) {
  return a + b;
}
```
- TypeScript 无法推断 `a` 和 `b` 的类型，于是将它们视为 `any`。
- 鼠标悬停显示：`function add(a: any, b: any): any`
- `any` 完全禁用了类型检查：`add(10, null)` 不会报错。

**问题**：
- 隐式 `any` 会悄悄传递，破坏类型安全。
- 许多错误被掩盖。

#### 2.2 开启 `noImplicitAny` 时（强烈推荐）

```ts
function add(a, b) {
  // 错误：参数 'a' 隐式具有 'any' 类型
  // 错误：参数 'b' 隐式具有 'any' 类型
  return a + b;
}
```
**修复**：显式注解参数类型。
```ts
function add(a: number, b: number) {
  return a + b;
}
```
或者，如果你确实需要 `any`，可以显式写 `: any`（但通常应避免）。

**最佳实践**：
- **新项目**：始终开启 `noImplicitAny`，从一开始就为所有变量和参数提供类型。
- **迁移旧项目**：可暂时关闭，但应在转换完成前尽早开启（参见 Item 83）。

---

### 三、`strictNullChecks`：严格处理 `null` 和 `undefined`

#### 3.1 关闭 `strictNullChecks` 时

```ts
const x: number = null; // OK
```
- `null` 和 `undefined` 可以被赋值给任何类型，这会导致大量运行时错误（如 `undefined is not an object`）。

#### 3.2 开启 `strictNullChecks` 时

```ts
const x: number = null; // 错误：Type 'null' is not assignable to type 'number'
```
要允许 `null`，必须显式使用联合类型：
```ts
const x: number | null = null;
```

**处理可能为 `null` 的值**：
```ts
const statusEl = document.getElementById('status');
statusEl.textContent = 'Ready'; // 错误：statusEl 可能为 null
```
解决方案：
- **类型收窄（narrowing）**：
  ```ts
  if (statusEl) {
    statusEl.textContent = 'Ready'; // OK
  }
  ```
- **非空断言（non-null assertion）**（谨慎使用）：
  ```ts
  statusEl!.textContent = 'Ready'; // 告诉 TS 你确信它不是 null
  ```

**建议**：
- 有经验的项目应该开启 `strictNullChecks`，它能预防一大类常见错误。
- 对于新手或迁移项目，可以先开启 `noImplicitAny`，再逐步开启 `strictNullChecks`。

---

### 四、`strict` 模式：一键开启所有严格检查

`strict: true` 会同时启用：
- `noImplicitAny`
- `strictNullChecks`
- `strictFunctionTypes`
- `strictBindCallApply`
- `strictPropertyInitialization`
- `noImplicitThis`
- `useUnknownInCatchVariables`

**建议**：新项目直接使用 `strict: true`（`tsc --init` 默认会开启）。这是 TypeScript 能提供的最全面检查。

---

### 五、比 `strict` 更严格的选项：`noUncheckedIndexedAccess`

即使在 `strict` 模式下，下面的代码不会报错，但运行时会抛出异常：

```ts
const tenses = ['past', 'present', 'future'];
tenses[3].toUpperCase(); // 运行时 TypeError
```

- TypeScript 假设数组索引访问总是有值，但实际可能返回 `undefined`。

开启 `noUncheckedIndexedAccess` 后，上述代码会报错：
```ts
tenses[3].toUpperCase(); // 错误：Object is possibly 'undefined'
```
**代价**：即使是合法的访问（如 `tenses[0]`）也会被标记为可能 `undefined`，需要额外的非空断言或条件检查。

这个选项并非默认开启，需要根据项目情况权衡。

---

### 六、总结：关键选项一览

| 选项 | 作用 | 推荐设置 |
|------|------|----------|
| `noImplicitAny` | 禁止隐式 `any` | 开启（除非临时迁移） |
| `strictNullChecks` | 严格区分 `null`/`undefined` | 开启（预防常见错误） |
| `strict` | 同时启用上述多项严格检查 | 开启（新项目默认） |
| `noUncheckedIndexedAccess` | 标记可能为 `undefined` 的索引访问 | 可选，根据需求权衡 |

**最终建议**：
- 始终使用 `tsconfig.json` 管理配置。
- 运行 `tsc --init` 开始项目，保持 `strict` 默认开启。
- 如果遇到别人分享的 TypeScript 示例但无法重现其错误，请检查你们的编译器选项是否一致。

**记住**：TypeScript 的行为很大程度上取决于配置。了解并统一团队的配置是高效协作的基础。