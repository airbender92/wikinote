## Item 48 详细讲解：避免可靠性陷阱（Soundness Traps）

这一节的核心是：**TypeScript 的类型系统并不是“可靠”的（not sound）——静态类型与运行时实际值之间可能出现偏差，导致代码通过类型检查却在运行时崩溃。** 但是，这不意味着 TypeScript 是糟糕的语言；相反，它是在**表达能力**、**便利性**和**可靠性**之间做了权衡。理解这些不可靠性的来源，可以帮助你避开常见陷阱，写出更健壮的代码。

---

### 1. 什么是“可靠性”（Soundness）？

一个类型系统是**可靠的**，如果程序中的每个符号的**静态类型**都保证与它的**运行时实际类型**兼容。换言之，运行时的实际值一定属于静态类型的值域（参见 Item 7 的“集合”视角）。

**可靠例子**：

```ts
const x = Math.random();  // 静态类型: number，运行时一定是 number ✅
```

**不可靠例子**：

```ts
const xs = [0, 1, 2];     // 静态类型: number[]
const x = xs[3];          // 静态类型: number，运行时却是 undefined ❌
x.toFixed(1);             // 运行时崩溃
```

这里 `x` 的静态类型是 `number`，但实际是 `undefined`，这就是不可靠。TypeScript 故意不追求完全可靠，因为在可靠性和方便性之间需要权衡。例如，如果对所有数组访问都做边界检查，会带来大量噪音，降低开发效率。

---

### 2. 常见的可靠性陷阱及应对方法

#### 2.1 `any` 类型

`any` 可以赋值给任何类型，也可以接收任何类型，它完全绕过了类型检查。

```ts
function logNumber(x: number) { console.log(x.toFixed(1)); }
const num: any = "forty two";
logNumber(num);  // 类型检查通过，运行时抛出错误
```

**解决方案**：  
- 尽量不使用 `any`。  
- 必须使用时，限制其作用域（Item 43）。  
- 优先使用 `unknown`（Item 46）。  
- 对于 `JSON.parse` 等返回 `any` 的内置函数，可以通过声明合并（Item 71）修改其返回类型为 `unknown`。

#### 2.2 类型断言（Type Assertion）

`as T` 告诉 TypeScript “相信我，它就是 `T` 类型”，但实际可能不是。

```ts
const hour = new Date().getHours() || null;  // number | null
logNumber(hour as number);  // 断言为 number，但运行时可能为 null
```

**解决方案**：  
- 尽量用条件判断代替断言。  
- 使用类型收窄（narrowing）让 TypeScript 自动推断。  
- 如果必须断言，确保有充分的运行时验证（Item 74）。

#### 2.3 对象与数组的越界访问

```ts
const xs = [1, 2, 3];
const x = xs[3];   // 推断为 number，实际 undefined
```

**为什么允许？**  
TypeScript 无法静态确定索引是否有效，允许这种访问是出于便利性。

**解决方案**：  
- 启用 `noUncheckedIndexedAccess` 编译选项（但会导致许多本来安全的访问也被标记为可能 `undefined`）。  
- 或者显式声明类型包含 `undefined`：`const xs: (number | undefined)[] = [1,2,3];`。  
- 尽量使用 `for...of`、`.map()` 等不会越界的方式。

#### 2.4 不精确的类型定义（Inaccurate Type Definitions）

第三方库的 `.d.ts` 文件可能不准确，比如曾经 `@types/react` 中的 `React.FC` 允许 `children` 即使组件不接受它。这是社区类型定义中的人为错误。

**解决方案**：  
- 提交修复到 DefinitelyTyped。  
- 临时通过声明合并（augmentation）修正。  
- 最后手段是使用类型断言。

另外，某些函数（如 `String.prototype.replace`）的参数类型非常复杂，无法完美建模，导致回调参数类型为 `any`。这时只能自己小心处理。

#### 2.5 类层次结构中的双变性（Bivariance）

**背景**：函数类型的子类型关系：  
- 返回值类型是**协变**（covariant）：子类型返回值必须是父类型返回值的子类型。  
- 参数类型是**逆变**（contravariant）：子类型参数必须是父类型参数的**父类型**（即参数类型可以更宽泛）。

但在 TypeScript 的类中，方法参数被视为**双变**（bivariant）——父类和子类的方法参数只要有一方能赋值给另一方即可。这会导致不安全：

