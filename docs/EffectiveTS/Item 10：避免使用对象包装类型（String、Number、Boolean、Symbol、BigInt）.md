## Item 10：避免使用对象包装类型（String、Number、Boolean、Symbol、BigInt）—— 详细讲解

TypeScript 同时拥有**原始类型**（`string`、`number`、`boolean` 等）和它们对应的**对象包装类型**（`String`、`Number`、`Boolean` 等）。这两组类型在 TypeScript 中是不同的，新手（尤其是从 Java/C# 背景来的）很容易误用大写开头的包装类型，导致难以追踪的类型错误和运行时奇怪行为。本 Item 告诉你为什么要避免它们，以及如何正确使用原始类型。

---

## 1. JavaScript 中的原始值与对象包装器

JavaScript 有 7 种原始值类型：`string`、`number`、`boolean`、`null`、`undefined`、`symbol`、`bigint`。  
原始值的特点：
- 不可变（immutable）
- 没有方法（例如 `'abc'.charAt` 看起来像是方法，但实际上是临时包装）

### 字符串方法背后的真相

```javascript
'primitive'.charAt(3);  // 'm'
```

这能工作是因为当你在原始字符串上调用方法时，JavaScript **隐式地**将其包装成一个临时的 `String` 对象，调用方法，然后丢弃该对象。你可以通过修改 `String.prototype` 来观察：

```javascript
const originalCharAt = String.prototype.charAt;
String.prototype.charAt = function(pos) {
    console.log(this, typeof this, pos);
    return originalCharAt.call(this, pos);
};
'primitive'.charAt(3);
// 输出：[String: 'primitive'] object 3
// 然后返回 'm'
```

`this` 是一个 `String` 对象，而不是原始字符串。这说明隐式包装确实发生了。

### 直接实例化包装对象的陷阱

```javascript
"hello" === new String("hello");  // false（一个是原始值，一个是对象）
new String("hello") === new String("hello"); // false（两个不同对象）
```

### 给原始值添加属性会“消失”

```javascript
let x = "hello";
x.language = "English";
console.log(x.language); // undefined
```

解释：`x` 被临时包装成 `String` 对象，属性添加在该对象上，然后对象被丢弃。原始值本身没有变化。

---

## 2. TypeScript 中的区分

TypeScript 为每一种原始类型和对应的包装类型都定义了不同的类型：

| 原始类型（小写） | 包装类型（大写） |
|-----------------|-----------------|
| `string` | `String` |
| `number` | `Number` |
| `boolean` | `Boolean` |
| `symbol` | `Symbol` |
| `bigint` | `BigInt` |

**关键点**：
- 原始类型 `string` 可以赋值给包装类型 `String`（因为 JavaScript 可以自动装箱）。
- 包装类型 `String` **不能**赋值给原始类型 `string`（因为包装对象不是原始值）。

```typescript
let s1: string = "hello";
let s2: String = s1;     // ✅ string 可以给 String
let s3: string = s2;     // ❌ 错误：String 不能给 string
// 提示：'string' 是原始值，'String' 是包装对象。请尽可能使用 'string'
```

这也是 TypeScript 官方类型声明和几乎所有第三方库都使用小写原始类型的原因。

---

## 3. 意外使用大写包装类型的常见方式

### 3.1 显式类型注解

```typescript
const s: String = "primitive";   // 仍然赋值为原始值，但类型标注为 String
const n: Number = 12;
const b: Boolean = true;
```

TypeScript 允许这样做，因为原始类型可以赋值给包装类型。但这样的注解是**误导和冗余**的（参见 Item 18）。运行时值依然是原始值，但类型系统会认为它是包装对象，可能引发后续错误。

### 3.2 函数参数声明为包装类型

```typescript
function getStringLen(foo: String) {
    return foo.length;
}
getStringLen("hello");            // ✅ 原始值可以传入
getStringLen(new String("hello")); // ✅ 包装对象也可以
```

看上去没问题，但当你试图将 `String` 传递给期望 `string` 的函数时就会出错：

```typescript
function isGreeting(phrase: string) {
    return ['hello', 'good day'].includes(phrase);
}
const p: String = "hello";
isGreeting(p);   // ❌ 错误：String 不能赋值给 string
```

因此，**永远不要用 `String`、`Number`、`Boolean`、`Symbol`、`BigInt` 作为类型注解**。始终使用小写的原始类型。

---

## 4. `Symbol` 和 `BigInt` 的特殊情况

- 调用 `Symbol('sym')` 不需要 `new`，它返回 `symbol` 原始值。
- 调用 `BigInt(1234)` 也不需要 `new`，它返回 `bigint` 原始值。
- 可以使用 `123n` 字面量直接创建 `bigint`。

TypeScript 中的类型分别是 `symbol` 和 `bigint`（小写）。大写 `Symbol` 和 `BigInt` 代表包装对象类型，也应避免使用。

---

## 5. 为什么原始类型的方法调用能工作（回顾）

JavaScript 在底层做了自动装箱，但这是语言规范的一部分，我们不需要手动创建包装对象。因此，直接使用原始值就足够了。

---

## 6. ESLint 规则：`ban-types`

如果你使用 `typescript-eslint`，推荐启用 `ban-types` 规则（`@typescript-eslint/recommended` 中已包含）。它会禁止使用 `String`、`Number`、`Boolean`、`Symbol`、`BigInt` 作为类型名称，并提示使用小写版本。

---

## 7. 总结与记忆要点

| 类型种类 | 应使用 | 应避免 | 原因 |
|---------|--------|--------|------|
| 字符串 | `string` | `String` | 包装类型不兼容原始类型，且多余 |
| 数字 | `number` | `Number` | 同上 |
| 布尔 | `boolean` | `Boolean` | 同上 |
| 符号 | `symbol` | `Symbol` | 同上 |
| 大整数 | `bigint` | `BigInt` | 同上 |

**Things to Remember（中文）**

1. **避免使用 TypeScript 对象包装类型**。始终使用小写原始类型：`string`、`number`、`boolean`、`symbol`、`bigint`。
2. 理解对象包装类型是为原始值提供方法而存在的，但**不要直接实例化它们**（除了 `Symbol` 和 `BigInt` 作为函数调用时）。
3. 使用原始值已经足够，JavaScript 会自动装箱。
4. 使用 `typescript-eslint` 的 `ban-types` 规则来强制禁止错误的大写包装类型。

---

如果你想继续学习 Item 11（区分多余属性检查与类型检查），请告诉我！