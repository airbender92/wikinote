下面我把这篇 **MDN JavaScript Modules 完整知识点** 从头到尾**逐段精讲 + 例子拆解**，保证不遗漏任何关键内容，同时用更清晰、好理解的方式重讲一遍。

---

# 一、模块出现的背景：为什么需要 JS 模块？
早期 JS 代码量小，只做简单交互，不需要拆分。
现在前端/Node 全栈应用越来越大，必须：
- 把代码拆成独立文件
- 控制作用域，避免全局污染
- 按需加载，提升性能
- 方便复用、维护

历史上的模块方案：
- CommonJS（Node.js 使用）
- AMD（RequireJS）
- 打包工具：webpack、Babel

现代浏览器**原生支持 ES 模块（ESM）**，不需要编译也能跑。
但打包工具依然有用：代码分割、压缩、Tree Shaking 等。

---

# 二、官方示例结构
文章用一个**画布绘图**的小项目讲解：

```
index.html
main.js
modules/
    canvas.js    // 画布相关
    square.js    // 正方形相关
```

功能：
- `canvas.js`：创建画布、创建报告列表
- `square.js`：绘制正方形、计算面积/周长

---

# 三、.mjs 与 .js 的区别（重要坑点）
- `.mjs`：明确表示这是 ES 模块
- `.js`：默认是普通脚本，需要 `<script type="module">`

浏览器要求：
- 服务器必须返回正确 MIME 类型 `text/javascript`
- 很多服务器默认支持 `.js`，但不一定支持 `.mjs`

所以学习阶段**直接用 `.js` + `type="module"` 最稳妥**。

---

# 四、导出模块功能：export
## 1. 行内导出
直接在变量/函数前加 `export`：
```js
// square.js
export const name = "square";

export function draw(ctx, length, x, y, color) {
  ctx.fillStyle = color;
  ctx.fillRect(x, y, length, length);
  return { length, x, y, color };
}
```

## 2. 集中导出（更常用）
```js
// square.js
const name = "square";
function draw() {}
function reportArea() {}
function reportPerimeter() {}

export { name, draw, reportArea, reportPerimeter };
```

规则：
- 只能导出**顶层**声明，不能在函数/块里 export
- 可导出：function、var/let/const、class

---

# 五、导入模块功能：import
```js
// main.js
import { name, draw, reportArea, reportPerimeter } from "./modules/square.js";
```

## 模块路径规则
- `./`：相对当前文件
- `/`：网站根目录
- 绝对 URL 也可以

导入后就像本地定义一样使用：
```js
const square = draw(myCanvas.ctx, 50, 50, 100, "blue");
reportArea(square.length, reportList);
```

## 重要特性：导入是**只读视图（live binding）**
- 不能重新赋值导入的变量
- 但可以修改对象的属性
- 原模块可以更新导出值，导入处会同步变化

---

# 六、Import Maps（浏览器裸标识符）
浏览器默认**不支持裸包名**：
```js
import lodash from "lodash"; // 浏览器会报错
```

需要 import map 映射路径：
```html
<script type="importmap">
{
  "imports": {
    "square": "./modules/square.js",
    "lodash": "/node_modules/lodash/lodash.js"
  }
}
</script>
```

然后就能写：
```js
import { draw } from "square";
```

## import map 三大用途
1. 用**裸模块名**导入（像 Node 一样）
2. 路径前缀映射（批量重定向）
3. 版本管理（scopes）
4. 缓存优化：哈希文件名映射

## 作用域映射（scopes）
不同路径导入同一个包名，可以映射到不同版本：
```json
{
  "scopes": {
    "/node_modules/a/": {
      "lodash": "/v1/lodash.js"
    },
    "/node_modules/b/": {
      "lodash": "/v2/lodash.js"
    }
  }
}
```

---

# 七、导入非 JS 资源（Import Attributes）
语法：`with { type: ... }`

```js
// 导入 JSON
import colors from "./colors.json" with { type: "json" };

// 导入 CSS
import sheet from "./styles.css" with { type: "css" };
```

