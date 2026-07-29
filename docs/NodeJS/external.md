`external` 表示 **Node.js 中由 C++ 层面管理、不属于 V8 堆的外部内存**，最常见来源是：
`Buffer`、`ArrayBuffer`、TypedArray、addon 扩展等。

### 一句话关系
```
rss（进程总内存）
  = heapTotal（V8已申请堆）
  + external（外部C++内存）
  + 其他系统开销
```

你这行代码：
```js
console.log('external:', (mem1.external / 1024 / 1024).toFixed(2), 'MB');
```
就是把 **external 字节数转成 MB** 打印出来。

---

### 简单类比
- **heapUsed / heapTotal**：JS 对象、变量用的“JS 堆内存”
- **external**：Buffer 这类“底层二进制内存”
- **rss**：整个 Node 进程占操作系统的真实物理内存

---

### 典型大小规律
一般情况：
```
rss > heapTotal ≥ heapUsed
external 通常比较小（几 MB 以内）
```
但如果你大量创建 `Buffer`，`external` 会明显变大。

需要我帮你把 **rss / heapTotal / heapUsed / external** 四者关系整理成一句好记的口诀吗？