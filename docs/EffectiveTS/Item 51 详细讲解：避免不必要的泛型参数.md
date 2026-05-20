## Item 51 详细讲解：避免不必要的泛型参数

这一节的核心是 **“泛型的黄金法则”**：**类型参数应该出现两次或以上**。  
如果一个类型参数在函数/类的类型签名中只出现一次（即没有与其他参数或返回值建立联系），那么它很可能是不必要的，甚至是有害的。这样的泛型参数不会带来类型安全，反而会干扰类型推断，给调用者带来困惑。

---

### 1. 黄金法则：类型参数用于关联多个值的类型

```ts
function identity<T>(arg: T): T
```

这里 `T` 出现在参数类型和返回值类型中，**出现了两次**。它建立了输入与输出之间的关系：返回值的类型与输入参数的类型相同。这是泛型的好用法。

相反：

```ts
function third<A, B, C>(a: A, b: B, c: C): C
```

- `C` 出现了两次（参数 `c` 和返回值），没问题。  
- 但 `A` 和 `B` 各只出现一次（只在参数位置，没有在其他地方使用），它们没有关联任何东西。  
- 因此这些是多余的泛型参数。完全可以简化为：

```ts
function third<C>(a: unknown, b: unknown, c: C): C
```

甚至如果 `a` 和 `b` 完全不被使用，也可以用 `unknown` 类型代替。

---

### 2. 危险的反模式：“仅返回泛型”（Return-Only Generic）

```ts
declare function parseYAML<T>(input: string): T;
```

`T` 只出现在返回值类型中。这等价于一个类型断言，但写法上像是“类型推导”，会给用户虚假的安全感。

```ts
const w: Weight = parseYAML('');  // 看起来安全，实际毫无检查
```

无论你期望什么类型（`Weight`、`Car`、`Person`），`parseYAML` 都会“通过”类型检查，因为 `T` 会被推断为你期望的类型。这实际上是一个隐藏的 `as any`。

**修复**：返回 `unknown`，强制调用者显式断言：

```ts
declare function parseYAML(input: string): unknown;
const w = parseYAML('') as Weight;
```

这样不安全操作是显式的，不会误导。

---

### 3. 区分必要和不必要的泛型参数：`printProperty` vs `getProperty`

#### 坏的例子：`printProperty`

```ts
function printProperty<T, K extends keyof T>(obj: T, key: K) {
  console.log(obj[key]);
}
```

- `K` 只出现了一次（在参数 `key` 的位置）。  
- 它没有用于返回值，也没有在其他地方建立关联。  
- 实际上，`key` 的类型只需要是 `keyof T` 即可，不需要额外的泛型参数 `K`。

**改进**：

```ts
function printProperty<T>(obj: T, key: keyof T) {
  console.log(obj[key]);
}
```

#### 好的例子：`getProperty`

```ts
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}
```

这里 `K` 出现了两次：一次在参数 `key` 的类型中，一次在返回值类型 `T[K]` 中。它建立了“键”与“值的类型”之间的关系，因此是必要的。

---

### 4. 类中的泛型参数

- 如果一个泛型参数被类的多个方法使用（例如 `ClassyArray<T>` 中的 `T` 出现在 `arr`、`get`、`add`、`remove` 中），那么它是必要的。  
- 如果泛型参数只在一个方法中使用，就应该将这个泛型移到方法级别，而不是整个类。

#### 坏例子：`Joiner<T>`

```ts
class Joiner<T extends string | number> {
  join(els: T[]) { ... }
}
```

`T` 只用于 `join` 方法，不用于其他方法或属性。因此应该把泛型移到方法上：

```ts
class Joiner {
  join<T extends string | number>(els: T[]) { ... }
}
```

但是，此时 `T` 在方法签名中只出现一次（参数 `els`），它仍然违反黄金法则。实际上，这个方法不需要泛型，可以直接用联合类型：

```ts
class Joiner {
  join(els: (string | number)[]) { ... }
}
```

进一步，如果这个类没有其他状态，完全可以简化为一个独立函数：

```ts
function join(els: (string | number)[]) { ... }
```

---

### 5. 不必要的约束：`getLength`

```ts
interface Lengthy { length: number; }
function getLength<T extends Lengthy>(x: T) { return x.length; }
```

`T` 只出现了一次（参数 `x`）。它没有建立任何关联。完全可以用 `Lengthy` 直接作为参数类型：

```ts
function getLength(x: Lengthy) { return x.length; }
```

或者更简单的结构类型：

```ts
function getLength(x: { length: number }) { return x.length; }
```

甚至直接用内置的 `ArrayLike<unknown>`。

---

### 6. 例外情况（很少见）

有时候，引入一个额外的泛型参数可以帮助实现某些需要约束的实现细节，但这种情况非常罕见。书中举例：

```ts
declare function processUnrelatedTypes<A, B>(a: A, b: B): void;
```

两个泛型参数各出现一次，显然是坏的。但如果你**在函数体内**需要禁止 `a` 和 `b` 互相赋值（即保持它们类型不同），那么保留这两个参数是有意义的。然而这种需求很少。通常直接用 `unknown` 即可。

---

### 7. 总结：如何判断是否必要？

| 场景 | 是否必要 | 原因 / 改进 |
|------|----------|--------------|
| `identity<T>(arg: T): T` | ✅ 必要 | `T` 出现两次，关联输入输出 |
| `third<A,B,C>(a:A,b:B,c:C):C` | ❌ A,B 多余 | 移除 A,B，用 `unknown` |
| `parseYAML<T>(...): T` | ❌ 危险 | 改为返回 `unknown`，强制断言 |
| `printProperty<T,K>(obj, key)` | ❌ K 多余 | 直接用 `keyof T` |
| `getProperty<T,K>(obj, key): T[K]` | ✅ 必要 | `K` 关联参数与返回值 |
| 类 `ClassyArray<T>` 多处使用 `T` | ✅ 必要 | 绑定整个类 |
| 类 `Joiner<T>` 只在 `join` 中使用 | ❌ 多余 | 移到方法、再简化为联合类型，甚至独立函数 |
| `getLength<T extends Lengthy>(x)` | ❌ 多余 | 直接用 `Lengthy` 类型 |

**黄金法则**：类型参数必须出现至少两次，否则它没有在关联任何东西。  
**第一条泛型规则**：不要轻易引入泛型；先问自己是否真的需要。

**最终建议**：避免“只是为了好玩”而添加泛型。每一次引入泛型参数，都应该是因为你需要用它来关联两个或更多位置上的类型。否则，使用具体类型（如 `unknown`、`object`、具体接口）会更简单、更清晰。