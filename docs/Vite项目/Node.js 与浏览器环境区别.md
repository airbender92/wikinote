# Node.js 与浏览器环境的核心区别
一句话总结：**浏览器是面向“网页渲染 + 用户交互”的环境，Node.js 是面向“服务端/工具开发”的 JavaScript 运行时**，两者 API、权限、用途完全不同。

## 1. 全局对象不同
- **浏览器**：`window`（顶层对象）
- **Node.js**：`global`（新版也支持 `globalThis`）

共同全局：`console`、`setTimeout`、`Promise`、`Date` 等。

## 2. 可用 API 天差地别
### 浏览器独有（DOM/BOM）
- `document`、`getElementById`
- `window`、`location`、`history`
- `localStorage` / `sessionStorage`
- `XMLHttpRequest`、`fetch`
- 画布、音频、视频、WebGL 等

### Node.js 独有（系统/服务）
- 文件系统：`fs`
- 网络：`http` / `https` / `net`
- 进程：`process`、`child_process`
- 路径：`path`、`os`、`stream`
- 模块系统：`require`、`module.exports`、`__dirname`、`__filename`

## 3. 模块系统
- **浏览器**：
  - 早期无模块化
  - 现在支持 ES Module：`import / export`
- **Node.js**：
  - 默认 CommonJS：`require / module.exports`
  - 也支持 ES Module（`.mjs` 或设置 `type: module`）

## 4. 顶层 this 指向
- **浏览器全局作用域**：`this === window`
- **Node.js 模块作用域**：`this === exports`（不是 global）

## 5. 安全与权限
- **浏览器**：沙箱环境，**不能直接操作本地文件**，受同源策略限制
- **Node.js**：拥有系统级权限，可读写文件、创建服务、监听端口

## 6. 引擎与宿主
- 两者都用 **V8 引擎**解析 JS
- 浏览器额外加了**渲染引擎 + Web API**
- Node.js 额外加了 **libuv**（异步 I/O、事件循环）、底层系统调用

## 7. 事件循环差异
- 浏览器：宏任务（script、setTimeout、ajax）+ 微任务（Promise.then）
- Node.js：阶段更复杂（timers、pending callbacks、idle/prepare、poll、check、close callbacks），微任务执行时机与浏览器不完全一致

## 快速对比表
| 对比项         | 浏览器环境                  | Node.js 环境               |
|----------------|-----------------------------|----------------------------|
| 顶层对象       | window                      | global                     |
| DOM/BOM        | ✅ 有                        | ❌ 无                       |
| 文件操作       | ❌ 受限                      | ✅ fs 完全操作              |
| 网络能力       | ajax/fetch（受跨域限制）| http 服务器/客户端         |
| 运行用途       | 页面渲染、交互              | 服务端、CLI、工具、爬虫    |
| 模块化         | ES Module                   | CommonJS / ES Module       |

需要我给你一段**同时在浏览器和 Node 里运行、能看出差异的测试代码**吗？