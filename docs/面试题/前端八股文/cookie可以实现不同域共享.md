# Cookie 跨域/不同域共享

**普通 Cookie 默认不能跨不同域名共享**，但有 `Domain` 属性可以实现**二级域名共享**；**完全不同一级域名（a.com 和 b.com）Cookie 无法直接共享**，这是浏览器同源策略强制限制。

## Cookie Domain 属性核心规则

Cookie有4个关键属性：`Domain`、`Path`、`Secure`、`SameSite`。

> Domain 决定这个 cookie 可以被哪些域名访问。

### 1. 同根域名，二级域名共享（可以实现）

示例：

- 主域：`example.com`
- 子域：`a.example.com`、`b.example.com`

设置 Cookie 的 `Domain=.example.com`（注意前面的点，现代浏览器可以省略点，写 `example.com` 效果一致）

```http
Set‑Cookie: token=abc123; Domain=example.com; Path=/; Secure
```

✅ 此时：

- `example.com`
- `a.example.com`
- `b.example.com`

**都可以读写这个 cookie**，实现多子域共享登录态。

> 关键点：设置cookie的时候，**只能把Domain设置为当前域名或者它的父域名**。
> 你在 `a.example.com` 不能设置 Domain=`other.com`，浏览器直接拒绝。

### 2. 完全不相关一级域名：`a.com` 和 `b.com`

❌ **不能直接设置Domain实现cookie共享**。
浏览器安全机制，禁止一个一级域名读写另外一个一级域名的Cookie。

> `a.com` 无法写一个 cookie 给 `b.com`。

## 如何实现不同一级域名之间传递登录态（a.com ↔ b.com）

Cookie不能直接共享，有几种常见工程方案：

### 方案1：中转页面跳转（SSO单点登录）

1. 用户访问 `a.com` 需要登录，跳转到统一认证中心 `sso.com`
2. `sso.com` 登录成功，种下属于 `sso.com` 的cookie
3. 再跳转回 `a.com`，带回token；a.com把token存自己业务cookie。
4. 访问 `b.com` 同样跳转 sso.com；sso.com 携带自己的cookie识别已登录，回传给b.com。

> 本质：**cookie只属于sso.com，业务域名不互相读对方cookie，靠跳转传递凭证**。

### 方案2：通过后端接口代理（CORS + 后端转发）

前端 `a.com` 的页面请求后端接口，后端服务去请求 `b.com`，服务端不受浏览器cookie同源限制；

> **服务端之间可以随便携带cookie，限制只存在浏览器端。**

### 方案3：使用 localStorage / postMessage 传递token

localStorage 完全隔离，不同域不能直接读；
可以通过 iframe + postMessage 跨域传递 token 字符串，业务拿到后写入自己域的cookie。

> 注意安全，做好origin校验，防止CSRF。

## 容易混淆点：SameSite 对Cookie跨站发送的影响

`SameSite` 不是控制能不能读写cookie，而是**跨站请求时，会不会自动带上Cookie**。

- `SameSite=Lax`（浏览器默认）：GET跳转可以携带，AJAX跨站请求不带cookie
- `SameSite=None; Secure`：**跨站请求可以自动携带Cookie**

> ⚠️注意：`SameSite=None` ≠ 可以读写对方域Cookie！
> 只是你发请求的时候，可以带上本域自己的cookie，**依然读不到别人域的cookie**。

举个例子：
页面 `a.com` 发起fetch请求 `https://b.com/api`，设置 `credentials: 'include'`，并且b.com返回cookie `SameSite=None; Secure`。
👉 请求会带上**属于b.com的cookie**（b域的），**但是 a.com 的 JS 拿不到、读取不到 b.com 的cookie，只是http请求自动携带**。

> JS document.cookie 只能读取**当前页面域名下**的cookie。

## 浏览器端 Cookie 访问权限总结

1. **JS `document.cookie`**：只能拿到**当前页面域名**下匹配 Domain、Path 的 Cookie。拿不到其他域cookie。
2. **HttpOnly Cookie**：JS完全读不到，只有http请求自动携带。
3. 子域共享：设置 `Domain=主域名.com`，所有二级子域共享cookie。
4. **完全不同一级域名：浏览器层面无法直接共享cookie**，只能靠SSO、后端中转、postMessage传递凭证。

## 常见坑

1. 设置Domain的时候写错，例如在 `a.example.com` 设置 `Domain=example.com`，协议必须是https，配合Secure；http下很多浏览器会忽略Domain父域。
2. SameSite 默认Lax，跨站iframe、跨站ajax不会携带cookie，需要显式设置 `SameSite=None; Secure`。
3. Domain不能随意设置别的根域名，浏览器会直接丢弃这条Set‑Cookie。
4. localhost是特殊域名，Domain设置不生效。

## 面试简答

> 1. **子域之间可以共享Cookie**：设置 `Domain=父域名`，所有二级子域都能读写该cookie。
> 2. **完全不同一级域名，浏览器不能直接共享Cookie**，浏览器安全策略禁止A域读写B域Cookie。
> 3. 跨一级域名登录共享需要SSO单点登录跳转、后端代理等方案。
> 4. `SameSite=None` 只是允许跨站http请求自动携带cookie，并不能让JS读取其他域的cookie。

补充：现在很多新方案放弃Cookie跨域共享，直接使用 JWT token，存在 localStorage / sessionStorage，通过参数、header传递，规避Cookie各种域限制。
