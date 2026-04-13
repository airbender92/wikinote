# `__dirname` 到底是什么？（Webpack 必用）
`__dirname` 是 **Node.js 中的全局变量**，不是浏览器变量，**只在 webpack 配置文件里用**。

## 1. 核心含义
- **当前文件所在的【绝对路径】**
- 永远返回**完整的文件夹路径**（不包含文件名）
- 不随运行位置改变，**路径稳定可靠**

---

## 2. 举个例子
如果你的项目结构：
```
my-project/
  webpack.config.js   ← __dirname 在这里
  src/
    index.js
  dist/
```

在 `webpack.config.js` 里打印：
```javascript
console.log(__dirname)
```

输出结果（Mac/Linux）：
```
/Users/xxx/my-project
```

输出结果（Windows）：
```
C:\Users\xxx\my-project
```

---

## 3. 为什么 Webpack 必须用它？
因为 Webpack 的 `output.path` **必须是绝对路径**，不能写相对路径。

✅ 正确写法：
```javascript
const path = require('path');

module.exports = {
  output: {
    // 拼接成：项目根目录/dist
    path: path.resolve(__dirname, 'dist'),
  }
};
```

❌ 错误写法：
```javascript
path: 'dist' // 报错！必须是绝对路径
```

---

## 4. 常用搭配：path.resolve
`__dirname` 几乎总是和 `path.resolve` 一起用：

```javascript
// 拼接路径：当前目录 → src → index.js
path.resolve(__dirname, 'src', 'index.js')

// 结果（绝对路径）
/Users/xxx/my-project/src/index.js
```

作用：
- 跨平台兼容（Mac/Windows 路径自动适配）
- 生成**稳定、安全、不会出错**的路径

---

## 5. 与 __filename 区别
- `__dirname`：**文件夹路径**
- `__filename`：**文件完整路径（含文件名）**

例子：
```
__dirname    → /my-project
__filename   → /my-project/webpack.config.js
```

---

## 6. 重要提醒
✅ **可以在 webpack.config.js 中使用**  
✅ **可以在 Node.js 代码中使用**  
❌ **不能在前端业务代码中使用**（浏览器没有这个变量）

---

### 总结
1. `__dirname` = **当前文件所在文件夹的绝对路径**
2. Webpack 配置**必须用它**来指定路径
3. 配合 `path.resolve()` 使用最安全
4. 只在 Node 环境有效，浏览器代码不能用

需要我帮你把 **__dirname + path 最佳路径模板** 写到你的完整 Webpack 配置里吗？