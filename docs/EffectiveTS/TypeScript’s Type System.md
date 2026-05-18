感谢分享 **Item 6**。这一节的核心是：**充分利用编辑器的 TypeScript 语言服务（Language Service）来探索类型系统、理解类型推断、提升开发效率**。

### 关键要点总结：

1. **TypeScript 安装后提供两个可执行文件**  
   - `tsc`：编译器  
   - `tsserver`：语言服务后端，提供自动补全、悬停提示、导航、重构等功能

2. **编辑器的核心能力**  
   - **悬停查看类型**：了解变量、函数、对象的推断类型  
   - **检查函数返回值类型**：若与预期不符，可添加显式类型注解并排查  
   - **观察类型收窄（narrowing）**：在条件分支中查看变量类型的变化  
   - **查看泛型类型**：在链式调用中检查中间结果的类型（如 `Array<string>`）

3. **通过错误理解类型系统**  
   - 示例：`typeof null === 'object'` 导致类型收窄失效，需要先检查 `null`  
   - `document.getElementById` 可能返回 `null`，必须处理

4. **重构工具**  
   - **重命名符号**：智能重命名，只影响同一作用域的变量，并更新模块导入  
   - 其他：移动文件、将符号移到新文件等

5. **导航到类型声明**  
   - “Go to Definition” 可跳转到 `lib.dom.d.ts` 等内置声明文件  
   - 查看 `fetch`、`Request`、`RequestInit` 的类型定义，学习如何建模 API

### 条目总结（Things to Remember）：

- 使用支持 TypeScript 的编辑器，利用语言服务  
- 通过编辑器建立类型系统的工作直觉  
- 熟悉重构工具  
- 学会跳入类型声明文件，理解库的行为模型

---

**Item 7 的核心思想：将 TypeScript 的类型看作“值的集合”**。这是一个非常强大且基础的心智模型，能帮助你理解赋值兼容性、`extends`、联合/交叉类型等几乎所有类型系统行为。

### 关键结论总结：

1. **每个类型都是一个集合（称为该类型的“域”）**  
   - 例如：`number` 是所有数字的集合；`'A'` 是只包含字符串 `"A"` 的单元素集合；`never` 是空集；`unknown` 是全集。

2. **“可赋值性”（assignable）就是“子集关系”**  
   - `T1` 可赋值给 `T2` 当且仅当 `T1` 的集合是 `T2` 集合的子集。  
   - 因此 `'A'` 可赋值给 `string`，但 `string` 不可赋值给 `'A'`。

3. **联合类型（`|`）对应并集，交叉类型（`&`）对应交集**  
   - `A | B` 的域 = `A` 的域 ∪ `B` 的域  
   - `A & B` 的域 = `A` 的域 ∩ `B` 的域  
   - 例如 `Person & Lifespan` 包含同时拥有 `name`、`birth`、`death` 属性的对象（可能还有额外属性）。

4. **`extends` 也是子集关系**  
   - `interface Student extends Person` 意味着 `Student` 的域 ⊆ `Person` 的域。  
   - 在泛型约束 `K extends string` 中，`K` 必须是 `string` 的子集（如 `'a'`、`'a'|'b'`、`string` 本身）。

5. **类型是“开放的”**  
   - 一个值只要包含类型要求的属性（可能还有更多属性）就属于该类型的集合。  
   - 例如 `{x:3, y:4, z:5}` 仍然属于 `Vector2D` 的集合（因为含有 `x` 和 `y`）。

6. **`keyof` 在联合/交叉上的行为可以从集合角度推导**  
   - `keyof (A & B) = keyof A | keyof B`  
   - `keyof (A | B) = keyof A & keyof B`  
   - 理解这两个等式有助于深入掌握类型系统。

7. **两个类型如果集合相同，则它们是同一个类型**（但 `readonly` 等修饰符会影响“能做什么”，所以不完全等价）。

### 条目总结（Things to Remember）：

