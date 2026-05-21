## Item 65 详细讲解：将 TypeScript 和 @types 放在 devDependencies 中

### 1. npm 依赖类型回顾

在 `package.json` 中，npm 定义了三种主要的依赖类型：

- **`dependencies`**  
  生产环境依赖。这些包是**运行你的代码所必需的**。例如 `react`、`lodash` 等。当别人通过 `npm install` 安装你的包时，`dependencies` 中的包也会被一并安装（传递性依赖）。

- **`devDependencies`**  
  开发环境依赖。这些包只在**开发、测试、构建**时需要，而**不需要在生产环境中运行**。例如测试框架（jest）、打包工具（webpack）、代码检查工具（eslint）以及 **TypeScript 编译器**本身。当你发布一个包时，`devDependencies` 不会被传递给使用你包的用户。

- **`peerDependencies`**  
  同伴依赖。当你写一个插件或组件库时，你需要的某个包（如 React）应该由**使用者自行提供**，而不是由你指定版本并打包进去。这样可以避免多个版本冲突。

---

### 2. TypeScript 应该放在 `devDependencies` 中

#### 原因 1：TypeScript 是开发工具，不是运行时依赖

TypeScript 编译器（`tsc`）以及 TypeScript 语言服务只在**编译时**使用。一旦你的代码被编译成 JavaScript，运行时就不再需要 TypeScript 了。这与 `dependencies` 的定义冲突——`dependencies` 中的包是“运行代码所必需的”，而 TypeScript 不是。

#### 原因 2：避免全局安装的问题

有些人习惯于 `npm install -g typescript` 全局安装 TypeScript。这样做有两个主要问题：

- **版本不一致**：团队成员或 CI 环境可能安装了不同版本的 TypeScript，导致类型检查结果不一致，甚至出现“在我机器上能通过”的问题。
- **项目环境依赖**：新成员 clone 项目后，除了 `npm install` 还需要额外安装全局工具，增加了设置步骤。

将 TypeScript 作为 `devDependency` 安装后，每个项目都有自己的 TypeScript 版本，运行 `npm install` 就会自动安装，并且 `npx tsc` 会使用项目本地的版本，保证一致性。

---

### 3. `@types` 也应该放在 `devDependencies` 中

`@types` 包（例如 `@types/react`、`@types/lodash`）只包含**类型声明文件**（`.d.ts`），不包含任何实际的 JavaScript 代码。这些类型仅在**开发/编译阶段**需要，运行时完全不需要。

- **运行时不需要**：编译后的 JavaScript 代码中，所有类型都被擦除了（Item 3），因此运行时不会依赖类型包。
- **避免传递性依赖**：如果你将 `@types` 放在 `dependencies` 中，那么任何依赖你包的用户（即使是纯 JavaScript 用户）都会被强制安装这些类型包，增加不必要的下载体积和 node_modules 膨胀。

因此，正确的做法是：

```bash
npm install react
npm install --save-dev @types/react
```

最终 `package.json` 中：

```json
{
  "dependencies": {
    "react": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.23",
    "typescript": "^5.2.2"
  }
}
```

---

### 4. 即使你不发布库（例如只构建 Web 应用），也有好处

有些人认为，既然 Web 应用最终部署的是编译后的 JavaScript，并且不会作为 npm 包被其他人安装，那么 `dependencies` 和 `devDependencies` 的区别就不重要了。但实际上依然有好处：

- **生产镜像更小**：如果你的部署流程使用 `npm install --production`（只安装 `dependencies`），那么 TypeScript 和 `@types` 不会被安装，减少了 `node_modules` 的大小，加快容器启动速度。
- **依赖更新工具更智能**：像 Renovate 或 Dependabot 这样的工具可以区分生产依赖和开发依赖，优先更新生产依赖（安全补丁更重要）。将 TypeScript 和 `@types` 放在 `devDependencies` 中可以避免它们干扰生产依赖的更新策略。

---

### 5. 注意事项

- 有些库（例如某些用 TypeScript 编写的库）会在其发布包中**自带类型声明**（通过 `package.json` 中的 `"types"` 字段）。这种情况下你不需要额外安装 `@types`，但 TypeScript 本身依然应该放在 `devDependencies`。
- 如果你正在开发一个**供他人使用的 TypeScript 库**，应该将 `@types` 放在 `devDependencies` 中，并在文档中告知用户如果需要类型则自行安装对应的 `@types`（或者使用自带的类型）。这样可以避免强制下游用户安装不必要的类型包（Item 70 会进一步讨论如何切断类型依赖）。

---

### 6. 总结（Things to Remember）

- **理解 `dependencies` 与 `devDependencies` 的区别**：前者是运行时必需的，后者只在开发/构建时需要。
- **将 TypeScript 放在 `devDependencies` 中**，不要全局安装。这样可以确保团队使用一致的版本，并且简化项目初始化。
- **将 `@types` 也放在 `devDependencies` 中**，因为类型在运行时被擦除，并且不应该传递给你的用户。
- 即使是 Web 应用，区分依赖类型也有助于减小生产镜像体积和优化依赖更新。

通过遵循这一条目的建议，你可以保持项目的依赖结构清晰、可移植，并避免给使用者带来不必要的负担。