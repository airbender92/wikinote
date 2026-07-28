`process.on()` 就是给 **当前 Node 进程** 监听事件，相当于给进程加一个“事件监听器”。

# 最常用的几种用法

## 1. 子进程监听主进程发来的消息
```js
// 子进程里
process.on('message', (data) => {
  console.log('主进程对我说：', data)
})
```

## 2. 监听进程退出、关闭信号
```js
// 程序要退出时
process.on('exit', (code) => {
  console.log('进程要退出了，码：', code)
})

// Ctrl + C
process.on('SIGINT', () => {
  console.log('收到 Ctrl+C')
  process.exit(0)
})
```

## 3. 捕获未捕获的异常（防止崩）
```js
process.on('uncaughtException', (err) => {
  console.error('崩了：', err)
})
```

## 4. 监听 Promise 未捕获 reject
```js
process.on('unhandledRejection', (reason, promise) => {
  console.error('Promise 崩了：', reason)
})
```

---

# 和 cluster / child_process 配合记忆

- 主进程监听子进程消息：  
  `worker.on('message', ...)`
- 子进程监听主进程消息：  
  **`process.on('message', ...)`**

- 子进程发消息：  
  **`process.send(...)`**
- 主进程发消息：  
  `worker.send(...)`

---

# 一句话总结
- `process.on(事件名, 回调)`  
  → **监听当前进程的系统/IPC事件**
- 最常用就是：**接收主进程消息**、**处理退出**、**抓全局错误**。