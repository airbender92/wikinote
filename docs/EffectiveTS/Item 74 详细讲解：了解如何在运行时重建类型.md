## Item 74 详细讲解：了解如何在运行时重建类型

TypeScript 的类型系统只在编译时存在，运行时会被完全擦除（Item 3）。这意味着你不能像在 Java 或 C# 中那样，使用 `instanceof` 或反射来检查一个对象是否符合某个接口。这给**运行时数据验证**带来了困难：例如，当你从 API 接收到一个 JSON 请求体时，你需要验证它是否具有预期的字段和类型，但 TypeScript 接口在运行时不可用。

本节讨论了三种解决“运行时需要类型信息”问题的常见方法，并分析了各自的优缺点。

---

### 1. 问题场景：验证 HTTP 请求体

假设你有一个创建评论的 API 端点，希望请求体符合 `CreateComment` 接口：

```ts
interface CreateComment {
  postId: string;
  title: string;
  body: string;
}
```

你需要编写验证逻辑，确保请求体包含所有必需字段且类型正确。如果手动编写，代码会非常冗长且容易出错：

```ts
app.post('/comment', (req, res) => {
  const { body } = req;
  if (!body || typeof body !== 'object' || Object.keys(body).length !== 3 ||
      !('postId' in body) || typeof body.postId !== 'string' ||
      !('title' in body) || typeof body.title !== 'string' ||
      !('body' in body) || typeof body.body !== 'string') {
    return res.status(400).send('Invalid request');
  }
  const comment = body as CreateComment; // 断言，实际已手动验证
  // ...
});
```

- 代码冗长，尤其当接口字段增多时。
- 类型定义（`interface`）与验证逻辑分离，容易不同步（例如新增字段后忘记添加验证）。
- 没有单一事实来源。

---

### 2. 解决方案概览

有三种主要方法可以解决“运行时重建类型”的问题：

| 方法 | 原理 | 示例工具 |
|------|------|----------|
| **从其他来源生成类型** | 使用 OpenAPI/GraphQL 等 schema 作为事实来源，同时生成 TypeScript 类型和运行时验证代码 | `openapi-typescript` + `ajv` |
| **用运行时库定义类型** | 使用一个在运行时存在的值（如 Zod schema）来同时定义类型和验证逻辑，再从中推断 TypeScript 类型 | `Zod` |
| **从 TypeScript 类型生成运行时值** | 使用工具从 TypeScript 接口生成 JSON Schema 或验证器 | `typescript-json-schema` |

下面分别详解。

---

### 3. 方法一：从其他来源生成类型

如果你的 API 已经有规范（如 OpenAPI、GraphQL schema），可以直接将其作为事实来源，生成 TypeScript 类型和验证代码。

- **优点**：单一事实来源，类型和验证同步，无需手动维护。
- **缺点**：需要额外的构建步骤（生成代码），可能增加工具链复杂度。
- **适用场景**：你已经或可以拥有一个机器可读的 API 规范。

示例：从 OpenAPI 生成 JSON Schema，再用 Ajv 验证。

---

### 4. 方法二：使用运行时库定义类型（以 Zod 为例）

Zod 允许你定义一个 schema 对象（运行时存在），然后从中**推断**出 TypeScript 类型。

```ts
import { z } from 'zod';

const CreateCommentSchema = z.object({
  postId: z.string(),
  title: z.string(),
  body: z.string(),
});

type CreateComment = z.infer<typeof CreateCommentSchema>;
// 等价于 { postId: string; title: string; body: string; }
```

在请求处理中，直接调用 `CreateCommentSchema.parse(body)`，它会执行验证，如果通过则返回类型安全的对象（类型为 `CreateComment`），否则抛出异常。

- **优点**：
  - 单一事实来源（schema 对象），类型和验证自动同步。
  - 无需额外构建步骤（纯 TypeScript 库）。
  - 可以表达比 TypeScript 更复杂的约束（如 email、最小值、自定义校验）。
- **缺点**：
  - 需要学习新的库语法（`z.object`、`z.string()` 等），团队必须接受这种风格。
  - “传染性”：一旦你开始使用 Zod，整个数据层可能都需要用 Zod 定义，与外部类型（如来自数据库生成器）集成时可能不便。

---

### 5. 方法三：从 TypeScript 类型生成运行时值

如果你希望继续使用纯 TypeScript 接口（`interface`）作为定义，但需要运行时验证，可以使用工具（如 `typescript-json-schema`）从 `.ts` 文件生成 JSON Schema，然后在运行时用 Ajv 等验证。

```bash
npx typescript-json-schema api.ts '*' > api.schema.json
```

然后在代码中导入 JSON Schema 并使用 Ajv 验证：

```ts
import Ajv from 'ajv';
import apiSchema from './api.schema.json';

const ajv = new Ajv();
if (!ajv.validate(apiSchema.definitions.CreateComment, body)) {
  // 验证失败
}
```

- **优点**：
  - 纯 TypeScript 语法定义类型，无需学习新的 schema 库。
  - 可以引用已有的第三方类型（如 `@types/node`）。
- **缺点**：
  - 需要额外构建步骤，必须保持 JSON Schema 与 TS 类型同步（可通过 CI 检查 `git diff` 确保）。
  - JSON Schema 表达力有限，某些 TypeScript 类型（如联合类型、交叉类型）可能无法完美转换。

---

### 6. 如何选择？

- **如果你已经有 OpenAPI / GraphQL 等规范** → 直接用规范生成类型和验证代码，保持单一事实来源。
- **如果你不想引入额外构建步骤，且团队愿意接受新语法** → 使用 Zod 这类运行时库。
- **如果你希望保持纯 TypeScript 接口，且可以接受构建步骤** → 使用 `typescript-json-schema` 生成 JSON Schema。
- **如果数据量小、结构稳定，且你信任输入来源** → 也可以不完全验证，仅依赖类型断言（但风险高，不推荐用于公开 API）。

没有完美答案，每个方案都是权衡。关键是意识到**类型擦除**这一限制，并主动选择合适的运行时验证策略，而不是盲目信任编译时的类型检查。

---

### 7. 总结（Things to Remember）

- TypeScript 类型在运行时不可用，必须借助额外工具才能进行运行时验证。
- 三种主流方案：从外部 schema 生成类型、使用运行时 schema 库（Zod）、从 TypeScript 类型生成 JSON Schema。
- 优先利用已有的 API 规范作为事实来源。
- 如果必须从 TypeScript 类型生成运行时验证，引入构建步骤并确保同步。
- 选择方案时权衡：构建步骤 vs 学习新语法 vs 保持纯 TS 定义。

**最终建议**：对于任何接收外部数据（HTTP 请求、文件、数据库记录）的边界，不要只依赖 TypeScript 接口。采用上述方法之一进行运行时验证，确保数据符合预期形状，然后再将其断言为 TypeScript 类型。