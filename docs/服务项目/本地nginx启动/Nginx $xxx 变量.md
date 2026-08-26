# Nginx $xxx 变量

`$remote_addr`、`$http_x_forwarded_for` 这些带 `$` 的，是 **Nginx内置变量**。
不是js、不是shell变量，是nginx配置文件专用的变量，只能写在nginx.conf里面。

> 来源：**Nginx源码内部定义，不需要你在conf里声明、不需要var定义，开箱直接用**，不能自己随便造名字。

## 两个重点变量解释

1. **`$remote_addr`**
   直接客户端IP。

- 用户直连nginx：就是用户真实IP
- 如果前面还有一层代理（比如CDN），拿到的是上一级代理服务器IP，不是真实用户。

2. **`$http_x_forwarded_for`**
   读取HTTP请求头 `X‑Forwarded‑For` 的值。

> 客户端经过代理时，上游代理会把真实用户IP塞到这个请求头里。
> `proxy_set_header X‑Forwarded‑For $proxy_add_x_forwarded_for;`
> ✅**推荐用 `$proxy_add_x_forwarded_for`，不要直接用`$http_x_forwarded_for`**
> `$proxy_add_x_forwarded_for` 会自动拼接链条，兼容没有这个头的请求。

---

## 分类：Nginx内置变量分3大类

### 1、客户端连接类（TCP层面）

| 变量           | 含义                |
| -------------- | ------------------- |
| `$remote_addr` | 客户端IP地址        |
| `$remote_port` | 客户端端口          |
| `$server_addr` | nginx接收请求本机IP |
| `$server_port` | nginx监听端口       |
| `$connection`  | 连接序号            |

### 2、HTTP 请求相关（请求行、header）

- `$request`：完整原始请求行 `GET /api/getData HTTP/1.1`
- `$request_method`：请求方法 `GET/POST`
- `$request_uri`：完整原始uri，带参数 `/api/getData?a=1`
- `$uri`：处理后解码的uri，不带query参数
- `$args`：url后面的query参数 `a=1&b=2`
- `$http_host`：请求头 Host 的值
- `$http_user_agent`：浏览器UA
- `$http_referer`：来源referer

> 通用规则：**读取任意请求头：`$http_小写头名字`，横杠变下划线**
> 例如请求头 `X‑Real‑Ip` → nginx变量：`$http_x_real_ip`
> `X‑Forwarded‑For` → `$http_x_forwarded_for`

### 3、代理专用变量（proxy模块，反向代理必用）

| 变量                         | 作用                                                                       |
| ---------------------------- | -------------------------------------------------------------------------- |
| `$host`                      | 优先取请求Host，没有则server_name，**proxy_set_header Host $host; 最常用** |
| `$proxy_add_x_forwarded_for` | **最推荐**，拼接代理IP链，把`$remote_addr`追加到X‑Forwarded‑For            |
| `$proxy_host`                | proxy_pass后面的主机名                                                     |
| `$proxy_port`                | proxy_pass端口                                                             |

### 4、响应、日志变量

- `$status`：http响应码 200/404/502
- `$request_time`：整个请求耗时（秒，保留小数）
- `$bytes_sent`：返回给客户端字节数

## 在哪里定义？

1. **不是写在conf配置文件里！**
   这些变量硬编码在Nginx C源码，编译的时候就存在。

> 位置源码：`src/http/ngx_http_variables.c`，全部内置注册。
> 你打开conf看不到这些变量的定义，直接拿来使用。

2. 还有一部分变量是**模块带来**：

- `proxy_add_x_forwarded_for` 属于 `ngx_http_proxy_module`（代理模块，windows nginx默认编译进去）
- 如果没有编译该模块，这个变量就不存在。windows发行版全部带。

### 可以自定义变量

你可以自己造变量，用 `set` 指令，这个是在conf中定义：

```nginx
set $my_msg "hello";
```

之后就可以用 `$my_msg`，这个是用户自定义变量。

## 如何看全部变量？

官方文档有完整清单：

> nginx官方内置变量文档：`Module ngx_http_core_module` Variables章节

本地快速验证，把变量打印到日志：

```nginx
location /test {
    # 输出到访问日志观察变量值
    return 200 " remote_addr=$remote_addr \n host=$host \n proxy_add_x_forwarded_for=$proxy_add_x_forwarded_for \n request_uri=$request_uri";
}
```

访问 `http://localhost/test`，浏览器直接打印各个变量的值，方便调试。

## 你反向代理那段的标准写法（修正）

```nginx
location /api/ {
    proxy_pass http://127.0.0.1:3000/api/;

    proxy_set_header Host $host;
    proxy_set_header X‑Real‑IP $remote_addr;
    # ✅用这个，不要直接 $http_x_forwarded_for
    proxy_set_header X‑Forwarded‑For $proxy_add_x_forwarded_for;
}
```

> `$http_x_forwarded_for` 的缺陷：客户端伪造请求头可以篡改IP；
> `$proxy_add_x_forwarded_for` 在每一层代理追加真实socket IP，更加安全。

## Node后端拿到这两个头

node原生http里面拿：

```js
// nginx传递过来的真实客户端ip
const realIp = req.headers["x-real-ip"];
const forwarded = req.headers["x-forwarded-for"];
```

### 小结记忆

1. 所有`$xxx`是nginx变量；大部分是**源码内置，不用声明直接用**；
2. 请求头转变量规则：`X‑Abc‑Def` → `$http_x_abc_def`；
3. 代理拿真实IP优先用 `$proxy_add_x_forwarded_for`；
4. `set $xxx value;` 是用户自定义变量，写在conf中。

如果你需要，我可以给你一份开发中高频使用的精简变量速查表。
