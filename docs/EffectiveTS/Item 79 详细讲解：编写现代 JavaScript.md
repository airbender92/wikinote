## Item 79 详细讲解：编写现代 JavaScript

在将旧项目迁移到 TypeScript 之前，最好的第一步不是直接添加类型，而是**将 JavaScript 代码升级到现代 JavaScript（ES2015+）**。因为 TypeScript 是 JavaScript 的超集，它完全支持所有新特性，并且可以将其编译到旧版 JS（如 ES5）。使用现代语法不仅能让代码更简洁、更易维护，还能让 TypeScript 的类型推断更准确，迁移更顺利。

---

### 1. 为什么现代 JavaScript 是迁移到 TypeScript 的基础

- TypeScript 本身就是围绕现代 JavaScript 设计的。使用 `class`、`import/export`、`async/await` 等特性，TypeScript 能更好地理解代码结构，提供更精确的类型推断。
- 旧式 JS 代码（如原型链、回调、`var`、CommonJS）往往让 TypeScript 难以分析，需要更多的类型注解。
- 迁移过程中，现代 JS 代码可以平滑地加入类型注解，而旧式代码往往需要先重构。

---

### 2. 最重要的两个特性：ES 模块和类

#### 2.1 使用 ECMAScript 模块（`import` / `export`）

- **旧方式**（CommonJS）：`require()` 和 `module.exports`
- **现代方式**：`import` 和 `export`
- **优势**：
  - 静态结构，支持 tree shaking。
  - TypeScript 可以更好地进行模块分析和类型检查。
  - 允许逐模块迁移（Item 82）。

示例对比：

```js
// CommonJS (旧)
const b = require('./b');
module.exports = { name };
```

```ts
// ES module (新)
import * as b from './b';
export const name = 'Module B';
```

即使你仍需要输出 CommonJS（例如 Node.js 环境），可以在 `tsconfig.json` 中设置 `"module": "commonjs"`，TypeScript 会自动转换。但源代码中应当使用 ES 模块语法。

#### 2.2 使用 `class` 替代原型操作

- **旧方式**：构造函数 + 原型方法
- **现代方式**：`class` 语法
- **优势**：更清晰、更安全，TypeScript 能自动推断成员类型，并提供 IDE 支持（快速修复可将旧式“类”转换为 ES2015 类，图 10-1）。

示例对比：

```js
// 旧：原型
function Person(first, last) {
  this.first = first;
  this.last = last;
}
Person.prototype.getName = function() { return this.first + ' ' + this.last; };
```

```ts
// 现代：class
class Person {
  constructor(public first: string, public last: string) {}
  getName() { return `${this.first} ${this.last}`; }
}
```

---

### 3. 其他重要的现代 JavaScript 特性

| 特性 | 旧方式 | 现代方式 | 优势 |
|------|--------|----------|------|
| 变量声明 | `var` | `let` / `const` | 块作用域，避免提升带来的混淆 |
| 循环 | `for (var i=0; i<arr.length; i++)` | `for-of`、`forEach`、`map` | 避免索引变量，可直接迭代值 |
| 异步 | 回调函数 | `async` / `await`（Item 27） | 线性代码，错误处理统一 |
| 函数 | `function() {}` | 箭头函数 `() => {}` | 词法 `this`，简洁 |
| 参数默认值 | 函数体内检查 `if (x === undefined)` | `function foo(x = 123) {}` | 清晰，且 TypeScript 可推断类型 |
| 对象字面量 | `{ x: x, y: y }` | `{ x, y }`（简写） | 简洁 |
| 解构赋值 | `var a = arr[0]; var b = arr[1];` | `[a, b] = arr` | 从数组/对象中快速取值 |
| 集合 | 使用普通对象模拟 | `Map`、`Set` | 避免原型链冲突，键值对更可靠 |
| 可选链 | `x && x.y && x.y.z` | `x?.y?.z` | 安全访问深层属性 |
| 空值合并 | `value || defaultValue`（会将 `0`、`''` 视为假） | `value ?? defaultValue` | 仅当 `value` 为 `null` 或 `undefined` 时使用默认值 |
| 严格模式 | `"use strict"` 指令 | 无需写（ES 模块自动严格模式） | TypeScript 更严格 |

---

### 4. 迁移策略建议

1. **首先将整个代码库转换为 ES 模块（`import/export`）**，即使暂时不添加类型。这可以让你后续逐文件迁移（Item 82）。
2. **将原型风格的“类”转换为 ES2015 `class`**，并利用 TypeScript 的快速修复工具。
3. **替换回调为 `async/await`**（如果项目涉及异步操作）。
4. **将 `var` 替换为 `let`/`const`**（通常可通过 lint 自动修复）。
5. 逐步采用其他现代特性（如解构、可选链等），但不必一次性全部改完。

**注意**：在迁移到 TypeScript 之前进行这些现代化重构，可以大幅减少添加类型注解时的工作量，并且许多现代化重构本身就能暴露潜在的 bug。

---

### 5. 总结（Things to Remember）

- TypeScript 允许你编写现代 JavaScript，无论目标运行环境如何。充分利用这一特性。
- **采用 ES 模块和 `class` 是迁移到 TypeScript 最重要的两步**。
- 学习并使用 `let`/`const`、`for-of`、`async/await`、箭头函数、解构、`Map`/`Set`、可选链、空值合并等现代语法。
- 不需要手动写 `"use strict"`，TypeScript 会自动处理。
- 关注 TC39 提案和 TypeScript 发行说明，了解即将到来的新特性。

**最终建议**：在开始添加任何类型注解之前，花一两天时间将你的 JavaScript 代码升级到现代语法。这会让后续的 TypeScript 迁移变得顺畅许多，甚至有些类型可以自动推断出来。