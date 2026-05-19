## Item 30 详细讲解：输入宽松，输出严格（鲁棒性原则）

这一节的核心是 **Postel 定律**（鲁棒性原则）：**“对自己要保守，对他人要宽容。”** 在函数设计中体现为：**接受参数的类型可以宽松灵活，但返回值的类型应该精确严格**。这样可以降低调用者的负担，同时避免把复杂性传递给使用者。

---

### 1. 问题示例：一个“过于宽松”的返回类型

假设有一个 3D 地图 API，提供了两个函数：

- `setCamera(camera: CameraOptions)`：设置相机参数（中心点、缩放、朝向等）。
- `viewportForBounds(bounds: LngLatBounds)`：根据给定的地理范围计算最佳相机参数。

最初的定义如下：

```ts
interface CameraOptions {
  center?: LngLat;
  zoom?: number;
  bearing?: number;
  pitch?: number;
}

type LngLat = 
  | { lng: number; lat: number }
  | { lon: number; lat: number }
  | [number, number];   // [经度, 纬度]
```

`CameraOptions` 所有字段都是**可选**的，这样你可以只修改 `center` 而不影响 `zoom` 等。  
`LngLat` 类型允许三种表示：带 `lng/lat` 的对象、带 `lon/lat` 的对象、或二元组。这给调用者提供了很大灵活性。

`viewportForBounds` 的输入也是一个宽松类型 `LngLatBounds`，它有 19 种可能的写法。但它的**返回值类型也是 `CameraOptions`** —— 这意味着它返回的对象中，`center` 可能是三种格式中的任意一种，`zoom` 可能是 `number` 也可能是 `undefined`。

于是，当用户编写如下代码时，就会遇到类型错误：

```ts
function focusOnFeature(f: Feature) {
  const bounds = calculateBoundingBox(f);
  const camera = viewportForBounds(bounds);
  setCamera(camera);

  const { center: { lat, lng }, zoom } = camera;
  // ~~~~~~~ Property 'lat' does not exist on type 'LngLat | undefined'
  // ~~~~~~~ Property 'lng' does not exist on type 'LngLat | undefined'
  // zoom 的类型是 number | undefined
}
```

**问题**：
- `camera.center` 的类型是 `LngLat | undefined`，而 `LngLat` 是一个联合类型，TypeScript 不知道你具体得到的是哪种格式，所以无法直接访问 `.lat`。
- `camera.zoom` 可能是 `undefined`，调用者每次都要判断。

**根源**：`viewportForBounds` 返回了一个**过于宽松**的类型，把输入的模糊性传染给了输出。

---

### 2. 解决方案：区分“宽松输入类型”和“规范输出类型”

改进的思路是：  
- 对于**输入**，保持宽松（多种形式），方便调用者。  
- 对于**输出**，使用一种**确定的、规范的格式**，让调用者可以直接使用，无需再判断。

于是引入两个新类型：

```ts
// 规范格式（输出用）
interface LngLat {
  lng: number;
  lat: number;
}

// 宽松格式（输入用）
type LngLatLike = LngLat | { lon: number; lat: number } | [number, number];

// 完整的相机参数（输出用）
interface Camera {
  center: LngLat;
  zoom: number;
  bearing: number;
  pitch: number;
}

// 输入参数仍可部分可选，但 center 接受宽松格式
interface CameraOptions extends Omit<Partial<Camera>, 'center'> {
  center?: LngLatLike;
}
```

`CameraOptions` 巧妙地复用了 `Camera` 的类型，但将 `center` 改为可选的 `LngLatLike`，其余属性通过 `Partial<Camera>` 变为可选。

然后修改 `viewportForBounds` 的返回类型为 `Camera`（严格规范）：

```ts
declare function viewportForBounds(bounds: LngLatBounds): Camera;
```

现在 `focusOnFeature` 中的代码就能正确工作了：

```ts
const { center: { lat, lng }, zoom } = camera;  // OK
// lat, lng 一定是 number，zoom 也一定是 number
```

**优点**：
- 输入仍然非常灵活（19 种写法），调用者方便。
- 输出非常精确，无需额外的类型收窄。
- 类型定义虽然变长，但清晰且安全。

---

### 3. 进一步推广：参数使用 `Iterable<T>` 代替 `T[]`

这是同一原则的另一个体现：**接受更宽泛的输入，但返回精确的结果**。

一个简单的求和函数：

```ts
function sum(xs: number[]): number {
  let s = 0;
  for (const x of xs) s += x;
  return s;
}
```

返回值 `number` 很精确，但参数 `number[]` 其实**过于严格**。如果传入一个 `Set<number>` 或一个生成器（generator），就会报错，尽管函数只需要迭代元素。

更好的做法：使用 `Iterable<number>`。

```ts
function sum(xs: Iterable<number>): number {
  let s = 0;
  for (const x of xs) s += x;
  return s;
}
```

现在你可以传入**数组、`Set`、`Map` 的 `values()`、生成器函数**等任何可迭代对象：

```ts
function* range(limit: number) {
  for (let i = 0; i < limit; i++) yield i;
}
const fortyFive = sum(range(10));  // 0+1+...+9 = 45，完全正确
```

**原则**：如果函数只需要遍历输入，就用 `Iterable<T>`；如果需要随机访问或长度，才使用 `Array<T>` 或 `ArrayLike<T>`。这样既保持了实现的简单，又最大程度地兼容了各种数据源。

---

### 4. 总结：输入宽松、输出严格的实践要点

| 维度 | 推荐做法 | 避免 |
|------|----------|------|
| 参数类型 | 尽量宽泛（联合类型、可选属性、`Iterable`） | 过于具体的类型（如 `number[]`） |
| 返回类型 | 精确、规范（单一形式，无 `undefined` 或不必要的可选） | 联合类型、含 `undefined` 的返回 |
| 输入与输出之间的关系 | 可以定义“规范型”和“宽松型”两个版本，内部转换 | 把输入的模糊性直接传递到输出 |

**最后一句提醒**：如果你的函数需要同时接受多种输入格式并返回相应格式的输出（例如 `string | number` 输入，返回 `string | number`），优先考虑使用**泛型 + 条件类型**（Item 52）来保持输入输出类型之间的关联，而不是简单地返回联合类型。

**记住 Postel 定律：对自己严格，对他人宽容 —— 在 TypeScript 中，就是对输出严格，对输入宽容。**