- 把类型看作值的集合（域），可以是有限或无限集合。  
- TypeScript 类型形成相交的集合（韦恩图），而非严格的继承层次。  
- 一个对象可以因为拥有要求的属性而属于某个类型，即使它有额外属性。  
- 类型操作作用于集合：`|` 是并集，`&` 是交集。  
- 将 `extends`、`assignable to`、`subtype of` 统一理解为“子集”。

----

感谢分享 **Item 8**。这一节的核心是：**TypeScript 中的符号（symbol）要么属于类型空间（type space），要么属于值空间（value space），两者完全独立，同一名称可能在不同空间中指代不同的事物**。理解这一点对于避免常见错误至关重要。

### 关键结论总结：

1. **两个空间彼此独立**  
   - 类型空间：`interface`、`type`、类型别名、类型注解等  
   - 值空间：`const`、`let`、函数实现、类实例等  
   - 例如 `interface Cylinder {}` 与 `const Cylinder = () => {}` 是两个完全无关的符号。

2. **`class` 和 `enum` 同时引入类型和值**  
   - 类型：类的实例形状  
   - 值：构造函数本身  
   - 因此 `instanceof Cylinder` 可以工作（因为 `Cylinder` 作为值存在）。

3. **`typeof` 在类型空间和值空间含义不同**  
   - 类型空间：返回值的 TypeScript 类型（如 `type T = typeof someValue`）  
   - 值空间：返回 JavaScript 运行时类型字符串（`"string"`, `"number"`, `"object"` 等）。

4. **`[]` 属性访问在类型空间中必须用字符串索引**  
   - `obj['field']` 与 `obj.field` 在值空间等价，但在类型空间中只能使用前者来获取属性的类型（如 `Person['first']`）。

5. **其他运算符/关键词在不同空间含义不同**  
   - `&`、`|`：值空间为位运算，类型空间为交叉/联合类型  
   - `const`：值空间声明变量，类型空间用于 `as const` 常量断言  
   - `extends`：值空间用于类继承，类型空间用于子类型约束  
   - `in`：值空间用于 `for...in` 循环，类型空间用于映射类型  
   - `!`：值空间为逻辑非，类型空间为非空断言。

6. **常见错误示例：在函数参数解构中混淆空间**  
   - 错误写法：`function email({to: Person, subject: string})` 试图用类型名称作为变量名  
   - 正确写法：`function email({to, subject}: {to: Person, subject: string})` 分离解构和类型注解。

### 条目总结（Things to Remember）：

- 学会在阅读 TypeScript 表达式时判断当前处于类型空间还是值空间。可使用 TypeScript playground 查看生成的 JS 来辅助判断（类型空间的内容会被擦除）。  
- 每个值都有静态类型，但该类型只能在类型空间访问。类型空间的结构（如 `type`、`interface`）在值空间不可用。  
- `class`、`enum` 等同时引入类型和值。  
- `typeof`、`this` 等运算符/关键词在两个空间中含义不同。

------

感谢分享 **Item 9**。这一节的核心是：**优先使用类型注解（type annotation）而非类型断言（type assertion），因为注解会进行类型检查，而断言会绕过检查，可能隐藏错误**。

### 关键结论总结：

1. **类型注解 vs 类型断言**  
   - `const alice: Person = { name: 'Alice' }`：注解，TypeScript 会验证值是否符合 `Person` 接口。  
   - `const bob = { name: 'Bob' } as Person`：断言，告诉 TypeScript “相信我，它就是 `Person`”，即使对象缺少属性或有额外属性也不会报错。  
   - **注解提供安全性，断言可能掩盖问题**。

2. **箭头函数中使用类型注解的推荐写法**  
   - 错误方式：`map(name => ({name} as Person))`（断言）  
   - 更好方式：`map((name): Person => ({name}))`（注解返回类型）  
   - 括号重要：`(name): Person` 表示参数 `name` 类型推断，返回类型为 `Person`；`(name: Person)` 则表示参数类型为 `Person`，返回类型推断，可能出错。

