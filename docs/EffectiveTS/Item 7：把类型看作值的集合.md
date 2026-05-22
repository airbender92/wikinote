## Item 7：把类型看作值的集合 —— 详细讲解

这个 Item 提出了一个看待 TypeScript 类型的全新（且极其有用）的视角：**一个类型就是一组可能的值的集合**。这个集合被称为该类型的 **“定义域”（domain）**。类型检查器大部分工作其实就是判断一个值是否属于某个集合，或者一个集合是否是另一个集合的子集。

理解了这个观点，你就能真正读懂 `extends`、`assignable`、`|`、`&`、`never`、`unknown` 等概念背后的统一逻辑。

---

## 1. 类型就是值的集合

在运行时代码中，每个变量都有一个具体的值（例如 `42`、`'Canada'`、`{animal: 'Whale'}` 等）。而在编译时，TypeScript 只知道这个变量可能取值的**范围**，这个范围就是它的类型。

- `number` 类型：所有数字的集合（无限大）。
- `string` 类型：所有字符串的集合。
- `null` 类型：只有一个值 `null` 的集合。
- 字面量类型 `'A'`：只有一个值 `"A"` 的集合。
- `never` 类型：**空集**，没有任何值。

```typescript
const x: never = 12;  // ❌ 12 不在空集中
```

> **关键**：一个变量能赋给某个类型，当且仅当它的实际值属于该类型的集合。  
> 一个类型 `T1` 能赋给类型 `T2`，当且仅当 `T1` 的集合是 `T2` 集合的**子集**。

---

## 2. 字面量类型与联合类型：有限集合

```typescript
type A = 'A';          // 集合 { "A" }
type B = 'B';          // 集合 { "B" }
type AB = 'A' | 'B';   // 集合 { "A", "B" }
type AB12 = 'A' | 'B' | 12;  // 集合 { "A", "B", 12 }
```

- 联合类型 `|` 对应集合的**并集**。
- `'C'` 是 `{ "C" }`，不是 `{ "A", "B" }` 的子集，所以不能赋给 `AB`。

```typescript
const a: AB = 'A';     // ✅ "A" ∈ { "A", "B" }
const c: AB = 'C';     // ❌ "C" ∉ { "A", "B" }
```

`assignable` 就是“子集”关系：

```typescript
const ab: AB = Math.random() < 0.5 ? 'A' : 'B';
const ab12: AB12 = ab;   // ✅ { "A", "B" } ⊆ { "A", "B", 12 }
const back: AB = ab12;   // ❌ { "A", "B", 12 } ⊈ { "A", "B" }，因为 12 不在后者中
```

---

## 3. 无限集合：通过描述定义

大多数类型是无限的。我们无法列出所有可能的 `string` 值，但可以通过“描述”来定义集合：

```typescript
interface Identified {
    id: string;
}
```

这个类型包含**所有具有 `id: string` 属性的对象**（不管它还有没有其他属性）。这就是结构类型系统的本质：只要形状兼容就属于该集合。

---

## 4. 类型操作：交集（&）与并集（|）

- `A & B`：集合的**交集**。一个值必须同时属于 `A` 和 `B` 的集合。
- `A | B`：集合的**并集**。一个值属于 `A` 或 `B` 即可。

书中例子：

```typescript
interface Person { name: string; }
interface Lifespan { birth: Date; death?: Date; }
type PersonSpan = Person & Lifespan;
```

初看 `Person` 和 `Lifespan` 没有共同属性，直觉上交集可能是空集。但因为对象可以有额外属性，所以一个同时拥有 `name`、`birth`、`death` 的对象就同时属于两个集合，因此它属于交集。

```typescript
const ps: PersonSpan = {
    name: 'Alan Turing',
    birth: new Date('1912/06/23'),
    death: new Date('1954/06/07'),
}; // ✅
```

### keyof 在交集和并集上的表现

- `keyof (A & B) = (keyof A) | (keyof B)`  
  因为交集中的值同时具有 A 和 B 的所有键。
- `keyof (A | B) = (keyof A) & (keyof B)`  
  因为并集中的值可能是 A 也可能是 B，只有那些在 A **和** B 中都存在的键才是安全的。

```typescript
type K = keyof (Person | Lifespan);  // never，因为 Person 和 Lifespan 没有共同键
```

