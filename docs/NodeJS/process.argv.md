# 一句话解释
**`process.argv` 是 Node.js 专门用来获取「命令行参数」的数组**
你在终端敲命令时，后面跟的参数，全靠它拿到！

---

# 超通俗拆解
## 1. 它是什么？
- `process`：Node.js 全局对象（不用 require）
- `argv` = **Argument Vector（参数向量）** 的缩写
- 本质：**数组**，里面存了你敲命令时的所有内容

---

## 2. 举个最真实的例子
你在终端敲：
```bash
node build.js --mode production --clean
```

那么 `process.argv` 得到的数组是：
```javascript
[
  '/usr/local/bin/node',   // 第0位：node 执行程序路径
  '/xxx/build.js',         // 第1位：当前执行的文件路径
  '--mode',                // 第2位：第一个参数
  'production',            // 第3位：第二个参数
  '--clean'                // 第4位：第三个参数
]
```

---

## 3. 怎么用？
**真正有用的参数从第 2 位开始！**
```javascript
// 获取命令行参数
const args = process.argv.slice(2);

console.log(args);
// 输出：['--mode', 'production', '--clean']
```

---

## 4. 你项目里一般用来干嘛？
最常见场景：
1. **区分开发/生产环境**
   ```bash
   node build.js --prod
   ```
2. **控制是否需要清理目录**
   ```bash
   node build.js --clean
   ```
3. **传入自定义配置**

代码里判断：
```javascript
const isProd = process.argv.includes('--prod');
const needClean = process.argv.includes('--clean');

if (needClean) {
  del.sync(distPath); // 你刚才问的删除！
}
```

---

# 超级总结
`process.argv`
= **获取你在终端敲命令时，后面跟的所有参数**

---
### 小测验（一看就会）
命令：`node app.js hello 123`
`process.argv[2]` = **hello**
`process.argv[3]` = **123**

需要我教你**更优雅解析命令行参数**的方法吗？（比如用 `minimist` 库）