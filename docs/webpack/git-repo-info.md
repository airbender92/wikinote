**`git-repo-info`** 是一个轻量级的 **Node.js 库**，核心作用是**直接读取 `.git` 文件夹**来获取 Git 仓库信息，**无需依赖系统安装的 `git` 命令**。

### 一、核心特性
- **无外部依赖**：纯 JavaScript 实现，不调用 `git` 命令
- **自动查找**：从当前目录向上递归查找 `.git` 文件夹
- **信息全面**：支持分支、SHA、标签、提交人、提交信息等
- **轻量高效**：体积小、读取快，适合构建/CI 场景

### 二、安装
```bash
npm install git-repo-info
# 或
yarn add git-repo-info
```

### 三、基础用法
```javascript
const getRepoInfo = require('git-repo-info');

// 获取当前目录 Git 信息
const info = getRepoInfo();

console.log(info);
```

### 四、返回信息字段
| 字段 | 说明 |
| :--- | :--- |
| **branch** | 当前分支名（如 `main`/`master`） |
| **sha** | 完整提交哈希（40位） |
| **abbreviatedSha** | 短哈希（前10位） |
| **tag** | 当前提交的标签（无则 `null`） |
| **lastTag** | 最近的祖先标签 |
| **commitsSinceLastTag** | 距最近标签的提交数 |
| **committer** | 提交人姓名 |
| **committerDate** | 提交时间（ISO） |
| **author** | 作者姓名 |
| **authorDate** | 作者提交时间 |
| **commitMessage** | 最新提交信息 |
| **root** | 仓库根目录路径 |

### 五、进阶用法
#### 1. 指定路径
```javascript
// 读取指定目录的 Git 信息
const info = getRepoInfo('/path/to/your/repo/.git');
```

#### 2. 错误处理（非 Git 目录）
```javascript
const info = getRepoInfo();
if (!info.branch && !info.sha) {
  console.log('当前目录不是 Git 仓库');
}
```

### 六、典型应用场景
- **CI/CD 构建**：自动注入版本/分支信息到产物
- **版本生成**：基于 Git 信息生成版本号（如 `v1.2.3+5`）
- **开发工具**：IDE/CLI 插件显示仓库状态
- **日志/监控**：记录代码版本便于问题回溯

### 七、与原生 `git` 命令对比
- **`git-repo-info`**：纯 JS、无依赖、速度快、信息有限
- **原生 `git`**：功能最全、支持所有操作、需系统安装

### 八、注意事项
- 仅支持读取 **本地 Git 仓库**
- 不支持远程操作、提交、推送等写入功能
- 子模块/工作树（worktree）可正常读取

### 九、同类工具
- **`git-info`**：基于 `git` 命令，信息更全
- **`hosted-git-info`**：解析 GitHub/GitLab 等远程 URL

---

要不要我帮你写一个**可直接运行的完整示例**，包含**类型定义（TypeScript）**和**错误处理**，方便你直接集成到项目中？