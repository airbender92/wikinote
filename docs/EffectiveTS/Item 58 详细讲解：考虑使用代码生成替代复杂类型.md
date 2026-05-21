## Item 58 详细讲解：考虑使用代码生成替代复杂类型

这一节的核心是：**虽然 TypeScript 的类型系统非常强大（甚至图灵完备），但并非所有复杂类型逻辑都适合在类型层面实现。当类型逻辑变得极其复杂、难以维护或容易出错时，可以考虑使用代码生成（codegen）——即在外部用普通语言（如 TypeScript、Python、Shell）生成类型声明文件，而不是在类型系统内部实现所有逻辑。**

---

### 1. 背景：类型系统的“图灵泥沼”

Alan Perlis 有一句名言：“当心图灵泥沼（Turing tar-pit），在那里一切皆可能，但有趣的事情都不容易。”  
TypeScript 的类型系统是图灵完备的，理论上你可以用类型系统做任何计算（例如解析 SQL、实现正则引擎）。但是，这样做往往会导致代码极其复杂、难以理解、编译缓慢、错误信息晦涩。作者指出，对于某些场景（例如从 SQL 查询自动推导结果类型），用类型系统手动实现一个 SQL 解析器是非常困难的，而且很容易违反 Item 40 的“不精确优于不准确”原则。

---

### 2. 问题示例：从 SQL 查询推导类型

假设你有一个数据库查询函数：

```ts
async function getBooks(db: Database) {
  const result = await db.query(`SELECT title, author, year, publisher FROM books`);
  return result.rows;
}
```

你希望 TypeScript 能够自动推断出 `result.rows` 的类型为 `{ title: string; author: string; year: number; publisher: string }[]`。这可以通过解析 SQL 字符串来实现——在类型层面用模板字面量类型和条件类型解析 SQL。虽然理论上可行，但实现非常复杂，且只能处理简单的 `SELECT *` 或固定列名的查询。

当遇到更复杂的查询（例如带 `GROUP BY`、聚合函数 `MAX`、参数占位符 `$1`）时：

```ts
async function getLatestBookByAuthor(db: Database, publisher: string) {
  const result = await db.query(
    `SELECT author, MAX(year) FROM books GROUP BY author WHERE publisher=$1`,
    [publisher]
  );
  return result.rows;
}
```

手动在类型系统中实现一个完整的 SQL 解析器几乎是不现实的。你会陷入“图灵泥沼”——什么都能做，但什么都难做。而且，解析器本身可能包含 bug，导致类型不准确，比没有类型更糟糕。

---

### 3. 替代方案：代码生成（Codegen）

代码生成的思想是：**在编译时运行一个外部程序（用普通语言编写），分析你的代码或 schema，并自动生成对应的 TypeScript 类型声明文件**。这样，你就可以将复杂的类型逻辑从 TypeScript 类型系统转移到常规编程语言中，利用成熟的工具和库来完成。

**优点**：
- 生成代码的开发难度远低于在类型系统中实现相同逻辑。
- 生成的类型是具体、直观的，没有复杂的泛型嵌套。
- 可以通过工具控制类型的显示方式（Item 56），无需手工 `Resolve`。
- 对 TypeScript 编译器的负担小，不会导致性能问题。

**缺点**：
- 需要额外添加一个构建步骤（运行 codegen 工具）。
- 必须确保生成的类型与源文件保持同步（例如数据库 schema 变更后重新生成）。

---

### 4. 具体案例：使用 `PgTyped` 为 SQL 查询生成类型

`PgTyped` 是一个 Node.js 库，它可以连接真实数据库，解析 SQL 查询，并自动生成 TypeScript 类型。

**使用步骤**：

1. 在 TypeScript 文件中，用 `sql` 模板标签标记 SQL 查询：

```ts
// books-queries.ts
import { sql } from '@pgtyped/runtime';

const selectLatest = sql`
  SELECT author, MAX(year)
  FROM books
  GROUP BY author
  WHERE publisher = $publisher
`;
```

