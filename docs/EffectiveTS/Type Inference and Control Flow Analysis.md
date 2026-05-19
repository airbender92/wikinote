## Item 18 核心总结：避免用可推断的类型注解污染代码

这一节的核心是：**TypeScript 的类型推断能力很强，大多数局部变量的类型可以被自动推断出来，无需手动添加冗余的类型注解**。理想的 TypeScript 代码应在函数/方法签名上保留类型注解，而在函数体内部的局部变量上省略它们。

### 关键结论

1. **基本变量和对象字面量**  
   - ❌ `let x: number = 12;`  
   - ✅ `let x = 12;`  
   - TypeScript 会根据初始值推断类型。显式注解是多余的，只会增加噪音。

2. **数组和函数返回值**  
   - 函数返回值通常也能被正确推断：  
     ```ts
     function square(nums: number[]) {
       return nums.map(x => x * x);  // 返回类型自动推断为 number[]
     }
     ```

3. **类型推断有助于重构**  
   - 如果后来修改了 `Product` 中 `id` 的类型（从 `number` 改为 `string`），那些手动注解了 `const id: number` 的地方会报错，而让 TypeScript 推断的代码则自动适配，无需修改。

4. **解构赋值与类型推断**  
   - 使用解构赋值可以让代码更简洁，同时保留类型推断：  
     ```ts
     function logProduct(product: Product) {
       const { id, name, price } = product;  // 所有类型自动推断
       console.log(id, name, price);
     }
     ```
   - 不能在解构内部写类型注解（会被当作重命名语法），应避免这种冗长写法。

5. **必须保留类型注解的位置**  
   - **函数参数**（TypeScript 不会根据函数体内的使用推断参数类型）  
   - **对象字面量**（为了启用多余属性检查，让错误出现在定义处而不是使用处）  
   - **函数返回值**（特别是公共 API、有多个返回语句、或需要命名返回类型时）

6. **何时应显式注解返回值**  
   - 函数有多个返回分支（确保所有分支返回相同类型）  
   - 函数是公共 API 的一部分（避免实现错误泄漏到调用方）  
   - 希望返回值使用命名类型（而不是推断出的匿名结构）  
   - 在大代码库中可提升编译器性能（减少类型推断工作量）

7. **回调参数的推断**  
   - 当函数作为库的回调时，参数类型通常可以省略，因为库的类型声明提供了上下文：  
     ```ts
     app.get('/health', (request, response) => {  // 类型自动推断
       response.send('OK');
     });
     ```

### 条目总结（Things to Remember）

- 当 TypeScript 能推断出相同类型时，不要写类型注解。  
- 理想的 TypeScript 代码：函数/方法签名有类型注解，但函数体内的局部变量没有。  
- 考虑对对象字面量使用显式注解，以启用多余属性检查，并确保错误报告在定义处而非使用处。  
- 除非函数有多个返回语句、是公共 API、或需要命名返回类型，否则不要注解函数返回值。

----

## Item 19 核心总结：为不同类型使用不同的变量

这一节的核心是：**在 TypeScript 中，变量的类型通常不会改变（即使值可以改变）。因此，不要重用同一个变量来保存不同类型的数据，而应为不同概念创建新的变量。**

### 关键结论

1. **TypeScript 变量类型通常不变**  
   - 一旦变量被初始化，其类型就被固定了（除非通过类型收窄缩小范围，但不会扩大）。  
   - 尝试将 `number` 赋给被推断为 `string` 的变量会导致类型错误。

2. **使用联合类型（`string | number`）可以修复错误，但引入新问题**  
   - 联合类型虽然能让赋值通过，但后续使用时通常需要进行类型检查（收窄）。  
   - 语义上，ID 和序列号是两个不同的概念，不应混用同一个变量。

3. **最佳实践：为不同概念使用不同变量**  
   ```ts
   const productId = "12-34-56";
   fetchProduct(productId);
   const serial = 123456;
   fetchProductBySerialNumber(serial);
   ```
   优点：
   - 分离了不相关的概念  
   - 可以使用更具体的变量名  
   - 类型推断无需注解，类型更简单（字面量而非联合类型）  
   - 可以使用 `const` 而非 `let`，更易推理

