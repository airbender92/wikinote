结合你前面问的 **libuv 线程池、worker_threads、cluster**，Node.js 里的 **crypto 模块** 是最容易踩坑的一块，我一次性给你讲清楚：**哪些异步、哪些阻塞、哪些走线程池、哪些适合放 Worker**。

# crypto 模块到底怎么跑？
## 1. 先分两类：阻塞 / 非阻塞
### （1）**同步方法：直接阻塞主线程**
- `crypto.createHash()`、`crypto.createHmac()`
- `crypto.randomBytesSync()`
- 加解密、签名的同步版

这些**会直接卡住事件循环**，高并发服务里千万别乱用。

---

### （2）**异步方法：走 libuv 线程池**
重点：**crypto 里的“慢算法”全部丢给 libuv 线程池**。

典型：
- `crypto.pbkdf2()`
- `crypto.scrypt()`
- `crypto.generateKeyPair()`
- 部分大数据异步加解密

它们的特点：
- **CPU 密集 + 慢**
- 不在主线程跑，扔给 **libuv 线程池**
- 线程池默认只有 **4 个线程**
- 一旦并发多，线程池占满，**所有 fs、dns、crypto 一起排队卡住**

这就是为什么登录接口一多，整个服务都慢——**pbkdf2 把线程池占满了**。

---

# 2. 和 libuv 线程池的关系（面试必考）
- crypto **异步哈希/密钥派生** → **libuv 线程池**
- 文件 I/O、dns.lookup → **同一个线程池**
- 默认 4 线程，大家抢位置

所以：
**大量 pbkdf2 并发 = 线程池堵死 = fs 也变慢 = DNS 也变慢**

解决方式：
1. 调大 `UV_THREADPOOL_SIZE`
2. 把重密码学计算丢给 **worker_threads**

---

# 3. 什么时候用 worker_threads 跑 crypto？
满足任意一条就建议放 Worker：
- 高频调用 `pbkdf2` / `scrypt`
- 做大量非对称加密、大文件签名
- 不想影响主线程和文件 I/O

因为：
- libuv 线程池是**全局共享**的
- worker_threads 是**独立 JS 线程**，不抢那 4 个坑位

---

# 4. 和 cluster 的关系
cluster 是多进程，每个子进程**都有自己独立的 libuv 线程池**。
所以：
- 8 核机器开 8 个 worker 进程
- 每个进程 4 个线程池
- 总并发能力 = 8 × 4 = **32 路**

这就是为什么服务端一般用 **cluster + 调高线程池** 扛高并发密码学操作。

---

# 5. 极简总结
- **crypto 同步方法**：阻塞主线程
- **crypto 慢异步方法**：走 **libuv 线程池**
- **线程池默认 4 个**，和 fs、dns 共用
- 并发高 → 线程池堵 → 整个服务慢
- 真·高并发密码学 → 丢 **worker_threads**
- 利用多核 → 用 **cluster**

---

如果你需要，我可以给你一段：
**worker_threads 专门跑 pbkdf2 的生产可用代码**，不占主线程、不占 libuv 线程池。