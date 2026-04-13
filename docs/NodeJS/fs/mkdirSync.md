# `fs.mkdirSync` 超直白解释
**一句话：同步创建文件夹（mkdir = make directory）**

就是 Node.js 里**手动新建文件夹**的方法。

---

## 1. 完整写法
```javascript
const fs = require('fs');
fs.mkdirSync(路径);
```

---

## 2. 最关键、最常用的参数
**一定要加 `{ recursive: true }`，否则创建多层目录会报错！**
```javascript
fs.mkdirSync(distPath, { recursive: true });
```

### 作用：
- 自动创建**多层嵌套文件夹**
- 如果文件夹已经存在，**不会报错**

---

## 3. 你项目里的真实场景
结合你之前问的代码，完整逻辑是：
```javascript
const fs = require('fs');
const path = require('path');
const distPath = path.resolve(__dirname, 'dist');

// 1. 先删掉旧的 dist
del.sync(distPath);

// 2. 重新创建空的 dist 文件夹
fs.mkdirSync(distPath, { recursive: true });
```

### 流程：
1. 删除 dist 目录
2. **重新创建一个空的 dist 文件夹**
3. 然后开始打包输出

---

## 4. 不加 recursive 会怎样？
```javascript
fs.mkdirSync('dist/a/b/c'); // 报错！
```
因为不能一次性创建多层目录。

**加了就完美解决：**
```javascript
fs.mkdirSync('dist/a/b/c', { recursive: true }); // ✅ 正常
```

---

### 总结
`fs.mkdirSync(路径, { recursive: true })`
= **同步创建文件夹（支持多层、安全不报错）**

就是你**打包前重建 dist 目录**用的！