使用：
```js
document.adoptedStyleSheets = [sheet];
console.log(colors.blue);
```

---

# 八、在 HTML 中使用模块
必须加 `type="module"`：
```html
<script type="module" src="main.js"></script>
```

内联模块：
```html
<script type="module">
import { draw } from "./square.js";
</script>
```

普通 `<script>` 不能用 import/export。

## 预加载模块
```html
<link rel="modulepreload" href="modules/square.js">
```

---

# 九、模块 vs 普通脚本的核心区别（必背）
1. **自动严格模式（strict mode）**
2. **自动 defer**，不会阻塞 HTML 解析
3. **只执行一次**，无论引入多少次
4. **模块拥有独立作用域**，不污染全局
5. 必须在**HTTP/HTTPS** 运行，本地 `file://` 会跨域报错
6. 导入的变量**不在全局**，控制台无法直接访问

---

# 十、默认导出 vs 命名导出
## 1. 命名导出（前面讲的都是）
```js
export { a, b, c };
import { a, b } from "...";
```

## 2. 默认导出（一个模块只能一个）
```js
// square.js
export default function randomSquare() {}
```

导入时**不用大括号**：
```js
import randomSquare from "./modules/square.js";
```

等价于：
```js
import { default as randomSquare } from "...";
```

适合：模块只提供一个主要功能（类、主函数）

---

# 十一、命名冲突解决
## 方法 1：重命名导入/导出（as）
```js
import {
  name as squareName,
  draw as drawSquare
} from "./square.js";

import {
  name as circleName,
  draw as drawCircle
} from "./circle.js";
```

也可以导出时重命名：
```js
export { name as squareName }
```

## 方法 2：模块命名空间对象（最推荐）
```js
import * as Square from "./square.js";
import * as Circle from "./circle.js";

Square.draw(...)
Circle.draw(...)
```

干净、无冲突。

---

# 十二、模块 + Class
模块天然适合导出类：
```js
// square.js
class Square {
  constructor() {}
  draw() {}
}

export { Square };
```

导入：
```js
import { Square } from "./square.js";
const s = new Square(...);
```

---

# 十三、模块聚合（统一出口）
创建一个**入口模块**集中导出多个子模块：

```js
// shapes.js
export { Square } from "./shapes/square.js";
export { Circle } from "./shapes/circle.js";
export { Triangle } from "./shapes/triangle.js";
```

使用时只导入这一个：
```js
import { Square, Circle } from "./shapes.js";
```

适合做库的入口文件。

---

# 十四、动态导入（import()）
返回 Promise，**按需加载**：

```js
import("./modules/square.js").then((module) => {
  const square = new module.Square(...);
});
```

或 async/await：
```js
async function load() {
  const module = await import("./square.js");
}
```

用途：
- 路由懒加载
- 点击按钮再加载
- 普通脚本里使用模块

---

# 十五、顶层 await（仅限模块）
模块**顶层可以直接写 await**，不用包 async 函数。

```js
// getColors.js
const res = fetch("../colors.json");
const colors = res.json();

export default await colors;
```

导入它的模块会**等待数据加载完成**再执行，但不阻塞其他模块。

---

# 十六、import 声明会提升（hoisted）
```js
// 即使 import 写在后面也能用
const canvas = new Canvas();
import { Canvas } from "./canvas.js";
```

规范写法依然是：**import 全部放顶部**。

---

# 十七、循环依赖（Cyclic Imports）
```
a.js → b.js → a.js
```

不一定报错，取决于**何时访问变量**。

成功例子（异步访问）：
```js
// a.js
import { b } from "./b.js";
setTimeout(() => console.log(b));
export const a = 2;

// b.js
import { a } from "./a.js";
setTimeout(() => console.log(a));
export const b = 1;
```

失败例子（同步访问）：
```js
// b.js
import { a } from "./a.js";
console.log(a); // ReferenceError
```

