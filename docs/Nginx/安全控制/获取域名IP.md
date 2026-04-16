可以的，但**不是在 JavaScript 控制台里直接“读取”浏览器地址栏域名的 IP**，而是通过**间接方式获取**。下面分情况说明。

---

## 一、在浏览器控制台（Console）里能做什么 ✅

### ✅ 方法 1：使用 `fetch` / XHR + DevTools 看 IP
这是**最常用、最靠谱**的方式。

```js
fetch(location.href)
  .then(res => res.text())
  .then(console.log);
```

然后在：
- **Network（网络）面板**
- 点击该请求
- 查看 **Remote Address**

示例：
```
Remote Address: 104.21.23.112:443
```

✅ 这个就是**浏览器实际连接到的 IP 地址**

📌 说明：
- 包含 CDN / 负载均衡的真实出口 IP
- 最贴近浏览器行为

---

### ✅ 方法 2：WebRTC（只能拿本机 IP，不是域名 IP）⚠️

```js
const pc = new RTCPeerConnection({ iceServers: [] });
pc.createDataChannel("");
pc.createOffer().then(pc.setLocalDescription.bind(pc));

pc.onicecandidate = e => {
  if (e.candidate) {
    console.log(e.candidate.candidate);
  }
};
```

输出示例：
```
candidate: ... 192.168.1.10 ...
```

❌ **这是你本机的局域网 IP**
❌ 不是地址栏域名的 IP

---

### ✅ 方法 3：Service Worker（本质上还是请求）

```js
navigator.serviceWorker.register('/sw.js');
```

在 Service Worker 的 fetch 事件中：
- 同样依赖 Network 面板
- 本质和方法 1 一样

---

## 二、为什么 Console 里不能直接拿到域名 IP ❌

原因主要有：

1. **浏览器安全模型限制**
   - JS 不能直接访问 DNS 解析结果
   - 不能获取 socket / TCP 层信息

2. **同源策略**
   - 禁止跨主机网络信息暴露

3. **CDN / 多 IP**
   - 一个域名可能对应多个 IP
   - 浏览器只连接其中一个

---

## 三、真正“解析域名 IP”的方式（非 Console）

### ✅ 命令行方式（最准确）

```bash
# Windows
nslookup example.com

# macOS / Linux
dig example.com
```

或：

```bash
ping example.com
```

⚠️ 注意：
- 可能和浏览器访问的 IP **不一致**
- 浏览器可能使用：
  - HTTPSSVC / ECH
  - 不同的 DNS（DoH）
  - 不同的 CDN 节点

---

## 四、总结对比

| 方式 | 能否获取域名 IP | 说明 |
|----|----|----|
| Console JS | ❌ | 无法直接获取 |
| fetch + Network | ✅ | 实际连接 IP |
| WebRTC | ❌ | 本地 IP |
| dig / nslookup | ✅ | DNS 解析 IP |
| ping | ✅ | 系统 DNS |

---

如果你愿意，我可以：
- ✅ 帮你写一个 **一键控制台脚本**
- ✅ 解释 **为什么 CDN 下 IP 会变**
- ✅ 分析 **HTTPS / ECH 对 IP 的影响**

你现在是在 **调试、安全测试还是学习目的**？