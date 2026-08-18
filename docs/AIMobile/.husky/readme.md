`.husky` 目录是**半自动生成 + 半手写**的，分两层说：

## 1. 目录和文件从哪来
- `.husky/` 这个目录、`pre-commit`、`commit-msg` 这两个文件，是 husky 工具生成的（通常通过 `husky init` 或 `npx husky add` 命令创建），不是你从零手敲出来的。
- 但你项目里**这两个文件的内容是定制过的**，不是默认值。看 `package.json` 里的 `"prepare": "husky"`：每次 `pnpm install` 时 husky 会自动把 `.husky` 里的钩子链接到 `.git/hooks`，所以别人拉代码装依赖后钩子就自动生效，不用手动装。

> 注：`.husky/_/` 是 husky v9 的内部胶水文件（自动生成，别动）；你项目里它甚至提示 `DEPRECATED`，因为 v9 已经不需要再 `source husky.sh` 了，钩子直接写命令即可。另外你这里的钩子特意用 `node "$(git rev-parse --show-toplevel)/node_modules/xxx/bin/xxx.js"` 直接调用（而不是 husky 默认的 sh 包装），是为了绕过本地沙箱对 git 写 `.git` 的拦截——这是当初专门调过的。

## 2. 内容各干啥

**`.husky/pre-commit`**（提交前触发）：
```
node .../lint-staged/bin/lint-staged.js
```
→ 跑 `lint-staged`，只对你**本次暂存( staged )**的文件做处理：`*.ts/*.tsx` 跑 `eslint --fix` + `prettier --write`，`*.json/*.md/*.css/*.html` 跑 `prettier --write`。也就是提交前自动格式化+修 lint，且只动你改的文件，不会整库扫。

**`.husky/commit-msg`**（写提交信息时触发）：
```
node .../@commitlint/cli/cli.js --edit "$1"
```
→ 跑 `commitlint`，按 `commitlint.config.js` 里的规则校验提交信息必须符合 Conventional Commits 规范（`feat:`/`fix:`/`docs:`/`refactor:`… 等前缀）。不符合就直接**拒绝提交**。

## 一句话总结
它是 husky 生成的 Git 钩子目录，里面的两个文件分别负责：**提交前自动 lint+格式化暂存文件**，以及**强制提交信息走约定式规范**。目的就是让团队的代码风格和提交历史统一、自动化，少靠人肉复查。

-----

好问题，把"自动的"和"手动的"彻底分开讲。

## 一、自动生成用了什么命令

```bash
pnpm dlx husky init      # 或 npx husky init
```

它在你的项目里**自动**做了三件事（你不用手写）：

1. 创建 `.husky/` 目录和内部的 `.husky/_/husky.sh`（这个 `_` 是 husky 自己的胶水文件，**千万别改**）
2. 在 `package.json` 里加 `"prepare": "husky"` 脚本（这样别人 `pnpm install` 时钩子会自动挂上）
3. 生成一个**示例性的** `.husky/pre-commit`（默认是 `npm test` 之类的占位内容，等你替换）

> 注意：`husky` 依赖本身得先在 `devDependencies` 里（`pnpm add -D husky`）。你项目里它已经在 `package.json` 了，所以 `init` 只是把目录和脚本补齐。

## 二、生成之后，需要你手动按项目改/补的部分

`husky init` 只给了个空架子，**真正有用的东西都是手加的**：

| 文件/配置 | 自动生成？ | 你要手动做的事 |
|---|---|---|
| `package.json` 的 `prepare` 脚本 | ✅ 自动加 | 一般无需改 |
| `.husky/pre-commit` | ⚠️ 只有占位示例 | **替换成真命令**：`lint-staged` |
| `.husky/commit-msg` | ❌ 不生成 | **手动新建**：`commitlint` 命令 |
| `commitlint.config.js` | ❌ 不生成 | **手动新建**：继承 config-conventional + 你的规则 |
| `package.json` 的 `lint-staged` 字段 | ❌ 不生成 | **手动加**：指定哪些文件跑 eslint/prettier |
| 依赖 `lint-staged` / `@commitlint/cli` / `@commitlint/config-conventional` | ❌ 不装 | **手动安装** `pnpm add -D ...` |

所以"按项目修改"的本质就是：**钩子里挂什么命令、commitlint 用什么规则、lint-staged 管哪些文件——这些都因项目而异，husky 不会替你定。**

## 三、你这个项目里做的"非标准"修改

对比标准 husky 教程，你工程里有两处是**特意改过的**，不是默认值：

1. **钩子用 `node <root>/node_modules/xxx/bin/xxx.js` 直调**，而不是标准的 `npx lint-staged` / `npx commitlint`。
   - 标准写法：`npx --no-install commitlint --edit "$1"`
   - 你的写法：`node "$(git rev-parse --show-toplevel)/node_modules/@commitlint/cli/cli.js" --edit "$1"`
   - 原因：你本地有**沙箱拦截**，走 `npx` 的 PATH/shim 解析会出问题，改成 node 直接指绝对路径更稳。

2. **`commitlint.config.js` 里自定义了 `type-enum` 白名单**（就是上一条实测里 `wtf:` 被拒的那串）。默认 config-conventional 本身已限制类型，但你们把允许的类型明确列出来写死，更可控。

---

简单说：**`husky init` 只负责"通电"（建目录+挂 prepare），"接什么电器"（lint-staged / commitlint / 各自规则）全是你后来手配的。** 你项目现在的配置就是这条标准链路 + 一处为绕过沙箱做的 node 直调改造。

需要的话我可以把这套搭建步骤整理成一份 `docs/` 里的初始化说明文档，方便后面的人照着来。