尽量避免循环依赖，解决方案：
- 合并模块
- 抽公共代码到第三个模块
- 调整依赖方向

---

# 十八、同构模块（Isomorphic Modules）
能同时在**浏览器 + Node** 运行的模块。

做法：
1. 核心逻辑纯 JS，不依赖平台 API
2. 检测环境：`typeof window` / `typeof process`
3. 使用 `globalThis` 统一全局对象
4. 动态导入 polyfill

```js
const env = typeof window !== "undefined" ? "browser" : "node";
```

---

# 十九、常见排错指南
1. **file:// 协议报错**
   模块必须跑在 HTTP 服务器，不能直接打开 HTML。

2. **MIME 类型错误**
   服务器未正确返回 `text/javascript`。

3. **路径写错**
   相对路径必须以 `./` 或 `/` 开头。

4. **普通脚本用了 import**
   忘记加 `type="module"`。

5. **命名冲突**
   用 `as` 或命名空间 `* as mod` 解决。

---

# 二十、整篇文章核心总结（极简版）
- ES 模块用 `export`/`import`
- 两种导出：**命名导出**、**默认导出**
- 路径支持相对/绝对/import map
- 模块有独立作用域、严格模式、自动 defer
- 支持动态加载 `import()`
- 支持顶层 await
- 可导入 JSON/CSS
- 可聚合模块、重命名、命名空间
- 循环依赖要小心
- 本地必须用服务器运行

---

如果你需要，我可以：
- 把所有知识点整理成**一张速记脑图**
- 或出一套**JS 模块面试题 + 答案**
- 或带你**逐行手写一遍文章里的完整示例**


# 结论：**完全不需要必须写 node_modules/**
`scopes` 的 key 是**任意浏览器URL目录路径**，`node_modules` 只是工程里最常用的路径示例，不是规范强制要求。

## 一、scope 路径规则
1. scope 键是**网站URL绝对路径前缀**，必须以 `/` 开头、目录结尾加 `/`，代表该目录+全部子目录内所有JS文件。
2. **谁发起import、脚本自身URL在哪，就匹配哪个scope规则**，和文件夹名字无关。

## 二、大量非node_modules实战写法（可直接运行）
### 示例1：项目src目录区分版本
```html
<script type="importmap">
{
  "imports": {
    "axios": "/lib/axios-v1.6.js"
  },
  "scopes": {
    "/src/admin/": {
      "axios": "/lib/axios-v1.4.js"
    },
    "/src/test/": {
      "axios": "/mock/mock-axios.js"
    }
  }
}
</script>
```
- `/src/admin/**/*.js` 里`import axios` → v1.4
- `/src/test/**/*.js` → mock假接口
- 其余全局代码 → v1.6

### 示例2：微前端多子应用隔离（最常用）
```json
{
  "imports": { "react": "https://esm.sh/react@18" },
  "scopes": {
    "/app/legacy/": { "react": "https://esm.sh/react@17" },
    "/app/new/": { "react": "https://esm.sh/react@18" }
  }
}
```
老项目子目录用React17，新项目用18，**没有任何node_modules**。

### 示例3：分层业务目录
```json
"scopes": {
  "/pages/pay/": {"lodash": "/vendor/lodash4.js"},
  "/pages/user/": {"lodash": "/vendor/lodash3.js"}
}
```

## 三、补充两个关键细节
1. **路径匹配：最长路径优先**
```json
"scopes": {
  "/src/": {"utils": "/v1/utils.js"},
  "/src/admin/": {"utils": "/v2/utils.js"}
}
```
`/src/admin/xxx.js` 优先命中更长的`/src/admin/`规则。

2. **优先级：scope局部映射 > 顶层imports全局映射**
匹配不到scope才降级用外层`imports`配置。

## 四、什么时候才用 node_modules？
只有项目打包后依赖都放在`/node_modules/`目录时才写，**纯源码项目、CDN项目、src源码项目一律不用**。

需要我给你一套**无node_modules、完整可打开的HTML demo**吗？