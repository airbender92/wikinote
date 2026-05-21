## Item 72 详细讲解：优先使用 ECMAScript 特性而非 TypeScript 特性

TypeScript 的早期版本（2010 年左右）为 JavaScript 填补了许多“缺失”的语言特性，比如类、枚举、模块系统、装饰器等。但后来 TC39 标准化了这些特性，且实现方式与 TypeScript 的原始版本不完全兼容。如今 TypeScript 的指导原则是：**TC39 定义运行时行为，TypeScript 只在类型空间创新**。因此，对于能够使用标准 ECMAScript 语法解决的问题，应避免使用 TypeScript 特定的历史遗留特性。

本节列举了几个应该避免的 TypeScript 特性，以及推荐的现代 ECMAScript 替代方案。

---

### 1. 枚举（`enum`）

#### 问题

TypeScript 的 `enum` 有多种变体（数字枚举、字符串枚举、常量枚举等），行为不一致，且与标准的 JavaScript 模式脱节。

- **数字枚举**：`enum Flavor { Vanilla, Chocolate }` 编译后是一个双向映射对象，并且数字可以赋值给枚举类型（不安全）。
- **字符串枚举**：编译后生成对象，但类型是**名义型**（nominal），不是结构型。例如 `enum Flavor { Vanilla = 'vanilla' }`，`'vanilla'` 字符串不能直接赋值给 `Flavor` 类型，导致 TypeScript 用户必须导入枚举，而纯 JavaScript 用户可以直接传字符串——API 体验不一致。
- **常量枚举（`const enum`）**：编译时会被内联（例如 `Flavor.Chocolate` 变成 `1`），但需要编译器选项，且与普通枚举的行为差异大，容易造成困惑。

#### 替代方案：使用字面量联合类型

```ts
type Flavor = 'vanilla' | 'chocolate' | 'strawberry';
let favorite: Flavor = 'chocolate'; // 直接赋值，类型安全
```

- 运行时就是字符串，没有额外对象，与 JavaScript 自然兼容。
- 编辑器提供自动补全（如图 9-1）。
- TypeScript 和 JavaScript 用户有完全一致的体验。

对于数字枚举场景，也优先用字符串字面量，因为 `{"flavor": 1}` 比 `{"flavor": "vanilla"}` 更难调试。

---

### 2. 参数属性（Parameter Properties）

TypeScript 允许在构造函数参数前加上 `public`/`private`/`protected`/`readonly` 来同时声明和初始化属性：

```ts
class Person {
  constructor(public name: string) {}
}
```

这等价于：

```ts
class Person {
  name: string;
  constructor(name: string) { this.name = name; }
}
```

#### 问题

- 代码可读性下降：类的所有属性不能一目了然，需要仔细检查构造函数参数列表。
- 混合使用普通属性和参数属性会隐藏类的设计。
- 如果类没有方法，通常用 `interface` 加对象字面量更合适。

#### 替代方案

- 显式声明属性并赋值（传统写法）。
- 对于简单数据容器，使用 `interface` 和普通对象（利用结构类型兼容性）。

---

### 3. 命名空间与三斜线导入（`namespace` 和 `/// <reference>`）

在 ES2015 模块标准出现之前，TypeScript 有自己的模块系统，使用 `module` 关键字（后改为 `namespace`）和三斜线指令 `/// <reference path="..." />`。

这些现在已被 ES2015 的 `import`/`export` 完全取代。除类型声明文件（`.d.ts`）中可能仍需要三斜线指令外，普通代码应一律使用标准模块语法。

---

### 4. 实验性装饰器（`experimentalDecorators`）

TypeScript 在 2015 年实现了装饰器的早期提案，需要开启 `--experimentalDecorators` 编译选项。但随后 TC39 的装饰器提案发生了重大变化，最终标准（Stage 3，2023 年）与 TypeScript 的实现不兼容。

#### 建议

- 如果可能，关闭 `experimentalDecorators`，使用标准装饰器（无需标志）。标准装饰器语法略有不同（例如 `@logged` 放在方法上，函数签名也不同）。
- 如果你被框架（如旧版 Angular）强制使用实验性装饰器，尽量不要再编写新的自定义装饰器，以免将来迁移困难。
- 普通代码中，装饰器并非总是最佳选择，过度使用会降低可读性。

---

### 5. 成员可见性修饰符（`private`、`protected`、`public`）

TypeScript 的 `private` 只在类型检查层面有效，编译后会被擦除，运行时完全暴露。例如：

```ts
class Diary {
  private secret = 'my secret';
}
const d = new Diary();
(d as any).secret; // 运行时可以访问
```

这本质上只是“建议”而非真正的封装。

#### 替代方案：ECMAScript 私有字段（`#`）

ES2022 引入了真正的私有字段，使用 `#` 前缀：

```ts
class Diary {
  #secret = 'my secret';
  getSecret() { return this.#secret; }
}
const d = new Diary();
d.#secret; // 语法错误，只能在类内部访问
```

- 即使在编译到低版本时，TypeScript 也会通过 `WeakMap` 等机制模拟，保证运行时私有性。
- `protected` 和 `public` 很少需要：`public` 是默认的，`protected` 鼓励继承，而组合优于继承原则下很少使用。

**注意**：`readonly` 是类型层面的修饰符，不影响运行时，可以安全使用。一个字段可以同时是 `#private` 和 `readonly`。

---

### 总结

为了保持代码清晰、与未来 JavaScript 标准兼容、避免被特定 TypeScript 版本绑定，应遵循以下原则：

- **枚举** → 字面量联合类型
- **参数属性** → 显式声明属性并赋值
- **命名空间/三斜线导入** → ES2015 `import`/`export`
- **实验性装饰器** → 标准装饰器（或避免使用）
- **`private`/`protected`** → `#` 私有字段

最终目标：让 TypeScript 真正成为“JavaScript with types”，而不是一种与标准 JavaScript 割裂的方言。