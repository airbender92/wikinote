## Item 28 详细讲解：使用类和柯里化创建新的推断站点

### 问题背景

假设我们有一个 REST API，其端点路径和返回类型可以通过 TypeScript 接口来描述：

```ts
export interface SeedAPI {
  '/seeds': Seed[];              // GET /seeds 返回 Seed 数组
  '/seed/apple': Seed;           // GET /seed/apple 返回单个 Seed
  '/seed/strawberry': Seed;      // GET /seed/strawberry 返回单个 Seed
}
```

我们希望编写一个通用的 `fetchAPI` 函数，它能够：
- 接受一个路径（如 `'/seed/strawberry'`）作为参数。
- **检查该路径是否在 `SeedAPI` 接口中定义**（即端点存在）。
- 返回正确的数据类型（由接口中对应的值类型决定）。

理想的使用方式：

```ts
// 正确用法
const berry = await fetchAPI<SeedAPI>('/seed/strawberry'); // 应返回 Seed
// 错误用法：路径不存在
fetchAPI<SeedAPI>('/seed/chicken');          // 应报错
// 错误用法：返回类型不匹配
const seed: Seed = await fetchAPI<SeedAPI>('/seeds'); // '/seeds' 返回 Seed[]，不能赋给 Seed
```

---

### 初次尝试：单函数泛型

我们尝试这样声明 `fetchAPI`：

```ts
declare function fetchAPI<API, Path extends keyof API>(
  path: Path
): Promise<API[Path]>;
```

这里：
- `API` 是接口类型（如 `SeedAPI`）。
- `Path` 必须是 `API` 的键（即路径字符串字面量）。
- 返回值类型为 `Promise<API[Path]>`，即路径对应的值类型。

**问题**：当你调用 `fetchAPI<SeedAPI>('/seed/strawberry')` 时，TypeScript 会报错：

```
Expected 2 type arguments, but got 1.
```

原因是：**TypeScript 的泛型参数推断是“全有或全无”**。要么你让 TypeScript 推断**所有**类型参数（不写任何 `<>`），要么你显式提供**所有**类型参数（不能只提供一部分）。这里我们想显式提供 `API`（因为无法推断），但让 `Path` 被推断，然而语法上不允许。

你可能会想：我们可以给 `API` 一个默认值？但默认值只能引用其他参数，不能从参数推断，而且默认值不能解决“显式指定 `API` 同时推断 `Path`”的问题。

**权宜之计**：两个都显式写出来：

```ts
const berry = fetchAPI<SeedAPI, '/seed/strawberry'>('/seed/strawberry');
```

这样可行但重复（路径写了两次），很不方便。

---

### 核心需求：分离推断站点

我们需要将“显式指定 `API`”和“推断 `Path`”放在两个不同的位置。TypeScript 允许在不同的**调用**中分别提供类型参数，只要它们处于不同的函数调用中。因此，我们可以通过**引入额外的调用**来创建新的“推断站点”。

书中提供了两种标准方法：**类** 和 **柯里化**。

---

### 解决方案一：使用类

定义一个泛型类 `ApiFetcher`，将 `API` 类型参数绑定到类本身，然后在类的方法中再引入新的泛型参数 `Path`：

```ts
declare class ApiFetcher<API> {
  fetch<Path extends keyof API>(path: Path): Promise<API[Path]>;
}
```

使用方式：

```ts
const fetcher = new ApiFetcher<SeedAPI>();   // 显式指定 API 类型
const berry = await fetcher.fetch('/seed/strawberry');   // Path 被推断为 '/seed/strawberry'
// berry 类型为 Seed
```

这里：
- 在构造 `ApiFetcher` 实例时，我们显式提供了 `SeedAPI` 作为 `API` 类型参数。
- 调用 `fetch` 方法时，TypeScript 可以根据参数 `'/seed/strawberry'` 推断 `Path` 为字面量类型 `'/seed/strawberry'`，并自动检查该路径是否属于 `keyof SeedAPI`。
- 返回值类型通过 `API[Path]` 计算得出。

错误示例：

```ts
fetcher.fetch('/seed/chicken');   // 错误：'/seed/chicken' 不在 'keyof SeedAPI' 中
const seed: Seed = await fetcher.fetch('/seeds');  // 错误：返回 Seed[] 不能赋给 Seed
```

**优点**：
- 简单直观，适合有多个方法共用同一个 `API` 类型的场景。
- 类型参数绑定在对象实例上，避免反复传递。

**缺点**：
- 需要实例化一个类（可能引入运行时开销，但可忽略）。
- 无法在类型定义中创建局部类型别名（见下文柯里化的优势）。

---

### 解决方案二：使用柯里化

柯里化是将多参数函数转化为一系列单参数函数的技术。我们可以让 `fetchAPI` 先接收 `API` 类型参数（显式指定），然后返回一个新函数，该函数再接收 `path` 参数并推断 `Path`。

```ts
declare function fetchAPI<API>(): 
  <Path extends keyof API>(path: Path) => Promise<API[Path]>;
```

注意这里的语法：`fetchAPI` 是一个无参数的泛型函数，它返回一个泛型函数。使用时：

```ts
const berry = await fetchAPI<SeedAPI>()('/seed/strawberry');
//            ↑ 显式指定 API        ↑ 调用返回的函数，并推断 Path
```

我们甚至可以拆分为两步：

```ts
const fetchSeedAPI = fetchAPI<SeedAPI>();   // 此时返回一个函数，类型为 <Path>(path: Path) => Promise<SeedAPI[Path]>
const berry = await fetchSeedAPI('/seed/strawberry');
```

**为什么这样可以**：第一次调用 `fetchAPI<SeedAPI>()` 显式提供了 `API` 类型参数，第二次调用 `fetchSeedAPI('/seed/strawberry')` 时，TypeScript 可以根据参数推断 `Path`，两者在不同的调用中，互不干扰。

**优势**：
- 不需要创建类实例。
- **可以在实现中创建局部类型别名**，这是柯里化独有的好处。例如：

```ts
function fetchAPI<API>() {
  type Routes = keyof API & string;   // 局部类型别名，避免重复写 keyof API
  return <Path extends Routes>(path: Path): Promise<API[Path]> => {
    return fetch(path).then(r => r.json());
  };
}
```

这里 `Routes` 是函数内部的局部类型，只能在实现的作用域内使用。这可以减少重复的类型表达式，尤其当 `keyof API` 复杂时很有用。类无法做到这一点，因为类的方法不能在其内部定义仅用于类型计算的局部别名（虽然可以在方法内部定义，但不能用于约束泛型参数）。

---

### 对比与选择

| 特性 | 类方案 | 柯里化方案 |
|------|--------|------------|
| 创建额外运行时对象 | 需要 `new` 实例 | 只需要函数调用 |
| 适用于多个方法共享同一类型参数 | 自然（多个方法） | 需要返回包含多个方法的对象 |
| 能否创建局部类型别名 | 否（类级别不行） | 是（在函数实现内） |
| 风格倾向 | 面向对象 | 函数式 |

书中建议：两者皆可，根据个人或团队的风格选择。如果你需要局部类型别名来简化复杂的类型表达式，柯里化更优。

---

### 核心启示

**当你想部分显式指定泛型参数、部分让 TypeScript 推断时，你必须创建两个不同的“推断站点”**。类通过构造函数绑定一部分参数，方法推断另一部分；柯里化通过多次函数调用实现同样的效果。

这是 TypeScript 泛型推理的一个重要边界情况，理解它可以帮助你设计更灵活的 API。