验证浏览器环境**没有命令行命令**，浏览器环境是**在浏览器里直接跑 JS**，常用两种方式：

---

## 1. 最简单：浏览器控制台（直接验证）
1. 打开 Chrome / Edge / 任意浏览器
2. 按 `F12` 或 `右键 → 检查 → Console`
3. 把测试代码粘贴进去回车

比如测试：
```js
console.log(typeof window)
console.log(typeof process)
console.log(this === window)
```

- 浏览器：`window` 存在，`process` 是 `undefined`
- Node：`window` 是 `undefined`，`process` 存在

---

## 2. 标准一点：建 HTML 文件用浏览器打开
新建 `test.html`：
```html
<script>
console.log('环境：', typeof window !== 'undefined' ? '浏览器' : 'Node')
console.log('this === window', this === window)
console.log('window', window)
console.log('process', typeof process)
</script>
```

直接双击打开这个 HTML 文件，按 F12 看 Console。

---

## 一句话总结
- 验证 Node 环境：`node test.js`
- 验证浏览器环境：**浏览器控制台 / 浏览器打开 HTML**

需要我给你一段**同时能在两边跑、自动打印环境差异**的完整对比代码吗？