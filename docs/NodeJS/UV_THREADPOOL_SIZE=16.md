`UV_THREADPOOL_SIZE=16` 就是：
**把 Node.js 底层 libuv 线程池大小设置为 16**

---

## 它是干嘛的？
Node.js 里这些操作**不跑在 JS 主线程**，而是丢进线程池：
- `crypto.pbkdf2` / `scrypt` 等加密计算
- `fs` 文件异步操作
- DNS 查询、zlib 压缩

默认线程池大小 = **4**
你改成 16，就意味着：
> **同一时间可以并行跑 16 个这类任务**

---

## 对你的 pbkdf2 测试意味着什么？
- 单次耗时：假设 100ms
- 并发 8 个：
  - 线程池 4 → 耗时 ≈ 200ms
  - 线程池 16 → 耗时 ≈ 100ms（一次性跑完 8 个）

---

## Windows 下正确设置方式

### PowerShell
```powershell
$env:UV_THREADPOOL_SIZE=16; node yourfile.js
```

### CMD
```cmd
set UV_THREADPOOL_SIZE=16 && node yourfile.js
```

### 在代码里设置（最稳）
```javascript
process.env.UV_THREADPOOL_SIZE = '16';
```
**必须写在最顶部**，在引用 crypto、fs 之前。

---

## 重要注意点
1. **进程启动后就不能改**
   一旦 Node 启动，线程池大小固定，改环境变量也没用。
2. **不是越大越好**
   超过 CPU 核心数后，收益变小，反而增加切换开销。
   一般设置为 **CPU 核心数 × 1~2** 比较合理。
3. **只影响线程池任务**
   不影响普通 JS 计算、网络 IO（网络 IO 不靠线程池）。

---

## 一句话总结
`UV_THREADPOOL_SIZE=16`
= **让 Node 同时并行处理更多加密、文件操作，提高密集型异步任务吞吐量**。