## Item 16 详细解读：优先选择更精确的替代方案而非索引签名

在 JavaScript 中，对象可以方便地使用字符串（或 symbol）作为键，任意类型作为值。TypeScript 通过**索引签名**（index signature）来建模这种灵活的结构：

```typescript
type Rocket = { [property: string]: string };
const rocket: Rocket = {
  name: 'Falcon 9',
  variant: 'v1.0',
  thrust: '4,940 kN',
};
```

索引签名 `[property: string]: string` 指定了：
- 键的名称（仅用于文档，类型检查器忽略）
- 键的类型（必须是 `string | number | symbol` 的子类型）
- 值的类型

尽管这种写法通过类型检查，但存在诸多缺点。

---

### 1. 索引签名的缺点

| 缺点 | 说明 | 示例问题 |
|------|------|----------|
| **允许任意键** | 即使拼写错误，仍然有效 | `{ Name: 'Falcon 9' }` 也被认为是 `Rocket` |
| **不要求特定键存在** | 空对象 `{}` 也是合法的 `Rocket` | 可能缺少必要字段 |
| **所有键值类型必须相同** | 无法为不同键指定不同类型 | 若希望 `thrust` 是 `number`，无法做到 |
| **语言服务失效** | 没有自动补全、跳转定义、重命名支持 | 编码体验下降 |

因此，**索引签名应尽量避免**，它类似 `any`，会侵蚀类型安全性和开发体验。

---

### 2. 更精确的替代方案

#### 2.1 使用具体的接口

如果已知对象的结构，直接定义接口：

```typescript
interface Rocket {
  name: string;
  variant: string;
  thrust_kN: number;   // 可以有不同的类型
}
```

优势：类型检查、自动补全、重命名等全部可用。

---

#### 2.2 使用 `Map` 处理动态数据

对于真正的动态数据（如 CSV 解析，列名未知），使用 `Map` 替代对象 + 索引签名：

```typescript
function parseCSVMap(input: string): Map<string, string>[] {
  // ...
  const row = new Map<string, string>();
  row.set(headers[i], cell);
  // ...
}
```

**优点**：
- 存取必须通过 `.get()`，返回值总是 `string | undefined`，强制处理缺失情况。
- 避免原型链污染问题。
- 可以后续解析为强类型对象。

```typescript
const rockets = parseCSVMap(csvData).map(parseRocket); // parseRocket 返回强类型 Rocket
```

---

#### 2.3 使用可选字段或联合类型

当字段集合有限但可选时，用接口的可选字段或联合类型：

```typescript
interface Row2 { a: number; b?: number; c?: number; d?: number; }   // 可选字段

type Row3 = 
  | { a: number; }
  | { a: number; b: number; }
  | { a: number; b: number; c: number; }
  | { a: number; b: number; c: number; d: number; };               // 精确联合
```

后者最精确，但可能不方便操作。根据需求选择。

---

#### 2.4 使用 `Record` 类型约束键集

`Record<K, V>` 是内置泛型，相当于映射类型，可以限定键为特定联合：

```typescript
type Vec3D = Record<'x' | 'y' | 'z', number>;
// 等价于 { x: number; y: number; z: number; }
```

---

#### 2.5 保留索引签名但收窄键类型

如果确实需要索引签名（如允许任意字符串键），可以将其类型收窄为更具体的模式，例如只允许 `data-` 开头的属性：

```typescript
interface ButtonProps {
  title: string;
  onClick: () => void;
  [key: `data-${string}`]: unknown;   // 模板字面量类型
}
```

这样既保留了灵活性，又限制了额外属性的格式。

---

#### 2.6 使用索引签名禁用多余属性检查

有时你可能希望一个接口有明确的几个属性，同时允许其他任意属性。添加一个索引签名（值为 `unknown`）可以禁用多余属性检查，同时保持已知属性的类型安全：

```typescript
interface ButtonProps {
  title: string;
  onClick: () => void;
  [otherProps: string]: unknown;
}
```

---

### 3. 总结：何时使用索引签名？

| 场景 | 推荐方案 | 原因 |
|------|----------|------|
| **已知字段** | 接口（或 `Record`） | 类型安全 + 语言服务 |
| **动态列名（CSV等）** | `Map<string, string>` | 强制处理 `undefined`，避免原型链问题 |
| **有限可选字段** | 可选属性接口或精确联合 | 明确可能出现的键 |
| **已知键名但类型可变** | 映射类型或 `Record` | 精确控制每个键的类型 |
| **需要允许多余属性但不失安全** | 接口 + 索引签名（值为 `unknown`） | 保留已知属性的严格检查 |
| **不得不使用索引签名** | 尽量收窄键类型（如模板字面量） | 减少意外键的出现 |

**核心原则**：索引签名是最后的手段，在大多数情况下，有更精确、更安全的替代方案。优先使用这些方案，可以让你充分利用 TypeScript 的类型检查和语言服务。