你这段代码**确实启动了 shell**，只是你**看不见它被创建的过程**，它是 Node 底层悄悄开的。

# 核心原因
`exec` 内部默认会走这个逻辑：
1. 启动系统 shell（Windows 是 `cmd.exe`，Linux/macOS 是 `/bin/sh`）
2. 把你传的字符串丢给 shell 执行
3. shell 再去启动 `node` 进程

你看不到，是因为这一步**封装在 Node 内置 C++ 代码里**，不是你 JS 代码里写出来的。

---

# 怎么证明它真的启动了 shell？
非常简单：**你用了 shell 才支持的语法，它能跑，就说明开了 shell**

比如你这段：
```js
exec('node -e "console.log(\'exec 输出：\' + process.platform)"')
```

这就是**典型的 shell 命令格式**：
- 双引号包裹参数
- 多条命令用 `&&`、`|`、`>`
- 环境变量 `$PATH` 解析

这些**只有 shell 能处理**，`execFile` 直接跑是跑不了的。

---

# 直观对比一眼看懂

## exec（启动 shell）
```js
exec('node -e "console.log(123)" && dir', callback)
```
✅ 支持引号、`&&`、`|`、`>`
✅ 会创建 shell
❌ 不安全、有命令注入风险

## execFile（不启动 shell）
```js
execFile('node', ['-e', 'console.log(123)'], callback)
```
❌ **不支持** shell 语法
❌ 不会创建 shell
✅ 更安全、更快

---

# 总结
你代码里没写 `shell`，不代表没启动。
**只要用 `exec`，Node 就默认启动一个 shell 帮你解析命令。**

如果你想**肉眼看到 shell 被创建**，可以加个参数强制显示开启：
```js
exec('xxx', { shell: true }, () => {})
```
这个 `shell: true` 就是默认值，写不写都会开。