4. **区分“重用变量”与“变量遮蔽（shadowing）”**  
   - 变量遮蔽（在不同作用域中声明同名变量）不会引起类型错误，但可能混淆人类读者。  
   - 建议仍使用不同名称，或通过 ESLint 规则 `no-shadow` 禁止遮蔽。

5. **对对象的类似考虑见 Item 21**（一次性创建对象，而非逐步构建）

### 条目总结（Things to Remember）

- 变量的值可以改变，但它的类型通常不会改变。  
- 为避免混淆（对人和类型检查器都是如此），避免为不同类型的数据重用变量。

---

## Item 20 核心总结：理解变量如何获得其类型（类型拓宽）

这一节的核心是：**TypeScript 在从字面量推断类型时会进行“拓宽”（widening），即在保证灵活性的前提下选择一个足够宽的类型。理解这一过程有助于解释为什么某些代码会报错，以及如何控制类型推断的精确度。**

### 关键结论

1. **拓宽是必要的权衡**  
   - 当你写 `let x = 'x'` 时，TypeScript 推断 `x` 为 `string`，而不是字面量 `"x"`。  
   - 原因：变量可能被重新赋值，如果推断为 `"x"` 就无法再赋其他字符串。  
   - 对象属性也会被拓宽：`{ x: 1 }` 被推断为 `{ x: number }`，允许重新赋值数字，但不允许赋字符串或添加新属性。

2. **控制拓宽的方法（从宽松到严格）**  
   - **`const`**：将 `let` 改为 `const`，变量不可重新赋值，类型保持为字面量（如 `"x"`）。  
   - **显式类型注解**：`const obj: { x: string | number } = { x: 1 }`。  
   - **上下文类型**：将值传递给有明确参数类型的函数，TypeScript 会根据上下文推断。  
   - **`as const` 断言**：将整个对象或数组推断为最窄的只读类型（深度只读）。  
     - `{ x: 1, y: 2 } as const` → `{ readonly x: 1; readonly y: 2 }`  
     - `[1, 2, 3] as const` → `readonly [1, 2, 3]`  
   - **辅助函数**：如 `tuple(1, 2, 3)` 可以推断为 `[number, number, number]`。  
   - **`Object.freeze`**：产生类似的只读效果，但运行时也会生效。  
   - **`satisfies` 操作符**：确保值符合某个类型，同时保留精确的键和字面量类型。  
     - 对比：`const cap: Record<string, Point> = {...}` 会丢失精确的键名；  
       `const cap = {...} satisfies Record<string, Point>` 保留键名，且值不会被拓宽。

3. **`satisfies` 的优势**  
   - 既对值进行类型检查（确保符合形状），又保留字面量的精确类型。  
   - 错误发生在定义处而非使用处，比 `as const` 更便于定位问题。

### 条目总结（Things to Remember）

- 理解 TypeScript 如何通过拓宽从字面量推断类型。  
- 熟悉影响拓宽行为的方式：`const`、类型注解、上下文、辅助函数、`as const` 和 `satisfies`。

-----

## Item 21 核心总结：一次性创建对象

这一节的核心是：**TypeScript 中变量的类型通常不会改变，因此应避免逐步构建对象，而是使用对象字面量或扩展运算符一次性创建完整的对象**。这样能获得更准确的类型推断，并避免因遗漏属性导致的运行时错误。

### 关键结论

1. **逐步赋值会导致类型错误**  
   ```ts
   const pt = {};
   pt.x = 3;  // ❌ Property 'x' does not exist on type '{}'
   ```
   原因：`pt` 初始被推断为 `{}`，之后无法添加新属性。

2. **类型断言（`as Point`）能绕过错误，但不安全**  
   - 允许逐步赋值，但 TypeScript 不会检查是否所有必需属性都已赋值。  
   - 容易遗漏属性，导致运行时 `NaN` 或异常。

3. **最佳实践：使用对象字面量一次性定义**  
   ```ts
   const pt: Point = { x: 3, y: 4 };  // ✅
   ```

