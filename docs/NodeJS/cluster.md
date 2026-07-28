`cluster` 是 Node.js 内置模块，专门用来**利用多核 CPU、创建多进程服务**，解决 Node 单线程无法吃满 CPU 的问题。

它和 `child_process.fork` 关系非常紧密：
- **cluster 底层就是基于 fork 实现的**
- 但 cluster 专门为 **网络服务（HTTP/TCP）** 做了优化，能让多个子进程**共享同一个端口**

# 核心作用
1. **启动多个 Node 进程**，分别占用一个 CPU 核心
2. 所有进程**监听同一个端口**（如 3000）
3. 主进程（master）负责管理，工作进程（worker）负责处理请求
4. 自动负载均衡，充分利用服务器性能

# 基本结构
```js
const cluster = require('cluster');
const http = require('http');
const numCPUs = require('os').cpus().length;

if (cluster.isPrimary) {
  // 主进程：只负责 fork 子进程
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }
} else {
  // 子进程：启动服务
  http.createServer((req, res) => {
    res.end('Hello from worker');
  }).listen(3000);
}
```

# 关键概念
- `cluster.isPrimary`：是否为主进程（原来叫 `isMaster`）
- `cluster.isWorker`：是否为工作进程
- `cluster.fork()`：创建一个工作进程
- 多个 worker 可以**共享同一个端口**，内核会自动分发连接

# 和 fork 的区别
| 场景                | child_process.fork | cluster.fork |
|---------------------|--------------------|--------------|
| 用途                | 通用子进程         | 多进程服务   |
| 共享端口            | 不能               | 可以         |
| 适合                | 计算任务、脚本      | Web 服务     |
| 进程间通信          | 支持 IPC           | 支持 IPC     |

# 典型使用场景
- 搭建高并发 HTTP 服务
- 充分利用多核 CPU，提升吞吐量
- 进程异常退出后自动重启

需要我给你一段**完整可运行的 cluster 多进程服务器代码**，或者讲讲**主进程与子进程通信**吗？

----

`if (cluster.isWorker) { ... }`
就是判断：**当前代码是不是运行在 cluster 的子工作进程里**。

# 一句话解释
- `cluster.isPrimary`（原 isMaster）→ 主进程
- `cluster.isWorker` → 子工作进程

你写的这段：
```js
if (cluster.isWorker) {
  // 这里只有子进程才会执行
  // 一般在这里启动服务器、处理请求
}
```

# 典型完整用法
```js
const cluster = require('cluster');
const http = require('http');
const os = require('os');

if (cluster.isPrimary) {
  // 主进程：只负责创建子进程
  const cpus = os.cpus().length;
  for (let i = 0; i < cpus; i++) {
    cluster.fork();
  }
} else {
  // 子进程：真正启动服务
  http.createServer((req, res) => {
    res.writeHead(200);
    res.end(`Hello from worker ${process.pid}\n`);
  }).listen(3000);

  console.log(`Worker ${process.pid} started`);
}
```

# 关键点
- 主进程不处理请求，只管理子进程
- 每个 `isWorker` 分支都会**独立执行一遍**
- 多个子进程可以**共用同一个端口 3000**（内核自动负载均衡）

# 和 worker_threads 对比
- `cluster.isWorker` → 多**进程**
- `isMainThread` → 多**线程**

如果你愿意，我可以给你整理一张**终极对比表**：
child_process / cluster / worker_threads 三者彻底分清，再也不混淆。