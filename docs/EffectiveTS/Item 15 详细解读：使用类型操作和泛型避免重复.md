## Item 15 详细解读：使用类型操作和泛型避免重复

DRY（Don't Repeat Yourself）是软件开发中最基本的原则之一，但很多开发者在写类型定义时却常常忘记它。TypeScript 提供了丰富的类型操作工具（如 `extends`、`keyof`、`typeof`、索引类型、映射类型、泛型等），帮助我们在类型层面消除重复，就像在代码层面使用函数和循环一样。

---

### 1. 问题：类型定义中的重复

```typescript
interface Person {
  firstName: string;
  lastName: string;
}

interface PersonWithBirthDate {
  firstName: string;
  lastName: string;
  birth: Date;
}
```

如果后来需要给 `Person` 添加一个可选字段 `middleName`，`PersonWithBirthDate` 就会不同步。这种重复在类型定义中很常见，但常常被忽视。

**类比**：代码中我们不会重复写 `PI = 3.14159` 和 `2*PI`，而是定义常量 `PI` 并复用。类型定义也需要类似的抽象。

---

### 2. 最基础的 DRY：命名类型

不要重复写内联类型：

```typescript
// 不好的写法
function distance(a: {x: number, y: number}, b: {x: number, y: number}) { ... }

// 好的写法
interface Point2D { x: number; y: number; }
function distance(a: Point2D, b: Point2D) { ... }
```

---

### 3. 重复的函数签名

多个函数具有相同类型签名时，使用命名类型：

```typescript
type HTTPFunction = (url: string, opts: Options) => Promise<Response>;
const get: HTTPFunction = (url, opts) => { ... };
const post: HTTPFunction = (url, opts) => { ... };
```

---

### 4. 使用 `extends` 扩展接口

当两个类型共享一部分字段时，提取公共基类型：

```typescript
interface Person {
  firstName: string;
  lastName: string;
}
interface PersonWithBirthDate extends Person {
  birth: Date;
}
```

**更复杂的例子**：Bird 和 Mammal 共享体重、颜色、是否夜行，提取 `Vertebrate`：

```typescript
interface Vertebrate {
  weightGrams: number;
  color: string;
  isNocturnal: boolean;
}
interface Bird extends Vertebrate {
  wingspanCm: number;
}
interface Mammal extends Vertebrate {
  eatsGardenPlants: boolean;
}
```

这样修改基类型会同步影响所有子类型，并且 TSDoc 注释也会被继承。

---

### 5. 使用 `&` 交叉类型扩展（适用于联合类型）

当你想给一个联合类型添加属性时，`extends` 无法使用，可以用交叉类型：

```typescript
type PersonWithBirthDate = Person & { birth: Date };
```

更复杂的例子：给 `Input | Output` 联合类型添加 `name` 属性：

```typescript
type NamedVariable = (Input | Output) & { name: string };
```

---

### 6. 从大类型中提取子集：索引类型、映射类型、`Pick`

假设有一个完整的 `State` 类型，我们需要一个只包含部分字段的 `TopNavState`：

```typescript
interface State {
  userId: string;
  pageTitle: string;
  recentFiles: string[];
  pageContents: string;
}

// 手动重复字段类型（不理想）
interface TopNavState {
  userId: State['userId'];
  pageTitle: State['pageTitle'];
  recentFiles: State['recentFiles'];
}

// 使用映射类型（更好）
type TopNavState = {
  [K in 'userId' | 'pageTitle' | 'recentFiles']: State[K];
};

// 使用标准库的 Pick（最佳）
type TopNavState = Pick<State, 'userId' | 'pageTitle' | 'recentFiles'>;
```

`Pick` 是 TypeScript 内置的泛型类型，相当于对类型进行“映射+过滤”。

---

### 7. 从联合类型中提取字段类型

有标签联合时，想要提取标签的联合类型：

```typescript
interface SaveAction { type: 'save'; ... }
interface LoadAction { type: 'load'; ... }
type Action = SaveAction | LoadAction;

// 手动写重复的标签
type ActionType = 'save' | 'load';

// 使用索引访问自动推导
type ActionType = Action['type'];  // "save" | "load"
```