```ts
class Parent { foo(x: number | string) {} }
class Child extends Parent { foo(x: number) {} }  // 允许，但 unsafe
const p: Parent = new Child();
p.foo("string");  // 类型检查通过，但 Child.foo 实际只接受 number，运行时崩溃
```

**解决方案**：  
- 启用 `strictFunctionTypes`（它会使独立函数参数变为逆变，但对类方法仍然双变？实际上 `strictFunctionTypes` 对方法无效，这是设计原因）。  
- **最佳实践**：子类重写方法时，应保持与父类完全相同的参数类型。  
- 修改父类方法签名后，务必检查所有子类。

#### 2.6 对象/数组的可变性导致的不可靠性

```ts
function addFoxOrHen(animals: Animal[]) {
  animals.push(Math.random() > 0.5 ? new Fox() : new Hen());
}
const henhouse: Hen[] = [new Hen()];
addFoxOrHen(henhouse);  // 悄悄混入了 Fox 或 Hen
```

这里 `Hen[]` 被当作 `Animal[]` 传入函数，函数修改了数组，导致类型安全被破坏。

**解决方案**：  
- 不要让函数修改传入的参数（使用 `readonly` 修饰符）。  
- 如果必须修改，返回新数组而不是修改原数组。  
- 或改写为返回新值而不是修改参数。

#### 2.7 函数调用不使类型细化失效

TypeScript 的收窄（refinement）在 `if` 分支内有效，但调用一个函数后，收窄不会被自动撤销，即使该函数可能修改对象。

```ts
function processFact(fact: FunFact, processor: (fact: FunFact) => void) {
  if (fact.author) {
    processor(fact);          // 可能删除 fact.author
    console.log(fact.author.blink());  // 仍认为 author 是 string，实际可能已 undefined
  }
}
```

**解决方案**：  
- 不要在回调中修改参数。  
- 如果必须修改，将对象标记为 `Readonly<T>` 来防止修改。  
- 或者将需要保留的字段提前取出（局部变量）。

#### 2.8 可选属性与结构类型的组合

由于 TypeScript 类型是开放的（可以有额外属性），将一个具有 `age: string` 的对象赋给 `Person`（没有 age），再赋给 `PossiblyAgedPerson`（age 可选），就可能造成可选属性被赋值为字符串而不是数字。

```ts
interface Person { name: string; }
interface PossiblyAgedPerson extends Person { age?: number; }
const p1 = { name: "Serena", age: "42 years" };
const p2: Person = p1;                     // 允许，因为额外属性
const p3: PossiblyAgedPerson = p2;         // 允许，但 p3.age 是 string | undefined
p3.age?.toFixed(1);                        // 运行时错误（字符串没有 toFixed）
```

**解决方案**：  
- 尽量使用具体属性名避免冲突（如 `ageYears` 和 `ageFormatted`）。  
- 避免让一个可选属性与一个不兼容的实际类型通过多次赋值传播。  
- 启用 `strictNullChecks` 可以捕获部分此类问题。

---

### 3. 总结：如何与不可靠性共存

- **接受权衡**：TypeScript 的设计目标是方便表达 JavaScript 模式，而不是追求完美可靠性。  
- **利用编译选项**：`strictNullChecks` 和 `noUncheckedIndexedAccess` 可以提高可靠性，但会牺牲一些便利性。  
- **编写防御性代码**：  
  - 避免使用 `any` 和类型断言。  
  - 不要修改函数参数；使用 `readonly`。  
  - 在边界处进行运行时验证（Item 74）。  
- **保持警惕**：了解上述常见陷阱，在代码审查时特别注意。

最终，TypeScript 仍然是日常开发中极其强大和高效的工具。理解它的局限性，而不是盲目信任或指责，才能写出更健壮的应用。


---

你问的这个问题触及了 TypeScript 一个非常微妙且容易出错的点——**可选属性与结构类型系统的交互，以及静态类型与运行时值的不一致**。

先直接回答：**为什么允许 `const p3: PossiblyAgedPerson = p2;`？**  

因为 TypeScript 的**静态类型检查**只看变量的**声明类型**，而不是它的**实际运行时值**。

