# `fs.existsSync` 超直白解释
**一句话：判断一个 文件 / 文件夹 是否真的存在。**

---

## 1. 完整写法
```javascript
const fs = require('fs');
const isExist = fs.existsSync(路径);
```

- 返回 **`true`**：存在
- 返回 **`false`**：不存在

---

## 2. 你项目里最常见用法
```javascript
const distPath = path.resolve(__dirname, 'dist');

// 如果 dist 目录存在，就删掉它
if (fs.existsSync(distPath)) {
  del.sync(distPath);
}
```

作用：
**先判断文件夹在不在，在就删，不在就跳过，避免报错。**

---

## 3. 小知识点
- **同步方法**：会阻塞代码，等判断完再往下走
- 专门用来判断：**文件 / 目录** 都可以
- 几乎所有**构建脚本、清理脚本**都会用它

---

### 总结
`fs.existsSync(路径)`
= **判断路径是否存在 → 存在返回 true，不存在 false**

你前面问的 `del.sync` + 这个 `fs.existsSync` 就是**打包前清理目录的标准组合**！