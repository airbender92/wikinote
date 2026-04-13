`child_process` 是 Node.js 的**核心内置模块**，用于在主进程（父进程）中创建和管理**子进程**，以执行系统命令、外部程序或其他 Node.js 脚本，从而实现并行计算、CPU 密集型任务处理或系统交互。

### 一、核心方法（异步 vs 同步）
`child_process` 提供 **4 种异步**、**3 种同步**方法，功能对比如下：

| 异步方法 | 特点 | 适用场景 |
|:--- |:--- |:--- |
| `spawn()` | 最底层、流式输出、无缓存上限 | 大量输出、长时间运行（如 `tail -f`、`ffmpeg`） |
| `exec()` | 启动 Shell、缓存全部输出 | 简短命令、需获取完整结果（带回调） |
| `execFile()` | 不启动 Shell、直接执行文件 | 安全、高效执行外部二进制（如 `.exe`、脚本） |
| `fork()` | `spawn()` 特例，创建 Node.js 子进程 | **IPC 通信**、多核并行、分布式任务 |

| 同步方法（阻塞事件循环） | 对应异步 | 适用场景 |
|:--- |:--- |:--- |
| `spawnSync()` | `spawn()` | 脚本初始化、同步依赖 |
| `execSync()` | `exec()` | 简单命令、获取字符串结果 |
| `execFileSync()` | `execFile()` | 安全同步执行外部文件 |

---

### 二、常用 API 示例

#### 1. spawn() — 流式处理
```javascript
const { spawn } = require('child_process');

// 执行命令：ls -lh /usr
const child = spawn('ls', ['-lh', '/usr']);

// 监听标准输出
child.stdout.on('data', (data) => {
  console.log(`stdout:\n${data}`);
});

// 监听错误输出
child.stderr.on('data', (data) => {
  console.error(`stderr: ${data}`);
});

// 退出事件
child.on('close', (code) => {
  console.log(`子进程退出，退出码：${code}`);
});
```

#### 2. exec() — 缓存式回调
```javascript
const { exec } = require('child_process');

exec('node -v && npm -v', (error, stdout, stderr) => {
  if (error) {
    console.error(`执行错误: ${error.message}`);
    return;
  }
  if (stderr) {
    console.error(`错误输出: ${stderr}`);
    return;
  }
  console.log(`标准输出:\n${stdout}`);
});
```

#### 3. fork() — Node.js 子进程 + IPC
**父进程 parent.js**
```javascript
const { fork } = require('child_process');
const child = fork('./child.js');

// 发消息给子进程
child.send({ msg: 'Hello from parent' });

// 接收子进程消息
child.on('message', (msg) => {
  console.log('父进程收到:', msg);
});
```

**子进程 child.js**
```javascript
// 接收父进程消息
process.on('message', (msg) => {
  console.log('子进程收到:', msg);
  // 回复
  process.send({ msg: 'Hi from child' });
});
```

---

### 三、常用选项 options
- `cwd`：子进程工作目录
- `env`：环境变量（默认继承父进程）
- `stdio`：标准流配置（`pipe`/`inherit`/`ignore`/数组）
- `shell`：`true` 则用 Shell 执行（Windows 需开启）
- `detached`：`true` 可脱离父进程独立运行
- `maxBuffer`：`exec/execFile` 缓存上限（默认 `1024*1024`）

---

### 四、close vs exit 事件
- `exit`：进程退出，但流可能未关闭
- `close`：所有 stdio 流已关闭（更适合清理）

---

### 五、安全注意
- **避免**将用户输入直接拼接到 `exec`/`execFile` 命令（防止命令注入）
- 优先用 `spawn`/`execFile` + 参数数组，而非字符串拼接
- Windows 环境注意路径转义和 Shell 行为差异

---

### 六、典型用途
- 执行系统命令、脚本、二进制工具
- 处理 CPU 密集型计算（分担 V8 主线程压力）
- 多进程并行任务、分布式爬虫/构建
- 调用第三方 CLI（如 Git、FFmpeg、Docker）

要不要我帮你写一个可直接运行的 **child_process 完整工程模板**（含 spawn/exec/fork 三种最佳实践、错误处理、超时、IPC 通信）？