3. **何时应该使用类型断言**  
   - 当你知道比 TypeScript 更多的信息，例如 DOM 元素的具体类型：  
     `e.currentTarget as HTMLButtonElement`  
   - 使用断言时应添加注释说明为何安全。

4. **非空断言 `!`**  
   - `document.getElementById('foo')!` 断言值不为 `null` 或 `undefined`。  
   - 与可选链 `?.` 不同：`?.` 是运行时安全访问，`!` 是编译时断言，若运行时为 `null` 会抛出异常。

5. **类型断言的限制**  
   - 只能在两个有非空交集（non-empty intersection）的类型之间转换。  
   - 若想强制转换不相关的类型（如 `HTMLElement` 到 `Person`），需通过 `unknown` 中转：`as unknown as Person`。这明确表示你在做危险操作。

6. **`as const` 是安全的**  
   - `as const` 不是普通的类型断言，而是“常量上下文”，会使类型推断更精确（如将 `[1, 2]` 推断为 `readonly [1, 2]` 而非 `number[]`）。

### 条目总结（Things to Remember）：

- 优先使用类型注解（`: Type`）而非类型断言（`as Type`）。  
- 掌握箭头函数返回类型注解的写法。  
- 仅在你知道 TypeScript 不知道的信息时才使用类型断言和非空断言，并附上注释说明。  
- `as const` 是安全的，可以放心使用。

---

感谢分享 **Item 10**。这一节的核心是：**TypeScript 中应使用原始类型（primitive types）的写法（`string`、`number`、`boolean`、`symbol`、`bigint`），而不是它们的大写对象包装器类型（`String`、`Number`、`Boolean`、`Symbol`、`BigInt`）**。后者不仅容易引起混淆，还会导致类型不兼容和运行时意外。

### 关键结论总结：

1. **JavaScript 的原始类型与对象包装器**  
   - 原始值（string, number, boolean, null, undefined, symbol, bigint）是不可变的，本身没有方法。  
   - 当调用 `'primitive'.charAt(3)` 时，JavaScript 会临时将其包装成 `String` 对象，调用方法后丢弃该对象。  
   - 这种隐式包装会导致奇怪现象：给原始值添加属性会“消失”，因为属性被加到了临时对象上。

2. **TypeScript 区分原始类型与对象包装器类型**  
   - 小写：`string`, `number`, `boolean`, `symbol`, `bigint`（原始类型）  
   - 大写：`String`, `Number`, `Boolean`, `Symbol`, `BigInt`（对象包装器类型）  
   - **原始类型可赋值给包装器类型，反之不行**。  
   - 例如：`let s: string = "hello"; let str: String = s;` ✅  
     `let str: String = new String("hello"); let s: string = str;` ❌

3. **为什么应避免使用大写包装器类型**  
   - 会导致类型不兼容错误（如将 `String` 传给期望 `string` 的函数）。  
   - 即使使用大写注解（如 `const s: String = "primitive"`），运行时值仍是原始值，但注解误导了读者。  
   - 官方类型声明和几乎所有库都使用小写原始类型。

4. **例外情况**  
   - 调用 `Symbol('sym')` 和 `BigInt(1234)`（不带 `new`）是安全的，它们返回原始类型 `symbol` 和 `bigint`。  
   - 可以直接用 `123n` 创建 `bigint` 原始值。

5. **工具链支持**  
   - `typescript-eslint` 的 `ban-types` 规则默认禁止使用这些大写包装器类型，推荐使用小写原始类型。

### 条目总结（Things to Remember）：

- **避免使用 TypeScript 的对象包装器类型**，优先使用原始类型：  
  `string` 代替 `String`，`number` 代替 `Number`，`boolean` 代替 `Boolean`，`symbol` 代替 `Symbol`，`bigint` 代替 `BigInt`。  
