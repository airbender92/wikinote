## Item 73 详细讲解：使用 Source Maps 调试 TypeScript

TypeScript 代码最终会被编译成 JavaScript 运行。当出现 bug 时，你看到的错误栈、断点位置都指向生成的 JavaScript 文件，而不是你写的 TypeScript 源码。直接调试生成的 JS 非常痛苦，尤其是当编译器进行了大量转换（如将 `async/await` 转为状态机、降级语法）后，JS 代码与 TS 源码几乎无法对应。

**Source Map（源映射）** 解决了这个问题。它是一种映射文件（`.js.map`），记录了生成代码与原始代码之间的位置对应关系。支持 Source Map 的调试器（浏览器 DevTools、VS Code 等）可以让你直接在 TypeScript 源码上设置断点、查看变量，仿佛在运行 TS 代码一样。

---

### 1. 问题演示：没有 Source Map 的调试困境

#### 简单示例（TS → JS 基本对应）

```ts
// index.ts
function addCounter(el: HTMLElement) {
  let clickCount = 0;
  const button = document.createElement('button');
  button.textContent = 'Click me';
  button.addEventListener('click', () => {
    clickCount++;
    button.textContent = `Click me (${clickCount})`;
  });
  el.appendChild(button);
}
addCounter(document.body);
```

编译后（`target="ES5"`）生成的 JS 与 TS 非常相似，勉强可以对应。但即使如此，你也不希望在调试时看到 `var _this = this` 之类的代码。

#### 复杂示例：`async/await` 导致 JS 面目全非

```ts
// index.ts
async function addCounter(el: HTMLElement) {
  let clickCount = 0;
  const button = document.createElement('button');
  button.textContent = 'Click me';
  button.addEventListener('click', async () => {
    clickCount++;
    const response = await fetch(`https://numbersapi.com/${clickCount}`);
    const trivia = await response.text();
    // ... 显示 trivia
  });
}
```

编译到 ES5 时，`async/await` 会被转换为状态机，生成的 JS 包含 `__awaiter`、`__generator` 等辅助函数，与原始 TS 源码几乎无法对照。直接调试 JS 会非常困难。

---

### 2. 开启 Source Map

在 `tsconfig.json` 中设置：

```json
{
  "compilerOptions": {
    "sourceMap": true
  }
}
```

运行 `tsc` 后，每个 `.ts` 文件会生成：

- `.js` 文件（编译后的 JavaScript）
- `.js.map` 文件（Source Map）

例如 `index.ts` → `index.js` 和 `index.js.map`。

`.js` 文件的末尾会包含一条注释指向对应的 source map：

```js
//# sourceMappingURL=index.js.map
```

浏览器或 Node.js 调试器会读取该文件，从而将执行位置映射回 TypeScript 源码。

---

### 3. 在浏览器中调试 TypeScript

开启 source map 后，在 Chrome DevTools 中：

- **Sources 面板**中会出现原始的 `.ts` 文件（通常以斜体显示，表示它来自 source map，而非真实网络资源）。
- 你可以直接在 `.ts` 文件上设置断点、单步执行，查看变量值——全部基于原始源代码。
- 错误堆栈也会指向 `.ts` 文件的行号。

**注意**：如果使用了打包工具（webpack、vite 等），它们可能也会生成 source map。需要确保 source map 链条完整：TypeScript → JS → 打包后的 bundle，并且最终映射回原始 TS。大多数现代打包工具开箱即支持。

---

### 4. 在生产环境使用 Source Map 的注意事项

- **性能**：浏览器仅在打开 DevTools 时才会下载 source map，对普通用户无性能影响。
- **内联 source map**：如果将 source map 直接嵌入 JS 文件（`inlineSourceMap` 选项），会增加 JS 体积，不推荐生产环境使用。
- **隐私与安全**：source map 可能包含原始 TypeScript 源码（如果设置为 `"sourceMap": true` 且未去除）。如果你不希望暴露源代码（例如专有逻辑、敏感注释），则不应在生产环境部署 source map，或者使用工具生成只包含行号映射但不包含源码内容的 source map（但大多数工具不支持）。通常建议：生产环境**不部署 source map**，或者仅在内部错误监控系统（如 Sentry）中使用。

---

### 5. 在 Node.js 中调试 TypeScript

Node.js 也支持 source map，可以通过 Chrome DevTools 或 VS Code 进行调试。

#### 步骤：

1. **编译 TypeScript**：确保 `tsconfig.json` 中 `"sourceMap": true`。
2. **运行 Node 并启用 Inspector**：
   ```bash
   node --inspect-brk dist/bedtime.js
   ```
   - `--inspect-brk` 会在第一行暂停，等待调试器连接。
3. **打开 Chrome**，访问 `chrome://inspect`，在 “Remote Target” 列表中看到你的 Node 进程，点击 “inspect”。
4. **DevTools 打开后**，你会看到生成的 JavaScript。但是因为 source map 的存在，你可以在 Sources 面板中找到原始的 `.ts` 文件（通常在一个 `webpack://` 或 `file://` 的树中）。
5. **在 TypeScript 源码中设置断点**，然后恢复执行，即可像在浏览器中一样调试。

**替代方案**：使用 VS Code 的内置调试器（`.vscode/launch.json` 配置 `"sourceMaps": true`），可以直接在编辑器中调试 TypeScript。

---

### 6. 类型声明的 Source Map（`declarationMap`）

如果你发布了一个 TypeScript 库，并希望其他开发者在“跳转到定义”时能够直接看到 TypeScript 源码（而不是生成的 `.d.ts` 文件），可以启用 `declarationMap`：

```json
{
  "compilerOptions": {
    "declaration": true,
    "declarationMap": true
  }
}
```

这会在生成 `.d.ts` 的同时生成 `.d.ts.map` 文件，使得编辑器可以映射回原始的 `.ts` 源码，极大提升使用体验。

---

### 7. 总结与最佳实践

- **始终在开发环境中启用 source map**：可以显著提高调试效率。
- **确保 source map 链条完整**：如果使用打包工具，检查其 source map 配置，保证最终映射到原始 TypeScript 源码。
- **生产环境谨慎部署**：默认不部署 source map，除非你有充分的理由（如需要生产环境错误溯源）且不介意暴露源码。可使用 `"sourceMap": false` 或单独移除 `.map` 文件。
- **利用 `debugger` 语句**：在 TS 源码中写入 `debugger;` 会在运行到该行时自动中断，配合 source map 非常方便。

**最终建议**：把 Source Map 视为 TypeScript 调试体验的必备组件。开启它，你就再也不用面对那些难以阅读的编译后 JavaScript 了。