---

## 5. `extends` = 子集关系

```typescript
interface PersonSpan extends Person { birth: Date; death?: Date; }
```

`extends` 在这里不是“继承”，而是“子集”：`PersonSpan` 的集合是 `Person` 集合的子集。每一个 `PersonSpan` 都有 `name` 属性（因为它是 Person 的子集），但反之不成立。

还可以改变属性的类型，只要新类型是原类型的子集：

```typescript
interface NullyStudent {
    name: string;
    ageYears: number | null;
}
interface Student extends NullyStudent {
    ageYears: number;   // ✅ number ⊆ number|null
}
```

如果尝试扩大（如 `number | string` 不是 `number|null` 的子集），就会报错。

---

## 6. 用维恩图理解类型关系

层级结构（子类/超类）容易误导，维恩图更准确：

- `Vector1D`（只有 x）⊇ `Vector2D`（x,y）⊇ `Vector3D`（x,y,z）。
- 但 `string|number` 和 `string|Date` 有重叠（string），却互不为子集。维恩图能清晰表达这种重叠关系。

---

## 7. 泛型约束中的 `extends`

```typescript
function getKey<K extends string>(val: any, key: K) { ... }
```

这里的 `K extends string` 要求 `K` 的集合必须是 `string` 集合的子集。所以 `K` 可以是 `"x"`（字面量）、`"a"|"b"`（联合）、`string` 本身，但不能是 `number`。

这与集合子集关系完全一致。

---

## 8. 数组与元组的集合视角

- `number[]`：所有数字数组的集合（长度任意）。
- `[number, number]`：恰好两个数字的元组的集合。

显然 `number[]` 不是 `[number, number]` 的子集（因为空数组、单元素数组都不在后者中）。所以不能赋值。反过来 `[number, number]` 是 `number[]` 的子集（每个二元组都是数组），所以可以赋值。

三元组 `[number, number, number]` 为什么不能赋值给二元组？  
因为 TypeScript 为元组增加了 `length` 属性，三元组的 `length` 是 `3`，而二元组的 `length` 是 `2`，所以不是子集。

---

## 9. `never` 与 `unknown`

- `never`：空集。没有任何值可以赋给它，但它可以赋给任何类型（空集是任何集合的子集）。
- `unknown`：全集（所有 JavaScript 值的集合）。任何类型都是它的子集，但它只能赋给自身和 `any`。

这两个构成了类型层次的两极。

---

## 10. 注意事项：不可变性（readonly）

`{code: number}` 和 `{readonly code: number}` 的**值集合完全相同**（都是包含一个数字 `code` 属性的对象）。但它们的“可允许操作”不同：前者可写，后者只读。所以类型不仅仅是值的集合，还包括**你能对这些值做什么**。这是该 Item 的唯一 caveat。

---

## 总结：集合视角下的 TypeScript 术语对照表

| TypeScript 术语 | 集合论术语 |
|----------------|------------|
| `never` | ∅（空集） |
| 字面量类型 | 单元素集合 |
| 值 `v` 可以赋给类型 `T` | `v ∈ T` |
| `T1` 可赋给 `T2` | `T1 ⊆ T2`（子集） |
| `T1 extends T2` | `T1 ⊆ T2` |
| `T1 \| T2` | `T1 ∪ T2`（并集） |
| `T1 & T2` | `T1 ∩ T2`（交集） |
| `unknown` | 全集 |

---

## Things to Remember（中文总结）

1. **把类型当作值的集合（定义域）**。  
2. 这些集合可以是有限的（如 `boolean`、字面量）或无限的（如 `string`、`number`）。  
3. TypeScript 的类型是**相交的维恩图**，而不是严格的树形层次。两个类型可以重叠而不互为子类型。  
4. 一个对象即使有额外未声明的属性，仍然可以属于该类型（结构性）。  
5. 类型操作应用在集合的定义域上：`A | B` 的定义域是 `A` 和 `B` 定义域的并集。  
6. `extends`、`assignable to`、`subtype of` 都是“子集”的同义词。

---

如果你希望我继续讲解其他 Item（例如 Item 8 关于类型空间与值空间，或者 Item 11 关于多余属性检查），请随时告诉我！