- 理解对象包装器类型的作用（为原始值提供方法），但不要直接实例化或使用它们。  
- `Symbol` 和 `BigInt` 作为函数调用（不带 `new`）是安全的。

---

感谢分享 **Item 11**。这一节的核心是：**区分“多余属性检查”（excess property checking）与常规的结构类型兼容性检查**。前者只发生在直接将对象字面量传给有明确类型的位置时，用于捕捉拼写错误等意外；后者是 TypeScript 结构类型系统的常规行为。

### 关键结论总结：

1. **多余属性检查是什么**  
   - 当你将**对象字面量**直接赋值给一个已知类型的变量、作为函数参数或返回值时，TypeScript 会检查该字面量是否包含目标类型中未声明的属性。  
   - 示例中 `const r: Room = { numDoors, ceilingHeightFt, elephant }` 报错，因为 `elephant` 不是 `Room` 的属性。

2. **与常规类型兼容性的区别**  
   - 常规结构类型允许额外属性（只要包含所需属性即可）。  
   - 通过中间变量赋值可以绕过多余属性检查：`const obj = { numDoors, ceilingHeightFt, elephant }; const r: Room = obj;` ✅  
   - 原因：`obj` 不是对象字面量，不触发该检查。

3. **多余属性检查的目的**  
   - 捕获拼写错误（如 `darkmode` 而不是 `darkMode`）或无意中传递了不该有的属性。  
   - 纯结构类型系统无法捕捉这类错误，因为 `{ title, darkmode }` 结构上兼容 `{ title, darkMode? }`。

4. **如何禁用多余属性检查**  
   - 使用类型断言：`{ darkmode } as Options`  
   - 使用索引签名：`interface Options { darkMode?: boolean; [other: string]: unknown }`  
   - 但通常建议保留此检查（优先使用类型注解而非断言）。

5. **弱类型（weak types）**  
   - 仅包含可选属性的接口称为“弱类型”。  
   - 对于弱类型，TypeScript 要求赋值的对象至少有一个共同的属性，否则报错。  
   - 示例：`LineChartOptions` 只有可选属性，赋值 `{ logScale }` 会因没有共同属性而报错。  
   - 这与多余属性检查不同：弱类型检查在所有赋值中都会发生，即使使用中间变量也无法绕过。

### 条目总结（Things to Remember）：

- 将对象字面量赋值给已知类型变量或作为函数参数时，会触发**多余属性检查**。  
- 多余属性检查能有效发现错误，但它与常规的结构类型兼容性检查是不同的过程。混淆两者会阻碍你理解 TypeScript 的类型兼容性模型。记住：TypeScript 类型不是“封闭”的（Item 4）。  
- 注意多余属性检查的局限性：使用中间变量会绕过它。  
- “弱类型”是指只包含可选属性的对象类型。对于这些类型，兼容性检查要求至少有一个匹配的属性。

----

感谢分享 **Item 12**。这一节的核心是：**在可能的情况下，将类型注解应用于整个函数表达式，而不是分别注解参数和返回值**。这种做法可以减少重复、提高类型安全性，并利用 TypeScript 的上下文推断。

### 关键结论总结：

1. **函数表达式 vs 函数声明**  
   - 函数声明：`function add(a: number, b: number): number { ... }`  
   - 函数表达式：`const add: BinaryFn = (a, b) => a + b`  
   - 优势：可以一次性为整个函数指定类型，参数和返回值类型自动推断。

2. **减少重复**  
   - 多个具有相同签名的函数可以共享一个函数类型别名：  
     ```ts
     type BinaryFn = (a: number, b: number) => number;
     const add: BinaryFn = (a, b) => a + b;
     const sub: BinaryFn = (a, b) => a - b;
     ```
   - 类型注解集中在类型定义上，实现更清晰。

