# child_process.spawn 完整梳理（承接你前面整套知识栈：libuv线程池 / cluster / worker_threads / crypto）
## 一句话核心
**spawn 是 Node 创建操作系统子进程的底层API，调用操作系统 `fork/CreateProcess`，生成独立OS进程；**
✅ **它不占用 libuv 线程池！**（高频面试重点区分）

> 先划最重要分界线：
> - libuv线程池：进程**内部的C线程**，跑阻塞任务（fs、pbkdf2）
> - spawn：新建**独立操作系统进程**，完全另一套资源

## 1. 基础用法
```js
const { spawn } = require('child_process');
// 执行shell命令/外部程序，返回流对象
const child = spawn('ls', ['-lh']);

// stdout、stderr 都是Stream（流式输出）
child.stdout.on('data', buf => console.log(buf.toString()));
child.on('close', code => console.log('进程退出', code));
```

### 关键特性
1. **流式输出**
stdout/stderr 是可读流；**不会缓存全部输出**，适合长时间运行、大量输出程序（ffmpeg、持续日志、数据导出）。
2. **默认不开shell**
直接执行二进制；如果需要管道 `|`、通配符 `*`，必须手动开启 `{shell:true}`。
3. **异步创建进程**
`spawn()` 调用本身**不阻塞事件循环**；
⚠️ `spawnSync()` 同步版本，会卡死主线程。

## 2. spawn / exec / execFile / fork 四者关系（必背）
1. **spawn**：底层原语，创建进程，流式IO；无输出大小限制
2. **exec**：封装 spawn，**新建shell执行命令**，缓存全部输出，有缓冲区上限（默认200KB）；适合简短命令
3. **execFile**：优化版exec，**不启动shell**，更安全、无注入风险；推荐优先使用
4. **fork**：**特殊的 spawn**，专门启动 Node.js 脚本
   - 自动建立 **IPC通信通道**（`.send()` / `message` 事件）
   ```js
   // fork 等价于 spawn('node', ['script.js'], {stdio: [0,1,2,'ipc']})
   const cp = fork('./sub.js');
   cp.send({type: 'task'});
   ```

> 💡 cluster 模块底层就是大量调用 `fork()`！

## 3. 重点：spawn 与 libuv 线程池关系（极易混淆）
**spawn 创建子进程这件事本身，不走 libuv 线程池！**
原理：
libuv 通过跨平台接口（Windows IOCP / Linux epoll）监听子进程信号、管道IO；
父子之间的 stdio pipe I/O **属于libuv网络式异步IO**，和socket一套逻辑，**不抢占那4条线程池**。

对比一张清单：
| API | 是否占用 libuv 线程池 |
|-----|----------------------|
| fs.readFile、crypto.pbkdf2 | ✅ 占用 |
| dns.lookup | ✅ 占用 |
| http/tcp网络、spawn管道IO | ❌ 不占用 |

现实意义：
当你的服务线程池被大量 `pbkdf2` 占满，**spawn 依然可以正常创建子进程、收发stdout数据**，不会被线程池瓶颈卡住。

## 4. spawn VS worker_threads VS cluster（整合你之前所有知识点）
### 1）spawn / fork（子进程）
- 创建：**操作系统独立进程**
- 内存：完全隔离，不共享堆
- 通信：stdio管道 / IPC消息（序列化拷贝数据）
- 开销：创建开销最大（OS进程创建成本高）
- 用途：调用外部程序、运行其他语言程序；cluster多进程服务

### 2）worker_threads JS工作线程
- 创建：**同一进程内的线程**，独立V8实例
- 内存：默认隔离，可选 `SharedArrayBuffer` 共享内存
- 开销：轻于进程，重于普通C线程
- 用途：JS CPU密集计算，避免阻塞主线程事件循环

### 3）libuv线程池
- 创建：进程内原生C线程，**没有独立V8，不能跑JS**
- 用途：模拟异步，执行阻塞系统调用（文件IO、密码运算）

### 直观层级
```
Node主进程
├─ 主线程（事件循环，执行JS）
├─ libuv线程池（4条C线程：fs、pbkdf2、dns.lookup）
├─ worker_threads（同进程，独立V8 JS线程）
└─ spawn/fork → 生成全新OS子进程（独立内存、独立libuv、独立线程池）
```

## 5. 生产常见坑
1. **shell:true 存在命令注入风险**
用户可控参数不要直接拼接命令；优先使用 execFile / spawn 参数数组形式。
```js
// 安全写法，参数分开传递
spawn('curl', [url])
// 危险！shell开启极易注入
spawn(`curl ${userInput}`, {shell:true})
```

2. **忘记监听 stderr，子进程异常无声崩溃**
3. **大量频繁spawn会造成系统进程风暴**
进程创建成本很高，不要循环高频创建；大量计算优先考虑 worker_threads 或者进程池复用。

4. IPC通道只能传递可序列化数据，不能直接传递Buffer、类实例（会被序列化）

## 6. 面试极简总结
`spawn` 是 Node 创建操作系统子进程的底层API，exec/execFile/fork都基于它实现；
产生独立OS进程，stdio采用流式异步管道，**不占用libuv线程池**；
fork是spawn针对Node脚本的封装，自带IPC；
适合调用外部程序、长时间输出任务；进程内存完全隔离，创建开销高于worker_threads。

如果你需要，我可以写一段**进程池简易demo**或者对比：用spawn vs worker_threads 处理CPU密集任务的性能差异代码。