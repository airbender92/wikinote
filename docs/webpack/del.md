# 一句话解释
`require('del')` 就是 **在 Node.js 里引入一个专门用来**删除文件/文件夹**的第三方工具包**。

它是前端工程化（webpack、gulp 项目）**最常用的清理工具**，用来在打包前**清空旧的 dist 目录**。

---

# 详细通俗拆解
## 1. 它是什么？
- **del** = delete 的缩写
- 一个 npm 包（需要先安装才能用）
- 作用：**安全删除文件、文件夹**（比原生 fs 模块好用、安全）

## 2. 为什么要用它？
Node.js 自带的文件删除方法：
- 不能**递归删除**文件夹
- 写法麻烦
- 容易出错

`del` 解决了这些问题：
- 一行代码删除整个目录
- 支持通配符 `*`
- 安全（不会误删系统重要文件）
- 返回 Promise，支持 async/await

---

# 3. 典型用法（你项目里一定是这么用的）
```javascript
const del = require('del');

// 打包前先删除旧的 dist 文件夹
async function clean() {
  await del('dist/**'); // 删除 dist 下所有内容
}
```

**你项目里的作用：**
每次执行 `npm run build` 时，**先清空旧的打包文件**，再生成新的。

---

# 4. 安装命令（必须先装才能用）
```bash
npm install del --save-dev
# 或
yarn add del -D
```

---

# 5. 常用语法
```javascript
// 删除 dist 目录
del(['dist']);

// 删除 dist + 所有 .log 文件
del(['dist/**', '*.log']);

// 保留某个文件不删
del(['dist/**', '!dist/config.js']);
```

---

### 总结
`require('del')` =
**引入文件删除工具 → 用于打包前清空旧文件目录**

这是你项目**构建脚本（build script）**里的标准代码。

需要我帮你看看你项目里**具体在清理哪些目录**吗？