3. **匹配现有函数的签名**  
   - 使用 `typeof fn` 确保新函数与原函数签名完全一致。  
   - 示例：`const checkedFetch: typeof fetch = async (input, init) => { ... }`  
   - 好处：若实现中返回类型错误（如返回 `Error` 而非抛出），TypeScript 会直接报错。

4. **修改返回类型但保留参数类型**  
   - 使用 `Parameters<typeof fn>` 和 rest 参数：  
     ```ts
     async function fetchANumber(...args: Parameters<typeof fetch>): Promise<number> {
       const response = await checkedFetch(...args);
       // ...
     }
     ```
   - 编辑器会显示正确的参数名称（`input`, `init`），而不是 `args`。

5. **适用场景**  
   - 多个函数具有相同或相关的类型签名时。  
   - 需要确保一个函数与另一个函数签名完全一致时。  
   - 对于独立的、签名独特的函数，传统的函数声明完全可以，不必过度抽象。

6. **库作者**  
   - 应为常见回调提供类型（如 React 的 `MouseEventHandler`），方便用户直接应用于整个函数表达式。

### 条目总结（Things to Remember）：

- 考虑将类型注解应用于整个函数表达式，而不是分别注解参数和返回值。  
- 如果反复编写相同的类型签名，请将其抽取为一个函数类型或查找已有的类型。  
- 作为库作者，请为常见的回调提供类型。  
- 使用 `typeof fn` 匹配另一个函数的签名，或使用 `Parameters` 和 rest 参数来改变返回类型。

----

## Item 13 核心总结：`type` 与 `interface` 的异同与选择

这一节详细对比了 TypeScript 中定义对象类型的两种方式：**类型别名（`type`）** 和 **接口（`interface`）**。虽然大部分情况下它们可以互换使用，但了解其细微差别有助于写出更清晰、更一致的代码。

### 相似点（大部分场景可互换）

- 都可以描述对象形状、索引签名、函数类型、泛型。
- 类都可以实现（`implements`）两者。
- 都可以递归定义。

### 主要差异

| 特性 | `interface` | `type` |
|------|-------------|--------|
| **合并声明** | ✅ 支持（声明合并） | ❌ 不支持 |
| **联合类型** | ❌ 无法表示 `A \| B` | ✅ 原生支持 |
| **交叉类型** | 通过 `extends` 可部分实现，但 `&` 更灵活 | ✅ 支持 `&` |
| **元组/数组类型** | 不自然（需要手动写索引签名） | ✅ 简洁（如 `[number, number]`） |
| **映射/条件类型** | ❌ 无法直接定义 | ✅ 支持（高级类型编程） |
| **错误检查** | 扩展不兼容属性时会报错 | 使用 `&` 交叉不兼容属性时不报错，但产生 `never` 类型 |
| **显示名称** | 错误消息和 `.d.ts` 中尽量保留名称 | 可能被内联展开，名称消失 |
| **声明文件（.d.ts）** | 推荐使用，支持合并 | 内联可能导致类型重复 |

### 关键点详解

1. **声明合并（Declaration Merging）**  
   只有 `interface` 可以多次定义同一名称并自动合并。TypeScript 标准库利用此特性为不同 ES 版本添加 `Array` 方法（如 `find`）。在普通代码中很少用到，但在编写类型声明文件（`.d.ts`）时很有用。

2. **联合类型与交叉类型**  
   - `type` 可以直接定义联合：`type AorB = 'a' | 'b'`。  
   - 无法用 `interface` 表示联合类型。  
   - 交叉类型 `&` 在 `type` 中更灵活；`interface extends` 只能扩展对象类型，且会检查属性兼容性。

3. **函数与元组**  
   - 函数类型用 `type` 更简洁：`type Fn = (x: number) => string`。  
   - 元组类型只能用 `type`：`type Pair = [number, number]`。

