# `fs.readdirSync` 超直白解释
**一句话：同步读取一个文件夹里的所有文件和子文件夹名称，返回一个数组。**

简单说：**查看文件夹里有什么东西**。

---

## 1. 完整用法
```javascript
const fs = require('fs');
// 读取当前目录下的所有文件/文件夹
const files = fs.readdirSync('./');
```

返回结果是**数组**，里面是所有文件/文件夹的名字：
```javascript
['index.html', 'app.js', 'css', 'images', 'dist']
```

---

## 2. 最常用场景
你项目里一般用它来：
1. **批量读取文件**（批量处理、批量打包）
2. **遍历目录**
3. **判断文件夹是否为空**

---

## 3. 真实代码示例
```javascript
const fs = require('fs');
const path = require('path');

// 要读取的目录
const distPath = path.resolve(__dirname, 'dist');

// 读取 dist 里所有内容
const fileList = fs.readdirSync(distPath);

console.log(fileList);
// 输出：['js', 'css', 'index.html']
```

---

## 4. 进阶：判断是文件还是文件夹
配合 `fs.statSync` 使用（你刚学过）：
```javascript
const fileList = fs.readdirSync(distPath);

fileList.forEach(item => {
  const fullPath = path.join(distPath, item);
  const stats = fs.statSync(fullPath);

  if (stats.isFile()) {
    console.log('是文件：', item);
  } else if (stats.isDirectory()) {
    console.log('是文件夹：', item);
  }
});
```

---

## 5. 你项目里的作用
**批量处理文件、遍历目录、批量打包**。

---

### 总结
`fs.readdirSync(文件夹路径)`
= **读取文件夹里所有内容，返回文件名数组**

---
你现在已经学会了 **Node.js 文件操作最核心的 6 件套**：
1. `path.resolve` → 拼路径
2. `fs.existsSync` → 判断存在
3. `fs.statSync` → 看信息
4. `fs.mkdirSync` → 创建文件夹
5. `fs.readdirSync` → 读文件夹内容
6. `del.sync` → 删除文件夹

这些就是你项目**构建脚本**的全部核心！