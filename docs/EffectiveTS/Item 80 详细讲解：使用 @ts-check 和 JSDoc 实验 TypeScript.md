## Item 80 详细讲解：使用 `@ts-check` 和 JSDoc 实验 TypeScript

在将大型 JavaScript 项目完全迁移到 TypeScript 之前，你可能希望先“试水”：了解类型检查会报告哪些问题，评估迁移的难度，而无需立即重写文件。TypeScript 提供的 `// @ts-check` 指令可以在普通的 `.js` 文件中启用类型检查，并结合 JSDoc 注释来标注类型。这是一种低成本的实验方式，能帮助你逐步为项目增加类型安全。

---

### 1. `@ts-check` 的基本用法

在 JavaScript 文件的第一行加上 `// @ts-check`，TypeScript 编译器（或编辑器语言服务）就会对该文件进行类型检查，就像它是一个 TypeScript 文件一样。

```js
// @ts-check
const person = { first: 'Grace', last: 'Hopper' };
2 * person.first; // 错误：算术运算右侧必须是 number、bigint 等，但 person.first 是 string
```

- 类型检查基于**类型推断**：`person.first` 被推断为 `string`，因此乘法操作报错。
- 无需添加任何类型注解，即可捕获许多常见错误（如属性名拼写错误、类型不匹配、函数参数个数错误等）。

**注意**：`@ts-check` 的严格程度甚至比 `noImplicitAny: false` 的 TypeScript 还要宽松一些，但已经能发现大量问题。

---

### 2. 常见错误类型及解决方案

#### 2.1 未声明的全局变量

如果代码中使用了在文件内未定义的全局变量（例如 HTML 页面中通过 `<script>` 定义的 `user` 对象），`@ts-check` 会报“找不到名称”的错误。

```js
// @ts-check
console.log(user.firstName); // 错误：找不到名称 'user'
```

**解决方案**：创建一个类型声明文件（例如 `globals.d.ts`），描述全局变量的类型。

```ts
// globals.d.ts
interface UserData {
  firstName: string;
  lastName: string;
}
declare let user: UserData;
```

确保 `tsconfig.json` 包含了该声明文件（如果没有 `tsconfig.json`，TypeScript 会自动包含 `.d.ts` 文件）。错误即消失。

#### 2.2 未知的第三方库

当你使用 jQuery、Lodash 等库时，TypeScript 不知道 `$` 或 `_` 等全局变量，需要安装对应的类型声明包。

```js
// @ts-check
$('#graph').style({ width: '100px' }); // 错误：找不到名称 '$'
```

**解决方案**：安装 `@types/jquery`

```bash
npm install --save-dev @types/jquery
```

安装后，`$` 被识别，但可能还会出现其他错误（例如 `style` 方法不存在，应为 `css`）。这正好帮助你发现 API 使用错误。

#### 2.3 DOM 元素类型不精确

`document.getElementById` 返回的类型是 `HTMLElement | null`，而许多具体元素属性（如 `value`）只存在于 `HTMLInputElement` 等子类型上。

```js
// @ts-check
const ageEl = document.getElementById('age');
ageEl.value = '12'; // 错误：HTMLElement 没有 value 属性
```

**解决方案**：使用 JSDoc 类型断言（因为 `.js` 文件中不能使用 `as` 语法）。

```js
const ageEl = /** @type {HTMLInputElement} */ (document.getElementById('age'));
ageEl.value = '12'; // OK
```

注意括号的位置：`/** @type {类型} */ (表达式)`，括号是必需的。

#### 2.4 不准确的现有 JSDoc

如果项目中已有 JSDoc 注释，但写得不对（例如参数类型错误、返回类型与实现不符），`@ts-check` 会暴露这些不一致。

```js
// @ts-check
/**
 * @param {Node} el
 * @return {{w: number, h: number}}
 */
function getSize(el) {
  const bounds = el.getBoundingClientRect(); // 错误：Node 上没有 getBoundingClientRect
  return { width: bounds.width, height: bounds.height }; // 错误：返回 { width, height } 不匹配 { w, h }
}
```

**解决方案**：修正 JSDoc 类型（将 `Node` 改为 `Element`，将返回类型改为 `{ width: number; height: number }`），或者直接删除错误的 JSDoc，让 TypeScript 自行推断。

---

### 3. 利用 JSDoc 添加类型注解

在 `.js` 文件中，你可以使用 JSDoc 的 `@param`、`@returns`、`@type` 等标签来提供类型信息，帮助 TypeScript 更准确地理解代码。

- **为函数参数和返回值添加类型**：

```js
// @ts-check
/**
 * @param {number} val
 * @returns {number}
 */
function double(val) {
  return 2 * val;
}
```

TypeScript 语言服务还提供了**快速修复**功能：当函数参数类型可以从使用中推断出来时，它会建议自动添加 JSDoc 注释（图 10-2）。

**注意**：自动生成的类型有时可能过于宽泛或奇怪（例如将 `data` 推断为包含 `files.forEach` 的复杂结构）。这提示你最好手动编写更精确的类型，或者直接转为 `.ts` 文件。

---

### 4. 注意事项与局限性

- **`@ts-check` 不是 TypeScript 的完全替代**：它的目标是帮助你渐进式地增加类型检查，但 JSDoc 语法比 TypeScript 类型注解更冗长，且无法表达所有 TypeScript 类型（如泛型约束、条件类型等）。
- **不要过度投资**：为整个项目写满 JSDoc 注释是成本很高的，而且最终你仍然需要将 `.js` 转换为 `.ts` 才能获得完整的 TypeScript 体验。因此，`@ts-check` 更适合作为**实验和评估工具**，而不是长期方案。
- **结合 `allowJs`**：当你开始正式迁移时，可以设置 `allowJs: true`，让 TypeScript 同时处理 `.js` 和 `.ts` 文件，然后逐步将 `.js` 重命名为 `.ts`（Item 81）。

---

### 5. 实践建议

1. **选择一个核心模块**：在项目中挑选一个不太复杂的 `.js` 文件，顶部加上 `// @ts-check`，观察报告的错误数量。
2. **处理三类错误**：
   - 添加全局声明文件（`.d.ts`）解决“找不到名称”。
   - 安装缺失的 `@types` 包。
   - 修正不准确的 JSDoc 或 DOM 类型断言。
3. **评估迁移成本**：如果错误数量可控，且修复后类型覆盖率明显提升，说明项目很适合迁移到 TypeScript；如果错误铺天盖地，可能需要先进行代码现代化（Item 79）。
4. **不要停留**：一旦你确认了迁移的价值，就应开始将文件从 `.js` 转换为 `.ts`，并移除 JSDoc 注解（或将其转为 TypeScript 类型注解），而不是永远停留在 JSDoc 阶段。

---

### 6. 总结

- **`// @ts-check`** 可以在不改变文件扩展名的情况下，对 JavaScript 文件启用类型检查。
- 它非常适合在迁移前**探测现有代码中隐藏的类型问题**，以及了解第三方库的类型质量。
- 配合 JSDoc 注解（`@type`、`@param` 等），可以逐步为代码添加更精确的类型。
- 但最终目标是**将 `.js` 改为 `.ts`**，因为 TypeScript 原生语法比 JSDoc 更简洁、强大，且便于长期维护。
- 使用 `@ts-check` 作为**过渡工具**，而不是永久解决方案。

**最终建议**：在决定全面迁移到 TypeScript 之前，用 `@ts-check` 做一次快速审计，它会告诉你哪里最容易出现问题，以及迁移的价值有多大。但不要花几周时间完善 JSDoc —— 当准备好时，果断转向 `.ts` 文件。