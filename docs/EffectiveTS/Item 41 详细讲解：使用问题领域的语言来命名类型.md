## Item 41 详细讲解：使用问题领域的语言来命名类型

这一节的核心是：**类型、属性、变量的命名应该来自你所解决的问题领域（problem domain），而不是泛泛的计算机术语。** 好的命名能提升代码的抽象层次和可读性，让团队成员和领域专家都能轻松理解；糟糕的命名则会造成歧义、误导和维护困难。

书中通过一个“动物数据库”的例子生动对比了模糊命名与领域命名的差异。

---

### 1. 糟糕的命名示例：`Animal` 接口

```ts
interface Animal {
  name: string;
  endangered: boolean;
  habitat: string;
}

const leopard: Animal = {
  name: 'Snow Leopard',
  endangered: false,
  habitat: 'tundra',
};
```

**问题分析**：

| 字段 | 问题 | 具体说明 |
|------|------|----------|
| `name` | 过于通用 | 是常见名（Common Name）还是学名（Scientific Name）？不同的动物可能有多个“名字”，歧义很大。 |
| `endangered` | 含义模糊 | 布尔值只能表示“是/否濒危”，但实际情况更复杂：濒危（EN）、易危（VU）、极危（CR）、灭绝（EX）等。`false` 是表示“无危（LC）”还是“数据缺乏（DD）”？另外，如果动物已经灭绝，`endangered: false` 会让人困惑。 |
| `habitat` | 过于宽泛 | 是“栖息地类型”（森林、湿地）？还是具体的地理区域？还是气候带？作为字符串，没有标准化的取值，难以查询和验证。 |
| 变量名 `leopard` 与 `name` 字段 | 不一致 | `leopard` 是动物名，但 `name` 字段的值却是 `'Snow Leopard'`。如果变量名已经是 `leopard`，那么 `name` 到底应该存什么？ |

这些问题导致：
- 任何阅读代码的人都需要猜测字段的准确含义。
- 无法利用类型系统进行有意义的验证（例如 `habitat` 可以是任意字符串，拼写错误无法检测）。
- 未来维护时，新开发者可能会误解字段用途，引入 bug。

---

### 2. 改进的命名示例：使用领域术语

```ts
interface Animal {
  commonName: string;
  genus: string;
  species: string;
  status: ConservationStatus;
  climates: KoppenClimate[];
}

type ConservationStatus = 'EX' | 'EW' | 'CR' | 'EN' | 'VU' | 'NT' | 'LC';
// 灭绝 | 野外灭绝 | 极危 | 濒危 | 易危 | 近危 | 无危

type KoppenClimate = 
  | 'Af' | 'Am' | 'As' | 'Aw'      // 热带
  | 'BSh' | 'BSk' | 'BWh' | 'BWk' // 干旱
  | 'Cfa' | 'Cfb' | ...           // 温带
  | 'Dfa' | 'Dfb' | ...           // 大陆性
  | 'EF' | 'ET';                  // 极地

const snowLeopard: Animal = {
  commonName: 'Snow Leopard',
  genus: 'Panthera',
  species: 'Uncia',
  status: 'VU',        // 易危
  climates: ['ET', 'EF', 'Dfd'], // 高山苔原、冰盖、亚寒带
};
```

**改进点**：

| 原始字段 | 改进后 | 理由 |
|----------|--------|------|
| `name` | `commonName`, `genus`, `species` | 使用生物学中的命名层次：常用名、属、种。精确且无歧义。 |
| `endangered: boolean` | `status: ConservationStatus` | 使用 IUCN 红色名录标准分类，覆盖从灭绝到无危的多个等级，比布尔值丰富且标准。 |
| `habitat: string` | `climates: KoppenClimate[]` | 使用柯本气候分类系统的代码，每个代码有明确定义，而且数组允许一个动物适应多种气候。 |

**效果**：
- 字段含义清晰，任何对生物学有基本了解的人都能理解。
- 类型系统可以约束 `status` 和 `climates` 的取值范围，拼写错误或无效值会被 TypeScript 捕获。
- 如果需要了解更多（例如某种柯本气候的具体含义），可以直接搜索该术语，有丰富的公开资料。

---

### 3. 命名的一般原则

书中除了动物例子外，还给出了三条重要的命名规则：

#### 3.1 区别要有意义

在自然语言中，我们经常换用同义词避免重复（例如“用户”、“客户”、“账户持有人”）。但在代码中，如果两个概念本质相同，就不要使用不同的名称，否则会让阅读者以为存在细微差异。

**错误示例**：在同一系统中混用 `User`、`Account`、`Profile` 表示同一个实体，但实际上它们的字段几乎一样。后来新人会困惑：“什么时候该用 `User`，什么时候该用 `Account`？”

**正确做法**：统一使用一个名称，或者只在有真正区别时才创建新类型。

#### 3.2 避免模糊的名称

像 `data`、`info`、`thing`、`item`、`object`、`entity` 这类词，除非在领域中有非常明确的定义，否则不要用作类型名或变量名。

- 它们不传达任何领域信息。
- 很容易导致名称冲突：一个项目里可能会有多个 `Data`、`Entity` 类型，开发者很难记住哪个是哪个。

**改进**：用具体的事物命名，例如 `Customer`、`InvoiceLine`、`SessionToken` 等。

#### 3.3 为事物本身命名，而不是为它的实现或内容命名

**错误示例**：`INodeList` 作为类型名。这个名字暴露了实现细节（“一个包含 i 节点的列表”）。如果将来改用数组、缓存或其他结构，名称就会过时。

**正确示例**：`Directory`（目录）。这个名字直接描述了业务概念，而不是它的实现方式。它提升了抽象层次，让开发者思考“目录”的语义，而不是“如何存储目录内容”。

> Good names can increase your level of abstraction.

---

### 4. 对函数参数、元组标签等同样适用

命名原则不限于类型和属性，也适用于：
- 函数参数名
- 元组元素标签（例如 `[x: number, y: number]`）
- 索引签名中的键名（虽然仅用于文档，但也应使用领域术语）

例如，不要写 `function process(data: any)`，而应该写 `function process(invoice: Invoice)`。

---

### 5. 总结：如何命名类型

| 原则 | 说明 |
|------|------|
| **使用领域词汇** | 从问题领域中借用术语（生物学、地理学、金融等），而不是发明通用术语。 |
| **准确使用** | 确保你使用的领域术语含义与领域一致，不要扭曲其原意。 |
| **区别要有意义** | 如果两个术语指代同一个概念，就用同一个名字；如果确实不同，就用不同的名字。 |
| **避免模糊词** | 避免 `Data`、`Info`、`Item`、`Entity` 等无信息量的词。 |
| **为事物本身命名** | 命名反映事物是什么（`Directory`），而不是它如何实现（`INodeList`）。 |

**最终目标**：让类型系统成为沟通工具，而不是障碍。当其他人（包括未来的你）阅读代码时，类型名就应该揭示业务意图，减少对注释和文档的依赖。