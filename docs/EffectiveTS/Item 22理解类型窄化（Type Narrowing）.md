## Item 22: 理解类型窄化（Type Narrowing）—— 详解与示例

### 核心概念

**类型窄化**（也叫**细化**）是 TypeScript 根据代码的控制流（如条件判断、循环、异常等）将一个**宽泛的类型**（如联合类型）推断为**更具体的类型**的过程。

这是 TypeScript 相对于许多静态语言（C++, Java, Rust）的一个独特能力：同一个变量在不同的代码位置可以具有**不同的静态类型**。理解窄化可以让你写出更简洁、更安全的 TypeScript 代码。

---

## 1. 最常见的窄化：`null` 检查

```typescript
const elem = document.getElementById('what-time-is-it');
// ^? const elem: HTMLElement | null

if (elem) {
    elem.innerHTML = 'Party Time!';
    // ^? const elem: HTMLElement   ← 窄化成功，排除了 null
} else {
    elem;
    // ^? const elem: null
}
```

当 TypeScript 看到 `if (elem)` 时，它知道在 `true` 分支中 `elem` 不可能为 `null` 或 `undefined`，因此将类型从 `HTMLElement | null` 窄化为 `HTMLElement`。在 `else` 分支中，它知道 `elem` 一定是 `null`。

这种通过条件语句跟踪执行路径的能力称为**控制流分析**。

---

## 2. 常见的窄化方式

### 2.1 抛出异常或提前返回

```typescript
const elem = document.getElementById('what-time-is-it');
if (!elem) throw new Error('找不到元素');
elem.innerHTML = 'Party Time!';   // 此处 elem 类型为 HTMLElement
```

因为如果 `elem` 为 `null` 就会抛出异常，后续代码不可能执行到，所以窄化有效。

### 2.2 `instanceof`

```typescript
function contains(text: string, search: string | RegExp) {
    if (search instanceof RegExp) {
        return !!search.exec(text);   // search 窄化为 RegExp
    }
    return text.includes(search);     // search 窄化为 string
}
```

### 2.3 属性检查 (`in`)

```typescript
interface Apple { isGoodForBaking: boolean; }
interface Orange { numSlices: number; }

function pickFruit(fruit: Apple | Orange) {
    if ('isGoodForBaking' in fruit) {
        fruit;   // 窄化为 Apple
    } else {
        fruit;   // 窄化为 Orange
    }
}
```

### 2.4 内置函数，如 `Array.isArray`

```typescript
function contains(text: string, terms: string | string[]) {
    const termList = Array.isArray(terms) ? terms : [terms];
    // termList 的类型总是 string[]
}
```

### 2.5 字面量类型检查（`typeof`）

```typescript
function printAll(strs: string | string[] | null) {
    if (typeof strs === 'object') {
        // 注意：typeof null === 'object'，所以这里 strs 可能是 null
        // 因此类型仍然是 string[] | null，而不是 string[]
        for (const s of strs) {   // 报错：可能为 null
        }
    }
}
```

**陷阱**：`typeof null === 'object'` 是 JavaScript 的历史遗留问题。因此不能单独用 `typeof val === 'object'` 来排除 `null`。正确的做法是加上 `&& val !== null`。

### 2.6 显式标签（区分联合 / 可辨识联合）

```typescript
interface UploadEvent { type: 'upload'; filename: string; contents: string; }
interface DownloadEvent { type: 'download'; filename: string; }
type AppEvent = UploadEvent | DownloadEvent;

function handleEvent(e: AppEvent) {
    switch (e.type) {
        case 'download':
            // 这里 e 窄化为 DownloadEvent
            console.log(e.filename);
            break;
        case 'upload':
            // 这里 e 窄化为 UploadEvent
            console.log(e.contents.length);
            break;
    }
}
```

这是 TypeScript 中最常见的窄化模式，称为**标签联合**或**可辨识联合**。第 4 章会详细讨论。

---

## 3. 用户定义的类型保护（User-Defined Type Guards）

当 TypeScript 无法自动窄化时，你可以编写一个返回**类型谓词**的函数来帮助它。

```typescript
function isInputElement(el: Element): el is HTMLInputElement {
    return 'value' in el;
}

function getElementContent(el: HTMLElement) {
    if (isInputElement(el)) {
        return el.value;   // el 窄化为 HTMLInputElement
    }
    return el.textContent; // el 仍为 HTMLElement
}
```