4. **从多个小对象构建大对象时，使用对象扩展运算符（`...`）**  
   ```ts
   const namedPoint = { ...pt, ...id };  // ✅ 类型正确推断为 { name: string; x: number; y: number; }
   ```
   避免使用 `Object.assign` 逐步赋值（会丢失类型信息）。

5. **逐步构建但保持类型安全的方法**  
   - 每次扩展后使用新变量，让 TypeScript 重新推断类型：  
     ```ts
     const pt0 = {};
     const pt1 = { ...pt0, x: 3 };
     const pt: Point = { ...pt1, y: 4 };  // 最终确认所有属性
     ```

6. **条件添加属性**  
   - 使用扩展运算符配合 `&&` 或三元表达式，添加的属性自动成为可选：  
     ```ts
     const president = { ...firstLast, ...(hasMiddle && { middle: 'S' }) };
     // 类型: { first: string; last: string; middle?: string }
     ```

### 条目总结（Things to Remember）

- 优先一次性构建对象，而不是分步赋值。  
- 使用多个对象和对象扩展语法（`{...a, ...b}`）以类型安全的方式添加属性。  
- 掌握如何条件性地向对象添加属性。

----
## Item 22 核心总结：理解类型收窄（Type Narrowing）

这一节的核心是：**TypeScript 能够根据条件判断（如 `if`、`switch`、`typeof`、`instanceof`、`in` 等）在代码块内将变量的类型从宽泛的联合类型收窄为更具体的类型**。这一过程称为“类型收窄”或“控制流分析”。利用好类型收窄，可以写出更简洁、安全的代码。

### 常见收窄方式

| 方式 | 示例 |
|------|------|
| `if` 判断（`null`/`undefined` 检查） | `if (elem) { elem.innerHTML }` → 排除 `null` |
| `throw` 或 `return` | 提前退出，后续代码类型收窄 |
| `instanceof` | `if (search instanceof RegExp)` → 收窄为 `RegExp` |
| 属性检查 `in` | `if ('isGoodForBaking' in fruit)` → 收窄为 `Apple` |
| 内置函数（`Array.isArray`） | 收窄为数组类型 |
| 可辨识联合（tagged union） | 根据 `type` 字段区分不同类型 |
| 用户定义类型守卫（`is`） | `function isInputElement(el): el is HTMLInputElement` |

### 重要陷阱

- **`typeof null === 'object'`**：不能用来排除 `null`，应先显式检查 `null`。  
- ** falsy 值检查 `if (!x)`**：`0`、`''`、`false` 也会进入分支，不会收窄到 `null/undefined`。  
- **回调内的收窄可能失效**：因为变量可能在回调执行前被修改。示例中 `setTimeout` 内访问 `obj.value` 时，类型已变回联合类型。  
- **`Map.has` + `Map.get`**：TypeScript 不理解两者的关联，应先调用 `get` 保存结果再判断是否为 `undefined`，或使用空值合并运算符 `??`。

### 条目标题中的关键建议

- 理解 TypeScript 如何根据条件和其他控制流收窄类型。  
- 使用可辨识联合和用户定义类型守卫来帮助类型收窄。  
- 考虑重构代码，让 TypeScript 能更容易地跟踪类型变化。

---

## Item 23 核心总结：保持别名使用的一致性

这一节的核心是：**对变量或属性创建别名（alias）时，如果不一致地使用别名，可能会导致 TypeScript 的类型收窄失效，从而产生类型错误**。保持一致的使用习惯，尤其是优先使用局部变量而非重复访问属性，可以帮助类型检查器更好地理解代码。

### 关键问题示例

```ts
const box = polygon.bbox;
if (polygon.bbox) {
  // ✅ polygon.bbox 类型已收窄为 BoundingBox
  // ❌ box 的类型仍然是 BoundingBox | undefined
  pt.x < box.x[0]  // 错误：box 可能为 undefined
}
```

**原因**：`polygon.bbox` 的检查只收窄了 `polygon.bbox` 本身的类型，并不会影响别名 `box` 的类型。两者是不同的引用。

### 解决方案

