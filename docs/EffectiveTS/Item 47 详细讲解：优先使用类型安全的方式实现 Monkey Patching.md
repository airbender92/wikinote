## Item 47 详细讲解：优先使用类型安全的方式实现 Monkey Patching

这一节的核心是：**JavaScript 允许在运行时给任何对象（包括内置对象、DOM 元素、全局对象）添加属性，这种做法被称为“猴子补丁”（monkey patching）。在 TypeScript 中，直接使用 `(window as any).user = ...` 虽然能绕过类型检查，但会失去类型安全和编辑器支持。更好的做法是使用**接口合并（declaration merging）** 或 **自定义交叉类型** 来安全地建模这些补丁。**

书中通过几个例子逐步展示了从最差到最好的解决方案。

---

### 1. 什么是 Monkey Patching？

JavaScript 的对象是“开放的”，你可以随时添加新属性：

```ts
window.monkey = 'Tamarin';          // 给全局 window 添加属性
document.monkey = 'Howler';         // 给 document 添加属性

const el = document.getElementById('colobus');
el.home = 'tree';                    // 给 DOM 元素添加属性
```

甚至可以在内置原型上添加方法（非常危险，不推荐）：

```ts
RegExp.prototype.monkey = 'Capuchin';
/123/.monkey;  // 'Capuchin'
```

**问题**：
- 这些属性变成隐式全局变量，难以追踪，容易引起命名冲突。
- 代码难以测试和维护，因为修改了全局状态。
- 在 TypeScript 中，类型系统不知道这些新属性，会报错。

---

### 2. 最简单但最不安全的方式：`as any`

```ts
(document as any).monkey = 'Tamarin';  // 类型错误消失
```

**缺点**：
- 完全失去类型检查：拼写错误（`monky`）不会报错。
- 赋值错误类型（如 `boolean`、`RegExp`）也不会被捕获。
- 编辑器无法提供自动补全、重命名等语言服务。
- `any` 会污染后续使用该对象的地方。

书中明确说：这“设定了安全和开发体验的低标准”，我们应该做得更好。

---

### 3. 方案一：使用接口合并（declaration merging）

TypeScript 的 `interface` 可以重复定义并自动合并。我们可以利用这一点来告诉 TypeScript `Window` 类型上新增了一个属性。

```ts
// global-augmentation.d.ts 或任意 .ts 文件（但需要在模块中或使用 declare global）
declare global {
  interface Window {
    user: User;   // 新增属性
  }
}
```

之后就可以直接使用 `window.user`，不再需要 `as any`。

```ts
window.user = user;          // OK
alert(`Hello ${window.user.name}`);  // 类型检查通过
```

**优点**：
- 类型安全：拼写错误或类型错误会被捕获。
- 可以添加 TSDoc 注释，鼠标悬停时显示文档。
- 支持自动补全和重命名。
- 明确记录了补丁的内容。

**缺点**：
- 这是**全局**的，影响整个项目。如果用户只在部分页面存在，全局声明会误导类型系统。
- 无法处理“在运行时可能未设置”的竞态条件（例如在赋值前读取 `window.user`）。

**改进**：将属性类型设为 `User | undefined`，强制调用方检查：

```ts
declare global {
  interface Window {
    user: User | undefined;
  }
}
```

这样 `window.user.name` 就会报错，提醒你处理 `undefined` 情况。

**另一个缺点**：如果你无法在页面加载时立即设置（例如通过内联脚本），这种声明会掩盖真实的竞态条件。

---

### 4. 方案二：使用内联脚本提前设置（适用于特定场景）

如果服务器端能够将用户数据直接注入 HTML，可以在 TypeScript 代码运行前就设置好 `window.user`：

```html
<script>
  window.user = { name: 'Bill Withers' };
</script>
<script src="your-code.js"></script>
```

这样就不需要 `undefined` 选项了，因为 `window.user` 在代码执行前已存在。但这依赖于服务端架构，不是通用方案。

---

### 5. 方案三：使用自定义交叉类型 + 局部类型断言（避免全局污染）

如果你不想修改全局 `Window` 类型（因为某些页面不需要该属性，或者你想让补丁仅限于当前模块），可以定义一个自定义类型：

```ts
type MyWindow = typeof window & {
  user: User | undefined;
};
```

然后在需要访问的地方使用类型断言：

```ts
(window as MyWindow).user = user;   // 赋值时断言
alert(`Hello ${(window as MyWindow).user?.name}`);  // 使用时断言
```

**优点**：
- 不污染全局的 `Window` 类型定义，作用域更可控。
- 仍然有类型检查（只要你不滥用 `any`）。

**缺点**：
- 每次使用 `window.user` 都需要写类型断言，比较繁琐。
- 仍然需要手动处理 `undefined`（这里已包含 `undefined`）。
- 无法防止团队成员在其他地方直接使用 `(window as any).user`，需要通过代码审查或 linter 规则禁止。

---

### 6. 对 DOM 元素的 Monkey Patching

同样适用于 DOM 元素。例如，给一个按钮添加自定义属性：

```ts
const btn = document.getElementById('myButton');
btn.home = 'tree';  // 错误：HTMLElement 上没有 home 属性
```

**不安全的方式**：`(btn as any).home = 'tree'`。

**类型安全的方式**：使用接口合并（针对 `HTMLElement` 接口）：

```ts
declare global {
  interface HTMLElement {
    home?: string;
  }
}
```

或者使用自定义类型断言：

```ts
type MyButton = HTMLElement & { home?: string };
(myBtn as MyButton).home = 'tree';
```

但注意，这些属性也会出现在所有 `HTMLElement` 上，可能不是你想要的。因此更推荐局部自定义类型。

---

### 7. 最佳建议：避免 Monkey Patching

无论是全局对象还是 DOM 元素，猴子补丁本质上是一种不良设计。书中强烈建议：

> Prefer structured code to storing data in globals or on the DOM.

也就是说，应该使用模块化的状态管理（例如 Store、Context、依赖注入）来替代将数据挂载到 `window` 或 DOM 元素上。只有在不得已（例如迁移遗留代码、必须与第三方库集成）时才使用上述类型安全方法，并且尽量限制在局部范围。

---

### 8. 核心原则总结

| 方法 | 类型安全 | 全局污染 | 使用便利性 | 推荐度 |
|------|----------|----------|------------|--------|
| `as any` | ❌ 无 | ✅ 实际污染（但类型系统不记录） | 简单 | ❌ 不推荐 |
| 全局接口合并 | ✅ 有 | ✅ 全局 | 直接访问 | ⚠️ 可接受，需注意作用域 |
| 全局合并 + `undefined` | ✅ 有 | ✅ 全局 | 直接访问 | ⚠️ 较好，但强制检查 |
| 内联脚本预定义 | ✅ 有 | ✅ 全局 | 直接访问 | ✅ 最佳（如果可行） |
| 局部交叉类型断言 | ✅ 有 | ❌ 无 | 每次使用需断言 | ✅ 适合模块化场景 |
| 重构为结构化代码 | ✅ 有 | ❌ 无 | 需要重新设计 | ✅✅ 最佳长期方案 |

**最终建议**：除非无法避免，否则不要使用猴子补丁。如果必须使用，优先选择**局部交叉类型断言**或**全局接口合并加上 `undefined`**，并确保添加注释说明原因。同时，通过代码审查和 linter 规则禁止出现 `as any` 的写法。