- `p2` 的声明类型是 `Person`（只有 `name: string`）。  
- `PossiblyAgedPerson` 的类型是 `{ name: string; age?: number }`（`age` 可选，即可以是 `undefined` 或 `number`）。  
- 在类型系统中，一个没有 `age` 属性的对象（如 `Person`）是兼容于 `{ name: string; age?: number }` 的，因为 `age` 是可选的，可以缺失。  
- 所以 `p3 = p2` 在**静态类型层面**是合法的——TypeScript 只看到“`p2` 这个变量声明的类型是 `Person`，它没有 `age`，因此赋值给 `PossiblyAgedPerson` 时 `age` 视为 `undefined`，符合可选条件”。

**但是**，`p2` 在运行时实际持有的对象是 `{ name: "Serena", age: "42 years" }`，这个对象是从 `p1` 赋值过来的，而 `p1` 是有 `age: string` 的。由于结构类型允许额外属性，`p1` 可以被赋值给 `Person`，这个赋值是安全的（因为 `Person` 只要求 `name` 存在）。于是 `p2` 的静态类型与运行时值脱节了。

所以当你再把 `p2` 赋值给 `p3` 时，静态类型检查通过了（认为 `age` 不存在或 `undefined`），但运行时值却带有一个**字符串**的 `age`。这就导致了不可靠性：`p3.age` 被 TypeScript 认为是 `number | undefined`，实际上它是 `string`，后续调用 `toFixed()` 就会崩溃。

---

### 更详细的解释：可选属性的兼容性规则

TypeScript 中，类型 `A` 可赋值给类型 `B` 的条件之一是：**`B` 中的每个属性，在 `A` 中必须有一个兼容的属性（或者 `A` 中该属性可以缺失，如果 `B` 中它是可选的）**。

对于 `Person`（无 `age`）和 `PossiblyAgedPerson`（`age?`）：
- `name`：`Person` 有 `string`，`PossiblyAgedPerson` 也有 `string` ✅
- `age`：`PossiblyAgedPerson` 中 `age` 是可选，因此 `Person` 中**可以没有 `age`** ✅

所以赋值被允许。

---

### 这种设计为什么存在？

TypeScript 的这种行为是为了保持**结构类型的灵活性和向后兼容性**。如果你有一个函数期望 `{ name: string; age?: number }`，你希望可以传入一个只有 `name` 的对象（表示年龄未知）。这很合理。问题出在：我们通过中间变量 `p2` 偷偷带上了一个不符合预期的 `age` 属性。

本质上，这是**静态类型无法追踪对象在运行时被附加额外属性**的一个局限。TypeScript 的类型系统是“开放”的，一旦你赋值给一个更宽的类型，那些额外属性并没有被擦除，只是被静态类型忽略了。后续再赋值给一个更精确的类型时，如果那个类型有可选属性，就会悄悄把实际存在的属性带进来，而不检查它的类型。

---

### 如何避免这种陷阱？

1. **避免滥用可选属性**：如果 `age` 总是应该存在但可能是 `number`，不要把它做成可选；如果需要表示“无年龄”，使用 `number | null` 或 `number | undefined` 并要求显式赋值。
2. **不要将具有额外属性的对象赋值给一个更窄的类型，然后再赋值给另一个依赖该属性的类型**。尽量保持类型一致，或者使用显式转换（例如 `as PossiblyAgedPerson` 加上运行时验证）。
3. **使用 `strictNullChecks` 和 `noUncheckedIndexedAccess`**，并考虑使用 `exactOptionalPropertyTypes`（TypeScript 4.4+ 的一个严格标志），它会让可选属性不允许被赋值 `undefined` 之外的值（但也不能解决这里的字符串问题）。
4. **在关键边界处进行运行时验证**（例如使用 Zod 或自定义类型守卫），确保对象形状真正符合预期。

在你的例子中，更安全的设计是：

```ts
interface Person {
  name: string;
  age?: number;   // 直接让 Person 也包含可选 age，类型统一
}
```

或者如果两个类型在不同场景下使用，不要通过 `Person` 作为中转站，而是直接构造 `PossiblyAgedPerson` 对象。

---

### 总结

允许 `p3 = p2` 的原因是 **TypeScript 只看静态类型，而静态类型中 `Person` 没有 `age`，所以赋值给 `PossiblyAgedPerson` 时 `age` 被视为缺失（`undefined`），这是合法的**。但运行时实际值却携带了一个字符串 `age`，导致了后续错误。这是 TypeScript 结构类型系统 + 可选属性 + 赋值放宽共同作用下的一个可靠性陷阱（见 Item 48 的最后一节“Assignability and Optional Properties”）。