# 一句话解释
`require('iconv-lite')` 就是 **在 Node.js 中引入一个专门解决【编码乱码】的工具库**。

它的核心作用：**把各种冷门编码（GBK、GB2312、Windows-1252 等）转换成 JS 能看懂的 UTF-8**。

---

# 超通俗拆解
## 1. 它是干嘛的？
Node.js 原生只支持 **UTF-8** 编码。
但**Windows 系统、老网站、老文件、老接口**常用：
- GBK / GB2312（中文系统默认编码）
- GB18030
- Windows-1252

如果不转码，直接读取会出现 **乱码：浣犲ソ、鍐呭、Ã½Ã¼**。

**iconv-lite 就是专门做编码转换的。**

---

## 2. 最常见的 2 种使用场景
### ① 读取 Windows 生成的文本文件（GBK → UTF-8）
```js
const iconv = require('iconv-lite');
const fs = require('fs');

// 读取 GBK 编码的文件，转成正常中文
const buffer = fs.readFileSync('gbk-file.txt');
const text = iconv.decode(buffer, 'gbk'); // 转码
console.log(text); // 正常中文，不乱码
```

### ② 请求老网站/老接口（爬取 GBK 页面）
```js
const data = iconv.decode(responseBuffer, 'gb2312');
```

---

## 3. 编码转换原理（极简）
- **decode**：Buffer（二进制） → 字符串（GBK/GB2312 → UTF-8）
- **encode**：字符串 → Buffer（UTF-8 → GBK）

---

# 你项目里为什么要用它？
大概率是：
1. **读取 Windows 环境下的配置/脚本**
2. **处理 GBK 编码的接口/文件**
3. **解决中文乱码问题**

这是 Node.js **处理中文编码乱码最标准、最常用的库**。

---

### 总结
`require('iconv-lite')` =
**编码转码工具 → 专门解决 GBK / 中文乱码问题**

需要我帮你定位你项目里**哪段代码在处理乱码**吗？