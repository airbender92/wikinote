## Item 42 详细讲解：避免基于零散数据（Anecdotal Data）编写类型

这一节的核心是：**不要根据自己看到的少数几个数据示例（例如测试数据库中的几行，或者 API 返回的几个样本）来手动编写 TypeScript 类型。** 这样做很容易遗漏边缘情况，导致类型不准确，给使用者带来虚假的安全感。更好的做法是从官方规范、社区维护的类型定义（如 DefinitelyTyped）或者从 Schema（如 OpenAPI、GraphQL）中生成类型。

书中通过 GeoJSON 类型的例子生动地说明了手动编写类型的陷阱，然后介绍了如何利用社区类型和工具生成类型。

---

### 1. 问题示例：手动编写 GeoJSON 类型

假设你需要计算 GeoJSON 要素（Feature）的包围盒（bounding box）。你查看了一些 GeoJSON 数据，发现它们看起来像这样：

```json
{
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [125.6, 10.1]
  },
  "properties": {}
}
```

于是你手动定义了一个 `GeoJSONFeature` 接口：

```ts
interface GeoJSONFeature {
  type: 'Feature';
  geometry: GeoJSONGeometry | null;
  properties: unknown;
}

interface GeoJSONGeometry {
  type: 'Point' | 'LineString' | 'Polygon' | 'MultiPolygon';
  coordinates: number[] | number[][] | number[][][] | number[][][][];
}
```

你的 `calculateBoundingBox` 函数使用了 `geometry.coordinates`：

```ts
function calculateBoundingBox(f: GeoJSONFeature): BoundingBox | null {
  let box = null;
  const helper = (coords: any[]) => { /* ... */ };
  const { geometry } = f;
  if (geometry) {
    helper(geometry.coordinates);  // 这里假定 geometry 一定有 coordinates 属性
  }
  return box;
}
```

这个代码通过了类型检查，因为你的 `GeoJSONGeometry` 中所有类型都有 `coordinates` 字段。

**但是，GeoJSON 规范中还有一种几何类型叫 `GeometryCollection`**，它是一个几何对象的集合，本身没有 `coordinates` 属性，而是有一个 `geometries` 数组：

```json
{
  "type": "GeometryCollection",
  "geometries": [
    { "type": "Point", "coordinates": [0, 0] },
    { "type": "LineString", "coordinates": [[1,1],[2,2]] }
  ]
}
```

由于你从未见过这样的数据，你的类型定义中漏掉了 `GeometryCollection`。如果你的函数传入这样的要素，运行时会报错：`Cannot read property '0' of undefined`（因为尝试访问 `coordinates`）。

**教训**：基于零散数据手动定义类型，很容易遗漏规范中真实存在的边缘情况。

---

### 2. 解决方案：使用社区维护的类型定义

TypeScript 社区已经在 DefinitelyTyped 上为 GeoJSON 提供了官方类型定义（`@types/geojson`）。安装后，使用其中的 `Feature` 类型：

```ts
import { Feature } from 'geojson';

function calculateBoundingBox(f: Feature): BoundingBox | null {
  // ...
}
```

此时 TypeScript 会立即报错：

```
Property 'coordinates' does not exist on type 'Geometry'
Property 'coordinates' does not exist on type 'GeometryCollection'
```

因为 `Geometry` 是一个联合类型，包括 `Point`、`LineString`、`Polygon`、`MultiPolygon`，以及 `GeometryCollection`。后者没有 `coordinates` 属性，所以直接访问是非法的。

**这迫使你去处理 `GeometryCollection` 的情况**，要么显式不支持并抛出清晰的错误，要么递归处理其中的每一个几何体。无论哪种，都比原先的“静默失败”要好得多。

---

### 3. 其他生成类型的方式

#### 3.1 GraphQL

GraphQL API 自带 Schema，定义了所有查询、变更和类型。可以使用工具（如 `graphql-code-generator`）直接从 Schema 生成 TypeScript 类型，确保类型与 API 完全同步。

#### 3.2 OpenAPI (Swagger)

许多 REST API 提供 OpenAPI 规范文件（JSON 或 YAML），其中用 JSON Schema 描述了请求和响应的结构。可以使用 `json-schema-to-typescript` 这样的工具生成 TypeScript 接口。

书中演示了从 OpenAPI 的 `components/schemas` 部分提取 `CreateCommentRequest` 并生成类型：

```bash
$ jq .components.schemas.CreateCommentRequest schema.json > comment.json
$ npx json-schema-to-typescript comment.json > comment.ts
```

生成的 `CreateCommentRequest` 接口准确反映了 schema 中的字段类型和必填性。

#### 3.3 从数据生成类型（最后手段）

如果没有规范、没有社区类型，只有一些数据样本（例如一批 JSON 文件），可以使用 `quicktype` 等工具从数据推断类型。但要警惕：这仍然基于零散数据，可能会遗漏边缘情况。仅当数据集是**有限的**（例如一个固定目录下的 1000 个文件）时，这种方法是可靠的。

---

### 4. 为什么这很重要？

- **准确性**：基于规范或社区类型能覆盖所有合法值，避免遗漏。
- **可维护性**：当规范更新时，重新生成类型即可，无需手动修改。
- **可靠性**：社区类型经过大量使用和测试，比个人手写的类型更可靠。

**即使你不写库，只写应用，也受益于这种实践**：例如 TypeScript 自带的 `lib.dom.d.ts` 就是从 MDN 的 API 描述自动生成的，这保证了 DOM 类型与浏览器标准一致，帮助我们在编码时捕获错误。

---

### 5. 总结：三种来源的优先级

| 优先级 | 来源 | 示例 | 优点 |
|--------|------|------|------|
| 最优 | 官方 TypeScript 客户端或社区类型 | `@types/geojson` | 直接可用，经过验证，覆盖全面 |
| 次优 | 从 Schema 生成 | OpenAPI → `json-schema-to-typescript`<br>GraphQL → `graphql-code-generator` | 与规范同步，准确，可自动化 |
| 最后手段 | 从数据样本生成 | `quicktype` | 仅当数据有限且无规范时使用，需谨慎 |

**核心原则**：**不要仅凭自己看到的几个数据示例手写类型**，因为这就像“盲人摸象”，很容易遗漏重要的边缘情况。始终优先使用基于规范或社区来源的类型。