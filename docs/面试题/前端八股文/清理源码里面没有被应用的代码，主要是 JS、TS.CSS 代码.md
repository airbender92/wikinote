# 清理源码未使用代码（JS/TS/CSS）

俗称**死代码清理（dead‑code elimination DCE）**，分为三类：

1. JS/TS：未引用变量、函数、导入、组件；
2. CSS：未被DOM使用的样式类；
3. 手动遗留：注释掉代码、废弃文件。

> 注意：**动态调用、动态class、运行时反射会让工具识别不出来，会误杀，不能完全依赖工具自动删，要人工复核。**

## 一、JS / TS 未使用代码清理

### 1. IDE 基础检测（VSCode）

VSCode内置TS语言服务，无需插件：

- 未使用 import、变量、函数：**灰色显示**
- 鼠标悬浮提示 `'xxx' is declared but its value is never read`

操作：

1. 快速修复：`Ctrl+.` → `Remove unused imports` 一键删除未使用导入。

> ⚠️局限：
>
> - 只能检测当前文件静态未使用；**跨文件、动态调用识别不到**；
> - 导出的函数/组件，IDE无法判断外部有没有引用，不会标灰。

### 2. 构建工具层面：Tree‑Shaking（Webpack / Vite / Rollup）

> Tree‑Shaking：**打包阶段移除没有被 import 引用的 ES Module 代码**
> 前提：必须是 `ESModule(import/export)`；**CommonJS(require)不支持tree‑shaking**。

Vite/Rollup 默认开启tree‑shaking；Webpack生产模式开启。

> ⚠️Tree‑shaking 只作用于**打包产物**，**不会修改你源码文件！**
> 只是打包的时候不带入死代码，源码里废弃代码依旧存在，源码清理不能只靠tree‑shaking。

### 3. 专业工具：ESLint + 插件（源码层面检测）

安装eslint规则检测未使用变量、导入：

```json
// .eslintrc
{
  "rules": {
    "no‑unused‑vars": "warn",
    "@typescript‑eslint/no‑unused‑vars": "warn"
  }
}
```

运行 eslint，输出所有未使用变量。

> 解决未使用import：`eslint‑plugin‑import`
> 可以配合脚本自动删除未使用import：`eslint‑fix`。

### 4. 找整个项目未被引用的文件（非常重要）

找出项目里**完全没有被任何地方import的ts/js文件**，这些是废弃文件。
工具：`unimported`（前端项目很常用）

```bash
npm i unimported -D
npx unimported
```

输出报告：

- files：哪些文件从未被导入；
- dependencies：哪些package从未使用；

> ⚠️注意：
> 入口文件、配置文件、vue路由动态导入、glob批量导入会误报，需要人工过滤，不要直接批量删除。

### 5. 边界坑 JS/TS

下面这些情况工具识别不出，会误判为“已使用”或“未使用”

1. 动态调用：`obj[fnName]()`；字符串反射调用；工具静态分析看不出来。
2. 导出 `export function xxx(){}`，仅用于后端接口、仅用于浏览器控制台调试；工具认为可能外部使用，不会标记未使用。
3. 动态组件：`component: isDynamicComp`。
4. 注释掉的大块代码：工具识别不了，需要人工删除，不要留在源码。

> 实践建议：导出的废弃函数不要只注释，直接删除；git有历史记录。

## 二、CSS / SCSS / Less 清理：查找未使用样式

CSS难点：很多class是JS动态拼接、动态绑定，静态工具容易误删。

### 1. PurgeCSS（最主流）

> PurgeCSS：扫描你的模板/JS，收集页面出现的class名称，把css里面没有出现的class剔除。
> ⚠️同样：**默认只修改打包产物，不会修改源文件**。

配合Vite插件：`vite‑plugin‑purgecss`
webpack：`purgecss‑webpack‑plugin`

> 如果想要**直接清理源码css文件**，PurgeCSS不做这个，它只处理构建输出。

### 2. 源码层面识别无用CSS工具：`stylelint`

stylelint 可以检测部分无用css规则：

