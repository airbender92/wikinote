# `child_process.spawn` 用法完全图解
`spawn` 是 Node.js 用来**开启子进程**的核心方法，用来跑一个**全新的系统命令/程序**（比如另一个 `node`、`npm`、`dir`、`ls` 等）。

---

## 1. 基础语法
```js
const { spawn } = require('child_process');

const child = spawn(命令, 参数数组, 配置项);
```

对应你代码：
```js
spawn(
  process.execPath,      // 命令：node 程序本身
  [benchFile],            // 参数：要执行的 js 文件
  {                      // 配置
    stdio: ['ignore', 'pipe', 'inherit'],
    env: { ...process.env, UV_THREADPOOL_SIZE: poolSize + '' }
  }
);
```

---

## 2. 三个参数分别干嘛

### ① 第一个参数：要执行的命令
- `process.execPath` → 当前 node 的路径，等价于直接用 `node` 命令
- 也可以写：`'npm'`、`'python'`、`'cmd'`、`'ls'` 等

### ② 第二个参数：命令的参数（数组）
比如你在终端敲：
```bash
node demo.js
```
用 spawn 写就是：
```js
spawn('node', ['demo.js'])
```

你代码里：
```js
spawn(process.execPath, [benchFile])
```
= 执行
```bash
node benchFile.js
```

### ③ 第三个参数：配置（重点）
```js
{
  stdio: ['ignore', 'pipe', 'inherit'],
  env: { ...process.env, UV_THREADPOOL_SIZE: poolSize.toString() }
}
```

---

## 3. stdio 是什么？
**标准输入输出配置**，一共 3 个位置，对应：
`[stdin, stdout, stderr]`

- `ignore`：忽略，不处理
- `pipe`：管道，父进程可以监听数据
- `inherit`：继承父进程控制台（直接打印出来）

你写的：
```js
stdio: ['ignore', 'pipe', 'inherit']
```
- 标准输入：忽略
- 标准输出：管道（父进程可以 `child.stdout.on('data', ...)`）
- 标准错误：直接打印到当前控制台

---

## 4. env：给子进程设置环境变量
```js
env: {
  ...process.env,        // 继承父进程所有环境变量
  UV_THREADPOOL_SIZE: poolSize.toString() // 覆盖线程池大小
}
```

作用：
- 子进程拿到的环境变量是**独立的**
- 不会影响父进程
- 最适合测试不同 `UV_THREADPOOL_SIZE`

---

## 5. 常用事件监听（必用写法）
```js
// 接收子进程输出
child.stdout.on('data', (data) => {
  console.log('子进程输出:', data.toString());
});

// 子进程退出
child.on('close', (code) => {
  console.log('子进程退出，code:', code);
});
```

---

## 6. spawn 和 exec 简单区别
- `spawn`：流式，适合**长时间运行、大量输出**（node 服务、ffmpeg 等）
- `exec`：缓冲全部输出，适合简单短命令

你测 pbkdf2 用 **spawn** 是最标准、最正确的。

---

## 极简总结
```js
spawn(
  'node',                // 运行 node
  [benchFile],           // 执行 benchFile.js
  {
    stdio: [...],        // 输入输出怎么处理
    env: { ... }         // 给子进程单独设置环境变量
  }
)
```
就是：**开一个独立的子 Node 进程，单独设置线程池大小，专门跑压力测试**。

# 1. 整句作用
```js
const child = spawn(process.execPath, [benchFile], {
  stdio: ['ignore', 'pipe', 'inherit'],
  env: { ...process.env, UV_THREADPOOL_SIZE: poolSize.toString() }
});
```

- `spawn`：启动一个**子进程**
- `process.execPath`：当前 node 程序路径 → 相当于 `node` 命令
- `[benchFile]`：要执行的测试脚本文件
- `env`：给子进程**单独设置环境变量**

关键点就是这一句：
```js
env: { ...process.env, UV_THREADPOOL_SIZE: poolSize.toString() }
```

意思：
> 继承父进程环境变量，但**强制覆盖 UV_THREADPOOL_SIZE**，
> 让这个子进程的 libuv 线程池大小 = poolSize

# 2. 为什么要这么写？
因为：
- **一旦进程启动，UV_THREADPOOL_SIZE 就不能改了**
- 想测试不同线程池大小，必须**开新的 Node 进程**

所以你这段代码是：
**启动独立子进程 → 单独设置线程池 → 跑 pbkdf2 压测 → 看耗时变化**

这是最标准、最科学的测试方法。

# 3. stdio 是什么意思？
```js
stdio: ['ignore', 'pipe', 'inherit']
```
对应三个管道：
- `stdin`：ignore → 子进程不需要输入
- `stdout`：pipe → 父进程可以拿到子进程输出
- `stderr`：inherit → 错误直接打印到控制台

# 4. 结合你之前的测试逻辑
你这段代码一般是这么用的：

1. 父进程：循环设置 poolSize = 4、6、8、10
2. 每次 spawn 一个子进程
3. 子进程里跑 `Promise.all` 并发 pbkdf2
4. 看：
   - poolSize=4 → 8个任务耗时≈2倍单次
   - poolSize=8 → 8个任务耗时≈1倍单次

这样就能**严格证明线程池大小确实控制并发数**。

# 5. 极简总结
- `spawn( node, 脚本 )`：开独立子进程
- `env: UV_THREADPOOL_SIZE`：给子进程单独设置线程池
- 用来**科学测试不同线程池下 crypto / fs 并发性能**
- 比在 PowerShell 里手打环境变量更稳定、可自动化

如果你愿意，我可以把你这段**完整的多进程压测 pbkdf2 代码**拼成可直接运行的一整套 demo。