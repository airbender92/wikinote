# @babel/runtime 作用

> 配套工具：`@babel/plugin‑transform‑runtime`（babel插件），**两者一般成对出现**。

## 解决什么问题

Babel 在转译 ES6+ 代码到 ES5 的时候，会产生两类东西：

1. **语法转译**：箭头函数、`class`、解构、扩展运算符等语法改写；
2. **工具辅助函数（helper）**：比如 `_classCallCheck`、`_defineProperties`、`_extends` 这些函数。

### ❌不使用 @babel/runtime 的问题

如果不开启插件，babel 会**在每一个文件头部重复生成一堆 helper 工具函数**。
多个文件，每个文件都复制一份相同helper，**打包体积膨胀，大量重复代码**。

示例：两个文件都用到 class，转译后每个文件都塞入一份 `_classCallCheck`。

### ✅@babel/runtime 方案

把这些通用 helper 抽成公共模块，**所有文件统一从 `@babel/runtime` 导入复用，不再重复内联到每个文件**，减少打包产物大小。

```js
// 不使用runtime：每个文件重复定义
function _classCallCheck(instance, Constructor) { ... }

// 使用runtime：统一导入
import { _classCallCheck } from '@babel/runtime/helpers/classCallCheck'
```

---

## 两个包区分（极易搞混）

1. **`@babel/runtime`**：**运行时依赖**，里面存放编译后的 helper 工具函数源码，打包进产物，生产环境需要。
2. **`@babel/plugin‑transform‑runtime`**：**babel编译插件（开发依赖 devDependencies）**，编译阶段，把代码里内联的helper，改成从 `@babel/runtime` import。

> 配置示例 babel.config.js

```js
module.exports = {
  plugins: [
    [
      "@babel/plugin-transform-runtime",
      {
        corejs: false, // 重点，控制是否处理polyfill
      },
    ],
  ],
};
```

## corejs 参数：polyfill 垫片能力

`@babel/runtime` **默认只处理 helper 工具函数，不处理 API polyfill**（比如 Promise、Array.prototype.includes）。

- `corejs: false`（默认）：只复用 helper，**不处理新API垫片**。
- `corejs: 3`：开启，使用 `@babel/runtime‑corejs3`，给实例方法、内置对象做 polyfill，**不会污染全局**。

> ⚠️开启 corejs:3 的时候，依赖包变成 `@babel/runtime‑corejs3`，不再是 `@babel/runtime`。

### 两种polyfill思路对比

1. **@babel/plugin‑transform‑runtime + runtime‑corejs3**
   - 按需导入垫片，**不污染全局变量**
   - ✅适合写 **库、组件库、SDK**，不能污染用户全局环境
   - ❌业务大项目一般不用这个做全局垫片

2. **`@babel/preset‑env` + useBuiltIns: 'usage'**
   - 会修改全局原型，污染全局
   - ✅适合业务项目应用

> 关键点：**写第三方库优先用 transform‑runtime + corejs3；业务应用一般用 preset‑env useBuiltIns**。

## 核心总结

1. **@babel/runtime = 存放通用helper函数的库**，避免每个文件重复生成helper，减少打包体积。
2. **@babel/plugin‑transform‑runtime**：编译插件，把内联helper替换成import这个包里的函数。
3. `corejs` 选项控制是否附带API polyfill；开启corejs3依赖变为 `@babel/runtime‑corejs3`。
4. 库/SDK：用它，避免全局污染；业务项目可以不用。

## 常见坑

1. 装了插件，忘记安装 `@babel/runtime`，运行报模块找不到。
2. 混淆 `devDependencies` 和 `dependencies`：
   - `@babel/plugin‑transform‑runtime` → devDependencies（编译用）
   - `@babel/runtime` / `@babel/runtime‑corejs3` → dependencies（运行时需要打进包）
3. corejs:3 不会填充全局，`Promise` 等全局构造函数不会被修改，只修改当前模块引用，适合库。
4. 和 `@babel/preset‑env` 不是互斥，可以同时存在，各司其职。

## 简单记忆

> helper重复多 → 上 `@babel/runtime` 抽公共函数；
> 写组件库SDK，不想污染全局 → 打开 `corejs:3`；
> 业务web项目，直接 preset‑env useBuiltIns。

如果你需要，我可以简单梳理 babel 整套体系：preset‑env、polyfill、runtime、corejs之间完整关系。
