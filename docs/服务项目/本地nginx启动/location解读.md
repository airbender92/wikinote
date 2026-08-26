# 逐段完整解读这两段location

> Nginx匹配规则：**最长前缀优先匹配**

- 请求以 `/api/` 开头 → 命中 `location /api/`，走反向代理转发给Node:3000
- 其余所有请求 → 落到 `location /`，处理静态资源+history路由

## 第一段：location /api/

```nginx
location /api/ {
    proxy_pass http://127.0.0.1:3000/api/;

    proxy_set_header Host $host;
    proxy_set_header X‑Real‑IP $remote_addr;
    proxy_set_header X‑Forwarded‑For $proxy_add_x_forwarded_for;
}
```

### 1. `location /api/`

匹配URI**以 `/api/` 开头**的请求
例：

- `/api/getData` ✅匹配
- `/api/user/list` ✅匹配
- `/apixxx` ❌不匹配（末尾带斜杠，必须是/api/前缀）

### 2. `proxy_pass http://127.0.0.1:3000/api/;`

> 末尾带`/`，会做**URI替换**

举例实际转发过程：
浏览器请求：`http://localhost/api/getData`
Nginx把匹配到的前缀`/api/`替换成`/api/`，转发给后端node：
`http://127.0.0.1:3000/api/getData`

> 重点区分斜杠：

1. `proxy_pass http://127.0.0.1:3000/api/;` 👉 有末尾斜杠：替换匹配的`/api/`
2. `proxy_pass http://127.0.0.1:3000/api;` 👉 无末尾斜杠：拼接，变成`/api/api/getData`（就错了）

### 3. proxy_set_header 作用

Nginx反向代理时，会重新组装http请求发给后端Node；**不设置这些头，后端拿到的信息是错的**。

1. `proxy_set_header Host $host;`
   把请求头`Host`传给Node。
   如果不设置，Node收到的Host会变成`127.0.0.1:3000`，而不是浏览器访问的`localhost`。很多框架依赖Host头。

2. `proxy_set_header X‑Real‑IP $remote_addr;`
   自定义请求头 `X‑Real‑IP`，值为**真实客户端TCP IP**。
   Node中读取 `req.headers['x-real-ip']` 获取用户IP。

3. `proxy_set_header X‑Forwarded‑For $proxy_add_x_forwarded_for;`
   `$proxy_add_x_forwarded_for` = 原有`X‑Forwarded‑For`内容 + `,` + 当前客户端`$remote_addr`

- 直连nginx：值就是客户端IP
- 如果前面还有CDN/多层代理，会拼接整条IP链路
  Node读取：`req.headers['x-forwarded-for']`

> ⚠注意：这些只是**HTTP请求头**，本身不改变TCP连接源IP；只是给后端应用层看的。

---

## 第二段 location /

```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

`location /` 是兜底规则，**所有没被上面location匹配到的请求，全部进这里**。
`try_files`：按顺序依次找文件，找到就直接返回；都找不到，最后内部重定向到 `/index.html`。

拆解三个参数：

```
try_files $uri $uri/ /index.html;
```

1. `$uri`：当前请求的uri

> 例：访问 `/` → $uri=/；访问 `/about` → $uri=/about

- 第一步 `$uri`：去root目录下找**真实文件**
  访问 `/js/main.js` → 找 `D:/wybD/appInstaller/nginx/www/js/main.js`，存在直接返回文件。

- 第二步 `$uri/`：看是不是文件夹，存在目录就访问目录（找index.html）

- 第三步 `/index.html`：**前两个都找不到，返回根目录index.html**
  👉 这就是**Vue/React history模式解决刷新404的核心**。

举例history路由场景：
前端路由：`http://localhost/about`

1. nginx www目录**没有about这个文件，也没有about文件夹**
2. `$uri`、`$uri/` 全部找不到
3. 降级返回 `/index.html`
4. 浏览器加载index.html，前端JS接管，渲染about页面。

> 注意：`try_files` 最后一项是**内部重定向**，不是302跳转，浏览器地址栏不会变。

---

# 完整请求链路实例

### 场景1：访问静态页面

浏览器：`http://localhost/home`

1. 不是以`/api/`开头，进入`location /`
2. try_files 在www目录找不到home文件，找不到home文件夹
3. 返回 `/index.html`，前端JS渲染home页面，**完全不走Node**

### 场景2：前端调用接口 fetch("/api/getData")

浏览器请求 `http://localhost/api/getData`

1. 匹配上 `location /api/`
2. proxy_pass 转发请求到 `http://127.0.0.1:3000/api/getData`
3. 同时带上 Host、X‑Real‑IP、X‑Forwarded‑For 请求头
4. Node服务收到请求，返回JSON
5. Nginx把JSON原样返回浏览器

### 场景3：请求js/css静态资源

`http://localhost/js/app.js`

1. 不匹配/api/，进入location /
2. `$uri` 在www目录找到 js/app.js，直接返回文件，不走后面 `/index.html`

## 常见踩坑点

1. `location /api/` 斜杠，如果你写 `location /api`（不带末尾斜杠），会匹配 `/apixxx`，出现错误匹配。
2. proxy_pass末尾斜杠，不要随意删除，删除后接口路径会多一层 `/api`。
3. try_files 最后一个参数 `/index.html`，前面必须带 `/`。
4. try_files 只会影响静态资源，**不会干预/api/**，因为/api请求被上一个location优先拦截。

## 小测试理解斜杠差异

> location /api/ {
> proxy_pass http://127.0.0.1:3000/api; #没有末尾/
> }
> 浏览器访问 `/api/getData`，转发后端变成：`/api/api/getData` → 404，这是高频出错。

## Node后端拿到头示例

```js
const realIp = req.headers["x-real-ip"];
const ipChain = req.headers["x-forwarded-for"];
const host = req.headers["host"];
```

如果你愿意，我给你对比：带斜杠 / 不带斜杠的 proxy_pass 一张对照表。
