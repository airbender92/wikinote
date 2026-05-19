## Item 33 详细讲解：将空值推到类型的边缘

这一节的核心是：**避免设计中一个值为空时另一个值也为空的隐式关系。相反，应把多个可能为空的值组合成一个整体，让这个整体要么完全为空，要么完全非空**。这样类型系统能更好地表达这种关系，减少错误。

书中通过两个例子来说明：一个是计算数值范围的 `extent` 函数，另一个是加载用户和帖子数据的 `UserPosts` 类。

---

### 例子一：计算一组数的范围（最小值/最大值）

#### 初始版本（有 bug 且类型不安全）

```ts
// @strictNullChecks: false
function extent(nums: Iterable<number>) {
  let min, max;
  for (const num of nums) {
    if (!min) {
      min = num;
      max = num;
    } else {
      min = Math.min(min, num);
      max = Math.max(max, num);
    }
  }
  return [min, max];
}
```

**问题分析**：

1. **当最小值或最大值为 0 时会被错误覆盖**  
   因为条件 `if (!min)` 会在 `min = 0` 时进入分支（`!0` 为 `true`），导致 min 和 max 被重置为当前的 `num`，而不是保留之前的 0。例如 `extent([0,1,2])` 会返回 `[1,2]` 而不是 `[0,2]`。

2. **空数组时返回 `[undefined, undefined]`**  
   没有元素，循环不执行，min 和 max 保持初始的 `undefined`。返回的数组中两个元素都是 `undefined`，但类型推断（在 `strictNullChecks: false` 下）为 `number[]`，掩盖了问题。

3. **隐式关系丢失**  
   实际上，要么两个都是 `undefined`，要么两个都是 `number`。但类型系统没有表达这种关系，调用者不得不分别检查两个元素是否为 `undefined`，容易出错。

#### 开启 strictNullChecks 后暴露问题

```ts
function extent(nums: Iterable<number>) {
  let min, max;   // 类型为 any
  for (const num of nums) {
    if (!min) {
      min = num;
      max = num;
    } else {
      min = Math.min(min, num);  // 错误：min 可能为 undefined
      max = Math.max(max, num);  // 错误：max 可能为 undefined
    }
  }
  return [min, max];  // 返回类型为 (number | undefined)[]
}
```

调用代码：

```ts
const [min, max] = extent([0,1,2]);
const span = max - min;  // 错误：max 和 min 可能为 undefined
```

现在问题变得明显，但修复的方法（例如在 `else` 分支里也加上 `if (min !== undefined)`）会使代码更复杂，且仍然没有解决“两者要么都有值，要么都没有”的表示问题。

#### 改进方案：将 min 和 max 放入一个对象，该对象整体可为空

```ts
function extent(nums: Iterable<number>) {
  let minMax: [number, number] | null = null;
  for (const num of nums) {
    if (!minMax) {
      minMax = [num, num];
    } else {
      const [oldMin, oldMax] = minMax;
      minMax = [Math.min(num, oldMin), Math.max(num, oldMax)];
    }
  }
  return minMax;
}
```

**改进点**：

- `minMax` 是一个 **要么是 `[number, number]` 元组，要么是 `null`** 的联合类型。空值（`null`）被“推”到了整个对象的层面。
- 如果数组非空，`minMax` 始终是一个包含两个数字的元组，不会出现一个为 `undefined` 另一个为数字的情况。
- 返回值类型现在是 `[number, number] | null`，明确表达了“要么有一对值，要么什么都没有”。

**调用方使用示例**：

```ts
const range = extent([0,1,2]);
if (range) {
  const [min, max] = range;
  const span = max - min;  // 安全
} else {
  console.log('empty array');
}
```

或者使用非空断言（如果确信数组非空）：

```ts
const [min, max] = extent([0,1,2])!;
const span = max - min;
```

**优点**：
- 消除了 `0` 被错误覆盖的 bug。
- 类型系统强制调用者处理空数组的情况（检查 `null`）。
- 代码逻辑清晰，关系显式。

---

### 例子二：类中混用 null 和非 null 属性

#### 糟糕的设计

```ts
class UserPosts {
  user: UserInfo | null;
  posts: Post[] | null;

  constructor() {
    this.user = null;
    this.posts = null;
  }

  async init(userId: string) {
    return Promise.all([
      async () => this.user = await fetchUser(userId),
      async () => this.posts = await fetchPostsForUser(userId)
    ]);
  }

  getUserName() {
    // 这里需要判断 this.user 是否为 null
  }
}
```

**问题**：

- `user` 和 `posts` 都是可为空的属性，且它们的空值状态密切相关：要么都未加载，要么都加载完成，或者一个加载了一个未加载？实际上，由于两个请求是并发的，存在四种可能的组合。
- 任何一个方法（如 `getUserName`）都必须检查 `this.user` 是否为 `null`，并且还要考虑 `this.posts` 可能也是 `null` 的情况。
- 这种复杂性会扩散到整个类，代码中会充满大量的 `if (this.user && this.posts)` 检查。
- 更重要的是，**类在构造后并不是处于可用状态**，必须先调用 `init` 方法。这破坏了“构造即有效”的原则。

#### 改进方案：将所有依赖的数据准备好后再构建对象

```ts
class UserPosts {
  user: UserInfo;
  posts: Post[];

  constructor(user: UserInfo, posts: Post[]) {
    this.user = user;
    this.posts = posts;
  }

  static async init(userId: string): Promise<UserPosts> {
    const [user, posts] = await Promise.all([
      fetchUser(userId),
      fetchPostsForUser(userId)
    ]);
    return new UserPosts(user, posts);
  }

  getUserName() {
    return this.user.name;  // 不需要检查 null
  }
}
```

**改进点**：

- `user` 和 `posts` 都是**非空**属性。
- 构造函数要求所有必需的数据都已准备好，因此构造出的实例总是有效的。
- 异步初始化逻辑封装在静态工厂方法 `init` 中，它返回一个 `Promise<UserPosts>`。
- 类的方法不再需要处理部分加载的状态，简单且类型安全。

**注意**：如果你确实需要支持部分加载的状态（例如展示加载进度条），那么你可能需要保留多个状态。但即使如此，也应该使用可辨识联合（Item 29）来精确建模，而不是让多个可为空的属性独立存在。

---

### 核心原则总结

1. **避免隐式关联的空值**  
   如果两个值要么同时为 `null`，要么同时非 `null`，不要用两个独立的可为空变量。应把它们打包成一个对象，该对象整体可为空。

2. **将空值推到“边缘”**  
   让函数的输入/输出或类的顶层属性体现可空性，内部则保持非空。例如 `extent` 返回 `[number,number] | null`，而不是 `(number|undefined)[]`。

3. **构造即有效**  
   类的构造函数应该接收所有必需的非空数据，而不是先创建一个“空壳”再通过异步方法填充。异步初始化使用静态工厂方法。

4. **不要用 `Promise` 替代可为空属性**  
   给属性赋 `Promise` 会让类的方法全部变成异步，且仍然需要处理未完成的状态，并没有真正解决问题。

**最终建议**：当你在代码中看到多个可空变量时，停下来思考它们是否应该被组合成一个单一的可空对象。这样能让类型系统更好地帮助你，也让代码更易懂。