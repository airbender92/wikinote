## Item 32 详细讲解：避免在类型别名中包含 `null` 或 `undefined`

这一节的核心是：**类型别名应该表示“一个东西”，而不是“一个东西或者可能没有”。** 如果在类型别名中混入 `null` 或 `undefined`，会让阅读代码的人产生误解 —— 他们看到 `User` 会认为它一定是一个用户对象，但实际它可能是 `null`。这种歧义会降低代码的可读性和可维护性。

---

### 1. 问题示例：`User` 到底是不是可能为 `null`？

考虑以下函数：

```ts
function getCommentsForUser(comments: readonly Comment[], user: User) {
  return comments.filter(comment => comment.userId === user?.id);
}
```

这里使用了可选链 `user?.id`。问题是：**`user` 真的可能为 `null` 或 `undefined` 吗？** 答案取决于 `User` 类型的定义。

**情况一：`User` 允许 `null`**

```ts
type User = { id: string; name: string; } | null;
```

此时 `user?.id` 是必要的，因为 `user` 可能是 `null`。但类型别名叫做 `User`，听起来应该是一个有效的用户，而不是一个可能缺失的值。

**情况二：`User` 不允许 `null`**

```ts
interface User {
  id: string;
  name: string;
}
```

那么 `user?.id` 就是多余的，因为 `user` 永远不会是 `null`。但只看函数签名，你无法判断，必须去查看 `User` 的定义。

**核心问题**：类型别名 `User` 的名称没有表达出“可能为 `null`”这一信息，导致读者需要跳转到定义才能理解。这违反了“自文档化”的原则。

---

### 2. 为什么不应该在类型别名中包含 `null`/`undefined`

- **误导性**：`User` 这个名字暗示它代表一个用户。如果它实际上是 `User | null`，那么它代表的可能是“没有用户”。两者语义不同。
- **增加认知负担**：读者每次看到 `User` 都要在心里记住“这个类型可能是 `null`”，或者被迫去查看定义。
- **降低可组合性**：如果你有一个 `User` 类型的变量，想要传给另一个期望 `User` 的函数，你可能会忘记检查 `null`，导致运行时错误。

**例外**：如果类型本身语义上就是“可空”的，那么应该用名字明确表达，比如 `NullableUser`。但更好的做法是直接用联合类型 `User | null`，而不是将其隐藏在别名中。

---

### 3. 正确做法：不要在顶层别名中包含 `null`/`undefined`

**错误示例**：

```ts
type User = { id: string; name: string } | null;   // ❌
type Config = { port: number } | undefined;        // ❌
```

**正确示例**：

```ts
interface User {
  id: string;
  name: string;
}

// 在使用时明确写出可为空
function getCommentsForUser(comments: readonly Comment[], user: User | null) {
  // ...
}
```

这样，函数的参数类型 `User | null` 一眼就能看出 `user` 可能为空，无需跳转定义。同时，`User` 本身仍然是一个纯净的、非空的类型，可以安全地用于其他不需要处理 `null` 的场景。

---

### 4. 特殊情况：可空属性 vs 可空对象

注意区分“对象的属性可能为 `null`/`undefined`”和“整个对象可能为 `null`/`undefined`”。

**可空的属性（可以接受）**：

```ts
type BirthdayMap = {
  [name: string]: Date | undefined;   // ✅ 属性值可能缺失
};
```

这里 `Date | undefined` 表示某个人的生日可能未知。这不影响 `BirthdayMap` 类型本身的含义 —— 它仍然是一个对象（非空），只是其属性值可能缺失。

**可空的对象（应当避免）**：

```ts
type BirthdayMap = {
  [name: string]: Date | undefined;
} | null;   // ❌ 整个映射可能为 null
```

这样做会让 `BirthdayMap` 这个名字产生歧义：它到底是一个映射，还是可能什么都不是？不如在使用时写成 `BirthdayMap | null`。

---

### 5. 为什么不用 `NullableUser` 别名？

你可能会想：那我定义 `type NullableUser = User | null` 不就好了？  
这样做虽然名称明确，但仍有缺点：

- 多了一个别名，增加记忆负担。
- 实际上 `User | null` 已经很清晰了，不需要额外的别名。
- 如果多处使用 `NullableUser`，你仍然无法一眼看出它和 `User` 的关系 —— 可能 `NullableUser` 里面还有别的花样。

书中建议：**直接使用 `User | null` 而不是为它起别名**。这样在函数签名中，可空性一目了然。

---

### 6. 总结

| 做法 | 评价 | 理由 |
|------|------|------|
| `type User = { id: string } \| null` | ❌ 避免 | 名称误导，隐藏了可空性 |
| `type NullableUser = { id: string } \| null` | ⚠️ 不推荐 | 别名多余，直接用 `User \| null` 更清晰 |
| `function f(user: User \| null)` | ✅ 推荐 | 可空性显式写在参数类型中 |
| `type Map = { [k: string]: string \| undefined }` | ✅ 允许 | 属性可空，但对象本身非空 |
| `type Map = { ... } \| null` | ❌ 避免 | 整个对象可空应显式写出 |

**最终建议**：  
- 让类型别名始终代表一个“非空、非未定义”的实体。  
- 在需要表示“可能没有”的地方，使用联合类型 `T | null` 或 `T | undefined`，并且写在最外层（如函数参数、变量类型），而不是隐藏在别名内部。  
- 这样代码的读者无需跳转就能理解可空性。