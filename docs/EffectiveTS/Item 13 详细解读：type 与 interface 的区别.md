## Item 13 详细解读：type 与 interface 的区别

在 TypeScript 中，定义命名类型有两种主要方式：**类型别名 (type alias)** 和 **接口 (interface)**。虽然它们在很多场景下可以互换使用，但理解它们的区别有助于写出更清晰、更健壮的代码。

### 1. 基本语法对比

```typescript
// 类型别名
type TState = {
  name: string;
  capital: string;
};

// 接口
interface IState {
  name: string;
  capital: string;
}
```

> **⚠️ 命名惯例提醒**：示例中使用了 `T` 和 `I` 前缀只是为了区分定义方式。实际编码中**不要**使用这种前缀（如 `IUser`），因为 TypeScript 是结构化类型系统，这种命名既无必要也不符合标准库风格。

---

### 2. 相似点（两者都能做到）

| 特性 | 说明 | 示例 |
|------|------|------|
| **多余属性检查** | 对象字面量赋值时，两者都会报错 | `{ name, capital, population }` 会提示 `population` 不存在 |
| **索引签名** | 支持动态属性名 | `{ [key: string]: string }` |
| **函数类型** | 两种语法均可定义函数类型 | `type Fn = (x: number) => string;` 或 `interface Fn { (x: number): string; }` |
| **泛型** | 支持泛型参数 | `type Box<T> = { value: T };` / `interface Box<T> { value: T; }` |
| **相互扩展** | `interface extends type` 和 `type & interface` 均可 | `interface I extends T { ... }` / `type T = I & { ... }` |
| **类实现** | `class implements` 两者都支持 | `class C implements TState` |
| **递归定义** | 两者都支持递归 | `type Tree = { value: number; children: Tree[] };` |

---

### 3. 主要区别

#### 3.1 联合类型 (Union Types)

**type 可以直接定义联合类型，interface 不能。**

```typescript
type AorB = 'a' | 'b';          // ✅ 联合类型
type InputOrOutput = Input | Output;  // ✅ 联合类型

// interface 无法直接表示联合
interface IAorB = 'a' | 'b';     // ❌ 语法错误
```

#### 3.2 表达能力：复杂类型操作

type 可以利用交叉类型 (`&`) 与联合结合，实现更灵活的类型组合，而 interface 无法表达此类模式。

```typescript
type Input = { /* ... */ };
type Output = { /* ... */ };
type NamedVariable = (Input | Output) & { name: string };  // ✅ 联合+交叉
// interface 无法直接写出这种类型
```

type 还支持**映射类型**、**条件类型**等高级特性，而 interface 只能用于描述对象形状。

#### 3.3 扩展时的错误检查差异

当扩展一个类型且出现属性类型不兼容时，`interface extends` 会立即报错，而 `type &` 不会报错，但会生成一个**不可用的类型**（如 `never` 或属性缺失）。

```typescript
interface Person {
  name: string;
  age: string;      // 注意：age 是 string
}

// 使用 type & 不会报错，但结果类型不可用
type TPerson = Person & { age: number };  // 无报错，但 age 类型变成 never

// 使用 interface extends 会明确报错
interface IPerson extends Person {
// ~~~~~~~ 报错：Property 'age' 类型不兼容
  age: number;
}
```

> **推荐**：对于对象类型的扩展，优先使用 `interface extends` 以获得更好的类型检查。

#### 3.4 元组与数组类型

type 可以简洁地表达元组和数组类型，而 interface 无法做到同样简洁。

```typescript
type Pair = [a: number, b: number];          // 元组
type StringList = string[];                  // 数组
type NamedNums = [string, ...number[]];      // 带标签的剩余元素元组

// 用 interface 模拟数组非常冗长且不自然
interface IArrayLike<T> {
  length: number;
  [n: number]: T;
}
```

#### 3.5 声明合并 (Declaration Merging)

