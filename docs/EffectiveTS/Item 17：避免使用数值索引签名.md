## Item 17: 避免使用数值索引签名 —— 详解与示例

### 核心观点

在 TypeScript 中，**不要在你自己的类型定义中使用数值索引签名**（如 `[n: number]: T`）。尽管 TypeScript 允许这样写，但它只是模拟了 JavaScript 数组的行为，而实际上 JavaScript 对象的所有键都是字符串（或 Symbol）。使用数值索引签名会误导你对 JavaScript 运行时的理解，并且有更安全、更清晰的替代方案。

---

### 背景知识：JavaScript 对象的键只能是字符串或 Symbol

在 JavaScript 中，对象是键值对的集合。**键只能是字符串或 Symbol**（ES2015 以后）。如果你使用其他类型的值作为键，JavaScript 会先将其转换为字符串：

```javascript
> let x = {}
> x[[1, 2, 3]] = 2
2
> x
{ '1,2,3': 2 }   // 数组 [1,2,3] 被 toString() 转为 "1,2,3"
```

**重点**：数字也不能作为键！如果你尝试用数字作为属性名，它会被自动转换成字符串：

```javascript
> { 1: 2, 3: 4 }
{ '1': 2, '3': 4 }
```

---

### 数组的“数值索引”是假象

数组确实是对象（`typeof [] === 'object'`）。我们习惯用数值下标访问数组元素：

```javascript
> let arr = [1, 2, 3]
> arr[0]
1
```

但底层发生了什么？**这个数值 `0` 也被转换成了字符串 `"0"`**。证据：

```javascript
> arr['1']   // 用字符串键也能访问
2
> Object.keys(arr)
[ '0', '1', '2' ]   // 返回的是字符串数组！
```

所以，数组的“数值索引”只是 JavaScript 提供的一个语法糖，让你感觉像在用数字，实际上内部全是字符串。

---

### TypeScript 的数值索引签名：一个有用的虚构

为了让你能写出 `arr[0]` 这样的代码并能进行类型检查，TypeScript 在 `lib.es5.d.ts` 中为 `Array` 接口声明了一个**数值索引签名**：

```typescript
interface Array<T> {
    // ...
    [n: number]: T;   // 这就是数值索引签名
}
```

这完全是一个**虚构**（fiction）。它在运行时不存在，只在 TypeScript 编译时起作用。它的好处是能捕获一些错误：

```typescript
const xs = [1, 2, 3];
const x0 = xs[0];           // ✅ OK
const x1 = xs['1'];         // ✅ 字符串形式的数字常量也允许

const inputEl = document.getElementsByTagName('input')[0];
const xN = xs[inputEl.value];   // ❌ 错误：索引表达式不是 number 类型
// 因为 inputEl.value 是 string，而索引签名要求 number
```

这个错误提示很有用：它提醒你 `inputEl.value` 是字符串，你应该用 `inputEl.valueAsNumber` 或其他方法。

---

### 数值索引签名的陷阱

1. **它只是编译时的虚构**：运行时，`Object.keys(xs)` 仍然返回字符串数组。

```typescript
const keys = Object.keys(xs);
// ^? const keys: string[]  而不是 number[]
```

2. **容易让人误解**：它会让你（或代码读者）误以为 JavaScript 真的支持数值属性键，而实际上不是。

3. **你很少需要自己写数值索引签名**：绝大多数情况下，你应该使用更精确的类型。

---

### 推荐的替代方案

#### 1. 使用 `Array<T>` 或元组类型

```typescript
// 普通数组
function sum(nums: number[]): number { ... }

// 固定长度的元组
type Point = [number, number];   // 索引 0 和 1
```

#### 2. 使用 `ArrayLike<T>`（当你需要接受类数组对象时）

如果你要写一个函数，它应该接受任何**有 `length` 属性和数值索引**的对象（比如 `NodeList`、`arguments` 等），可以使用 `ArrayLike<T>`：

```typescript
function checkedAccess<T>(xs: ArrayLike<T>, i: number): T {
    if (i >= 0 && i < xs.length) {
        return xs[i];   // ✅ 类型安全
    }
    throw new Error(`Index ${i} out of range`);
}

// 可以传入自定义类数组对象
const tupleLike: ArrayLike<string> = {
    '0': 'A',
    '1': 'B',
    length: 2,
};
checkedAccess(tupleLike, 0);   // 返回 "A"
```

**注意**：即使使用 `ArrayLike`，底层键仍然是字符串（`'0'`、`'1'`），但 TypeScript 允许你用数字索引访问。

#### 3. 使用 `Iterable<T>`（如果你只需要遍历）

如果你的函数只需要遍历元素，不需要随机访问索引，那么 `Iterable<T>` 是最宽松、最安全的选择：

```typescript
function logAll<T>(items: Iterable<T>): void {
    for (const item of items) {
        console.log(item);
    }
}

// 可以传入数组、生成器、Set、Map 等
logAll([1, 2, 3]);
logAll(new Set(['a', 'b']));
logAll(function*() { yield 10; yield 20; }());
```

---

### 对比总结

| 方案 | 适用场景 | 键的真实类型 |
|------|----------|--------------|
| `number[]` | 普通数组操作（需要修改、push等） | 字符串 |
| `[number, number]` 元组 | 固定长度，已知索引含义 | 字符串 |
| `ArrayLike<T>` | 类数组对象（有 length 和索引访问） | 字符串 |
| `Iterable<T>` | 只需要遍历，不需要索引 | 不关心键 |

---

### 书中示例完整翻译与解释

> **理解数组是对象，所以它们的键是字符串，而不是数字。将 `number` 用作索引签名纯粹是 TypeScript 为帮助捕获 bug 而设计的虚构。**

> 如果你抗拒使用 `Array` 类型，因为它有很多你可能不用的原型方法（如 `push`、`concat`），那说明你已经在用结构化的方式思考了，这很好！如果真需要接受任意长度的元组或任何类数组结构，可以用 `ArrayLike<T>`。

> 但记住：键仍然是字符串！
> ```typescript
> const tupleLike: ArrayLike<string> = {
>     '0': 'A',
>     '1': 'B',
>     length: 2,
> };
> ```

> **最后建议**：不要在你自己的类型中使用数值索引签名。优先使用 `Array`、元组、`ArrayLike` 或 `Iterable`。

---

### 实际操作中的注意事项

- 如果你设置 `noUncheckedIndexedAccess: true`（见 Item 48），TypeScript 会对数组访问进行更严格的检查，提醒你可能 `undefined`。
- 尽量**不要自己定义** `interface MyCollection { [index: number]: string }`，除非你确实在模拟一个真正的数值索引结构（比如链表或稀疏数组），但即使如此，`Map<number, string>` 通常是更好的选择。

---

### 一句话记忆

**JavaScript 对象没有真正的数字键 —— 数组的“数值索引”是语法糖。在 TypeScript 中，用 `Array`、元组、`ArrayLike` 或 `Iterable`，而不要自己写 `[n: number]: T`。**