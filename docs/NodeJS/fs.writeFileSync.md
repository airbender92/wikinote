`fs.writeFileSync` 就是 Node.js **fs 模块**里的：
**同步写入文件**的方法。

---

## 一句话核心
- **Sync = 同步、阻塞**
- 代码会**一直等**文件写完，才继续往下走
- 期间 JS 主线程卡死，啥都不干

## 基本用法
```js
const fs = require('fs');

// 写入字符串
fs.writeFileSync('./test.txt', '你好，这是内容');

// 写入 Buffer
fs.writeFileSync('./data.bin', Buffer.from([0x01, 0x02, 0x03]));
```

## 常用参数
```js
fs.writeFileSync(
  path,       // 文件路径
  data,       // 字符串 或 Buffer
  options     // 编码、flag 等
);
```

常用 options：
```js
fs.writeFileSync('a.txt', 'hello', {
  encoding: 'utf8',   // 默认 utf8
  flag: 'w'           // w=覆盖写入，a=追加
});
```

---

## 和异步版 `fs.writeFile` 的区别
- `writeFileSync`：同步阻塞，代码简单，**CPU 密集/大量写入会卡事件循环**
- `writeFile` / `fs.promises.writeFile`：异步非阻塞，不阻塞主线程

---

## 关键点（和你前面知识串起来）
1. **fs 同步方法**：
   会**阻塞事件循环**，不进 libuv 线程池
2. **fs 异步方法**：
   扔进 **libuv 线程池**（默认 4 线程），和 `crypto.pbkdf2` 共用线程池

所以：
- 大量 `writeFileSync` → 直接卡死服务
- 大量异步 `writeFile` → 会和 pbkdf2 抢线程池

---

## 极简总结
`fs.writeFileSync(路径, 内容)`
= **同步写文件，阻塞主线程**，简单但高并发下慎用。