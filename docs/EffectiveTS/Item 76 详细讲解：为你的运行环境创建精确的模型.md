## Item 76 详细讲解：为你的运行环境创建精确的模型

TypeScript 代码最终会被编译成 JavaScript 并在某个具体的运行时环境中执行（例如浏览器、Node.js、Deno、Electron 等）。不同的环境提供不同的全局对象、API 和语言特性。为了让 TypeScript 能够准确检查代码中使用的特性是否在目标环境中可用，你需要通过编译选项（如 `lib`）和类型声明文件（如 `@types/node`、自定义全局声明）来**构建一个精确的静态环境模型**。模型越准确，TypeScript 就越能帮助你捕捉错误。

---

### 1. 通过 `lib` 选项指定环境提供的 API

`tsconfig.json` 中的 `"lib"` 选项告诉 TypeScript 你的运行时环境提供了哪些内置的 JavaScript 功能和 DOM API。

```json
{
  "compilerOptions": {
    "lib": ["dom", "es2021"]
  }
}
```

- `"dom"`：包含浏览器 DOM 类型（`window`、`document`、`HTMLElement` 等）。
- `"es2021"`：包含 ES2021 及之前所有 JavaScript 标准库的类型（`Promise`、`Array.prototype.flatMap` 等）。如果你使用了 ES2022 的 `Array.prototype.toSorted()` 而 `lib` 只包含 `es2021`，TypeScript 会报错。

**原则**：根据你的**目标运行时**设置 `lib`。例如：
- 浏览器项目：通常包含 `"dom"` 和某个 ES 版本。
- Node.js 项目：一般不需要 `"dom"`，但可能需要 `"esnext"` 和特定的 `"node"` 类型（实际上 `@types/node` 会提供 Node.js API 类型，`lib` 只需包含 ES 部分）。
- 如果你不确定，可以使用 `"lib": ["esnext", "dom"]`，但这样可能允许某些在旧浏览器中不存在的特性。

---

### 2. 建模页面中的全局变量

当你的 TypeScript 代码运行在 HTML 页面中时，页面可能包含其他 `<script>` 标签定义的全局变量，或者加载了第三方库（如 jQuery、Google Analytics）。这些全局对象 TypeScript 默认不知道，需要你手动声明。

#### 2.1 自定义全局变量

假设页面中有内联脚本：

```html
<script>
  window.userInfo = { name: 'Jane Doe', accountId: '123-abc' };
</script>
```

你需要在 TypeScript 中声明这个全局变量：

```ts
// user-info-global.d.ts
interface UserInfo {
  name: string;
  accountId: string;
}

declare global {
  interface Window {
    userInfo: UserInfo;
  }
}
```

现在代码中可以安全地使用 `window.userInfo`，并获得类型检查和自动补全。

#### 2.2 第三方库

如果页面加载了 jQuery 或 Google Analytics，你需要安装对应的 `@types` 包：

```bash
npm install --save-dev @types/jquery @types/google.analytics
```

这会让 TypeScript 知道 `$` 或 `ga` 等全局函数的存在和类型。

**版本匹配**：确保 `@types` 包的版本与你在页面中实际加载的库版本兼容（参见 Item 66）。

---

### 3. 建模打包工具的特殊导入（如 webpack）

如果你使用 webpack 并允许导入图片、CSS 文件等，TypeScript 默认不知道这些模块的类型。你需要声明它们：

```ts
// webpack-imports.d.ts
declare module '*.jpg' {
  const src: string;
  export default src;
}

declare module '*.css' {
  const content: Record<string, string>;
  export default content;
}
```

这些声明告诉 TypeScript：当你从 `*.jpg` 文件导入时，会得到一个字符串（图片 URL），从 `*.css` 导入时得到一个包含类名映射的对象。这避免了“找不到模块”的错误。

---

### 4. 多环境建模：客户端 vs 服务器端

如果你的项目同时包含浏览器代码和 Node.js 代码（例如全栈应用），你应该使用**多个 `tsconfig.json` 文件**和**项目引用**（Item 78）来分别建模每个环境。

**目录结构示例**：

```
project/
├── tsconfig.base.json
├── tsconfig.client.json   # 浏览器环境
├── tsconfig.server.json   # Node.js 环境
├── client/                # 浏览器代码
└── server/                # 服务器代码
```

**`tsconfig.client.json`**：

```json
{
  "extends": "./tsconfig.base.json",
  "compilerOptions": {
    "lib": ["dom", "es2021"],
    "outDir": "./dist/client"
  },
  "include": ["client"]
}
```

**`tsconfig.server.json`**：

```json
{
  "extends": "./tsconfig.base.json",
  "compilerOptions": {
    "lib": ["es2021"],
    "types": ["node"],
    "outDir": "./dist/server"
  },
  "include": ["server"]
}
```

这样，浏览器代码可以使用 `window`、`document`，而服务器代码可以使用 `require`、`process`，彼此不会混淆。

---

### 5. Node.js 环境的精确建模

对于 Node.js 项目，除了设置 `"lib": ["es2021"]` 外，通常还需要安装 `@types/node`，并且版本应与实际运行的 Node.js 版本匹配。例如，Node.js 20 支持 `fetch` 和 `WebSocket` 全局对象，而 Node.js 16 不支持。安装对应版本的 `@types/node` 可以让 TypeScript 正确提示可用性。

```bash
npm install --save-dev @types/node@20
```

此外，如果你的代码运行在特定 Node.js 版本下（如 `--experimental-fetch`），需要在 `tsconfig.json` 中设置 `"lib": ["es2021", "dom"]` 吗？不需要，`fetch` 是 Node.js 18+ 的全局 API，`@types/node` 已经包含了。但仍需注意区分浏览器和 Node.js 的类型差异（例如 `Buffer` vs `Uint8Array`）。

---

### 6. 总结：如何创建精确的环境模型

| 环境要素 | 建模方法 | 示例 |
|----------|----------|------|
| 浏览器 DOM API | `"lib": ["dom"]` | `window`, `document` |
| ECMAScript 版本 | `"lib": ["es2021"]` | `Promise`, `Map`, `Array.prototype.flat` |
| 页面中的全局变量 | `declare global` 或 `.d.ts` 文件 | `window.userInfo` |
| 第三方库（jQuery等） | 安装 `@types/xxx` | `@types/jquery` |
| Webpack 导入（图片、CSS） | 模块声明 `declare module '*.jpg'` | 避免 import 错误 |
| Node.js 环境 | `"types": ["node"]` + `@types/node` | `process`, `Buffer` |
| 多环境（客户端/服务器） | 多个 `tsconfig.json` + 项目引用 | `client` 和 `server` 分开配置 |

**最终原则**：TypeScript 的类型检查器只知道你告诉它的环境信息。配置 `lib`、安装正确的 `@types`、声明自定义全局变量，这些都是为 TypeScript 提供准确“地图”的必要步骤。地图越精确，它就越能帮你避免使用运行时不可用的功能，减少因环境差异导致的错误。