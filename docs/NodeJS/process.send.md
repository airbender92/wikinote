`process.send()` 是 Node.js **进程间通信（IPC）** 的方法，用于**子进程给主进程发消息**。

---

# 核心一句话
- **主进程**：用 `child.send()` 发给子进程
- **子进程**：用 `process.send()` 发给主进程

只有通过 `fork` / `cluster.fork` 创建的**带 IPC 通道**的子进程，才能用 `process.send()`。

---

# 在 cluster 里的用法示例

主进程（primary）：
```js
if (cluster.isPrimary) {
  const worker = cluster.fork();

  // 接收子进程发来的消息
  worker.on('message', (msg) => {
    console.log('主进程收到：', msg);
  });
}
```

子进程（worker）：
```js
if (cluster.isWorker) {
  // 子进程发给主进程
  process.send({
    pid: process.pid,
    msg: '我启动好了'
  });
}
```

---

# 和 child_process.fork 对比

## 主进程
```js
const { fork } = require('child_process');
const child = fork('./child.js');

child.on('message', (msg) => { ... });
```

## child.js 子进程
```js
process.send('hello from child');
```

原理完全一样。

---

# 关键点
- `process.send()` **只能在子进程里用**
- 主进程没有 `process.send()`，主进程用 `worker.send()` / `child.send()`
- 发送的数据会被**结构化克隆**（对象、数组、Buffer 都能发）
- 不能发函数、循环引用

---

# 简单总结
- 子进程 → 主进程：`process.send()`
- 主进程 → 子进程：`worker.send()`
- 一对收发，完成进程间通信

需要我给你写一个**主进程 ↔ 子进程互相收发消息**的完整可运行 demo 吗？