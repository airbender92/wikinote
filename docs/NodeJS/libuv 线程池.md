# libuv 线程池（Thread Pool）完整讲解
结合你刚才问的**文件 I/O**，这是 libuv 最容易混淆的核心知识点。



## 一、一句话定位
libuv **事件循环主线程只处理网络IO（epoll/kqueue/iocp）**；
对于**操作系统没有原生异步支持的阻塞调用**（典型：文件IO），libuv 用**线程池模拟异步**：
> **子线程执行阻塞调用 → 完成后通知主线程事件循环执行回调**

> 重要区分：
> ✅ **网络socket I/O**：不走线程池，直接事件轮询
> ✅ **文件 I/O、dns.lookup、crypto 运算**：全部丢线程池

## 二、核心基础属性
1. **全局单例**
   整个进程**只有一个线程池**，所有 `uv_loop_t`（事件循环）共享；不是每个loop单独一份。
2. **默认大小：4 条工作线程**
   环境变量：`UV_THREADPOOL_SIZE`
   - 生效前提：**进程启动前设置**，线程池一旦初始化不能动态修改
   - 上限：**1024**（libuv ≥1.30）
   ```bash
   # Linux/macOS
   export UV_THREADPOOL_SIZE=16
   node app.js
   ```
3. **懒初始化**
   第一次投递任务时才创建所有线程，不是程序启动立刻创建。

## 三、哪些任务会进入线程池
### 1）libuv 内部自动投递
- 所有异步文件系统调用 `uv_fs_*`（`fs.readFile/fs.stat/fs.writeFile` 等，对应你问的**文件I/O**）
- DNS：`getaddrinfo` → Node.js `dns.lookup()`（⚠️ `dns.resolve` 不走线程池）

### 2）用户手动投递（API）
```c
int uv_queue_work(
    uv_loop_t* loop,
    uv_work_t* req,
    uv_work_cb work_cb,        // 在线程池子线程执行（可以阻塞）
    uv_after_work_cb after_cb  // 回到主线程事件循环执行（禁止阻塞）
);
```
- `work_cb`：子线程，可以写阻塞文件IO、复杂计算
- `after_cb`：**主线程！绝对不能阻塞**

### Node.js 上层对应（面试高频）
占用线程池：
- `fs` 所有异步方法（非同步版）
- `dns.lookup()`
- `crypto.pbkdf2、scrypt、randomBytes(带回调)`
- `zlib` 异步压缩解压

不占用线程池：
- http/tcp/udp 网络请求
- setTimeout / setInterval
- `dns.resolve()`

## 四、运行流程（文件IO例子，打通你上一个问题）
以 `fs.readFile` 为例：
1. JS调用 → 传入libuv
2. libuv 封装任务，**推入线程池任务队列**
3. 空闲worker线程取出任务，调用**阻塞系统调用 read()**
4. 文件读取完成，worker通过 `uv_async_t` 唤醒主线程事件循环
5. 事件循环捕获通知，把JS回调放入队列执行

> 关键点：**文件I/O底层仍然是阻塞调用，只是放到子线程，不让主线程卡住**。
> Linux AIO 很少被文件系统广泛支持，所以libuv不依赖原生aio，统一线程池方案跨平台兼容。

## 五、经典坑（生产常见问题）
### 1. 线程池容量瓶颈（最常考）
默认只有4个并发位置！
如果4个线程都被**慢文件读写、慢DNS、密码哈希占住**，新来的fs请求全部排队，服务延迟暴涨。
现象：接口没有CPU打满，但大量文件操作超时。

> 解决方案：调高 `UV_THREADPOOL_SIZE`，但不要无脑拉满1024，线程过多带来内核调度开销。

### 2. 线程池线程之间没有事件循环
worker线程**没有uv_loop**！
你不能在 `uv_work_cb` 里调用任何libuv异步API（不能发起新fs、网络请求），只能做纯粹同步阻塞操作。

### 3. 和 Node.js worker_threads 区分（极易混淆）
- **libuv线程池**：libuv内置C线程，**不能执行JS代码**，只用来跑阻塞系统调用；
- **worker_threads**：Node.js提供独立V8实例的JS线程，和libuv线程池完全两套东西，互不干扰。

## 六、精简对比
| 模块 | 执行位置 | 能否阻塞 |
|------|--------|--------|
| http/网络socket | 主线程事件循环（epoll） | ❌ 不能阻塞主线程 |
| fs.readFile、dns.lookup | libuv线程池子线程 | ✅ 子线程允许阻塞 |
| JS业务代码 | 主线程V8 | ❌ 任何长时间运算都会卡住事件循环 |

## 七、面试一句话总结答案
libuv线程池是一组固定数量的后台线程，用来执行**无法被操作系统原生异步支持的阻塞系统调用（文件I/O、域名查询等）**，模拟异步效果；任务在子线程阻塞执行，完成后通知主线程事件循环执行回调；进程全局共享，默认4线程，可通过环境变量调整。

如果你需要，我可以画一张**事件循环 poll阶段 + 线程池通信完整时序图**，或者给你一段C语言极简libuv文件IO示例代码。