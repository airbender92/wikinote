# Nginx 启动阶段打印变量/日志

先说关键限制：

> **nginx 启动（start nginx）阶段，`$remote_addr` / `$request_uri` 这类请求相关变量，启动时不能打印！**
> 原因：这些变量是**每一次HTTP请求来了才生成**；启动的时候还没有任何客户端连接，变量不存在，没有值。

启动阶段（master进程启动、读取conf）能输出的只有：

- nginx自身启动日志（error.log）
- 启动时**没有请求上下文**，请求类变量全部为空。

## 两种打印场景区分

1. ✅**启动阶段（start nginx / reload）**：进程初始化，无用户请求。只能打印常量、配置信息，拿不到客户端IP、uri。
2. ✅**请求阶段（浏览器访问页面）**：每来一次http请求，所有`$xxx`变量才有值，可以打印到日志、返回页面。

---

## 1、启动时看输出：控制台 & error.log

Windows nginx，`start nginx` 默认**不会往cmd控制台打印任何东西**。
所有启动信息、报错全部写入日志文件：

```
D:\wybD\appInstaller\nginx\logs\error.log
```

- 启动失败、端口占用、配置异常 → 写 error.log
- `nginx -t` 是校验工具，才输出到cmd窗口；正式start nginx不输出控制台。

> nginx官方设计：daemon后台运行，启动阶段不输出stdout。Windows版本也是遵循这个逻辑。
> **不能像node一样，启动的时候console.log打印变量。**

### 能不能让nginx启动时在cmd窗口打印？

可以关闭守护进程模式（前台运行），**Windows不推荐用于生产，适合调试**。
修改 nginx.conf，放到最顶层（http{}外面）：

```nginx
# 前台运行，不后台启动；窗口打开，日志直接打印cmd
daemon off;
```

然后不要用 `start nginx`，直接执行

```cmd
nginx
```

此时nginx就在当前cmd窗口前台跑，部分启动日志直接输出控制台。

> ⚠缺点：关掉cmd窗口nginx直接退出；本地调试用，改完记得注释掉 `daemon off;`。

> 但是！就算前台运行，**启动瞬间依旧拿不到 $remote_addr 这类请求变量**，没有客户端访问就没有值。

---

## 2、想要看变量值：请求时打印（最常用）

### 方式A：返回给浏览器看（调试用location）

```nginx
location /debug {
    return 200 "
remote_addr: $remote_addr
host: $host
request_uri: $request_uri
proxy_add_x_forwarded_for: $proxy_add_x_forwarded_for
args: $args
status: $status
";
}
```

浏览器访问 `http://localhost/debug`，就会把本次请求全部变量输出页面。

### 方式B：自定义访问日志，每一次请求写入access.log

打开nginx.conf的 `http{}` 块，自定义日志格式：

```nginx
http {
    # 自定义日志格式，把需要的变量全部放进去
    log_format my_format '$time_local | $remote_addr | $host | $request_uri | $status | $proxy_add_x_forwarded_for';

    access_log logs/access.log my_format;

    # ...下面原有include mime; server块等等
}
```

保存，`nginx -t && nginx -s reload`
每次浏览器访问，`logs/access.log` 文件里面就打印出全部变量。

Windows直接打开这个文件，或者cmd实时查看：

```cmd
# PowerShell 实时跟踪日志
Get-Content logs/access.log -Wait
```

---

## 3、那启动阶段可以打印什么？

启动阶段只有少量全局可用变量，几乎都是内置的编译版本信息，业务变量全部没有。
你可以用 `error_log notice` 输出文字，但是**不能输出请求变量**。

```nginx
# http外面，main块
error_log stderr notice;
```

只能打印固定文本，`$remote_addr` 写在这里是**空值**，毫无意义。

> 核心记住：
>
> - `$remote_addr`、`$request_uri`、`$args`：属于**请求上下文变量**，**有HTTP请求进来才产生**；nginx刚启动还没人访问，这些变量不存在。
> - 你想观察代理的IP、请求路径 → 放到access日志或者debug location，访问接口时查看。

---

## 对比 Node 和 Nginx 的区别

1. **Node**：启动的时候可以 `console.log()`；收到请求事件，req对象才有ip、url。
2. **Nginx**：master进程启动阶段没有请求对象；变量绑定在每一个请求。

- node：启动打印服务端口；请求回调内部拿ip url
- nginx：启动只能打印自身启动状态；**请求到来后才能拿到 $remote_addr**

## 实操建议你的调试流程

1. 打开前台模式 `daemon off;`，执行 `nginx`，看cmd窗口启动报错。
2. 配置自定义 `log_format`，观察access.log，查看反向代理时各个header变量真实值。
3. 调试完，注释 `daemon off;`，恢复 `start nginx` 后台运行。

如果你需要，我给你一段直接复制的完整http块日志配置。