1. **一致地使用别名**  
   - 在条件判断中也使用 `box`，而不是 `polygon.bbox`：  
     ```ts
     const box = polygon.bbox;
     if (box) {
       // 现在 box 的类型已收窄
     }
     ```

2. **使用对象解构**  
   - 解构可以避免重复访问属性，并使类型收窄更自然：  
     ```ts
     const { bbox } = polygon;
     if (bbox) {
       const { x, y } = bbox;
       // ...
     }
     ```

### 其他注意事项

- **函数调用可能使属性收窄失效**  
  - 即使 `polygon.bbox` 在 `if` 块内已被收窄为 `BoundingBox`，调用 `expandABit(polygon)` 后，TypeScript 仍会保持其收窄类型（出于实用考虑），但实际运行时该属性可能已被修改。**对局部变量的信任度应高于属性**。

- **别名的运行时陷阱**  
  - 如果先解构 `bbox`，然后调用函数修改 `polygon.bbox`，原来的 `bbox` 变量不会更新，导致数据不一致。

- **不可变数据更安全**  
  - 对于对象和数组，使用 `readonly` 修饰符可以防止意外修改，从而避免此类问题（详见 Item 14）。

### 条目总结（Things to Remember）

- 别名会阻止 TypeScript 收窄类型。如果创建了别名，请**一致地使用它**。  
- 注意函数调用可能使属性的类型收窄失效。对于局部变量的收窄，信任度高于属性。

---

## Item 24 核心总结：理解上下文在类型推断中的作用

这一节的核心是：**TypeScript 的类型推断不仅取决于值本身，还取决于值出现的“上下文”（context）。** 当我们将一个值从使用它的上下文中提取出来（例如赋给一个变量），可能会丢失上下文信息，导致类型推断变得不够精确，从而引发类型错误。

### 关键示例与解决方案

| 场景 | 问题 | 解决方案 |
|------|------|----------|
| **字符串字面量** | `let language = 'JavaScript'` 被推断为 `string`，无法赋给 `Language` 联合类型 | 1. 添加类型注解：`let language: Language = 'JavaScript'`<br>2. 使用 `const`：`const language = 'JavaScript'`（推断为字面量 `"JavaScript"`） |
| **元组** | `const loc = [10, 20]` 被推断为 `number[]`，无法赋给 `[number, number]` | 1. 类型注解：`const loc: [number, number] = [10, 20]`<br>2. 修改函数签名为 `readonly [number, number]` 并使用 `as const` |
| **对象属性** | 对象中的 `language` 属性被推断为 `string`，无法匹配联合类型 | 类型注解、`as const` 或 `satisfies` 操作符 |
| **回调函数** | 将回调提取为常量后丢失参数类型推断 | 1. 内联回调<br>2. 给参数添加类型注解<br>3. 给整个函数表达式添加类型（如 `const fn: (a:number,b:number)=>void = (a,b)=>...`） |

### 重要原则

- TypeScript 在变量**首次引入时**推断其类型，而不是根据后续使用（避免“幽灵般的作用”）。  
- 将值从上下文中提取出来是**有代价的**：它可能使类型变宽。  
- **优先使用内联形式**，除非有充分的理由提取变量。  
- 如果必须提取，可以通过**类型注解**、**`const`**（对于不可变值）或 **`as const`** 来保留精确类型，但要注意 `as const` 可能将错误延迟到使用处才暴露。

### 条目总结（Things to Remember）

- 注意上下文在类型推断中的作用。  
- 如果提取变量后产生类型错误，尝试添加类型注解。  
- 如果变量确实是常量，可以使用 `as const`（但要小心错误位置）。  
- 在可行的情况下，优先内联值以减少对类型注解的需求。

---
## Item 25 核心总结：理解演化类型（Evolving Types）

这一节的核心是：**TypeScript 中的变量类型通常在声明时确定，但有一个例外：当变量初始化为 `[]`、`null` 或 `undefined` 时，其类型可以随着后续赋值而“演化”**。这是一种为了方便而设计的行为，可以减少不必要的类型注解，但也需要谨慎使用。

### 关键行为

