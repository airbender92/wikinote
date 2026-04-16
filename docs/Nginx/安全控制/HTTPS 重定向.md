# 7.10 HTTPS 重定向（超级简单人话版）
我给你**一次性讲透、讲明白**，这是 Nginx 最常用、最简单的配置之一👇

---

# 核心一句话
**用户访问 http:// 网址 → 自动跳转到 https://**
让所有流量都走加密，不暴露数据。

---

# 配置分成两部分
## 1）80 端口（HTTP）
专门负责**重定向**
```nginx
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;
    return 301 https://$host$request_uri;
}
```

## 2）443 端口（HTTPS）
真正提供网页服务
```nginx
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    ssl_certificate /etc/nginx/ssl/example.crt;
    ssl_certificate_key /etc/nginx/ssl/example.key;
}
```

---

# 逐行解释（你一看就懂）

## `listen 80`
监听 HTTP 默认端口

## `server_name _;`
匹配**所有域名**

## `return 301 https://$host$request_uri;`
**重点！**
- 301 = 永久重定向（SEO 友好）
- `$host` = 你的域名
- `$request_uri` = 后面的路径

### 效果：
```
http://www.xxx.com/page
→ 自动跳转到
https://www.xxx.com/page
```

---

# 为什么要这么做？
- 用户可能手动输入 `http://`
- 老链接可能是 HTTP
- **强制走 HTTPS 加密更安全**

---

# 什么时候用 301？
✅ 永久迁移到 HTTPS  
✅ 推荐使用（浏览器会记住）

---

# 如果你只想部分页面加密
比如只对登录页走 HTTPS：
```nginx
location /login {
    return 301 https://$host$request_uri;
}
```

---

# 最终极简总结
**HTTP（80端口）只做一件事：
return 301 https://$host$request_uri;
全部自动跳转到 HTTPS。**

---

你现在 **100% 彻底懂了**！
这是网站上线**必配**的基础配置。

我们已经把 **第7章 安全相关全部讲完** ✅
你已经掌握了：
- IP 访问控制
- CORS 跨域
- HTTPS 配置
- 上游加密
- 安全链接（防盗链、过期、绑定IP）
- HTTP 自动跳转 HTTPS

要继续讲 **第8章 负载均衡、上游服务、代理** 吗？