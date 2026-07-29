# `Promise.all` 一句话讲透
**并行执行多个 Promise，等全部成功后一起返回结果；只要一个失败，整体立刻失败。**

---

# 核心特点
1. **并行执行**
   所有 Promise 几乎同时开始跑，不是一个一个排队。

2. **全部成功才成功**
   等到**最后一个**完成，才 resolve，并按**传入顺序**返回数组。

3. **一个失败就整体失败**
   只要有一个 rejected，`Promise.all` **立刻失败**，不会等其他的。

4. **返回顺序固定**
   结果数组顺序 = 你传入的顺序，跟谁先跑完无关。

---

# 最简单示例
```js
const p1 = Promise.resolve(1)
const p2 = Promise.resolve(2)
const p3 = Promise.resolve(3)

Promise.all([p1, p2, p3]).then(res => {
  console.log(res) // [1,2,3]
})
```

---

# 放到你刚才的 pbkdf2 压测里
```js
await Promise.all(
  Array.from({ length: 8 }, () => benchOne())
)
```

- 一次性发起 **8 个 pbkdf2 异步调用**
- 但 Node 底层 libuv 线程池默认只有 4 个线程
- 所以实际是 **4 个并行，剩下 4 个排队**
- 等 8 个全部跑完，`Promise.all` 才结束

这就是你测线程池的原理。

---

# 对比理解
- `Promise.all`：**全成功才算成功，并行**
- `Promise.race`：**谁先完算谁，不管成功失败**
- `Promise.allSettled`：**不管成功失败，全部等完**
- `Promise.any`：**只要一个成功就成功**

---

# 极简总结
`Promise.all([...promises])`
= **一起跑 → 等全部 → 一起返回**
= 并发异步任务的最常用工具。