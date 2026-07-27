`arrayBuffers` 就是 **`external` 内存里，专门由 ArrayBuffer / TypedArray / Buffer 占用的那一部分**。

### 关系一句话总结
- `arrayBuffers` ⊂ `external`
- 所以通常：
  ```
  arrayBuffers ≤ external
  ```

### 完整内存结构（最清晰版）
```
rss（进程总物理内存）
├── heapTotal（V8 已申请堆）
│    └── heapUsed（实际使用的 JS 对象内存）
├── external（C++ 管理的外部内存）
│    └── arrayBuffers（ArrayBuffer / Buffer / TypedArray 内存）
└── 其他系统开销
```

### 你这行代码的作用
```js
console.log('arrayBuffers:', (mem1.arrayBuffers / 1024 / 1024).toFixed(2), 'MB');
```
就是单独打印出 **Buffer / ArrayBuffer 占用的内存大小**。

---

### 小规律
- 普通 Node 程序：`arrayBuffers` 很小，几 MB 以内
- 大量文件读写、网络流、加密、图像处理：`arrayBuffers` 会明显变大
- 几乎永远满足：
  ```
  arrayBuffers ≤ external < heapTotal ≤ rss
  ```

如果你愿意，我可以把这 **5 个字段（rss、heapTotal、heapUsed、external、arrayBuffers）** 整理成一段**可直接复制运行、带单位格式化**的完整监控代码。