这样当 `Action` 联合增加新成员时，`ActionType` 会自动更新。

---

### 8. 将部分属性变为可选：`Partial`

在更新方法中，参数通常是原类型的可选版本：

```typescript
interface Options {
  width: number;
  height: number;
  color: string;
  label: string;
}

class UIWidget {
  constructor(init: Options) { ... }
  update(options: Partial<Options>) { ... }  // 所有属性变为可选
}
```

`Partial<T>` 的实现就是映射类型：`{ [K in keyof T]?: T[K] }`。

---

### 9. 同态映射类型

当映射类型使用 `K in keyof T` 这种形式时，它是**同态的**，会保留源类型的 `readonly`、可选修饰符以及 TSDoc 注释。

```typescript
interface Customer {
  /** 客户称谓 */
  title?: string;
  /** 完整姓名 */
  readonly name: string;
}

type PickTitle = Pick<Customer, 'title'>;     // { title?: string; }  保留可选和注释
type ManualName = { [K in 'name']: Customer[K] }; // { name: string; } 丢失 readonly
```

同态映射类型还能让原始类型（如 `number`）原样通过，例如 `Partial<number>` 仍是 `number`。

---

### 10. 从值推导类型：`typeof`

避免重复定义类型和值：

```typescript
const INIT_OPTIONS = {
  width: 640,
  height: 480,
  color: '#00FF00',
  label: 'VGA',
};
type Options = typeof INIT_OPTIONS;  // 自动推断类型
```

**注意**：通常建议先定义类型，再声明值符合该类型，这样更显式。但 `typeof` 在值作为唯一数据源时很有用（如配置文件、API 响应示例）。

---

### 11. 从函数返回值推导类型：`ReturnType`

```typescript
function getUserInfo(userId: string) {
  return { userId, name, age, height, weight, favoriteColor };
}
type UserInfo = ReturnType<typeof getUserInfo>;
```

`ReturnType` 作用于函数的**类型**（`typeof getUserInfo`），而不是函数的值。

---

### 12. 不要过度抽象

并非所有语法相同的属性都是语义相同。例如：

```typescript
interface Product { id: number; name: string; priceDollars: number; }
interface Customer { id: number; name: string; address: string; }
```

提取公共基类 `NamedAndIdentified` 是**过早抽象**，因为 `Product` 和 `Customer` 的 `id` 和 `name` 代表不同的业务概念，未来可能独立变化。

**原则**：如果很难为公共部分取一个有意义的名称（如 `NamedAndIdentified` 只是结构描述），那很可能不是好抽象。好抽象的名字应该能表达业务含义，如 `Vertebrate`。

> 引用 Sandi Metz：“重复比错误的抽象便宜得多。”

---

### 13. 总结：类型 DRY 工具表

| 场景 | 解决方案 | 示例 |
|------|----------|------|
| 重复的内联类型 | 命名类型 | `type Point = { x: number; y: number; }` |
| 重复的函数签名 | 命名函数类型 | `type Fn = (x: number) => string;` |
| 扩展已有接口 | `extends` | `interface B extends A { ... }` |
| 扩展类型（含联合） | `&` 交叉 | `type T = A & B;` |
| 从大类型取子集 | `Pick<T, K>` | `Pick<State, 'userId'>` |
| 从联合提取标签 | `Action['type']` | `type Tag = Action['tag'];` |
| 将属性变为可选 | `Partial<T>` | `Partial<Options>` |
| 从值推导类型 | `typeof val` | `type Opts = typeof init;` |
| 从函数推导返回类型 | `ReturnType<typeof fn>` | `ReturnType<typeof getUserInfo>` |
| 同态映射保留修饰符 | `{ [K in keyof T]: T[K] }` | `Pick`, `Partial`, `Readonly` 等 |
| 映射中重命名键 | `as` 子句 | `{ [K in T as NewKey]: ... }` |

**最终建议**：像对待代码一样对待类型，时刻留意重复，并学习使用 TypeScript 提供的各种类型工具来消除它们。