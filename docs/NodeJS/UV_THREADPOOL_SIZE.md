# UV_THREADPOOL_SIZE 完整讲透（面试+生产必懂）

## 1. 它是干嘛的？
控制 **libuv 线程池** 的最大线程数量。
- 影响：`fs` 异步文件 I/O、`dns.lookup`、`crypto.pbkdf2/scrypt`、`zlib` 异步
- 不影响：网络 I/O、`setTimeout`、`spawn/fork`、`worker_threads`

## 2. 默认值 & 范围
- **默认：4**
- 最小值：1
- 最大值：**1024**（libuv ≥1.30.0）
- 超过 1024 会被强制截断为 1024

## 3. 怎么设置？
**必须在 Node 进程启动前设置**，运行中改无效。

### Linux/macOS
```bash
export UV_THREADPOOL_SIZE=16
node app.js
```

### Windows cmd
```cmd
set UV_THREADPOOL_SIZE=16
node app.js
```

### Windows PowerShell
```powershell
$env:UV_THREADPOOL_SIZE=16
node app.js
```

## 4. 什么时候需要调大？
典型场景：
- 大量并发登录接口（`pbkdf2` 占满线程池）
- 大量文件读写、上传下载
- 大量 DNS 查询
- 接口出现**排队延迟**，但 CPU 不高、网络不堵

## 5. 是不是越大越好？
**不是。**
- 线程太多 → 内核频繁切换线程 → **上下文切换开销暴涨**
- 一般建议：
  - 普通 Web 服务：**8～32**
  - 大量文件/密码学：**32～64**
  - 极少情况才到 1024

## 6. 一个关键误区
**cluster 每个子进程都有独立的 libuv 线程池！**

例子：
- UV_THREADPOOL_SIZE = 4
- 机器 8 核，开 8 个 worker
- 总线程池并发 = 8 × 4 = **32 路**

## 7. 一句话总结
**UV_THREADPOOL_SIZE 控制 libuv 线程池大小，默认 4，启动前设置，影响 fs、dns.lookup、crypto.pbkdf2，不影响网络和子进程。**

需要我帮你判断你的服务应该设多少合适吗？我可以根据你的接口类型（登录多？文件多？）给你一个推荐值。