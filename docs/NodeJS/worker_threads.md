`worker_threads` 是 Node.js **真正的多线程**模块，用来解决 **CPU 密集型计算阻塞主线程** 的问题。

它和 `child_process`、`cluster` 完全不是一个东西，一定要分清：

# 一句话定位
- `child_process` / `cluster`：**多进程**，资源独立、重量级、不能共享内存
- `worker_threads`：**多线程**，同进程、轻量级、可共享内存（SharedArrayBuffer）

# 核心 API 含义
```js
const {
  Worker,        // 创建一个工作线程
  isMainThread,  // 判断当前是否在主线程
  parentPort,    // 子线程用来和主线程收发消息
  workerData     // 主线程传给子线程的初始数据
} = require('worker_threads');
```

# 各自用途
## 1. Worker
- 构造函数，用于**新建一个工作线程**
- 用法：
  ```js
  const worker = new Worker('./worker.js', {
    workerData: '传给线程的数据'
  });
  ```

## 2. isMainThread
- 布尔值：
  - `true` = 当前在**主线程**
  - `false` = 当前在**工作线程**
- 常用于同一个文件里写主线程/子线程逻辑：
  ```js
  if (isMainThread) {
    // 主线程逻辑
  } else {
    // 子线程逻辑
  }
  ```

## 3. parentPort
- **只在工作线程中可用**
- 用于：
  - `parentPort.postMessage(data)` 发消息给主线程
  - `parentPort.on('message', ...)` 接收主线程消息

## 4. workerData
- 主线程创建 Worker 时传入的**初始数据**
- 子线程直接读取，不用再发一次消息
- 数据会被**结构化克隆**复制一份

# 典型用法示例（同文件）
```js
const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');

if (isMainThread) {
  // 主线程
  const worker = new Worker(__filename, {
    workerData: 100
  });

  worker.on('message', (result) => {
    console.log('计算结果：', result);
  });
} else {
  // 工作线程
  const num = workerData;
  const sum = num * (num + 1) * (2 * num + 1) / 6;
  parentPort.postMessage(sum);
}
```

# 和 cluster、child_process 的核心区别
| 模块 | 本质 | 共享内存 | 开销 | 适用场景 |
|------|------|----------|------|----------|
| child_process | 多进程 | ❌ 不能 | 大 | 调用外部命令、独立任务 |
| cluster | 多进程 | ❌ 不能 | 大 | Web 服务多核复用端口 |
| worker_threads | 多线程 | ✅ 可以 | 小 | **CPU 密集计算**（加密、压缩、计算） |

# 总结
- 想**多核跑 HTTP 服务** → `cluster`
- 想**开子进程执行命令** → `child_process`
- 想**做大量计算不卡主线程** → `worker_threads`

需要我给你写一个**真实 CPU 密集型任务（比如加密、大数计算）用 worker_threads 优化**的完整示例吗？