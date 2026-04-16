# 2.1 HTTP 负载均衡 — 大白话解释
**HTTP Load Balancing**，就是把用户访问网站 / 接口的 HTTP 请求，均匀分给多台后端服务器，不让某一台压力过大、导致变慢或挂掉。

简单说：
**用户只访问 Nginx，Nginx 再把请求转发给后面一堆服务器，谁闲就分给谁。**

---

# 核心作用
- 分担流量压力，提高并发承载能力
- 某台后端服务器挂了，Nginx 自动不把请求发给它
- 可以平滑增加服务器，实现水平扩展

---

# 最典型的 Nginx 配置长这样
```nginx
http {
    upstream backend_servers {
        server 192.168.1.10;
        server 192.168.1.11;
        server 192.168.1.12;
    }

    server {
        listen 80;
        location / {
            proxy_pass http://backend_servers;
        }
    }
}
```

- `upstream`：定义一组后端服务器
- `proxy_pass`：把请求转发给这组服务器
- Nginx 自动按策略分发请求

---

# 超精简总结
**2.1 HTTP 负载均衡 = Nginx 接收 HTTP 请求 → 转发给多台后端服务器 → 分摊压力、保证稳定。**

----

```nginx
upstream backend { 
    server 10.10.12.45:80 weight=1;
    server app.example.com:80 weight=2;
    server spare.example.com:80 backup;
    }
    server { 
        location / { 
            proxy_pass http://backend;
    } }
```

# 核心大白话解释（一段彻底懂）
这段就是 **Nginx 最经典的 HTTP 负载均衡配置**，我用最简单的话讲清楚：

---

## 1. 这段配置在干嘛？
- 定义了一组叫 `backend` 的**后端服务器组**
- 里面有 **2 台主服务器** + **1 台备用服务器**
- 用户访问网站 → Nginx 自动把请求分给这 2 台主服务器
- **主服务器全挂了 → 备用服务器才会顶上**

---

## 2. 每台服务器什么意思？
```
server 10.10.12.45:80 weight=1;
```
- 第一台服务器，**权重 1**
```
server app.example.com:80 weight=2;
```
- 第二台服务器，**权重 2**
```
server spare.example.com:80 backup;
```
- 第三台服务器，**备用（backup）**

---

## 3. 权重 weight 是什么？
**权重 = 分配请求的比例**
- 权重 1 : 权重 2
- 意味着 **每 3 个请求**：
  - 1 个给第一台
  - 2 个给第二台

**不写 weight 默认就是 1**

---

## 4. backup 是什么？
**备用服务器**
- 平时不干活
- 只有**两台主服务器都不可用**时才自动启用

---

## 5. 最后这段干嘛？
```
location / {
    proxy_pass http://backend;
}
```
把用户请求**转发给上面定义的 backend 服务器组**，实现负载均衡。

---

# 超精简总结
- **upstream** = 定义一组服务器
- **weight** = 分配请求比例
- **backup** = 备用服务器
- **proxy_pass** = 转发请求实现负载均衡

这就是 Nginx 负载均衡的**标准用法**。

----

这段文字的核心意思，用**一段通俗、完整、不绕弯**的方式给你讲明白：

# 整体解释
`upstream` 模块是 Nginx 专门用来做 **HTTP 负载均衡**的核心模块。
它的作用就是：
- 定义一组后端服务器池（可以是 IP、域名、Unix 套接字随便混着写）
- 决定请求如何分发给这些服务器

里面用 `server` 指令添加每一台后端服务器，还可以加各种参数精细控制：
- `weight`：权重，决定分发比例
- 标记服务器是否可用、备用、下线
- 配置怎么判断服务器挂了

如果你用的是 **Nginx Plus 商业版**，还能额外控制：
- 后端连接数限制
- 更精细的 DNS 解析
- 服务器刚启动时缓慢增加连接（避免一上来就压垮）

---

# 超精简总结
**upstream = 定义服务器池 + 配置负载均衡规则
server = 添加后端并设置权重、状态等
Nginx 开源版够用，商业版功能更细。**