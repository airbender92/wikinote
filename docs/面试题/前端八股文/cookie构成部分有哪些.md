# Cookie 的组成部分

Cookie 是服务器下发、保存在浏览器的小型文本数据，**由响应头 `Set‑Cookie` 设置，请求头 `Cookie` 携带回服务器**。

一条完整 `Set‑Cookie` 由 **Cookie键值对 + 多个属性（可选）** 组成。

## 1. 必选部分：name=value（键值对）

> `username=zhangsan`

- `name`：cookie名称
- `value`：cookie的值

> 多条cookie用`; `分隔

## 2. 可选属性（Set‑Cookie 里的，浏览器发送Cookie请求头时**不会带这些属性**）

1. **Expires / Max‑Age** 过期时间
   - `Expires=Wed, 25‑Aug‑2027 00:00:00 GMT`：绝对GMT时间，到期删除cookie
   - `Max‑Age=86400`：相对秒数，0或负数代表立刻删除；优先级高于Expires
   - 如果两者都不写 → **会话Cookie**，浏览器关闭就销毁，不持久化磁盘。

2. **Domain** 域名
   - 指定哪些域名可以接收这个cookie
   - `Domain=example.com`：包含子域名 `a.example.com` 都生效
   - 不写默认是设置cookie的当前主机（不包含子域名）

3. **Path** 路径
   - `Path=/admin`：只有 `/admin` 及其子路径请求才带上该cookie
   - `Path=/`：整个网站全部路径生效，最常用

4. **Secure**
   - 不带值；设置后，**只有HTTPS加密请求才会发送cookie**，HTTP不会携带。

5. **HttpOnly**
   - 不带值；禁止JS通过 `document.cookie` 读取，**防御XSS窃取cookie**，依然会在http请求自动携带。

6. **SameSite**（防CSRF核心）
   - `SameSite=Strict`：严格，跨站请求完全不发送cookie
   - `SameSite=Lax`：默认值，大部分跨站POST不发送，GET导航允许携带
   - `SameSite=None`：允许跨站发送，**必须同时带上Secure**

---

## 示例完整 Set‑Cookie

```http
Set‑Cookie: sessionId=abc123; Max‑Age=86400; Domain=example.com; Path=/; Secure; HttpOnly; SameSite=Lax
```

## 请求头 Cookie（浏览器发给服务器）

> 只携带 `name=value`，**所有属性全部丢掉**，多条用分号空格分隔

```http
Cookie: sessionId=abc123; username=zhangsan
```

### 快速区分

- `Set‑Cookie`：服务端→浏览器，**完整全部组成：键值+所有属性**
- `Cookie`：浏览器→服务端，**只有键值对**

### 补充小知识点

- Cookie大小有限，单条一般4KB以内；每个域名cookie数量有限制。
- 会话Cookie：无Max‑Age/Expires，内存保存，关闭浏览器清除；持久Cookie写入本地磁盘。

如果你需要，我可以顺带讲下 Cookie、LocalStorage、SessionStorage 的对比表格。