2. 运行 `pgtyped` 命令，它会连接到数据库，分析查询，生成类型声明文件。

```bash
npx pgtyped -c pgtyped.config.json
```

3. 生成的文件 `books-queries.types.ts` 包含：

```ts
export interface selectLatestParams {
  publisher: string;
}
export interface selectLatestResult {
  author: string;
  year: number;
}
export interface selectLatestQuery {
  params: selectLatestParams;
  result: selectLatestResult;
}
```

4. 在原文件中导入生成的类型，并用于 `sql` 模板：

```ts
import { selectLatestQuery } from './books-queries.types';
export const selectLatestBookByAuthor = sql<selectLatestQuery>`...`;
async function getLatestBookByAuthor(db: Database, publisher: string) {
  const result = await selectLatestBookByAuthor.run({ publisher }, db);
  // result 的类型现在被正确推断为 selectLatestResult[]
}
```

**优势**：
- 无需手动编写复杂的类型，所有类型从真实数据库 schema 中推导。
- 即使查询包含聚合、分组、参数，也能获得精确的类型。
- 生成的类型清晰、直观，没有复杂的泛型。
- 易于维护：当数据库 schema 或查询改变时，重新运行 codegen 即可。

---

### 5. 与类型层面实现的对比

| 维度 | 类型层面实现（手工解析 SQL） | 代码生成（如 PgTyped） |
|------|-------------------------------|------------------------|
| 开发难度 | 极高（需要实现 SQL 解析器） | 低（使用现成工具） |
| 可维护性 | 差（类型逻辑复杂，易出错） | 好（生成代码自动同步） |
| 编译性能 | 差（深度递归，可能导致超限） | 好（生成的具体类型轻量） |
| 类型显示 | 可能显示为复杂泛型 | 显示为普通接口 |
| 依赖项 | 无（仅 TypeScript） | 需要 codegen 工具和构建步骤 |
| 适用范围 | 非常有限的 SQL 子集 | 几乎任意 SQL（依赖工具能力） |

---

### 6. 如何管理 codegen 的同步问题

由于生成的文件需要与源文件保持一致，必须确保 codegen 在合适的时候运行。常见做法：

- **本地开发**：在 `package.json` 中添加 `"codegen": "pgtyped -c config.json"`，开发者修改查询后手动运行。
- **pre-commit / pre-push 钩子**：在提交前自动运行 codegen，并检查是否有未提交的变更。
- **持续集成（CI）**：在 CI 流程中运行 codegen，然后执行 `git diff --exit-code`，如果生成的文件与仓库中不一致，则构建失败。这可以防止团队成员忘记运行 codegen。

---

### 7. 其他适用场景

除了 SQL 查询，代码生成也适合以下情况：

- **API 客户端**：从 OpenAPI / Swagger 规范生成 TypeScript 类型和请求函数（如 `openapi-typescript`）。
- **GraphQL**：从 GraphQL schema 生成类型（如 `graphql-codegen`）。
- **数据库 schema**：从数据库表结构生成 ORM 实体类型（如 `prisma`、`typeorm` 的迁移生成）。
- **国际化（i18n）**：从语言文件生成类型安全的键值类型。
- **数据验证**：从 JSON Schema 生成 TypeScript 类型和验证器。

---

### 8. 总结

- **复杂类型逻辑容易陷入“图灵泥沼”**：虽然 TypeScript 类型系统很强大，但不意味着你应该用它来实现所有逻辑。
- **代码生成是一个务实的选择**：用常规语言编写工具，在构建时生成类型，可以大幅降低复杂度，提高可维护性。
- **权衡成本**：代码生成会增加构建步骤和同步成本，但通常远低于维护一个庞大且脆弱的类型系统的成本。
- **实践建议**：当你发现自己在类型系统中编写“编译器”时（如解析 SQL、正则、DSL），停下来考虑是否可以通过代码生成来替代。

**最终建议**：保持简单。类型系统是工具，不是玩具。用最适合的方式保证类型安全，而不是为了炫技而滥用类型系统。