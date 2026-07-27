`fs.unlinkSync(benchFile)`  
= **同步删除文件**（就是删掉你刚才生成的那个临时测试脚本）

---

## 逐词拆开
- **`fs`**：Node.js 文件系统模块
- **`unlink`**：系统调用名，本意是“解除链接”，对普通文件就是**删除**
- **`Sync`**：同步、阻塞，删完之前代码不会往下走
- **`benchFile`**：你之前用 `spawn` 跑的那个临时 JS 文件路径

等价于终端命令：
```bash
rm benchFile.js
```

---

## 为什么你代码里会有这一句？
你的完整逻辑应该是这样：

1. 动态生成一段测试代码  
   → 写到 `benchFile`
2. 用 `spawn` 开子进程  
   → `node benchFile` 跑 pbkdf2 压测
3. 拿到结果、打印耗时
4. **用完就删，不留垃圾文件**  
   → `fs.unlinkSync(benchFile)`

这是典型**临时文件用完即删**的干净写法。

---

## 注意点
- 如果文件不存在，会**直接抛错**
- 删目录要用 `fs.rmdirSync`，不能用 `unlinkSync`
- 异步版是 `fs.unlink(benchFile, callback)`

---

### 一句话总结
`fs.unlinkSync(benchFile)`  
= **同步、立即删除 benchFile 这个临时测试脚本**。