**语法**：`parameterName is Type`。当函数返回 `true` 时，TypeScript 会将该参数的类型窄化为指定的类型。

**注意**：类型保护并不比类型断言（`as`）更安全——编译器不会检查函数体是否真的保证了这个类型关系。但你可以在类型保护内部编写更复杂的逻辑，并且可以在多处复用。

### 与 `filter` 一起使用

```typescript
const formEls = document.querySelectorAll('.my-form *');
const formInputEls = [...formEls].filter(isInputElement);
// formInputEls 的类型为 HTMLInputElement[]
```

TypeScript 能识别出 `filter` 使用了类型保护函数，并自动将结果数组的类型窄化。

---

## 4. 窄化常见陷阱与解决技巧

### 4.1 `Map` 的 `has` / `get` 问题

```typescript
const nameToNickname = new Map<string, string>();
let yourName = 'Alice';
let nameToUse: string;

if (nameToNickname.has(yourName)) {
    nameToUse = nameToNickname.get(yourName);   // 错误：可能 undefined
}
```

TypeScript 不知道 `has` 检查与后续 `get` 调用之间的关系。解决方法：将 `get` 结果存入变量，检查 `undefined`。

```typescript
const nickname = nameToNickname.get(yourName);
let nameToUse: string;
if (nickname !== undefined) {
    nameToUse = nickname;
} else {
    nameToUse = yourName;
}
```

更简洁的写法（空值合并运算符 `??`）：
```typescript
const nameToUse = nameToNickname.get(yourName) ?? yourName;
```

### 4.2 回调中的窄化失效

```typescript
function logLaterIfNumber(obj: { value: string | number }) {
    if (typeof obj.value === "number") {
        setTimeout(() => {
            console.log(obj.value.toFixed());   // ❌ 错误：obj.value 可能已是 string
        }, 100);
    }
}
```

**原因**：在 `setTimeout` 回调执行时，`obj.value` 可能已经被外部代码修改（例如 `obj.value = 'Cookie Monster'`）。TypeScript 无法保证窄化在异步回调中仍然有效，因此拒绝窄化。

**解决办法**：在回调之前提取值到局部变量（不变性）。

```typescript
if (typeof obj.value === "number") {
    const val = obj.value;   // 此时 val 类型为 number
    setTimeout(() => {
        console.log(val.toFixed());   // 安全
    }, 100);
}
```

---

## 5. 窄化与类型断言的关系

很多初学者遇到窄化不成功时会想用类型断言强制告诉 TypeScript 类型。**先别这么做！** 先检查窄化条件是否正确。例如：

```typescript
const elem = document.getElementById('foo');
if (typeof elem === 'object') {
    // 这里 elem 仍然是 HTMLElement | null，因为 typeof null === 'object'
    // 窄化失败！ 使用 if (elem !== null) 或 if (elem) 才对
}
```

TypeScript 的警告往往是有道理的。学会理解和信任窄化机制，可以让你避免很多 `as any`。

---

## 6. Things to Remember（书中总结）

- 理解 TypeScript 如何根据条件和其他控制流进行窄化。
- 使用标签联合（可辨识联合）和用户定义类型保护来辅助窄化。
- 思考是否可以重构代码，让 TypeScript 更容易跟随你的逻辑。

---

## 7. 补充示例：窄化与联合类型中的 `never`

结合 Item 59，你可以在 `switch` 的 `default` 分支使用 `never` 来确保所有情况都被处理：

```typescript
type Shape = Circle | Square;
function area(s: Shape) {
    switch (s.kind) {
        case 'circle': return Math.PI * s.radius ** 2;
        case 'square': return s.side * s.side;
        default:
            const _exhaustive: never = s;  // 如果漏掉某个情况，这里会报错
            return _exhaustive;
    }
}
```

这也是窄化的一种应用：`default` 分支中 `s` 的类型会被窄化为 `never`（因为所有可能的类型都已覆盖），从而触发检查。

---

**一句话总结**：**TypeScript 通过控制流分析，在条件分支中自动将联合类型窄化为更具体的类型，你还可以通过类型保护函数扩展这一能力；但要小心异步回调中的窄化失效以及 `typeof null` 的陷阱。**