4. **显示与内联**  
   当 `type` 别名作用域有限（如在函数内部定义）并导出时，生成的 `.d.ts` 会内联展开该类型，导致名称丢失。而 `interface` 会尝试保留名称，但若未导出则会报错。**建议将需要暴露的类型放在顶层并导出**。

### 选择建议（官方指南）

- **没有绝对对错**，根据团队风格保持一致即可。  
- **启发式规则**：能用 `interface` 时优先用 `interface`，直到你需要 `type` 特有的特性（联合、元组、映射、条件类型等）。  
- 对于**对象类型**，新项目推荐使用 `interface`（错误消息更清晰，扩展检查更严格）。  
- 对于**函数类型、元组、联合类型、复杂类型操作**，使用 `type`。

### 注意事项

- 不要使用 `I` 前缀（如 `IUser`），这在 TypeScript 社区已被视为不良风格。  
- 可使用 ESLint 规则 `consistent-type-definitions` 强制统一风格（默认偏好 `interface`）。

**总结：理解两者差异，根据需要选择。大多数对象类型用 `interface`，需要联合/元组/高级类型操作时用 `type`。**

---

## Item 14 核心总结：使用 `readonly` 避免与修改相关的错误

这一节的核心是：**TypeScript 的 `readonly` 修饰符可以防止意外的修改（mutation），帮助捕获由可变性引发的难以追踪的错误**。虽然 JavaScript 默认可变，但 `readonly` 提供了一种在类型层面表达“只读”意图并强制执行的方式。

### 关键结论总结

1. **`readonly` 用于属性**  
   - 标记对象属性为 `readonly` 后，无法重新赋值，但对象本身可能仍然可变（浅层只读）。  
   - 例如 `interface PartlyMutableName { readonly first: string; last: string; }`，`first` 不可重新赋值，`last` 可以。

2. **`Readonly<T>` 工具类型**  
   - 将类型 `T` 的所有属性变为 `readonly`。  
   - 如果函数不修改参数对象，应使用 `Readonly<T>` 作为参数类型，以明确契约并让 TypeScript 检查函数体内是否意外修改。

3. **浅层只读（shallow）**  
   - `readonly` 和 `Readonly<T>` 都是浅层的：只影响直接属性，不影响嵌套对象的内部属性。  
   - 示例：`Readonly<{ inner: { x: number } }>` 只保证 `inner` 引用不可变，但 `inner.x` 仍可修改。  
   - 深层只读需要自定义工具类型或第三方库（如 `ts-essentials` 的 `DeepReadonly`）。

4. **`Readonly<Date>` 不影响方法**  
   - `readonly` 只阻止属性赋值，不会删除修改对象的方法（如 `date.setFullYear()`）。  
   - 标准库中通过分离 `Array`（可变）和 `ReadonlyArray`（不可变）来解决此问题：`ReadonlyArray` 省略了 `pop`、`push` 等修改方法，并标记索引签名为 `readonly`。

5. **数组的 `readonly T[]` 语法**  
   - `readonly number[]` 是 `ReadonlyArray<number>` 的简写。  
   - `number[]` 是 `readonly number[]` 的子类型（因为更强大），所以可变数组可赋值给只读数组，但反过来不行。  
   - 这保证了传递只读视图不会意外获得修改能力。

6. **示例改进**  
   - 原示例中 `arraySum` 通过 `pop` 清空了数组，导致 `printTriangles` 输出错误。  
   - 通过将 `arraySum` 参数改为 `readonly number[]`，TypeScript 会报错不允许使用 `pop`。  
   - 修复后 `arraySum` 使用 `for...of` 遍历求和，不再修改原数组，问题解决。

7. **`readonly` 的传染性与优势**  
   - 一旦函数参数标记为 `readonly`，调用链下游的函数也可能需要标记，这是好事（契约更清晰，类型安全性提升）。  
   - 若需调用未标记 `readonly` 的第三方函数，可改用类型断言或补丁（Item 71）。

### 条目总结（Things to Remember）

