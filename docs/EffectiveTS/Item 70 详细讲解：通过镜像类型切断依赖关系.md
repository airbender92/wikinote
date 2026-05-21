## Item 70 详细讲解：通过镜像类型切断依赖关系

本节的核心是：**当你的 TypeScript 库依赖于另一个类型声明（例如 `@types/node`）时，不要把这种类型依赖变成生产依赖（`dependencies`），也不要让它强制传递给所有用户。而是通过“镜像类型”的方式，仅定义你所需要的最小形状（接口），利用 TypeScript 的结构类型系统来兼容真实的依赖，从而切断不必要的类型传递。**

---

### 1. 问题场景

假设你编写了一个 CSV 解析库，为方便 Node.js 用户，允许参数可以是 `string` 或 Node.js 的 `Buffer`。

```ts
// parse-csv.ts
import { Buffer } from 'node:buffer';

export function parseCSV(contents: string | Buffer): { [column: string]: string }[] {
  if (typeof contents === 'object') {
    // 如果是 Buffer，转成字符串处理
    return parseCSV(contents.toString('utf8'));
  }
  // ... 实际解析逻辑
}
```

为了使用 `Buffer` 类型，你需要在 `devDependencies` 中安装 `@types/node`（按照 Item 65 的原则）。当你发布库时，通过 `tsc --declaration` 生成的 `.d.ts` 文件会包含：

```ts
import { Buffer } from 'node:buffer';
export declare function parseCSV(contents: string | Buffer): { [column: string]: string }[];
```

### 2. 发布后的问题

- **JavaScript 用户**：他们不需要 `@types/node`，但是你的 `.d.ts` 文件中导入了 `node:buffer`。由于 JavaScript 项目通常不会安装 `@types/node`，当他们直接使用你的库时，TypeScript 编译器（如果他们在用 TS）或编辑器会报错“Cannot find module 'node:buffer' or its corresponding type declarations”。即使他们不用 TS，某些工具（如编辑器）仍可能因为类型文件的存在而报错。
- **TypeScript 用户但非 Node.js 环境**（例如浏览器项目）：他们同样会看到这个错误，因为他们的项目中没有 `node:buffer` 的类型定义。
- **Node.js TypeScript 用户**：他们可能已经有 `@types/node` 了，但版本可能与你的不兼容，导致冲突或重复定义。

### 3. 为什么不把 `@types/node` 放到 `dependencies` 中？

如果把 `@types/node` 移到 `dependencies`，那么所有用户（包括 JavaScript 用户和浏览器用户）都会被迫安装这个巨大的类型包（近 10 万行代码），而他们根本不需要它。这违反了最小依赖原则，并且会拖慢安装速度、增加 `node_modules` 体积。

### 4. 解决方案：镜像类型（Mirror Types）

利用 TypeScript 的**结构类型系统**：只要一个类型具有你需要的属性和方法，它就是兼容的，而不必是那个确切的类或接口。

你可以**自己定义一个小接口**，只包含你的库实际用到的 `Buffer` 方法：

```ts
export interface StringEncodable {
  toString(encoding?: string): string;
}

export function parseCSV(contents: string | StringEncodable): { [column: string]: string }[] {
  // ...
}
```

- `StringEncodable` 只需要一个 `toString` 方法，接受可选的编码参数。
- 真实的 `Buffer` 满足这个接口（`Buffer` 有 `toString(encoding?: string): string`），因此 `parseCSV(new Buffer(...))` 在 TypeScript 中完全合法。
- 你不再需要导入 `Buffer` 类型，也不需要依赖 `@types/node`。

**关键点**：你定义了一个“镜像”类型，它只是真实类型的一个极小子集。因为 TypeScript 是结构类型，所以只要对象具有所需的成员，就可以当作 `StringEncodable` 使用。

### 5. 如何确保兼容性？

你应该编写一个**单元测试**（在开发环境中，`@types/node` 仍然是 `devDependency`），验证真实的 `Buffer` 确实可以赋值给 `StringEncodable`：

```ts
import { Buffer } from 'node:buffer';
import { parseCSV } from './parse-csv';

test('parse CSV in a buffer', () => {
  const result = parseCSV(new Buffer("a,b\n1,2", "utf-8"));
  expect(result).toEqual([{ a: '1', b: '2' }]);
});
```

这个测试同时验证了运行时行为和类型兼容性。由于测试是开发依赖，`@types/node` 只存在于开发环境中，不会影响库的最终用户。

### 6. 扩展：如果库需要 `Buffer` 的更多方法怎么办？

如果你的库后续使用了 `Buffer` 的其他方法（例如 `slice`、`length`），只需在 `StringEncodable` 接口中添加这些方法即可。这被称为“按需镜像”——只复制你真正依赖的部分。

这种做法确实会产生一些重复（你定义了一个与 `Buffer` 部分相同的接口），但正如 Go 语言社区所说：“少量的复制比微小的依赖要好”。它避免了传递性的类型依赖，使得你的库可以在各种环境中无痛使用。

### 7. 其他应用场景

- **切断单元测试与生产系统的依赖**：Item 4 中的 `getAuthors` 示例，通过定义 `DB` 接口来解耦真实的 `PostgresDB`。
- **防止大型类型树被引入**：如果某个 `@types` 包本身就依赖许多其他类型包，镜像类型可以帮你切断整个依赖子树，从而提升编译器性能（Item 78）。

### 8. 总结

- **镜像类型** = 定义一个最小接口，只包含你需要的成员，利用结构类型兼容真实类型。
- **优点**：
  - 无需将 `@types` 变成生产依赖。
  - 不会强迫 JavaScript 或非 Node 环境的用户安装无关的类型包。
  - 避免版本冲突和重复定义。
  - 提升编译性能。
- **代价**：需要手动维护镜像接口（当底层库的 API 改变时可能需要更新），以及编写测试来确保兼容性。

**最终建议**：当你编写一个库并且只需要某个复杂类型的极小一部分时，优先考虑镜像类型，而不是直接依赖其 `@types` 包。这会让你的库更轻量、更便携，减少用户的抱怨。