1. **数组的演化**  
   ```ts
   const nums = [];     // 初始类型: any[]
   nums.push(1);        // 推入 number 后，类型演化为 number[]
   nums.push('a');      // 再推入 string，类型演化为 (string | number)[]
   ```
   TypeScript 会根据实际推入的元素类型逐步更新数组的类型。

2. **变量的演化**  
   ```ts
   let value;           // 初始类型: any
   if (Math.random()<0.5) value = /hello/;  // 演化为 RegExp
   else value = 12;                          // 分支中演化为 number
   // 最终 value 的类型为 number | RegExp
   ```

3. **`null` / `undefined` 初始值**  
   ```ts
   let value = null;    // 初始类型: any
   try {
     value = getNumber(); // 演化为 number
   } catch { ... }
   // 最终类型: number | null
   ```

### 与“窄化”的区别

- **窄化（narrowing）**：类型从宽变窄（如 `string | null` → `string`），是收缩。  
- **演化（evolving）**：类型从 `any` 或 `any[]` 逐步变成更具体的类型（如 `any[]` → `number[]`），是扩展。

### 注意事项

- **演化只发生在写入时**：如果在演化之前读取变量（如返回 `nums`），会触发隐式 `any` 错误。  
- **演化不会跨越函数调用**：将数组传给 `forEach` 并在回调中 `push`，TypeScript 无法追踪，会导致错误。  
- **演化不是危险的 `any`**：它不会像显式 `any` 那样污染整个代码，但仍然可能掩盖类型错误。

### 何时使用

- 适合快速编写原型或简单的数据收集逻辑，可以省去显式类型注解。  
- 对于重要或复杂的逻辑，**建议提供显式类型注解**（如 `const nums: number[] = []`），以获得更好的类型检查和错误定位。

### 条目总结（Things to Remember）

- TypeScript 的类型通常只收缩，但初始化为 `[]`、`null` 或 `undefined` 的变量类型**允许演化**。  
- 识别并理解这种构造，用它来减少类型注解。  
- 为了更好的错误检查，考虑使用显式类型注解替代演化类型。

----
## Item 26 核心总结：使用函数式结构和库帮助类型流动

这一节的核心是：**使用内置函数式方法（如 `map`、`flat`）或工具库（如 Lodash）可以显著改善 TypeScript 的类型推断，减少手动类型注解，让代码更简洁、更安全**。

### 关键示例对比

| 场景 | 命令式/手写循环 | 函数式 / Lodash |
|------|----------------|----------------|
| 解析 CSV | 使用 `forEach` 动态添加属性，需要手动注解 `Record<string, string>` | `_.zipObject(headers, rowStr.split(','))` 自动推断正确类型 |
| 扁平化数组 | 循环 + `concat`，需要显式声明 `let allPlayers: Player[] = []` | `Object.values(rosters).flat()` 自动推断为 `Player[]` |
| 分组并取每组最高薪球员 | 多个循环 + 手动分组 + 排序，需要多处类型注解 | `_(allPlayers).groupBy().mapValues(_.maxBy).values().sortBy().value()` 链式调用，类型始终正确 |

### 函数式方案的优势

1. **类型自动流动**：每个步骤的输入/输出类型都由库的类型声明保证，无需手动注解。  
2. **避免突变**：每次操作返回新值，有助于类型收窄（Item 19）。  
3. **更声明式**：代码更短、更易读，减少错误。  
4. **编辑器体验更好**：悬停查看链中任意一步，都能看到正确的中间类型。

### 注意事项

- 引入 Lodash 等库会增加依赖和学习成本，但在 TypeScript 项目中，类型安全带来的收益往往超过成本。  
- 对于简单的操作（如单层 `map`），原生方法已足够；对于复杂的数据转换，Lodash 的链式调用优势明显。  
- 非空断言（如 `_.maxBy(...)!`）仍可能偶尔需要，但比手写循环中的多处断言少得多。

### 条目总结（Things to Remember）

- 使用内置函数式结构（`map`、`flat`、`filter`、`reduce`）和工具库（Lodash）替代手写循环，以**改善类型流动、提高可读性、减少显式类型注解**。