**这是 interface 独有的特性**：同一个 interface 可以多次定义，TypeScript 会自动合并它们。

```typescript
interface IState {
  name: string;
  capital: string;
}
interface IState {
  population: number;   // 合并进来
}
const wyoming: IState = {
  name: 'Wyoming',
  capital: 'Cheyenne',
  population: 578_000    // ✅ 现在允许
};
```

type 不支持这种重复定义，相同名称的 type 会导致重复定义错误。

TypeScript 自身利用这一特性来增量添加标准库的方法：`Array` 接口在 `lib.es5.d.ts` 中定义了基本方法，在 `lib.es2015.core.d.ts` 中又定义了 `find`、`findIndex` 等，通过合并形成完整的 `Array` 类型。

> **注意**：声明合并主要用于**类型声明文件**（`.d.ts`）中。在普通代码中，只有定义在**同一模块**中的 interface 才能合并，这避免了全局污染。

#### 3.6 生成 .d.ts 文件时的行为差异

当 TypeScript 生成声明文件时（`declaration: true`）：

- **type 别名**：如果定义在函数内部或局部作用域，会被**内联**展开，名称消失。
- **interface**：会尽量保留名称，如果名称不可访问（如局部 interface），则导致错误。

```typescript
// 使用 type（内联）
export function getHummer() {
  type Hummingbird = { name: string; weightGrams: number; };
  const ruby: Hummingbird = { name: 'Ruby-throated', weightGrams: 3.4 };
  return ruby;
}
// 生成的 .d.ts 中返回类型被内联为 { name: string; weightGrams: number; }

// 使用 interface（保留名称，但未导出会报错）
export function getHummer() {
  interface Hummingbird { name: string; weightGrams: number; };
  const bee: Hummingbird = { name: 'Bee Hummingbird', weightGrams: 2.3 };
  return bee;
}
// 报错：Return type of exported function has or is using private name 'Hummingbird'
```

因此，如果希望类型在声明文件中保留名称，要么导出它，要么使用 type（因为 type 会内联，不会报错）。但内联可能导致类型重复膨胀，影响编译性能。**最佳实践**：将类型提升到顶层并导出。

---

### 4. 使用建议

根据 TypeScript 官方手册及本书作者的建议：

| 场景 | 推荐 | 原因 |
|------|------|------|
| **简单对象类型** | `interface` | 更好的错误信息、更清晰的错误显示、支持声明合并 |
| **需要联合类型** | `type` | `interface` 无法表达 |
| **函数类型** | `type` | 语法更简洁：`type Fn = (x: number) => string;` |
| **元组 / 数组** | `type` | 语法自然 |
| **映射类型 / 条件类型** | `type` | 只有 type 支持 |
| **第三方库的类型扩展** | `interface` | 声明合并允许用户添加新属性 |
| **已有代码风格** | 保持一致 | 不必强行改造 |

> **官方启发式建议**：**能用 `interface` 就用 `interface`，需要 `type` 特性时再用 `type`**。但不必过于纠结，两者在大多数情况下都能工作。

### 5. 总结

| 特性 | type | interface |
|------|------|-----------|
| 联合类型 | ✅ | ❌ |
| 对象类型 | ✅ | ✅（推荐） |
| 函数类型 | ✅（简洁） | ✅（但语法冗长） |
| 元组/数组 | ✅（自然） | ❌（不自然） |
| 高级类型（映射、条件） | ✅ | ❌ |
| 声明合并 | ❌ | ✅ |
| 扩展时的错误检查 | 差（不报错但产生不可用类型） | 好（立即报错） |
| 内联行为（.d.ts） | 会内联 | 保留名称（可能报错） |

**最终建议**：对于新项目，对象类型首选 `interface`，当遇到联合、元组、函数类型等场景时切换到 `type`。同时，可以借助 ESLint 规则 `consistent-type-definitions` 强制团队保持一致性。