## Item 78 详细讲解：关注编译性能

TypeScript 的类型系统在运行时零开销，但在**编译时**（`tsc`）和**编辑器语言服务**（`tsserver`）中可能会影响开发效率。本章介绍了两种性能问题的表现，并提供了多个优化策略。

---

### 1. 两种性能问题及其症状

| 组件 | 影响 | 症状 |
|------|------|------|
| `tsc`（编译器） | 构建 / CI 速度 | 类型检查慢、生成 JS 慢 |
| `tsserver`（语言服务） | 编辑器响应速度 | 悬停提示延迟、错误高亮滞后、自动补全卡顿 |

**核心原则**：先定位瓶颈（是构建还是编辑器），再选择相应优化方法。

---

### 2. 将类型检查与构建分离

- **原理**：`tsc` 既做类型检查又生成 JS。在许多工具链（如 `ts-node`、webpack、vite）中，默认会同时执行这两步，但类型检查比转译（emit）慢得多。
- **优化**：在开发迭代时使用 **“仅转译”模式** 跳过类型检查，例如：
  - `ts-node --transpileOnly`
  - webpack 的 `ts-loader` 设置 `transpileOnly: true`
  - 使用 `swc` 或 `esbuild` 代替 TypeScript 编译器进行转译
- **效果**：示例中 `ts-node` 运行时间从 1.6 秒降至 0.12 秒（提速 13 倍）。
- **注意**：类型检查并未消失——你可以继续依靠编辑器中的 `tsserver` 实时提示错误，并在 CI 或提交前运行 `tsc --noEmit` 确保类型正确。

---

### 3. 修剪未使用的依赖和死代码

- **影响**：同时改善 `tsc` 和 `tsserver` 性能，减少内存占用。
- **方法**：
  - 启用 `noUnusedLocals` 和 `noUnusedParameters` 检测未使用的本地变量/参数。
  - 使用 `knip` 或 `depcheck` 检测未使用的导出符号及第三方依赖。
  - 运行 `tsc --listFiles` 查看所有被包含的源文件，往往会发现大量未被使用的类型声明（例如 Google APIs 的巨型包）。
  - 使用 **treemap 可视化**：`tsc --noEmit --listFiles | xargs stat -f "%z %N" | npx webtreemap-cli`，找出体积异常的依赖。
- **案例**：作者的 `googleapis` 依赖占 80.5 MB，但项目只用其中两个 API。升级到支持按需导入的版本解决了问题。

---

### 4. 增量构建与项目引用

- **增量构建（`incremental`）**：`tsc` 首次编译后生成 `.tsbuildinfo` 文件，下次只重新编译变更的部分。
- **项目引用（Project References）**：
  - 将代码库划分为多个子项目（如 `src`、`test`），每个子项目有自己的 `tsconfig.json`。
  - 设置 `composite: true` 和 `declaration: true`，使子项目生成 `.d.ts` 文件。
  - 顶层 `tsconfig.json` 通过 `references` 列出子项目。
  - 使用 `tsc --build`（或 `-b`）按依赖关系构建，仅重建受影响的子项目。
- **效果**：修改 `src/fib.ts` 的实现（不改变 API）时，仅重新构建 `src` 项目，`test` 项目因依赖的 `.d.ts` 未变而无需重建，显著节省时间。
- **适用场景**：大型 monorepo，且**自有代码多于第三方代码**时效果明显；小型项目不必过度拆分。

---

### 5. 简化类型

- **避免巨大联合类型**：例如 `type Year = `2${Digit}${Digit}${Digit}`` 包含 1000 个成员，每次类型实例化都会造成性能爆炸。应使用 `number` 或品牌类型（brand）。
- **使用 `interface` 扩展而非交叉类型**：TypeScript 对 `interface extends` 的优化比 `type &` 更好（参见 Item 13）。
- **为函数返回值添加显式类型注解**：可以减少类型推断的工作量，尤其对于复杂函数（Item 18）。

---

### 6. 其他注意事项

- **递归类型**：尽量使用**尾递归**形式（Item 57），避免深度递归导致的性能问题。
- **监视模式**：使用 `tsc --watch` 时，增量编译会自动启用。
- **编辑器配置**：可以为工作区指定不同的 TypeScript 版本（例如使用项目本地版本而非全局版本）。

---

### 7. 总结（Things to Remember）

- 区分 `tsc` 构建慢与 `tsserver` 编辑器卡顿，分别优化。
- 开发时将类型检查与转译分离（`transpileOnly`），在 CI 中运行完整检查。
- 清理未使用的依赖和死代码，用 `tsc --listFiles` + treemap 发现依赖膨胀。
- 使用增量编译（`incremental`）和项目引用（`--build`）减少重复工作。
- 简化类型：避免超大联合，优先 `interface extends`，对复杂函数标注返回类型。

**最终建议**：性能优化应基于实际数据。通过 `tsc --generateTrace` 生成性能追踪文件，再用 `@typescript/analyze-trace` 分析，可以更精准定位瓶颈。对于绝大多数中小型项目，最简单的优化往往是保持依赖精简和类型简洁。