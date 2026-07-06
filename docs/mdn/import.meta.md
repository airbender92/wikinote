`import.meta` 是 ES 模块（ESM）里的**元信息对象**，用来获取当前模块自身的环境信息，只能在 **ES 模块** 中使用，CommonJS（`require`）里没有。

---

### 一、最常用属性

#### 1. `import.meta.url`
返回当前模块文件的 **完整 URL 路径**（类似浏览器里的 `document.currentScript.src`）。

```js
console.log(import.meta.url)
// 类似：file:///Users/xxx/project/foo.js
// 或 http://localhost:3000/foo.js
```

#### 2. `import.meta.resolve()`
解析相对路径为**绝对 URL**，常用于定位资源。

```js
const imgUrl = import.meta.resolve('./assets/logo.png')
```

---

### 二、在 Node.js 中的常见用法

#### 1. 替代 `__dirname` / `__filename`
Node ESM 中没有 `__dirname`，可以这样实现：
```js
import { fileURLToPath } from 'url'
import { dirname } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)
```

#### 2. 读取同目录文件
```js
import { readFileSync } from 'fs'
import { resolve } from 'path'

const data = readFileSync(resolve(__dirname, 'data.json'), 'utf8')
```

---

### 三、在浏览器 / 构建工具中

- Vite、Webpack、Rollup 都支持 `import.meta`
- Vite 扩展了常用环境变量：
  ```js
  import.meta.env.MODE
  import.meta.env.PROD
  import.meta.env.DEV
  import.meta.env.BASE_URL
  ```

---

### 四、使用限制
- 只能在 **顶层作用域** 或模块内使用
- 不能在 CommonJS（`.cjs` / `require`）中使用
- 老式浏览器不支持，需要打包工具转译

如果你是在 **Node、Vite、浏览器** 哪个环境用，我可以直接给你对应场景的完整可用代码。