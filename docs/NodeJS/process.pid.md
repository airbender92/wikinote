`process.pid` 就是**当前这个 Node 进程的进程 ID**，系统用来唯一标识一个进程的数字。

# 作用
- 每个进程都有一个唯一 pid
- 主进程、每个子进程 pid 都不一样
- 用来区分：现在是谁在跑代码

# 配合 cluster 使用
```js
if (cluster.isPrimary) {
  console.log('主进程 pid:', process.pid);
  cluster.fork();
} else {
  console.log('子工作进程 pid:', process.pid);
}
```

运行后你会看到类似：
主进程 pid: 58630
子工作进程 pid: 33729

# 常见用途
- 日志里标记是哪个进程在输出
- 排查哪个进程崩溃、占用 CPU 高
- 进程间通信时标识对方

简单记：**pid = 进程身份证号**。