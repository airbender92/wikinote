# Session‑Cookie模式完整讲解(JSESSIONID)

## 1. 什么是 JSESSIONID

`JSESSIONID` 是 **Java Servlet 规范里的会话ID**，是Tomcat、Jetty等Java服务端生成的标识：

1. 用户登录成功后，后端在服务器内存/Redis 创建一份用户会话对象 `Session`，里面保存用户id、账号、权限等登录信息。
2. 后端生成一串唯一字符串 `JSESSIONID`，通过响应头 `Set‑Cookie` 返回浏览器。

```http
Set‑Cookie: JSESSIONID=abc123xxxx; Path=/; HttpOnly
```

3. 浏览器收到，把这个值存到当前域名下的Cookie。
4. **之后浏览器访问该域名下任意接口，会自动把这条Cookie放进Request Headers的Cookie字段传给后端**。
5. 后端拿到请求里的`JSESSIONID`，去服务端查找对应的Session，就知道“这是哪个登录用户”。

> ⚠️关键点：
>
> - **真正用户登录信息保存在后端服务器，不在浏览器！Cookie只存一个会话编号ID。**
> - `HttpOnly`：JS脚本不能读取、修改这个Cookie，防止XSS窃取会话。
> - 过期：服务端Session超时销毁，就算浏览器Cookie还在，接口也会返回未登录。

---

## 2. 整套Session‑Cookie完整流程（就是你现在项目的模式）

### ① 登录请求

前端调用登录接口，提交账号密码，**前端不操作任何token/cookie**。
后端校验账号密码正确：

1. 在服务端创建Session，保存该用户信息
2. 返回HTTP响应头：`Set‑Cookie: JSESSIONID=xxx`
3. 浏览器收到`Set‑Cookie`，自动写入浏览器Cookie存储。**这里前端JS一行代码都不用写，浏览器自动存。**

### ② 之后调用任意业务接口（你的/homePage接口）

前端直接发axios请求，**代码完全不需要手动设置headers、不需要塞任何token**。
👉浏览器底层网络模块自动读取本域名全部Cookie，自动塞进Request Headers的`Cookie`字段发送给后端。

> 注意：Cookie不属于axios的`config.headers`，所以你在`request.interceptors`打印config永远看不到它。

### ③ 后端鉴权

后端从请求的Cookie拿到`JSESSIONID`，根据ID取出服务端Session，拿到登录用户信息，鉴权通过返回数据。

### ④ 登出逻辑

- 方式1：调用登出接口，后端销毁服务器上Session；浏览器Cookie还在，但是ID已经失效。
- 方式2：后端返回Set‑Cookie把JSESSIONID设置过期，浏览器清除该Cookie。

> ✨核心本质：**会话状态保存在后端服务器，浏览器只保存会话凭证ID，传输交给浏览器自动处理，前端代码无感。**

> 和Token模式对比：
>
> - Token模式：凭证全部返回给前端，前端手动存localStorage，请求拦截器手动塞到Header；后端不需要在服务端存会话。
> - Session‑Cookie模式：会话存在后端，浏览器自动携带Cookie，前端代码不用管凭证。

---

## 3. 问题：部分接口不需要登录鉴权（不需要session），是谁控制？

**全部是后端控制，前端不需要做任何特殊处理。**

举例子：登录接口、验证码接口、公开公告接口，不需要登录就能访问。

### 后端逻辑

1. 后端拦截器/过滤器统一拦截所有请求。
2. 维护一份**白名单URL列表**：`/login`、`/captcha`等。
3. 如果请求路径命中白名单：**直接放行，不去校验JSESSIONID是否有效**。
4. 如果不在白名单：读取Cookie里的`JSESSIONID`，查找session，session不存在/失效，返回401未登录。

> 👉不管接口要不要鉴权，**浏览器每次请求都会带上全部Cookie（包含JSESSIONID）**。
> 只是后端对白名单接口忽略这个Cookie，不去校验会话是否有效。
> 前端代码不需要区分接口，不用判断“这个接口要不要带凭证”，浏览器统一带上，后端决定要不要校验。

> ❗前端不能做鉴权判断！不安全。前端白名单可以做页面跳转控制，但是接口权限校验必须后端。

### 常见疑问

Q：不需要登录的接口，能不能不让浏览器带上JSESSIONID？
A：**同域请求浏览器一定会自动带上域名下所有Cookie，前端JS无法阻止浏览器发送Cookie**。只能后端忽略它。

---

## 4. 该模式常见坑点

### 坑1：为什么axios打印config.headers看不到JSESSIONID

Cookie是浏览器HTTP底层行为，不属于axios headers对象。axios的headers只管理你代码主动设置的请求头。Cookie是浏览器单独的一块。

### 坑2：跨域场景直接失效（重点）

- **同域（你现在场景：页面域名和接口域名完全一样）**：浏览器自动携带Cookie，啥都不用配置。
- **跨域场景（页面域名A，接口域名B）**：浏览器默认不会自动发送Cookie！
  此时axios必须配置：

```js
axios.defaults.withCredentials = true;
```

同时后端CORS配置不能返回`*`，要指定允许的源，否则浏览器拒绝携带Cookie。

> 你现在环境是同域，所以`withCredentials`不需要配置，一切正常。

### 坑3：JSESSIONID丢失问题

1. 后端重启，内存里Session全部清空，就算浏览器Cookie还在，会话失效，需要重新登录。

> 解决：后端把Session放到Redis共享存储，多实例、重启会话不丢失。

2. Cookie过期清除，会话丢失。
3. 页面打开新标签，同域名Cookie共享，会话共用，不用重复登录。

### 坑4：HttpOnly

JSESSIONID标记`HttpOnly`，`document.cookie` JS拿不到，无法在控制台读取，防止XSS脚本偷会话。

---

## 5. Session‑Cookie模式 vs Token模式（快速区分）

| 项目       | Session‑Cookie(JSESSIONID)             | Token模式(JWT等)                       |
| ---------- | -------------------------------------- | -------------------------------------- |
| 凭证存放   | 浏览器Cookie                           | localStorage/sessionStorage            |
| 携带凭证   | 浏览器自动发送Cookie，前端代码不用处理 | 请求拦截器手动加到Header Authorization |
| 会话存储   | 后端服务器存Session会话                | 后端不存会话，信息写在Token字符串内部  |
| 跨域       | 需要开启withCredentials，后端CORS配合  | 跨域友好，无Cookie限制                 |
| 登出       | 后端销毁服务端Session                  | 前端删除本地存储token                  |
| 你代码表现 | 打印axios config看不到鉴权信息         | headers可以看到token字符串             |

## 6. 结合你截图的现象再复盘一遍

1. 登录接口响应头返回`Set‑Cookie: JSESSIONID=xxx`，浏览器保存。
2. 你调用`getHomePage.do`，前端axios代码一行没有设置token。
3. 浏览器发出http请求，自动把`JSESSIONID`、`galaxy_token`塞进Request Header的Cookie字段。
4. 后端过滤器拿到Cookie中的JSESSIONID，找到服务端Session，确认登录身份，返回200数据。
5. 在axios request拦截器打印`config.headers`，看不到鉴权凭证，因为Cookie不归axios headers管理。
6. 如果后端把某个接口加入白名单，就算Cookie携带过来，后端也不校验登录状态，接口可以匿名访问。

如果你需要，我可以简单讲下这个模式下，**如果做前后端分离跨域部署会遇到哪些问题以及解决方案**。
