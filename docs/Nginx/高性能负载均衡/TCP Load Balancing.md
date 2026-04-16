# 2.2 TCP 负载均衡 — 大白话解释
**TCP 负载均衡**就是：
不只处理网页（HTTP），而是对**任意基于 TCP 协议的服务**做流量分发。

---

## 和 HTTP 负载均衡的区别
- **HTTP 负载均衡**：只懂网页、接口，能看懂网址、路径、Cookie。
- **TCP 负载均衡**：不懂具体内容，只负责**转发数据流**，适用于数据库、SSH、游戏服务、MQ 等。

## 适用场景
- MySQL、PostgreSQL、Redis
- SSH、远程桌面
- 游戏服务器、物联网服务
- 各种自定义 TCP 服务

## Nginx 里怎么写？
TCP 负载均衡不在 `http` 块，而是在顶层的 **`stream` 块**里：
```nginx
stream { 
    upstream mysql_read { 
        server read1.example.com:3306 weight=5;
        server read2.example.com:3306;
        server 10.10.12.34:3306 backup;
    }
    server { 
        listen 3306;
        proxy_pass mysql_read;
    } 
}
```

---

# 超精简总结
**TCP 负载均衡 = Nginx 转发底层 TCP 数据流，给数据库、SSH、游戏等非 HTTP 服务做负载均衡。**


---------------
------------

我给你**最通俗、最清晰、不啰嗦**的完整解释，一次性看懂这段到底在干嘛👇

# 核心一句话
这是 **Nginx 做 TCP 负载均衡（给 MySQL 数据库用）** 的完整正确配置方法。
和 HTTP 网站配置**完全分开**，不能放一起。

---

# 1. 这段配置是干嘛的？
给 **MySQL 数据库**做负载均衡：
- 2 台主库（读库）负责处理查询
- 1 台备用库，主库挂了才顶上
- Nginx 监听 3306 端口，自动分发请求

---

# 2. 关键区别（必须记住）
- **HTTP 网站** → 放在 `http {}` 里
- **TCP 服务（MySQL/Redis/SSH）** → 必须放在 `stream {}` 里
**不能混用！**

---

# 3. 正确的文件结构（官方规范）
```
/etc/nginx/
├── nginx.conf           # 主配置
├── conf.d/              # 放 HTTP 网站配置
└── stream.conf.d/       # 放 TCP 负载均衡配置（新建文件夹）
```

---

# 4. 主配置 nginx.conf 怎么写？
```nginx
stream {
    include /etc/nginx/stream.conf.d/*.conf;
}
```
意思：加载所有 TCP 负载均衡配置。

---

# 5. TCP 配置文件内容（mysql_reads.conf）
```nginx
upstream mysql_read {
    server read1.example.com:3306 weight=5;  # 权重 5
    server read2.example.com:3306;          # 权重默认 1
    server 10.10.12.34:3306 backup;         # 备用服务器
}

server {
    listen 3306;               # 监听 MySQL 端口
    proxy_pass mysql_read;     # 转发给上面的服务器组
}
```

---

# 6. 权重是什么意思？
- 第一台：权重 5
- 第二台：权重 1
**每 6 个请求：5 个给第一台，1 个给第二台**

---

# 7. backup 是什么？
备用服务器，**只有主服务器全部挂掉**才会启用。

---

# 超精简总结（最重要 3 点）
1. **stream {} = TCP 负载均衡**（给数据库等非HTTP服务）
2. **不能放在 conf.d/**，必须放 **stream.conf.d/**
3. **upstream 定义服务器组，proxy_pass 转发流量**

这就是 Nginx 做 **TCP 负载均衡**的完整标准用法。

***
***

我用**最直白、不绕弯、好理解**的方式，把这段长文一次性讲透👇

# 核心一句话
`http` 和 `stream` 的区别就是：**一个懂网页（7层），一个只转发数据流（4层）**。

---

# 逐段通俗解释

## 1. 最关键的区别：OSI 模型层级
- **http 模块**：工作在 **7层（应用层）**
  能看懂 HTTP 协议，懂域名、路径、Cookie、Header，能智能处理网页请求。

- **stream 模块**：工作在 **4层（传输层）**
  只负责转发 TCP 数据包，**看不懂网页内容**，只做流量转发，适合 MySQL、Redis、SSH 等。

---

## 2. stream 能干嘛？
- 做 **TCP 负载均衡**
- 监听一个端口
- 转发到后端服务器或 upstream 服务器组
- 可以配置超时、SSL、连接数等

---

## 3. upstream 配置和 HTTP 很像
stream 里的 upstream 用法基本和 HTTP 一样：
- 配置服务器 IP 或域名
- 设置权重 weight
- 设置 backup 备用
- 设置最大连接数
- 健康检查

---

## 4. NGINX Plus 商业版功能更多
比如更高级的健康检查、连接控制、动态配置等。

---

## 5. 健康检查后面会讲
不管是 HTTP 还是 TCP 负载均衡，都会讲怎么检测后端服务器是否挂了。

---

# 超精简总结
- **http = 7层，懂 HTTP，处理网页**
- **stream = 4层，不懂协议，只转发 TCP 流量**
- 两者 upstream 用法几乎一样
- stream 专门用来给数据库、游戏、SSH 做负载均衡