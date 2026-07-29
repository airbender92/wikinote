```js
function runMultiplexingProof(){
    const server = net.createServer(socket => {
        socket.end('hello from single-thread server \n');
    });

    server.listen(0, () => {
        const port = server.address().port;
        const clientCount = 50;
        let connected = 0;
        let closed = 0;
        const start = Date.now();

        for(let i = 0; i < clientCount; i++){
            const client = net.connect(port, '127.0.0.1', () => {
                connected++;
            });
            client.on('data', () => {});
            client.on('close', () => {
                closed++;
                if(closed === clientCount){
                    const cost = Date.now() - start;
                    console.log(`单线程 server 处理 ${clientCount} 个客户端连接耗时: ${cost}ms`);
                    console.log(`连接成功的客户端数量: ${connected}, 关闭的客户端数量: ${closed}`);
                    console.log(' 一个主线程，多路复用即可抗住大量客户端连接，单线程 server 也能处理大量客户端连接');
                    server.close(() => {

                    });
                }
            });
            client.on('error', err => {
                console.log(`[client error]`)
            })
        }
    });

    server.on('error', (err) => {
        console.log(`server err`)
    })
}

```

这段代码的核心目的只有一个：
**证明 Node.js 单线程 + IO 多路复用，就能轻松处理大量 TCP 连接，不需要开很多线程。**

我给你用最清晰、最直白的方式讲透。

---

# 1. 代码在干什么
1. 用 `net.createServer` 建一个 **最简单的 TCP 服务器**
2. 服务器逻辑：收到连接就返回一句 hello 并关闭
3. 一次性发起 **50 个客户端连接** 同时连上去
4. 统计全部连接建立 + 关闭的总耗时
5. 最后输出结论：
   **单线程就能扛大量连接，不需要多线程**

---

# 2. 关键知识点：IO 多路复用（epoll/kqueue/iocp）
你看到 50 个连接同时进来，但：

- **整个服务只有 1 个主线程**
- **没有额外开线程**
- **不使用 libuv 线程池**

操作系统内核提供 **IO 多路复用**：
- 一个线程可以**同时监听成千上万个 socket**
- 哪个 socket 有数据来了，就处理哪个
- 空闲连接完全不消耗 CPU

这就是 Node.js 高并发的根基。

---

# 3. 为什么这叫“多路复用”？
- **一路主线程**
- 监听 **多路（多个）TCP 连接**
- 内核帮忙监视所有连接状态
- 有事件才处理，没事件就休眠

所以：
**单线程 = 能处理成千上万连接**

---

# 4. 运行结果你会看到
```
单线程 server 处理 50 个客户端连接耗时: 几 ms
连接成功的客户端数量: 50, 关闭的客户端数量: 50
一个主线程，多路复用即可抗住大量客户端连接，单线程 server 也能处理大量客户端连接
```

非常快，几乎瞬间完成。

---

# 5. 和之前的 fs / crypto 对比（超级重要）
- **网络 IO（net / http）**：
  使用 **IO 多路复用**
  不占 libuv 线程池
  单线程能扛 10k+ 连接

- **文件 IO、crypto、dns**：
  用 **libuv 线程池**
  默认只有 4 个线程
  多了就排队

这就是 Node 高并发的核心区别。

---

# 6. 一句话总结
`runMultiplexingProof` 这个函数就是：

**用一个最简单的 demo，证明 Node.js 依靠 IO 多路复用，单线程就能处理大量客户端连接，不需要为每个连接开一个线程。**