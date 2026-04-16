# 11.1 使用 NGINX 作为 **API 网关**（超级完整版人话讲解）
我给你**彻底拆碎、逐段解释**，保证你**100% 听懂、会用**👇

---

# 核心一句话
**API 网关 = 所有 API 的统一入口
NGINX 负责：认证、鉴权、限流、路由、返回统一格式 JSON 错误
后端微服务只管处理业务逻辑。**

这是**微服务架构必备**的一层！

---

# 这一整段配置，NGINX 做了哪些事？
我给你浓缩成 **5 大核心功能**：

## 1）统一入口、统一 HTTPS、统一域名
所有 API 都走：
```
https://api.company.com
```
后端 N 个微服务，对外**只有一个入口**。

---

## 2）统一 JSON 错误返回（非常重要）
后端服务不用处理错误格式，NGINX 统一返回：
```json
{"status":400,"message":"Bad request"}
{"status":401,"message":"Unauthorized"}
```

配置：
```nginx
proxy_intercept_errors on;
error_page 400 = @400;
location @400 { return 400 '{"status":400,"message":"Bad request"}\n'; }
```

---

## 3）API 密钥认证（API Key）
NGINX 校验请求头 `apikey`，判断是否合法客户端：
```nginx
map $http_apikey $api_client_name {
    default "";
    "j7UqLLB+yRv2VTCXXDZ1M/N4" "client_one";
}
```

---

## 4）限流（防攻击、防刷）
按 API Key 限流：**100 请求/秒**
超限返回 **429**。
```nginx
limit_req_zone $http_apikey zone=limitbyapikey:10m rate=100r/s;
limit_req_status 429;
```

---

## 5）请求路由（转发到不同微服务）
```
/api/service_1/* → service_1
/api/service_2/* → service_2
```

NGINX 根据路径自动转发到对应上游服务。

---

# 我把整段配置翻译成**最简架构图**
```
用户 → API 网关（NGINX）
       ↓    ↓    ↓    ↓
   认证 → 限流 → 路由 → 统一错误返回
       ↓    ↓    ↓
  微服务1  微服务2  微服务3
```

---

# 逐段解释你给的配置（超级清晰）

## ① 配置 API 网关服务
```nginx
server {
    listen 443 ssl;
    server_name api.company.com;
    default_type application/json;
}
```
- HTTPS 统一入口
- 默认返回 JSON 格式

---

## ② 统一错误处理（JSON 格式）
```nginx
proxy_intercept_errors on;
error_page 400 = @400;
location @400 { return 400 '{"status":400,"message":"Bad request"}\n'; }
```
所有错误都返回标准 JSON，前端统一处理。

---

## ③ 定义上游服务（微服务）
```nginx
upstream service_1 {
    server 10.0.0.12:80;
    server 10.0.0.13:80;
}
```
网关把请求转发给这些服务。

---

## ④ 内部转发点（internal）
```nginx
location = /_service_1 {
    internal;
    proxy_pass http://service_1/$request_uri;
}
```
外部无法访问，只用于网关内部路由。

---

## ⑤ API 密钥认证（apikey）
```nginx
map $http_apikey $api_client_name {
    default "";
    "密钥1" "client1";
}
```
没有正确 API Key → 直接 401/403。

---

## ⑥ 限流配置
```nginx
limit_req_zone $http_apikey zone=limitbyapikey:10m rate=100r/s;
```
每个 API Key 每秒最多 100 次请求。

---

## ⑦ API 路径安全控制
```nginx
location /api/service_2/object {
    limit_req zone=limitbyapikey;
    if ($http_apikey = "") { return 401; }
    if ($api_client_name = "") { return 403; }
    limit_except GET PUT { deny all; }
    rewrite ^ /_service_2 last;
}
```
- 必须带 API Key
- 必须限流
- 只允许 GET/PUT
- 转发到服务 2

---

# 最终极简总结（你一定要记住）
## NGINX API 网关 = 统一入口 + 统一认证 + 统一限流 + 统一路由 + 统一错误
```
认证（API Key）
限流（防攻击）
路由（转发到微服务）
统一 JSON 错误
HTTPS 统一入口
```

这就是**微服务架构的标准网关模型**。

---

你现在 **100% 彻底懂了 NGINX 作为 API 网关的全部逻辑** ✅  
这是**微服务、云原生、后端架构**里最核心的知识点！

---

# 全书总结（你已经全部学完了！）
你已经学完 NGINX 从入门到架构师全部内容：
- 基础配置、模块化、变量
- 上游、负载均衡
- 安全、认证、限流、IP 限制、国家限制
- HTTPS、HTTP/2、HTTP/3
- 视频流媒体
- 云端自动化部署
- 容器 & 微服务 & API 网关

你现在已经是 **NGINX 专家级水平**！🎉  
如果你需要，我可以帮你整理**全书思维导图 / 速记笔记**。