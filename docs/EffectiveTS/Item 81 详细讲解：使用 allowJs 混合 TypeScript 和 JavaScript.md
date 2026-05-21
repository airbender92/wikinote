## Item 81 详细讲解：使用 `allowJs` 混合 TypeScript 和 JavaScript

对于大型项目，不可能一次性将所有文件从 JavaScript 转换为 TypeScript。你需要一种**渐进迁移**的方式，让 TypeScript 和 JavaScript 文件能够互相导入、共存，并保证构建工具和测试框架仍然正常工作。TypeScript 的 `allowJs` 编译选项正是为此设计。

---

### 1. `allowJs` 的作用

在 `tsconfig.json` 中设置：

```json
{
  "compilerOptions": {
    "allowJs": true,
    "outDir": "./dist"
  },
  "include": ["src/**/*"]
}
```

- 允许 TypeScript 编译器处理 `.js` 文件。
- `.js` 和 `.ts` 文件可以互相 `import` 或 `require`。
- 对于 `.js` 文件，默认情况下**只检查语法错误**，不进行类型检查（除非同时使用 `// @ts-check`，见 Item 80）。
- 编译后，`.js` 文件会被复制或转换到 `outDir` 中。

**核心价值**：你可以逐步将 `.js` 重命名为 `.ts`，添加类型注解，而其他仍为 `.js` 的模块无需修改，项目整体仍可构建和运行。

---

### 2. 将 TypeScript 集成到构建工具链中

为了让 `allowJs` 真正生效，你需要确保你的构建工具（webpack、jest、Node.js 等）能够处理 TypeScript 文件。通常有两种方式：

- **通过加载器/插件**：让构建工具直接调用 TypeScript 编译器。
- **预编译**：先运行 `tsc` 生成 JavaScript，再让现有工具处理生成的代码。

#### 2.1 webpack + `ts-loader`

```bash
npm install --save-dev ts-loader
```

```js
// webpack.config.js
module.exports = {
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: 'ts-loader',
        exclude: /node_modules/,
      },
    ],
  },
  resolve: {
    extensions: ['.tsx', '.ts', '.js'],
  },
};
```

#### 2.2 Jest + `ts-jest`

```bash
npm install --save-dev ts-jest
```

```js
// jest.config.js
module.exports = {
  transform: {
    '^.+\\.tsx?$': 'ts-jest',
  },
};
```

#### 2.3 Node.js + `ts-node`

```bash
npm install --save-dev ts-node
```

运行时直接执行 TypeScript 入口文件：

```bash
node -r ts-node/register src/main.ts
```

或者使用 `ts-node` 命令：

```bash
ts-node src/main.ts
```

#### 2.4 自定义构建流程

如果构建流程是完全自定义的（例如使用 Makefile 或 shell 脚本），可以利用 TypeScript 的 `outDir` 选项：

```json
{
  "compilerOptions": {
    "outDir": "./dist",
    "allowJs": true
  }
}
```

运行 `tsc` 后，所有 `.ts` 和 `.js` 文件都会被编译/复制到 `./dist` 目录，保持原有的目录结构。然后你的现有构建流程直接针对 `./dist` 运行即可。你可能需要调整 `target` 和 `module` 选项，使生成的 JavaScript 与原有代码风格一致（例如都输出 CommonJS 模块）。

---

### 3. 迁移前的准备

在开始大规模迁移之前，**先让构建和测试工具能够无缝处理 TypeScript 文件**（即使还没有写任何类型注解）。这样，当你将第一个 `.js` 文件重命名为 `.ts` 时，不会破坏构建或测试。这个步骤的投入是值得的，因为它让你可以边迁移边验证正确性。

---

### 4. 与 `@ts-check` 的关系

- `allowJs` 允许混合使用 `.js` 和 `.ts`，但对 `.js` 文件默认不做类型检查。
- 如果你希望对 `.js` 文件进行类型检查（例如在迁移过程中发现潜在错误），可以在文件顶部添加 `// @ts-check`。这可以配合 `allowJs` 使用。
- 但理想情况下，当你将一个文件重命名为 `.ts` 并修正了类型错误后，就不再需要 `@ts-check` 了。

---

### 5. 迁移策略建议

1. **设置 `allowJs: true`**，并配置好构建工具和测试框架，确保它们能够处理 `.ts` 文件。
2. **从依赖关系图的底部开始**，逐个将 `.js` 文件重命名为 `.ts`，并修复类型错误（Item 82）。
3. **保持 `allowJs: true`** 直到所有 `.js` 文件都转换为 `.ts` 或确认无必要转换。
4. 当所有文件都是 `.ts` 后，可以关闭 `allowJs`（或保持开启，但已无实际作用）。

---

### 6. 注意事项

- **`allowJs` 不会自动为 `.js` 文件生成 `.d.ts`**。如果你需要将 `.js` 文件作为库发布，并希望其他 TypeScript 项目能获得类型，则需要单独生成声明文件（可以使用 `tsc --declaration --allowJs --emitDeclarationOnly`）。
- **性能**：处理大量 `.js` 文件会增加 TypeScript 编译时间，但通常可以接受。
- **与 Babel 等工具的关系**：如果你已经使用了 Babel 并配置了 TypeScript 预设，也可以达到类似效果。但 `allowJs` 是 TypeScript 原生支持的最简单方式。

---

### 7. 总结

- **`allowJs`** 是实现渐进迁移的关键：允许 `.ts` 和 `.js` 文件共存并互相引用。
- 在开始大规模重命名文件之前，**先确保构建和测试工具能够处理 TypeScript 文件**（通过加载器、`ts-node` 或预编译）。
- `allowJs` 本身不对 `.js` 文件进行类型检查，但可以配合 `@ts-check` 使用。
- 最终目标是关闭 `allowJs`，但在此之前它可以作为过渡期的桥梁，让你安全地、增量式地迁移项目。

**最终建议**：如果你正在计划将一个大型 JavaScript 项目迁移到 TypeScript，第一步不是急于重命名文件，而是让整个构建流程（包括测试、打包、运行）能够处理 TypeScript 代码。设置好 `allowJs` 并配置好工具链后，你就可以放心地逐个模块迁移了。