```json
{
  "rules": {
    "no‑empty‑source": true,
    "block‑no‑empty": true
  }
}
```

只能清理空规则，**无法识别class有没有被业务代码使用**。

### 3. 工程实践：怎么安全清理源码CSS

没有工具可以100%安全直接删源码CSS，推荐流程：

1. 开启PurgeCSS打包；构建产物中被purge掉的css类，**标记为可疑废弃**。
2. 在源码中搜索这个className：
   - 如果全局搜索（包括vue/js/ts）完全搜不到这个class → 大概率废弃，可以删除源码css；
   - 如果JS有动态拼接 `'item‑' + type`，不能删。

> ❌千万不要直接工具批量删除源码CSS，动态class很容易删错样式。

### 4. Chrome DevTools 手动检测单页面

打开开发者工具 → Coverage(覆盖率)

- 可以看到当前页面哪些JS、CSS代码**没有运行/没有生效**。

> 局限：只针对当前打开页面；多页面要逐个测，适合局部排查。

## 三、完整落地工作流（团队真实做法）

> 原则：**工具输出可疑列表，人工复核，禁止工具全自动批量删除源码！**

1. **JS/TS**
   1. VSCode + ESLint：清理文件内部未使用变量、import；
   2. `unimported` 扫描项目，拿到从未被导入的文件列表；
   3. 对可疑文件：全局搜索文件名，确认没有动态导入、没有作为入口；确认后删除；
   4. git提交，方便回滚。

2. **CSS/SCSS**
   1. 构建阶段开启PurgeCSS，得到打包阶段被丢弃的样式列表；
   2. 对每一个被丢弃class，**全局全文搜索项目代码**，确认没有出现该class字符串；
   3. 确认无动态拼接后，再删除源码css。

3. 额外清理
   - 删除文件内大块注释掉的代码；
   - 清理无用console.log、debugger；eslint可以配置禁止debugger；
   - 清理package.json未使用依赖（`npx depcheck`）。

## 四、高危场景，工具会误删，一定要人工检查

1. JS
   - 动态导入 `import(`${path}`)`
   - 动态函数调用 `obj[key]()`
   - 导出给外部使用的公共API
   - 单元测试文件

2. CSS
   - JS动态拼接className：`const cls = 'card‑' + status`
   - vue :class 对象动态绑定
   - 组件库第三方class、html原生class
   - 媒体查询、打印样式，某些页面才会触发的样式

## 五、工具清单汇总

| 工具            | 作用                        | 是否修改源码    |
| --------------- | --------------------------- | --------------- |
| VSCode TS检测   | 未使用变量、import          | 手动修复才改    |
| ESLint          | 检测未使用变量/导入         | --fix可修复源码 |
| unimported      | 查找项目未被引用的JS/TS文件 | 只输出报告      |
| depcheck        | 查找package.json无用依赖    | 报告            |
| PurgeCSS        | 打包阶段移除未使用CSS       | 只修改构建产物  |
| Chrome Coverage | 查看当前页面未执行JS/CSS    | 仅查看          |
| Stylelint       | 清理空css规则               | 可修复源码      |

## 面试简答

> 清理源码未使用代码分为JS/TS和CSS：
>
> 1. JS/TS：
>
> - VSCode、ESLint检测文件内未使用变量、import；Tree‑Shaking只是打包移除死代码，**不会改动源码**。
> - 使用 `unimported` 扫描出项目完全没有被import的文件；注意动态导入、导出API会造成误报，人工复核后删除。
> - CommonJS不支持tree‑shaking。
>
> 2. CSS：
>
> - PurgeCSS可以在打包产物剔除未使用样式，但**不能直接清理源码**；
> - 拿到被剔除样式后，全局搜索源码确认没有动态class拼接，再手动删除源码CSS；Chrome覆盖率可以辅助查看页面未生效样式。
>
> 3. 风险：动态调用、动态class、字符串拼接会让静态分析工具识别失败，**禁止工具全自动批量删除源码，工具输出可疑列表，人工复核后再清理，利用git保障回滚**。

如果你需要，我可以给一份 vite + unimported + purgecss 的最简配置示例。
