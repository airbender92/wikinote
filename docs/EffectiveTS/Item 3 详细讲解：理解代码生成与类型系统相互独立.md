## Item 3 详细讲解：理解代码生成与类型系统相互独立

TypeScript 编译器 `tsc` 主要做两件事：**1) 将 TypeScript 代码转译（transpile）成指定版本的 JavaScript；2) 检查代码中的类型错误**。这两个行为是**完全独立**的。这意味着：
- 类型错误不会阻止生成 JavaScript 代码（除非开启 `noEmitOnError`）。
- 类型信息在运行时不复存在（类型被“擦除”）。
- 类型操作（如类型断言）不会影响运行时行为。
- TypeScript 类型对运行时性能零影响。

本节通过多个例子阐述了这些关键点，下面逐一详解。

---

### 一、运行时无法检查 TypeScript 类型

**问题示例**：试图用 `instanceof` 检查一个类型（`Rectangle`），但 `Rectangle` 是一个接口（type），不是值。

```ts
interface Square { width: number; }
interface Rectangle extends Square { height: number; }
type Shape = Square | Rectangle;

function calculateArea(shape: Shape) {
  if (shape instanceof Rectangle) {   // ❌ 错误：'Rectangle' 仅表示类型，但被用作值
    return shape.height * shape.width;
  } else {
    return shape.width * shape.width;
  }
}
```

**原因**：TypeScript 的类型在编译后被完全擦除。编译后的 JavaScript 中没有任何关于 `Rectangle` 接口的信息，因此 `instanceof Rectangle` 无法工作。

**解决方案**：
1. **检查属性存在性**（使用 `in` 操作符）：
   ```ts
   if ('height' in shape) { ... }
   ```
   TypeScript 能够理解这种检查，并在相应分支中将 `shape` 的类型收窄为 `Rectangle`。

2. **使用标签联合（tagged union）**：
   ```ts
   interface Square { kind: 'square'; width: number; }
   interface Rectangle { kind: 'rectangle'; width: number; height: number; }
   type Shape = Square | Rectangle;
   if (shape.kind === 'rectangle') { ... }
   ```
   运行时可以通过 `kind` 字段区分具体类型。

3. **使用类**：类同时引入类型和值，因此 `instanceof` 可以工作。
   ```ts
   class Square { width: number; constructor(width: number) { this.width = width; } }
   class Rectangle extends Square { height: number; ... }
   if (shape instanceof Rectangle) { ... }
   ```

**核心概念**：TypeScript 类型是“可擦除的”，仅在编译时存在，运行时不可用。需要运行时类型信息时，必须通过 JavaScript 值（属性、标签、构造函数等）来重建。

---

### 二、有类型错误的代码仍能生成 JS 输出

示例：
```ts
let x = 'hello';
x = 1234;   // 类型错误：不能将 number 赋值给 string
```
运行 `tsc test.ts` 后，虽然报错，但仍然生成了 `test.js`：
```js
var x = 'hello';
x = 1234;
```

**含义**：TypeScript 将类型错误视为“警告”，默认不会中断构建。这与 C++/Java 等语言不同，后者类型错误会阻止编译。

**实践建议**：
- 开发时可以利用这一特性：即使某些部分有类型错误，仍可测试其他部分。
- 但在提交代码前应确保零错误，避免混淆“预期错误”和“真实错误”。
- 如果想阻止生成 JS，可以设置 `noEmitOnError: true`。

**术语澄清**：说“TypeScript 编译失败”并不准确，更正确的是说“类型检查不通过”。因为代码生成（编译）仍然成功了。

---

### 三、类型操作不影响运行时值

示例：
```ts
function asNumber(val: number | string): number {
  return val as number;   // 类型断言
}
```
编译后的 JS：
```js
function asNumber(val) {
  return val;
}
```
没有任何转换。`as number` 只是告诉 TypeScript “我相信它是数字”，但不会在运行时进行任何强制类型转换。

**正确做法**：使用 JavaScript 运行时转换，如 `Number(val)`。

**启示**：类型断言不是“类型转换”，它不改变实际值。类型系统无法影响运行时行为。

---

### 四、运行时类型可能与声明的类型不一致

示例：
```ts
function setLightSwitch(value: boolean) {
  switch (value) {
    case true: turnLightOn(); break;
    case false: turnLightOff(); break;
    default: console.log("I'm afraid I can't do that.");
  }
}
```
这个函数怎么可能进入 `default` 分支？`value` 声明为 `boolean`，理论上只有 `true` 或 `false`。但运行时可以传入其他值：
- JavaScript 代码可能调用 `setLightSwitch("ON")`（没有类型检查）。
- 网络响应可能将 `lightSwitchValue` 定义为字符串，但代码中将其声明为 `boolean`：
  ```ts
  const result: LightApiResponse = await response.json();
  setLightSwitch(result.lightSwitchValue);
  ```
  如果实际 JSON 中 `lightSwitchValue` 是字符串 `"true"`，运行时就会进入 `default` 分支。

**教训**：TypeScript 类型只是“承诺”，运行时无法强制。处理外部数据（API、用户输入）时，必须进行运行时验证，不能仅依赖类型声明。

---

### 五、不能基于 TypeScript 类型重载函数

在 C++ 中可以定义同名但参数类型不同的多个函数。TypeScript 不支持这种运行时重载，因为类型在运行时已擦除。

TypeScript 允许提供**多个类型签名**（重载签名），但只能有一个**实现**：
```ts
function add(a: number, b: number): number;
function add(a: string, b: string): string;
function add(a: any, b: any) {
  return a + b;
}
```
编译后只有实现保留，签名消失。调用时 TypeScript 会根据参数类型选择正确的签名，但运行时仍然只有一个 `add` 函数。

**注意**：实现中的参数类型通常需要是 `any` 或联合类型，以便接受所有可能的输入。

---

### 六、TypeScript 类型对运行时性能零影响

因为类型被完全擦除，生成的 JavaScript 中没有任何类型信息，因此运行时没有任何额外开销。

**两个注意事项**（但并不否定“零成本”）：
1. **编译时开销**：类型检查会消耗构建时间，但这在开发/CI 阶段发生，不影响用户运行时。
2. **转译导致的性能差异**：如果使用新特性（如 `async/await`）并转译为 ES5，生成的辅助代码可能比原生实现稍慢。但这与类型系统无关，而是目标 JavaScript 版本的选择问题。

**结论**：任何声称“TypeScript 导致运行时变慢”的说法都是错误的。

---

### 七、总结要点（Things to Remember）

- **代码生成与类型系统独立**：类型错误不会阻止生成 JS。
- **运行时无法获取 TypeScript 类型**：需要使用标签联合、属性检查或类来重建类型信息。
- **类型操作不影响运行时值**：`as` 断言不是强制类型转换。
- **声明的类型与运行时类型可能不一致**：对不信任的数据要进行运行时验证。
- **不能基于 TypeScript 类型进行函数重载**：只能提供多个类型签名，单个实现。
- **TypeScript 类型对运行时性能零影响**：仅编译时有开销。

通过理解这些要点，你将能正确看待 TypeScript 的能力边界，避免常见的误解（如试图在运行时检查类型、过度依赖类型断言等）。