- 如果你的函数不修改参数，**将参数声明为 `readonly`（数组）或 `Readonly`（对象类型）**。这使函数契约更清晰，并防止实现中的意外修改。  
- 理解 `readonly` 和 `Readonly` 都是浅层的，且 `Readonly` 只影响属性，不影响方法。  
- 使用 `readonly` 来预防修改错误，并在代码中发现执行修改的位置。  
- 区分 `const` 与 `readonly`：**`const` 禁止重新赋值，`readonly` 禁止修改**。

----

## Item 15 核心总结：使用类型操作和泛型避免重复

这一节的核心是：**DRY（Don’t Repeat Yourself）原则不仅适用于代码逻辑，同样适用于类型定义**。TypeScript 提供了丰富的类型操作和泛型工具，帮助你消除类型层面的重复，提高可维护性。

### 常见的重复消除技巧

| 场景 | 重复写法 | 改进方式 |
|------|----------|----------|
| 多个函数共享相同签名 | 每个函数重复写 `(url: string, opts: Options) => Promise<Response>` | 抽取为类型别名 `type HTTPFunction = ...` |
| 接口有相同字段 | `Person` 和 `PersonWithBirthDate` 重复写 `firstName, lastName` | 使用 `extends`：`interface PersonWithBirthDate extends Person` |
| 从大类型中选取部分字段 | 手动列出 `userId: State['userId']` 等 | 使用映射类型 + `Pick<State, 'userId' \| 'pageTitle'>` |
| 将类型的所有属性变为可选 | 手动写 `width?: number; height?: number; ...` | 使用 `Partial<Options>` |
| 获取联合类型的某个字段的联合 | 手动写 `'save' \| 'load'` | 使用 `Action['type']`（索引访问） |
| 从值推导类型 | 手动写与初始化对象相同的接口 | 使用 `typeof INIT_OPTIONS` |
| 从函数返回值推导类型 | 手动写返回类型 | 使用 `ReturnType<typeof getUserInfo>` |

### 关键类型工具速览

- **`keyof T`**：获取类型 `T` 的所有键的联合。
- **`T[K]`**：索引访问类型，获取 `T` 中键 `K` 对应的值类型。
- **`Pick<T, K>`**：从 `T` 中挑选一组键 `K` 构成新类型。
- **`Partial<T>`**：将 `T` 的所有属性变为可选。
- **`ReturnType<T>`**：获取函数类型 `T` 的返回值类型。
- **`typeof value`**：从值推断出类型（用于类型上下文）。
- **映射类型**：`{ [K in keyof T]: T[K] }`，可配合 `as` 子句重命名键。

### 同态映射类型（Homomorphic Mapped Types）

- 当映射形式为 `{ [K in keyof T]: ... }` 时，TypeScript 会保留原属性的 `readonly`、可选修饰符以及 TSDoc 注释。
- 例如 `Pick<T, K>` 和 `Partial<T>` 都是同态的，而手动写 `{ [K in 'name']: T[K] }` 则不会保留修饰符。

### 注意事项

- **不要过度抽象**：如果两个类型只是偶然有相同结构的字段（如 `Product` 和 `Customer` 都有 `id` 和 `name`），但语义不同，不应强行抽取基类型。错误的抽象比重复更糟糕。
- **优先定义类型，再从值推导**：通常应先定义类型，然后声明值符合该类型，这样更清晰。只有在值确实是唯一真相来源（如配置对象、API 响应）时才使用 `typeof` 从值推导类型。

### 条目总结（Things to Remember）

- DRY 原则同样适用于类型系统。
- 使用 `extends`、`keyof`、`typeof`、索引访问、映射类型等工具消除重复。
- 泛型类型相当于类型层面的函数，使用 `Pick`、`Partial`、`ReturnType` 等内置泛型。
- 避免过度抽象：确保共享的属性和类型在语义上是相同的。

----
## Item 16 核心总结：优先使用比索引签名更精确的类型

