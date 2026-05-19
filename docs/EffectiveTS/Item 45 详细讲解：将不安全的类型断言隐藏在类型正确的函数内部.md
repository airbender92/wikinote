## Item 45 详细讲解：将不安全的类型断言隐藏在类型正确的函数内部

这一节的核心是：**当你必须使用不安全的类型断言（type assertion）或 `any` 时，应该把它们隐藏在函数实现内部，而对外暴露精确、安全的类型签名。** 绝对不要为了迎合类型检查器的错误而牺牲函数签名的质量，因为签名是公共 API，它的正确性比实现更重要。

书中通过几个例子展示了这一原则：从网络请求的类型断言，到对象浅比较中的 `any` 使用。

---

### 1. 问题情境：一个返回 `unknown` 的通用 `fetch` 包装

假设我们有一个安全的 `checkedFetchJSON` 函数，它返回 `Promise<unknown>`（比默认的 `any` 更安全）：

```ts
async function checkedFetchJSON(url: string): Promise<unknown> {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Unable to fetch! ${response.statusText}`);
  return response.json();  // 默认返回 any，但这里我们封装成 unknown
}
```

现在，我们想要为特定 API（山岳数据）编写一个 `fetchPeak` 函数，它应该返回 `Promise<MountainPeak>`：

```ts
interface MountainPeak {
  name: string;
  continent: string;
  elevationMeters: number;
  firstAscentYear: number;
}

export async function fetchPeak(peakId: string): Promise<MountainPeak> {
  return checkedFetchJSON(`/api/mountain-peaks/${peakId}`);
  // 错误：类型 'unknown' 不能赋给类型 'MountainPeak'
}
```

TypeScript 报错，因为 `unknown` 不能直接赋值给 `MountainPeak`。你有几种选择，其中两种是错误的，一种是正确的。

---

### 2. 错误做法一：修改函数签名以匹配实现（不推荐）

```ts
export async function fetchPeak(peakId: string): Promise<unknown> {
  return checkedFetchJSON(`/api/mountain-peaks/${peakId}`); // 类型检查通过
}
```

**问题**：现在调用方会得到 `Promise<unknown>`。每次使用 `fetchPeak` 的地方都必须进行类型断言或复杂的类型收窄：

```ts
const peaks = await Promise.all(sevenPeaks.map(fetchPeak)) as MountainPeak[];
```

断言散落在各处，容易出错且繁琐。这相当于把类型安全的责任推给了所有使用者。

**结论**：**不要为了通过类型检查而削弱函数签名的精度**。签名是公共契约，应该对使用者友好。

---

### 3. 错误做法二：全局使用 `any` 或删除类型检查（不推荐）

另一种错误是在调用链上使用 `as any` 或修改 `checkedFetchJSON` 返回 `any`。这会让不安全的 `any` 扩散到整个代码库。

书中没有展开这种错误，因为 Item 43 和 44 已经说明了 `any` 的传染性。

---

### 4. 正确做法：在实现内部使用类型断言，对外保持精确签名

```ts
export async function fetchPeak(peakId: string): Promise<MountainPeak> {
  return checkedFetchJSON(`/api/mountain-peaks/${peakId}`) as Promise<MountainPeak>;
}
```

**优点**：
- 对外签名仍然是 `Promise<MountainPeak>`，使用者不需要任何额外操作。
- 不安全的断言被**隐藏**在函数内部，只影响这一行。
- 类型检查器不再报错，同时调用代码保持干净。

**加强安全性**：你可以在断言之前添加一些运行时验证，确保响应确实符合 `MountainPeak` 的形状：

```ts
export async function fetchPeak(peakId: string): Promise<MountainPeak> {
  const maybePeak = await checkedFetchJSON(`/api/mountain-peaks/${peakId}`);
  if (!maybePeak || typeof maybePeak !== 'object' || !('firstAscentYear' in maybePeak)) {
    throw new Error(`Invalid mountain peak: ${JSON.stringify(maybePeak)}`);
  }
  // 验证通过后再断言
  return maybePeak as MountainPeak;
}
```

这样即使断言不安全，至少运行时有一定保障。这种验证代码只需写一次（在函数内部），而不是在每个调用点重复。

**注意**：如果你频繁需要这类运行时验证，可以考虑使用 Item 74 中介绍的方案（如 Zod 或 JSON Schema）。

---

### 5. 另一种隐藏方式：使用函数重载（overload）

你可以提供一个更精确的重载签名，而实现使用宽松的类型：

```ts
export async function fetchPeak(peakId: string): Promise<MountainPeak>;
export async function fetchPeak(peakId: string): Promise<unknown> {
  return checkedFetchJSON(`/api/mountain-peaks/${peakId}`);
}
```

调用方看到的签名是 `Promise<MountainPeak>`，而实现返回 `Promise<unknown>`（无需断言）。TypeScript 会检查两个签名是否兼容。这本质上也是一种隐藏不安全性的方式，但不如显式断言那么清晰。

---

### 6. 另一个例子：对象浅比较函数中的 `any`

考虑一个函数，它检查两个对象是否浅相等：

```ts
function shallowObjectEqual(a: object, b: object): boolean {
  for (const [k, aVal] of Object.entries(a)) {
    if (!(k in b) || aVal !== b[k]) {
      // 错误：b[k] 隐式 any，因为对象没有索引签名
      return false;
    }
  }
  return Object.keys(a).length === Object.keys(b).length;
}
```

TypeScript 无法理解 `k in b` 意味着 `b[k]` 是安全的，所以报错。错误的修复方式是改变参数类型：

```ts
function shallowObjectEqualBad(a: object, b: any): boolean { ... }
```

这会让 `b` 变成 `any`，导致调用方可以传入 `null` 等非法值，运行时崩溃。

**正确的做法**：只在必要时使用 `as any`，且限制在最小范围，并添加注释说明：

```ts
function shallowObjectEqualGood(a: object, b: object): boolean {
  for (const [k, aVal] of Object.entries(a)) {
    if (!(k in b) || aVal !== (b as any)[k]) {
      // `(b as any)[k]` is OK because we've just checked `k in b`
      return false;
    }
  }
  return Object.keys(a).length === Object.keys(b).length;
}
```

这里 `as any` 仅用于属性访问，函数签名仍然是 `(object, object) => boolean`，没有破坏公共 API。

---

### 7. 核心原则总结

| 场景 | 错误做法 | 正确做法 |
|------|----------|----------|
| 内部需要断言 | 修改函数签名（返回 `unknown` 或 `any`） | 保持精确签名，在函数体内使用 `as T` |
| 类型检查器无法理解安全逻辑 | 将参数类型改为 `any` | 在最小范围内使用 `as any` 或 `@ts-expect-error`，并加注释 |
| 多调用点需要断言 | 每个调用点都写 `as T` | 封装一个函数，内部断言一次 |

**关键点**：
- **不要为了修复实现中的类型错误而削弱公共 API 的类型**。
- 将不安全的操作（断言、`any`）封装在最小的作用域内（最好是一个函数内部）。
- 对于断言，尽量添加运行时验证和单元测试，以弥补类型安全性的缺失。
- 使用注释解释为什么该断言是安全的，方便后续维护者理解。

**最终建议**：类型断言和 `any` 是 TypeScript 的逃生舱。使用它们时，要像处理放射性材料一样：**封闭在容器（函数）内部，并确保辐射（不安全类型）不会泄漏到外部环境（函数签名）**。