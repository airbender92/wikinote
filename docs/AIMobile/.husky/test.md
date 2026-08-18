## 先给结论：**现在 husky + commitlint 已经完全跑通了！不再是脚本报错，是提交信息不规范被拦截。**

### 报错含义

```
⧗   --- input ---
ee
✖   subject may not be empty [subject-empty]
✖   type may not be empty [type-empty]
```

commitlint 采用规范提交格式（conventional-changelog），要求 commit message 格式：

```
<type>[optional scope]: <description>
```

你只写了 `ee`，缺少 **type 类型**，校验直接失败，阻止提交。

## 正确提交示例（直接复制测试）

```powershell
git commit -m "feat: 添加markdown文档"
```

### 常用 type 可选值

- `feat`：新功能
- `fix`：修复bug
- `docs`：文档修改（你当前新增md文件就用这个最合适）
- `style`：格式调整、空格、prettier格式化
- `refactor`：代码重构
- `test`：新增测试
- `chore`：构建、依赖、工程配置改动

你现在场景：新增markdown文档，推荐：

```powershell
git commit -m "docs: 新增静态目录markdown文件"
```

## 两个可选方案

### 方案1：遵守规范（推荐，保留commitlint作用）

以后提交统一使用 `type: 描述` 格式。

### 方案2：如果你暂时不想强制规范（不推荐）

修改 `commitlint.config.cjs`，放开严格校验，但是失去commitlint意义：

```js
module.exports = {
  extends: ["@commitlint/config-conventional"],
  rules: {
    "type-empty": 0,
    "subject-empty": 0,
  },
};
```

> 0 = 关闭规则；1 = 警告；2 = 报错阻止提交

## 梳理你一路踩坑全过程回顾

1. ❌ `.husky/commit-msg` 缺少 `#!/bin/sh` → 无法执行
2. ❌ 文件换行 CRLF → `No such file or directory`
3. ❌ `commitlint.config.js` 模块格式冲突（ESM/CJS）
4. ✅ 全部修复完成
5. ✅ **husky 钩子正常执行 commitlint**
6. ❌ 提交文案格式不符合规范 → 拦截

现在链路：
`git commit`

1. pre-commit → lint-staged → prettier 自动格式化md/json ✅
2. commit-msg → commitlint 校验提交信息 ✅（功能正常，只是内容不达标）

## 临时绕过校验（调试用，不建议长期）

```powershell
git commit -m "ee" --no-verify
```

你直接执行这条正常提交测试：

```powershell
git commit -m "docs: 添加markdown文档"
```