这一节的核心是：**索引签名（index signature）虽然灵活，但会牺牲类型安全性和编辑器支持，应尽可能使用更精确的替代方案**。

### 索引签名的缺点

- 允许任意键（包括拼写错误），`{}` 也是合法值。  
- 无法为不同键指定不同类型。  
- 语言服务（自动补全、跳转定义）失效。

### 替代方案对比

| 场景 | 索引签名（不推荐） | 精确方案（推荐） |
|------|-------------------|-----------------|
| 已知固定字段 | `{ [prop: string]: string }` | `interface Rocket { name: string; variant: string; thrust_kN: number }` |
| 字段集有限但未知哪些出现 | `{ [col: string]: number }` | 可选字段 `{ a: number; b?: number }` 或联合类型 `{ a: number } \| { a: number; b: number }` |
| 动态列名数据（CSV） | `{ [col: string]: string }` | 使用 `Map<string, string>` 并在解析时验证转换为具体类型 |
| 键空间是字符串子集 | `{ [k: string]: number }` | `Record<'x' \| 'y' \| 'z', number>` |
| 允许额外属性（如 `data-*`） | 索引签名 + 模板字面量 | `{ [key: `data-${string}`]: unknown }`（Item 54） |

### 关键建议

1. **能用接口就不用索引签名**  
   固定字段明确写出，获得类型检查和编辑器支持。

2. **动态数据优先用 `Map`**  
   `Map<string, string>` 可以明确表示“键未知但值为字符串”，且避免原型链问题。通过解析和验证将其转换为精确类型。

3. **有限可能的键集合用 `Record` 或映射类型**  
   `Record<'x'|'y'|'z', number>` 比 `{ [k: string]: number }` 精确得多。

4. **需要允许额外属性但又想保留已知字段检查**  
   添加索引签名 `[otherProps: string]: unknown` 可禁用多余属性检查，同时保持已知字段的类型安全。

### 条目总结（Things to Remember）

- 理解索引签名的缺点：类似 `any`，会侵蚀类型安全并削弱语言服务。  
- 尽可能使用更精确的类型：接口、`Map`、`Record`、映射类型，或约束键空间的索引签名。

----
## Item 17 核心总结：避免数值索引签名

这一节的核心是：**在 JavaScript 中，对象的键只能是字符串或 symbol，数值键会被转换为字符串。TypeScript 中的数值索引签名（`[n: number]: T`）是一个“虚构”特性，用于帮助捕获错误，但不应在自定义类型中使用**。

### 关键要点

1. **JavaScript 的键始终是字符串**  
   - 数组的 `[0]` 访问本质上是 `['0']`。  
   - `Object.keys(array)` 返回字符串数组（如 `['0', '1', '2']`）。

2. **TypeScript 的数值索引签名仅用于标准数组/元组类型**  
   - `lib.es5.d.ts` 中 `Array<T>` 定义了 `[n: number]: T`，这是为了方便使用并捕获类型错误（如用 `inputEl.value` 作为索引时会报错）。  
   - **不要在自定义类型中写数值索引签名**，它会误导读者认为 JavaScript 真的有数值键。

3. **替代方案**  
   - 需要按数字索引访问 → 使用 `Array<T>` 或元组 `[T, U]`。  
   - 需要类数组结构（如 `NodeList`） → 使用 `ArrayLike<T>`。  
   - 只需要可迭代 → 使用 `Iterable<T>`。

4. **`noUncheckedIndexedAccess` 选项**  
   - 开启后，数组/元组的索引访问会认为结果可能是 `undefined`，提高安全性（详见 Item 48）。

### 条目总结（Things to Remember）

- 理解数组是对象，其键是字符串而非数字。数值索引签名是 TypeScript 为捕获错误而添加的虚构特性。  
- 优先使用 `Array`、元组、`ArrayLike` 或 `Iterable` 类型，而不是自己写数值索引签名。