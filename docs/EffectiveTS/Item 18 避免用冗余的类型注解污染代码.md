## Item 18: 避免用冗余的类型注解污染代码 —— 详解与示例

### 核心观点

TypeScript 拥有强大的类型推断能力。**只要 TypeScript 能推断出与显式注解相同的类型，就省略注解**。为所有变量都写上类型注解是“过度类型化”，不仅增加噪音，还可能降低类型安全性（因为显式注解可能比推断出的类型更宽泛）。

理想 TypeScript 代码的模式：**函数/方法的签名保留类型注解，但函数体内的局部变量让 TypeScript 自动推断**。

---

### 1. 基础类型推断：无需注解

❌ 冗余写法：
```typescript
let x: number = 12;
const person: { name: string; born: { where: string; when: string } } = { ... };
```

✅ 简洁写法：
```typescript
let x = 12;                // 推断为 number
const person = { ... };    // 推断为精确的对象类型
```

**原因**：鼠标悬停即可看到推断结果，显式注解没有提供新信息，只是噪音。

---

### 2. 数组和函数返回值推断

```typescript
function square(nums: number[]) {
    return nums.map(x => x * x);
}
const squares = square([1, 2, 3, 4]);
// squares 推断为 number[] ✅
```

TypeScript 从输入和操作中正确推断返回类型，无需额外注解。

---

### 3. 推断可能比显式注解更精确 → 更安全

```typescript
const axis1: string = 'x';   // 类型 string（宽泛）
const axis2 = 'y';            // 类型 "y"（字面量，更精确）
```

显式注解 `: string` 反而**丢失了精度**，也**减少了类型安全性**（例如，`axis2` 不能被赋值为任意字符串，而 `axis1` 可以）。

---

### 4. 推断有助于重构

**初始代码**：
```typescript
interface Product {
    id: number;
    name: string;
    price: number;
}
function logProduct(product: Product) {
    const id: number = product.id;
    const name: string = product.name;
    const price: number = product.price;
    console.log(id, name, price);
}
```

**需求变更**：`id` 从 `number` 改为 `string`。

- **显式注解版本**：在 `logProduct` 内部产生类型错误（`number` 不能赋给 `string`），需要手动修改三处。
- **依赖推断版本**（无注解）：直接使用解构，无需修改任何代码。

✅ 更好的实现：
```typescript
function logProduct(product: Product) {
    const { id, name, price } = product;   // 类型自动推断
    console.log(id, name, price);
}
```

**注意**：不能在解构中直接写类型注解，因为那会被解释为重命名语法（Item 8）。正确做法是：
```typescript
// ❌ 错误
const { id, name, price }: { id: string; name: string; price: number } = product;
```

---

### 5. 仍需要显式注解的情况

虽然大多数局部变量可以推断，但以下情况**必须或建议**添加注解：

#### 5.1 函数参数（必须）
TypeScript 不会根据函数体推断参数类型，必须显式注解：
```typescript
function square(nums: number[]) { ... }   // nums 注解必须
```

**例外**：有默认值时参数类型可以推断：
```typescript
function parseNumber(str: string, base = 10) {  // base 推断为 number
    // ...
}
```

#### 5.2 回调参数（可省略，利用上下文推断）
当函数作为库回调时，参数类型通常可推断：
```typescript
// ❌ 冗余
app.get('/health', (request: express.Request, response: express.Response) => {...});

// ✅ 简洁
app.get('/health', (request, response) => {...});   // 类型自动推断
```

#### 5.3 对象字面量（建议注解以启用过剩属性检查）
```typescript
const elmo: Product = {
    name: 'Tickle Me Elmo',
    id: '048188 627152',   // 如果写错类型，这里立即报错
    price: 28.99,
};
```
没有注解时，错误可能在使用处才出现，远离定义位置：
```typescript
const furby = { name: 'Furby', id: 630509430963, price: 35 };
logProduct(furby);   // 错误在这里，但问题在 furby 的定义
```

#### 5.4 函数返回类型（特定情况建议注解）
默认可以不注解，但有三种情况建议显式注解：

1. **函数有多个 `return` 语句**：确保所有分支返回一致类型，避免遗漏错误。
    ```typescript
    function getQuote(ticker: string): Promise<number> { ... }
    ```
2. **函数是公共 API 的一部分**：防止实现错误泄漏到调用方，错误更贴近根源。
3. **想使用命名类型作为返回类型**：使文档和 IDE 提示更清晰。
    ```typescript
    function add(a: Vector2D, b: Vector2D): Vector2D { ... }
    ```

另外，注解返回类型可以减少 TypeScript 编译器工作量，对大型项目性能有益（Item 78）。

---

### 6. 总结：Things to Remember

| 情况 | 是否注解 | 原因 |
|------|----------|------|
| 局部变量（`let x = 12`） | ❌ 不注解 | 可推断，无噪音 |
| 函数参数 | ✅ 注解 | TypeScript 不推断参数类型 |
| 对象字面量赋值 | ✅ 注解（可选但推荐） | 启用过剩属性检查，错误就近报告 |
| 函数返回类型（简单单返回） | ❌ 默认不注解 | 让类型推断，方便重构 |
| 函数返回类型（多重返回/公共API/需命名） | ✅ 注解 | 保证一致性，改善文档和性能 |
| 回调参数 | ❌ 通常不注解 | 利用上下文推断 |

---

### 7. 实用技巧

- **使用 `typescript-eslint` 的 `no-inferrable-types` 规则**：自动提示并修复冗余注解。
- **解构 + 推断**是处理对象属性的最佳实践。
- **记住**：类型推断不是万能的，但它比你想象的更聪明。让 TypeScript 帮你工作，而不是与它对抗。

---

### 书中代码示例完整演示

**重构前的过度注解**（当 `Product.id` 从 `number` 改为 `string` 后产生错误）：
```typescript
function logProduct(product: Product) {
    const id: number = product.id;   // 错误
    const name: string = product.name;
    const price: number = product.price;
}
```

**重构后（无局部变量注解）**：
```typescript
function logProduct(product: Product) {
    const { id, name, price } = product;   // 类型自动正确
    console.log(id, name, price);
}
```

**需要注解返回类型的例子**（缓存实现错误）：
```typescript
// 错误实现：有时返回 number，有时返回 Promise<number>
function getQuote(ticker: string) {
    if (ticker in cache) return cache[ticker];   // number
    return fetch(...).then(r => r.json());       // Promise<number>
}
// 调用时出错：.then 不存在于 number | Promise<number>
getQuote('MSFT').then(...);

// 修复：注解返回类型让错误出现在函数内部
function getQuote(ticker: string): Promise<number> {
    if (ticker in cache) return cache[ticker];   // ❌ 错误立即提示
    // ...
}
```

---

**一句话总结**：**让 TypeScript 推断它自己能推断的东西，只在必要的地方（参数、公共边界、复杂逻辑）写注解。**