## 为什么 script 需要 `type="module"`

```html
<script type="module" src="/src/main.ts"></script>
```

### 核心原因

| 特性 | 普通 script | type="module" |
|------|------------|---------------|
| 语法 | 普通 JS | ES Module（import/export） |
| 作用域 | 全局 | 模块独立作用域 |
| 依赖加载 | 顺序执行 | 异步按依赖图加载 |
| 顶層 `this` | `window` | `undefined` |
| 自动严格模式 | ❌ | ✅ |

### 对比示例

```html
<!-- 普通脚本：所有变量挂载到 window -->
<script src="a.js"></script>
<script src="b.js"></script>
<!-- a.js 和 b.js 共享全局 window -->

<!-- 模块脚本：模块独立，import 是 ES 语法 -->
<script type="module" src="main.ts"></script>
```

### 实际效果

```javascript
// main.ts 中的代码
const name = 'Vue Demo'  // 不会污染 window

import { createApp } from 'vue'  // 只有 module 才支持 import
```

### 为什么 Vite 需要它？

Vite 使用 **ES Module** 开发模式：

```
浏览器请求 main.ts
    ↓
Vite 服务器拦截请求
    ↓
按需编译（不打包整个项目）
    ↓
返回 ES Module 给浏览器
```

如果去掉 `type="module"`，浏览器会报语法错误：`Unexpected token 'import'`

---

### 总结

`type="module"` 告诉浏览器：**"这是一段 ES Module 代码，请用模块方式解析"**。

需要继续了解 **路由配置** 吗？