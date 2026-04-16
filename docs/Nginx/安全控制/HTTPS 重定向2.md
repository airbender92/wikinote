# 7.11 七层代理/负载均衡下的 HTTPS 重定向
## **人话版彻底讲懂**

我来用最简单、最真实的场景给你讲，**你马上就能明白**👇

---

# 先搞懂这个场景：**SSL 不在 Nginx 上终止，而是在前面的代理上**

架构是这样的：
```
用户 → 阿里云/腾讯云/AWS ELB（负载均衡）→ Nginx
```

### 重点：
- **ELB/负载均衡 负责 SSL 证书**（443 端口）
- **Nginx 只收到 HTTP（80 端口）**

也就是说：
- 用户访问是 **HTTPS**
- 到 Nginx 这里已经变成 **HTTP**

---

# 问题来了：
Nginx 看到的**永远是 HTTP 80**，
它**不知道用户实际用的是 HTTPS**。

那怎么判断用户是不是用了 HTTP 未加密访问？

---

# 答案：**X-Forwarded-Proto** 请求头

负载均衡会把**用户真实的协议**通过这个头带给 Nginx：

- 用户用 HTTPS → `X-Forwarded-Proto: https`
- 用户用 HTTP → `X-Forwarded-Proto: http`

---

# 所以这个配置的意思：

```nginx
if ($http_x_forwarded_proto = 'http') {
    return 301 https://$host$request_uri;
}
```

## 翻译成人话：
> **如果用户是用 HTTP 访问的，就重定向到 HTTPS。
> 如果已经是 HTTPS，就不跳转。**

---

# 为什么要这么做？
因为：
- Nginx 前面有 **SLB/ELB/七层负载均衡**
- 证书在负载均衡上
- Nginx 看不到是否 HTTPS
- 只能靠 **X-Forwarded-Proto** 头判断

---

# 这个变量哪里来的？
```
$http_x_forwarded_proto
```

就是 Nginx 自动从 **请求头 X-Forwarded-Proto** 取出来的值。

---

# 最精简总结
## **正常 HTTPS 重定向（证书在 Nginx）：**
```
listen 80;
return 301 https://...;
```

## **七层代理下（证书在负载均衡）：**
```
if ($http_x_forwarded_proto = http) {
    return 301 https://...;
}
```

---

你现在 **100% 彻底懂了**！
这是**云服务器 + 负载均衡**架构里最常用的 HTTPS 重定向方式。

我们已经把 **第7章 安全所有内容全部讲完** ✅
你已经掌握了 Nginx 安全全部核心！

要不要继续讲 **第8章 负载均衡、上游、代理**？