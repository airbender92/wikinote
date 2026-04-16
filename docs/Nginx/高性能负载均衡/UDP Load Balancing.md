# 2.3 UDP 负载均衡 · 超通俗完整解释
这段话就是在讲：**Nginx 不仅能做 HTTP、TCP 负载均衡，还能做 UDP 负载均衡**，用法几乎一样，只多一个关键字 `udp`。

---

## 1. 什么是 UDP 负载均衡？
UDP 是一种**不建立稳定连接、只管发包**的协议，常见服务有：
- NTP 时间同步
- DNS 域名解析
- VoIP 网络电话
- OpenVPN
- HTTP/3（QUIC）

Nginx 可以把这些 UDP 请求均匀分给多台后端服务器。

---

## 2. 最简单的 UDP 配置（NTP 例子）
```nginx
stream {
  upstream ntp {
    server ntp1.example.com:123 weight=2;
    server ntp2.example.com:123;
  }

  server {
    listen 123 udp;  # 关键：加 udp
    proxy_pass ntp;
  }
}
```

- `listen 123 udp`：告诉 Nginx 这是 **UDP 端口**
- 其余 `upstream`、`weight`、`backup` 用法和 TCP/HTTP 完全一样

---

## 3. reuseport 是干嘛的？
```nginx
listen 1195 udp reuseport;
```
- 适用于**需要多次来回发包**的服务（OpenVPN、VoIP 等）
- 让内核把连接均匀分给 Nginx 多个工作进程
- 只在高版本 Linux、FreeBSD 上有效

---

## 4. 为什么不用 DNS 轮询，非要 Nginx？
- DNS 只能简单轮询，**没有负载均衡算法**
- DNS 不能做健康检查，服务器挂了还会解析过去
- Nginx 可以负载均衡 **DNS 本身**
- 能控制连接、限流、超时等

---

## 5. UDP 与 TCP 的主要区别
- TCP：面向连接，稳定可靠
- UDP：面向数据包（datagram），不建立长连接
- UDP 多了一个 `proxy_responses`：控制后端最多返回几个包
- 默认不限制，直到 `proxy_timeout` 超时关闭

---

# 超精简总结
- UDP 负载均衡 **在 stream 模块里**，和 TCP 写法几乎一样
- 只需要在 `listen` 后加 `udp`
- 用于 NTP、DNS、VoIP、OpenVPN、HTTP/3
- `reuseport` 优化多包交互场景性能
- 比 DNS 轮询更稳定、更强大、更可控