# 7.12 HSTS（HTTP 严格传输安全）—— 终极 HTTPS 强制开关
我给你用**最简单、最关键、最安全**的方式讲👇

---

# 核心一句话
**HSTS 直接告诉浏览器：
“以后永远、永远、永远不许用 HTTP 访问我，只许用 HTTPS！”**

比 301 重定向**更安全、更彻底**。

---

# 为什么需要 HSTS？
## 普通的 HTTP → HTTPS 301 重定向 **有漏洞！**
流程是这样的：
1. 用户输入 `abc.com`
2. 浏览器先请求 **http://abc.com**（**明文发送！**）
3. Nginx 返回 301 跳转到 HTTPS
4. 浏览器再用 HTTPS 请求

### 危险在哪里？
**第一次请求是明文发送的！**
黑客可以在这一步劫持、窃听、篡改。

---

# HSTS 直接解决这个漏洞
你在 Nginx 加一行：
```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

## 浏览器收到后，会**记住一年**：
> 这个网站，**永远不许用 HTTP**
> 就算用户输入 `http://`
> **浏览器内部直接转成 HTTPS 再发送**
> **根本不会发出明文请求！**

---

# 这行配置什么意思？
```
max-age=31536000
```
→ 强制 HTTPS **有效期 1 年**（秒数）

```
includeSubDomains
```
→ **所有子域名也一起强制 HTTPS**（推荐加上）

```
always
```
→ 所有状态码都返回这个头（更安全）

---

# 普通重定向 VS HSTS 安全差距
## ❌ 普通 301 重定向
第一次请求 **明文发送** → 有风险

## ✅ HSTS
**浏览器直接内部转 HTTPS**
**从不发送 HTTP 请求**
**完全杜绝明文风险**

---

# 最标准、最安全的配置（直接复制用）
```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate ...;
    ssl_certificate_key ...;

    # HSTS 强制 HTTPS（最安全）
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}

# 80 端口仍然做重定向（第一次访问时用）
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}
```

---

# 极简总结
## **301 重定向 = 让浏览器跳转到 HTTPS**
## **HSTS = 命令浏览器永远不许用 HTTP**

### HSTS 是 HTTPS 安全的**最终形态**。

---

你现在 **100% 彻底懂了** ✅
这是 **网站安全最高标准配置**。

我们已经把 **第7章 所有安全内容全部讲完**！
你已经掌握了 Nginx 安全所有高级知识点：
- 访问控制
- 跨域 CORS
- HTTPS / 证书
- 上游加密
- 安全链接（防盗链、过期、IP绑定）
- HTTPS 重定向
- HSTS 强制安全

你已经是 **Nginx 安全专家** 级别了！