## Item 12：尽可能将类型应用于整个函数表达式 —— 详细讲解

TypeScript 中的函数可以通过**函数声明**（statement）或**函数表达式**（expression）来定义。本 Item 建议：**当你需要为函数添加类型时，优先采用函数表达式，并将类型注解直接应用到整个表达式上，而不是分别注解每个参数和返回值**。这样做可以：

- 减少重复的类型注解。
- 使函数实现更清晰（类型与实现分离）。
- 利用 TypeScript 对上下文类型的推导，自动获得参数类型。
- 更好地保证返回值类型符合预期。

---

## 1. 函数声明与函数表达式的区别

```typescript
// 函数声明（statement）
function rollDice1(sides: number): number { /* ... */ }

// 函数表达式（expression）
const rollDice2 = function(sides: number): number { /* ... */ };
const rollDice3 = (sides: number): number => { /* ... */ };
```

函数表达式可以像普通值一样被赋值给变量，并且可以**一次性给整个函数指定类型**：

```typescript
type DiceRollFn = (sides: number) => number;
const rollDice: DiceRollFn = sides => { /* ... */ };
```

这里，`sides` 的类型被自动推导为 `number`，无需重复书写。参数名 `sides` 保持了语义清晰，而类型约束集中在 `DiceRollFn` 中。

---

## 2. 减少重复：一组同类型函数

如果你要定义多个具有相同函数签名的函数（例如数学运算），传统方式需要重复写很多类型注解：

```typescript
function add(a: number, b: number): number { return a + b; }
function sub(a: number, b: number): number { return a - b; }
function mul(a: number, b: number): number { return a * b; }
function div(a: number, b: number): number { return a / b; }
```

使用函数表达式 + 统一类型别名：

```typescript
type BinaryFn = (a: number, b: number) => number;

const add: BinaryFn = (a, b) => a + b;
const sub: BinaryFn = (a, b) => a - b;
const mul: BinaryFn = (a, b) => a * b;
const div: BinaryFn = (a, b) => a / b;
```

**好处**：
- 类型注解只写一次，大幅减少重复。
- 实现代码（右侧）变得非常简洁，只关心业务逻辑。
- TypeScript 会自动检查每个实现是否真的返回 `number`，防止意外返回其他类型。

---

## 3. 匹配另一个函数的签名：`typeof fn`

有时你需要编写一个与现有函数具有相同参数和返回值类型的新函数。例如，浏览器原生的 `fetch` 函数在遇到 HTTP 错误状态（如 404）时**并不会**抛出异常或返回一个 rejected Promise，而是正常返回 `Response` 对象，只是 `response.ok` 为 `false`。很多开发者会忘记检查 `ok`，导致错误处理不当。

我们可以封装一个 `checkedFetch`，它会检查 `response.ok`，如果不成功则抛出错误（使得 Promise 变为 rejected）。我们希望 `checkedFetch` 的签名与 `fetch` 完全一致。

### 使用函数声明的方式（冗长且容易出错）

```typescript
async function checkedFetch(input: RequestInfo, init?: RequestInit) {
    const response = await fetch(input, init);
    if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
    }
    return response;
}
```

这里手动写了参数类型，没有错误，但不够简洁。

### 更好的方式：函数表达式 + `typeof fetch`

```typescript
const checkedFetch: typeof fetch = async (input, init) => {
    const response = await fetch(input, init);
    if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
    }
    return response;
};
```

**解释**：
- `typeof fetch` 提取了 `fetch` 的类型签名：`(input: RequestInfo, init?: RequestInit) => Promise<Response>`。
- 将这个类型应用到整个函数表达式，TypeScript 自动推导 `input` 和 `init` 的类型，无需手动注解。
- 返回值类型也被约束为 `Promise<Response>`，任何不符合的返回都会被报错。

**错误捕获示例**：如果你错误地在失败时返回 `new Error(...)` 而不是 `throw`：

```typescript
const checkedFetch: typeof fetch = async (input, init) => {
    const response = await fetch(input, init);
    if (!response.ok) {
        return new Error('...');   // ❌ 错误：返回类型不匹配
    }
    return response;
};
```

TypeScript 会立即报错：`Promise<Response | Error>` 不能赋值给 `Promise<Response>`。这比在调用侧才发现问题好得多。

---

## 4. 使用 `Parameters` 工具类型改变返回类型

有时你想复用另一个函数的参数类型，但改变其返回类型。例如，写一个 `fetchANumber` 函数，它接受与 `fetch` 相同的参数，但返回 `Promise<number>`（期望响应体是一个数字）。

```typescript
async function fetchANumber(
    ...args: Parameters<typeof fetch>
): Promise<number> {
    const response = await checkedFetch(...args);
    const num = Number(await response.text());
    if (isNaN(num)) {
        throw new Error('Response was not a number.');
    }
    return num;
}
```

- `Parameters<typeof fetch>` 是一个元组类型，表示 `fetch` 的参数列表。
- 使用 `...args` 收集剩余参数，然后传递给 `checkedFetch`。
- 返回值类型被明确指定为 `Promise<number>`。

在编辑器中查看 `fetchANumber`，其函数签名会显示为：

```typescript
function fetchANumber(input: RequestInfo | URL, init?: RequestInit | undefined): Promise<number>
```

`args` 本身不会出现在签名中，它被展开了，用户体验完美。

**适用场景**：当你需要保持参数类型完全一致，但返回不同类型时，这种方法比手动重写所有参数类型更安全、更不易出错。

---

## 5. 什么时候不该用这种模式？

- 对于**单个、独立的函数**，且签名没有重复使用，直接用函数声明加参数注解更简单清晰，不必强行提取类型别名。
- 如果签名虽然相同但逻辑差异很大，提取类型别名可能反而增加间接性。

本 Item 强调 **“many” 和 “repeating”** —— 重复多次时才值得提取。

---

## 6. 间接的好处：利用上下文类型推导

当你将函数表达式传递给像 `map`、`filter` 这样的高阶函数时，TypeScript 会自动根据期望的类型来推导回调函数的参数类型。这其实就是“将类型应用于整个函数表达式”的一种体现，只不过类型是由库（如数组方法）提供的。例如：

```typescript
const lengths = ['a', 'bb', 'ccc'].map(s => s.length);
// s 自动推导为 string，因为 map 的签名中回调期望的参数类型是 string
```

这背后的机制正是上下文类型（contextual typing，Item 24）。

---

## 7. Things to Remember（中文总结）

1. **优先为整个函数表达式添加类型注解**，而不是分别注解参数和返回值。这样可以减少重复，并将类型与实现分离。
2. 当多个函数具有相同的类型签名时，提取一个函数类型别名（如 `BinaryFn`）并复用到各个表达式上。
3. 使用 `typeof fn` 可以轻松复用另一个函数的完整类型签名（参数 + 返回值），适合编写封装或装饰函数。
4. 使用 `Parameters<typeof fn>` 可以提取参数元组，结合剩余参数（`...args`）来改变返回类型，同时保持参数类型一致。
5. 这些技巧在**重复出现**时最有价值；对于一次性的独立函数，传统的函数声明加显式类型注解完全没问题。
6. 库作者应该为常见回调提供类型别名，方便用户直接应用到整个函数表达式。

---

如果你希望继续学习 Item 13（`type` 与 `interface` 的区别），我可以为你详细讲解。