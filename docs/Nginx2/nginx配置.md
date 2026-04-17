# 本章翻译 + Docker 适配说明（完整流畅版）
在本章中，我们将深入 **Nginx 配置的核心**——也就是真正“魔法发生”的地方！正如我们所学，Nginx 不仅是高性能 Web 服务器，更是强大的代理服务器与负载均衡器。它**完全按照配置运行**。无论你是搭建简单网站，还是管理复杂基础设施，正确配置 Nginx 对性能与安全都至关重要。

Nginx 配置的本质，是一系列写在**纯文本文件**中的指令。这些文件让管理员可以精细调整服务器如何处理入站 HTTP 请求与出站响应。这种灵活性让 Nginx 可以托管静态文件、处理动态内容、反向代理到应用服务器、实现负载均衡等。

在使用 Nginx 时，我们会频繁与配置文件打交道。本章将带你了解它们的结构，并解释每条指令如何影响 Nginx 的行为。

---

## 本章结构
本章将介绍：
- 理解 nginx.conf 文件
- 选择 location 块的匹配算法
- Nginx 常用指令
- Nginx 模块
- Nginx 变量
- 示例配置

我们从最重要的文件开始：**nginx.conf**，也叫**主配置文件**。

---

# 理解 nginx.conf 文件
nginx.conf 是 Nginx 的**主配置文件**。
它包含所有控制 Nginx 行为的指令与设置，包括服务器配置、代理设置、日志配置等。

**所有其他配置文件最终都会被包含进 nginx.conf**。
在 Nginx 加载时，所有配置（即使分散在不同文件）最终会合成为一份完整配置。我们拆分文件只是为了易读、易管理。

Nginx 配置由多个**上下文（Context）**组成，也叫**块（Block）**。
顶层最核心的上下文包括：
- main
- events
- http
- server
- location

下面逐一讲解。

---

# 1. main 上下文（全局块）
这是 Nginx 配置的**起点**，也叫**全局配置段**。
它位于 `http`、`events`、`server`、`location` 之外。

main 上下文用于配置：
- 运行 worker 进程的系统用户：`user nginx;`
- 工作进程数（与 CPU 核心相关）：`worker_processes auto;`
- Nginx 主进程 PID 文件：`pid /var/run/nginx.pid;`
- 全局错误日志：`error_log /var/log/nginx/error.log;`
- 文件句柄限制、加载第三方模块等

示例配置：
```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /var/run/nginx.pid;
worker_rlimit_nofile 17000;
load_module modules/ngx_http_js_module.so;
```

---

# 2. events 上下文（连接事件块）
在 `events` 块中，我们配置 **Nginx 如何处理连接**。
最关键指令是 `worker_connections`（每个工作进程最大连接数）。

**整个 Nginx 配置中只能有一个 events 块。**

示例：
```nginx
events {
    worker_connections 8192;
}
```

---

# events 上下文（翻译 + 说明）
## 翻译
**events 上下文**
在 events 上下文中，我们定义 Nginx **如何在通用层面处理连接**。
`worker_connections` 指令用于设置**每个工作进程可处理的最大连接数**。
**整个 Nginx 配置中只能有一个 events 上下文。**

---

## 示例配置（带注释）
```nginx
# main 上下文（全局配置）
load_module modules/ndk_http_module.so;
load_module modules/ngx_http_lua_module.so;
load_module modules/ngx_http_js_module.so;

user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /var/run/nginx.pid;
worker_rlimit_nofile 16192;

# events 上下文（连接处理配置）
events {
    worker_connections 8096;
}
```

---

## 关键解释
### `worker_connections 8096;`
表示 **每个 Nginx 工作进程最多同时处理 8096 个连接**。
这是 Nginx 高并发能力的核心参数之一。

---
### 翻译与解析
# http 上下文
**http 上下文**是顶层配置块，用于定义**Web（HTTP/HTTPS）流量**的专属设置与行为。
它通常写在 `/etc/nginx/nginx.conf` 文件中，位于 `events` 上下文之后。
它包含了作为 HTTP 服务器或反向代理所需的**全部配置**，并包裹着所有下层指令：
server 块、location 块、include 引入、日志格式、缓存规则、压缩策略等。

---

## 示例配置（带注释）
```nginx
# http 上下文
http {
    # 引入 MIME 类型文件
    include /etc/nginx/mime.types;

    # 自定义日志格式 main
    log_format main '"$time_local" client=$remote_addr '
                   'method=$request_method request="$request" '
                   'request_length=$request_length '
                   'body_bytes_sent=$body_bytes_sent '
                   'upstream_addr=$upstream_addr '
                   'upstream_status=$upstream_status '
                   'status=$status bytes_sent=$bytes_sent '
                   'request_time=$request_time '
                   'upstream_response_time=$upstream_response_time '
                   'upstream_connect_time=$upstream_connect_time '
                   'upstream_header_time=$upstream_header_time'
                   'body=$request_body';

    # 引入子配置文件
    include /etc/nginx/conf.d/configuration.conf;

    # 虚拟主机 server 块
    server {
        listen 8080;
        access_log off;

        # 精确匹配 /，强制 301 跳转到 dashboard
        location = / {
            return 301 /dashboard.html;
        }

        # API 路径开启读写权限
        location /api {
            api write=on;
        }

        # 控制面板页面
        location /dashboard.html {
            root /usr/share/nginx/html;
        }
    }
}
```

---

### 核心要点
1. **http 是所有网站配置的“容器”**
   所有 `server`、`location`、日志、缓存、压缩 都写在这里。

2. 可以**include 其他 .conf 文件**
   方便把多个网站拆成独立配置，结构更清晰。

3. 里面可以定义：
   - `log_format` 日志格式
   - `gzip` 压缩
   - `proxy_cache` 缓存
   - `upstream` 后端集群
   - `server` 虚拟主机
   - `location` 请求路由

---

# 完整翻译 + 修正格式（server 上下文）

## 翻译
**server 上下文**
server 上下文**必须定义在 http 上下文内部**。
这个上下文用于配置 Nginx 如何处理各类入站请求，非常重要。

你可以定义**多个 server 块**，让 Nginx 在**同一台服务器上运行多个网站/应用**。
每个 server 块通过唯一的 **server_name** 区分。
server_name 的值就是 **DNS 域名 或 主机名**。

---

## 什么是 DNS 或主机名？
DNS 名称（通常称为主机名）是人类可读的网址，让用户不用记忆数字 IP 地址就能访问网站。
这些名称会被映射到唯一的 IP 地址，所有映射关系都保存在全球 DNS 系统中。

例如：
不用输入 `93.184.216.34`
你可以输入 `www.example.com`

常见例子：
`www.amazon.com`、`www.google.com`

---

# server 上下文示例配置（修正语法错误）
```nginx
# http 上下文
http {
    include /etc/nginx/mime.types;

    log_format main '"$time_local" client=$remote_addr '
    'method=$request_method request="$request" '
    'request_length=$request_length '
    'status=$status bytes_sent=$bytes_sent '
    'body_bytes_sent=$body_bytes_sent '
    'upstream_addr=$upstream_addr '
    'upstream_status=$upstream_status '
    'request_time=$request_time '
    'upstream_response_time=$upstream_response_time '
    'upstream_connect_time=$upstream_connect_time '
    'upstream_header_time=$upstream_header_time '
    'body=$request_body';

    include /etc/nginx/conf.d/configuration.conf;

    # 第一个网站
    server {
        listen 80;
        server_name www.test.com;
    }

    # 第二个网站
    server {
        listen 80;
        server_name www.test1.com;
    }

    # 第三个网站（HTTPS）
    server {
        listen 443;
        server_name www.test2.com;
    }
}
```

---

# 核心知识点（必看）
1. **server 必须放在 http 里面**
2. **一个 server = 一个网站**
3. 多个网站共用一台服务器，靠 **server_name** 区分
4. 可以同时有 HTTP(80) 和 HTTPS(443)

---

# 完整翻译 + 格式修正 + 核心讲解（Location 上下文）
## 翻译
**Location 块**定义在 **server 上下文内部**。和 server 块一样，我们可以配置多个 location 块。
每个 location 用于**处理某一类客户端请求**，Nginx 会根据请求的 **URI 路径、字符串或正则表达式** 来匹配并选择对应的 location。

location 块还允许我们指定 Nginx 如何将请求**代理到后端服务器**、**返回静态文件**，或实现特定的业务行为。

---

## 修正后的完整配置（可直接使用）
```nginx
server {
    listen 80 default_server;
    listen 443 default_server;
    server_name localhost;

    # SSL 证书配置
    ssl_certificate /etc/nginx/dellcert/dcgonpCert.pem;
    ssl_certificate_key /etc/nginx/dellcert/dcgonpkey.pem;

    # 1. 匹配所有请求（默认首页）
    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
    }

    # 2. 匹配 Nginx 状态页面（仅本机访问）
    location /nginx_status {
        stub_status;
        allow 127.0.0.1;
        deny all;
    }

    # 3. 错误页面配置
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
```

---

# 核心知识点（必看）
### 1. location 作用
- 匹配用户访问的**网址路径**
- 对不同路径做**不同处理**（静态页面、反向代理、限流、权限等）

### 2. 示例里的三个 location
1. **`location /`**
   匹配所有请求，返回网站首页
2. **`location /nginx_status`**
   只匹配 `/nginx_status`，用于查看 Nginx 运行状态
3. **`location = /50x.html`**
   精确匹配错误页面，返回 50x 错误页

### 3. 关键指令
- `root`：静态文件所在目录
- `index`：默认首页文件
- `stub_status`：开启 Nginx 状态监控
- `allow/deny`：IP 访问控制
- `error_page`：自定义错误页面

---

# Location 块匹配算法
## 处理请求时选择 Location 块的算法
如前所述，Nginx 中可以配置多个 location 块，每个块负责处理特定的流量规则。因此，每当客户端请求到达 Nginx 服务器时，Nginx 就会开始判断应该使用哪个 location 块来处理该请求。
Nginx 遵循一套固定的**匹配算法**，理解这一流程是可靠、精准配置 Nginx 的关键要求。

---

### 正则表达式（regex）简介
regex 是 regular expression 的缩写，指一串用于定义**匹配模式**的字符。
通过指定字符规则，它可以用来匹配、查找和处理文本。正则表达式广泛用于编程、文本处理和配置工具（如 Nginx），以实现强大的模式匹配与文本处理。

在学习匹配算法之前，我们先熟悉几个重要的正则符号及其含义：

### 符号说明
| 符号 | 含义 |
|------|------|
| `=` | **精确匹配** |
| `~` | **区分大小写**的正则匹配 |
| `^` | 表示匹配字符串的**开头** |
| `$` | 表示匹配字符串的**结尾** |
| `~*` | **不区分大小写**的正则匹配 |
| `^~` | 优先前缀匹配（非正则），匹配到即停止搜索 |

> 表格说明：Nginx 使用 PCRE 正则表达式，你可以通过多种在线工具测试正则模式，例如 regex101（https://regex101.com/）。

---
# 理解匹配算法
当客户端发起 HTTP 请求时，Nginx 会将请求中的 URL 与配置中定义的 location 块**按特定规则**进行匹配，而不是简单按书写顺序匹配。匹配基于**规范化后的 URI**进行。

例如：
`http://example.com/index.html`
和
`http://EXAMPLE.COM//index.html`

都会被统一规范化为同一个标准形式：
`http://example.com/index.html`

---

当一个 HTTP 请求到达 Nginx 服务器时，执行顺序如下：

以示例 URL 为例：
`https://www.test.com/understanding/nginx/chapter/2`

Nginx 会从域名之后的部分开始匹配 location，也就是从 `/understanding/nginx/chapter/2` 这一段开始查找最符合的 location 块。
（其中主机/域名是 `www.test.com`）

---


# 精确匹配（Exact Match）
## 原文翻译
**精确匹配**
Nginx 首先会寻找是否存在能**精确匹配**请求路径的 location 块。
精确匹配要求 location 中定义的路径**与请求的 URI 完全一致**（包括大小写）。

精确匹配的 location 前面会带有 **`=`** 符号。
一旦请求 URI 与 location 实现精确匹配，Nginx 会**立即停止后续所有匹配**，直接执行这个 location。

---

## 示例配置（修正语法 + 可直接运行）
```nginx
server {
    listen 443 ssl;
    server_name www.test.com;

    # SSL 证书配置（省略）
    # ssl_certificate ...
    # ssl_certificate_key ...

    # 精确匹配 location
    location = /understanding/nginx/chapter/2 {
        return 301 https://www.test2.com;
    }
}
```

---

## 核心要点（必记）
1. **符号**：`location = /路径`
2. **规则**：**必须一模一样**才匹配（大小写敏感）
3. **优先级**：**最高**！匹配成功立刻停止搜索
4. **用途**：精准跳转、精准限制访问、精准返回特定内容

---

### 举例说明
请求 URL：
`https://www.test.com/understanding/nginx/chapter/2`

✅ **匹配成功**
`location = /understanding/nginx/chapter/2`

❌ **不匹配**
`/Understanding/Nginx/Chapter/2`（大小写不同）
`/understanding/nginx/chapter/2/`（多了斜杠）

---
# 前缀匹配 或 字符串匹配（Prefix Match / String Match）
如果没有找到**精确匹配（=）**的 location 块，Nginx 会寻找第二种优先匹配的 location 块，也就是**前缀匹配**。

简单来说，Nginx 会尝试寻找**以请求路径开头字符串**相匹配的 location。
比如请求是 `/understanding/nginx/chapter/2`，那么以下路径都能匹配：
- `/understanding`
- `/understanding/nginx`
- `/understanding/nginx/chapter`
- `/understanding/nginx/chapter/2`

**Nginx 会选择【最长的那个匹配】**，并记录下来。

---

## 示例配置（原文修正 + 正确语法）
```nginx
server {
    listen 443 ssl;
    server_name www.test.com;

    # SSL 证书配置
    # ssl_certificate ...
    # ssl_certificate_key ...

    # 前缀匹配（最长匹配优先）
    location ^~ /understanding/nginx/chapter/2 {
        return 301 https://www.test1.com;
    }

    location ^~ /understanding/nginx/chapter {
        return 301 https://www.test2.com;
    }

    location ^~ /understanding/nginx {
        return 301 https://www.test3.com;
    }
}
```

---

## 关键规则（必背）
1. **前缀匹配符号：`^~`**
2. **匹配规则：请求路径 以 location 路径 开头**
3. **优先级：多个都匹配时 → 选【最长的那个】**
4. **特点：比正则匹配优先级高，匹配后不再检查正则**

---

## 示例说明
请求路径：
`/understanding/nginx/chapter/2`

三个 location 都能匹配：
1. `/understanding/nginx`
2. `/understanding/nginx/chapter`
3. `/understanding/nginx/chapter/2`

✅ **最终生效：第3个（最长匹配）**

---

# 正则匹配（Regex Match）
## 原文翻译
**正则匹配**

如果找到了匹配的前缀（字符串）匹配项，Nginx 并不会立刻执行它，而是先把这个匹配结果暂存到内存中。
随后，匹配算法会继续去查找是否有符合条件的**正则匹配**。
这是因为 **正则匹配的优先级高于前缀字符串匹配**。

一旦某个正则 location 匹配到了请求 URI，匹配过程就会立即停止。
正则匹配是**按配置文件中书写的先后顺序**进行的，因此即使后面有更精准的正则表达式，**第一个匹配到的正则会生效**。

---

## 示例说明
对于 URL：
`https://www.test.com/understanding/nginx/chapter/2`

即使存在前缀匹配的 location，**正则匹配**
```
location ~* "^/understanding.*"
```
仍然会优先执行。

第二个正则：
```
location ~* "^/understanding/nginx.*"
```
根本不会被考虑，因为**第一个匹配的正则优先级更高**。

---

充分理解这套匹配算法，对正确配置 Nginx 至关重要。
无论是简单网站还是复杂架构，规则编写都是最关键的一步。

我们已经学习了编写 Nginx 配置涉及的各种上下文（context）。
在下一节，我们将学习 **Nginx 指令（Directives）**。
必须明确：Nginx 配置的核心本质就是**一堆指令的集合**，每条指令都决定了服务器如何处理请求、如何返回内容。

---

# 超精简总结（必背）
1. **先精确匹配 `=`**
2. 再找前缀匹配 `^~`，记下最长的那个
3. **再按顺序匹配正则 `~` / `~*`**
4. **正则 > 前缀匹配**
5. 正则是**谁写在前面，谁先生效**
6. 没有正则匹配，才用之前记下的最长前缀匹配

---

# 🔥 **Nginx Location 匹配算法 · 完整实战例子**
我把你刚才学的 **精确匹配 =**、**前缀匹配 ^~**、**正则匹配 ~ ~*** 全部整合到 **一个完整可运行的配置**里，并且告诉你**任何 URL 会匹配到谁**。

## 完整配置（直接复制可用）
```nginx
server {
    listen 80;
    server_name www.test.com;

    # --------------------------
    # 1. 精确匹配 = （最高优先级）
    # --------------------------
    location = /understanding/nginx/chapter/2 {
        return 200 "✅ 命中：精确匹配\n";
    }

    # --------------------------
    # 2. 前缀匹配 ^~
    # --------------------------
    location ^~ /understanding/nginx/chapter {
        return 200 "✅ 命中：最长前缀匹配\n";
    }

    location ^~ /understanding/nginx {
        return 200 "✅ 命中：普通前缀匹配\n";
    }

    # --------------------------
    # 3. 正则匹配 ~ 区分大小写
    # --------------------------
    location ~ ^/understanding/nginx.* {
        return 200 "✅ 命中：区分大小写正则\n";
    }

    # --------------------------
    # 4. 正则匹配 ~* 不区分大小写
    # --------------------------
    location ~* ^/understanding.* {
        return 200 "✅ 命中：不区分大小写正则\n";
    }

    # --------------------------
    # 5. 默认匹配 /
    # --------------------------
    location / {
        return 200 "✅ 命中：默认匹配 /\n";
    }
}
```

---

# 🧪 测试 5 个 URL，看结果（最关键）
## 1. 访问：`http://www.test.com/understanding/nginx/chapter/2`
**结果：✅ 精确匹配**
> 原因：`=` 优先级最高

## 2. 访问：`http://www.test.com/understanding/nginx/chapter/abc`
**结果：✅ 不区分大小写正则（~*）**
> 原因：正则 > 前缀匹配
> 而且**写在前面的正则先生效**

## 3. 把上面的正则顺序调换后
```nginx
location ~ ^/understanding/nginx.* { ... }  # 放前面
location ~* ^/understanding.* { ... }
```
访问：`/understanding/nginx/chapter/abc`
**结果：✅ 区分大小写正则**

## 4. 注释掉所有正则
访问：`/understanding/nginx/chapter/abc`
**结果：✅ 最长前缀匹配**
> 原因：没有正则，才用前缀匹配，且取**最长**

## 5. 访问：`/abc`
**结果：✅ 默认匹配 /**

---

# 📌 **最终优先级总规则（必背）**
1. **`location = /path`**  精确匹配（最高）
2. **`location ^~ /path`** 前缀匹配
3. **`location ~ /regex`**  区分大小写正则（按书写顺序）
4. **`location ~* /regex`** 不区分大小写正则
5. **`location /path`**    普通前缀匹配
6. **`location /`**        默认匹配（最低）

---

## 一句话总结
**先精确 → 存前缀 → 再正则 → 正则优先于前缀 → 都没匹配才用最长前缀 → 最后 /**

---

# Nginx 指令（Directives）核心讲解
## 翻译正文
### Nginx 指令是什么？
如果你熟悉 Java、C、C++ 等编程语言，就一定知道**关键字（keyword）**。
关键字是对编译器有**预定义含义**的保留词，是语法的一部分，不能被用作自定义变量名。

**Nginx 指令（Directives）** 就是 Nginx 配置中的**保留关键字**，每个指令都有特殊含义和专门作用。
整个 Nginx 配置就是靠这些指令来实现的。

例如：想在 Nginx 中开启压缩功能，就在 `http` 上下文里使用 `gzip` 指令：
```nginx
gzip on;
```
这代表让 Nginx 开启压缩功能。

Nginx 有上百种指令，下面我们逐个学习**最核心、最常用**的指令。

---

# 1. user 指令
**语法**：`user 用户 [用户组];`
**默认值**：`user nobody nobody;`
**上下文**：`main`（全局）
**示例**：`user nginx;`

**作用**：
指定 Nginx 工作进程以哪个**系统用户/用户组**运行。
示例中表示 Nginx 工作进程使用 `nginx` 用户权限运行。

**好处**：
通过指定低权限用户，可以**最小化安全漏洞带来的风险**。
注意：指定的用户必须拥有网站文件、目录的必要访问权限。

---

# 2. worker_processes 指令
**语法**：`worker_processes 数字 | auto;`
**默认值**：`worker_processes 1;`
**上下文**：`main`
**示例**：`worker_processes 4;`

**作用**：
设置 Nginx 启动时创建的**工作进程数量**。
工作进程负责处理所有连接、请求、响应。

**建议**：
设置为 **CPU 核心数**，或者直接用 `auto`（自动检测）。

- 太少 → 无法高效处理并发
- 太多 → 浪费系统资源
**最佳实践：`worker_processes auto;`**

---

# 3. worker_connections 指令
**语法**：`worker_connections 数字;`
**默认值**：`worker_connections 512;`
**上下文**：`events`
**示例**：`worker_connections 1024;`

**作用**：
设置**每个工作进程**能同时处理的**最大连接数**。

**Nginx 最大并发连接数计算公式：**
```
总并发连接 = worker_processes × worker_connections
```

示例：
```
worker_processes 4;
worker_connections 1024;
总连接 = 4 × 1024 = 4096
```

---

# 4. worker_rlimit_nofile 指令
**语法**：`worker_rlimit_nofile 数字;`
**默认值**：无
**上下文**：`main`
**示例**：`worker_rlimit_nofile 8192;`

**作用**：
设置每个工作进程能打开的**最大文件句柄数（file descriptors）**。

在 Linux 中：
- 1 个网络连接 = 1 个文件句柄
- 1 个静态文件 = 1 个文件句柄
- 反向代理会占用 2 个句柄（客户端+后端）

**句柄数量直接决定 Nginx 能支撑多少并发连接。**

注意：设置前必须确认操作系统本身允许的最大句柄数。

---

# 🔥 这四个指令组合成的【高性能 Nginx 基础配置】
```nginx
# main 上下文（全局）
user nginx;
worker_processes auto;
worker_rlimit_nofile 8192;
error_log /var/log/nginx/error.log;
pid /var/run/nginx.pid;

# events 上下文
events {
    worker_connections 10240;
}
```

---

# Linux 中的 ulimit、硬限制、软限制
- **软限制（Soft Limit）**：应用程序和用户实际使用的限制值。
- **硬限制（Hard Limit）**：软限制所能设置的**上限值**。
- 规则：**软限制 ≤ 硬限制**

查看硬限制：
```bash
ulimit -Hn
```

查看软限制：
```bash
ulimit -Sn
```

如何修改软硬限制会在后面 **Nginx 性能优化** 章节讲解。

---

# access_log 指令
用于记录客户端请求与服务端响应的历史日志。

**语法**
```
access_log 路径 [格式] [buffer=大小] [gzip=级别] [flush=时间] [if=条件];
access_log off;
```

**默认**
```
access_log logs/access.log combined;
```

**可用上下文**
http、server、location、if in location、limit_except

**示例**
```nginx
access_log /var/log/nginx/log_request.log mainformat;

# 带 64K 缓冲
access_log /var/log/nginx/log_request.log mainformat buffer=64K;

# gzip 压缩级别 8
access_log /var/log/nginx/log_request.log mainformat gzip=8;

# 条件日志
access_log /var/log/nginx/log_request.log mainformat if=$loggable;
```

**说明**
- 日志默认位置：`/var/log/nginx/`
- `buffer=64K`：日志先写入缓冲区，批量写入磁盘，提高性能
- `gzip=8`：日志压缩，1~9 级，9 压缩最高
- `if=$loggable`：条件日志，满足条件才记录

**条件日志示例逻辑**
通过 Nginx 变量 `$status` 判断：
- 2xx / 3xx 状态码 → `$loggable = 0` → **不记录**
- 4xx / 5xx 状态码 → `$loggable = 1` → **记录日志**

---

# log_format 指令
定义访问日志的**自定义格式**。

**语法**
```
log_format 名称 [转义格式] 字符串...;
```

**示例**
```nginx
log_format mainformat '"$time_local" client=$remote_addr '
'method=$request_method request="$request" '
'request_length=$request_length '
'status=$status bytes_sent=$bytes_sent '
'upstream_addr=$upstream_addr '
'upstream_status=$upstream_status '
'request_time=$request_time '
'upstream_response_time=$upstream_response_time '
'upstream_connect_time=$upstream_connect_time '
'upstream_header_time=$upstream_header_time '
'body=$request_body';
```

**作用**
- 自定义日志里要显示哪些字段
- 定义后可以在 `access_log` 中使用这个格式名
- 可以定义多种不同格式

---

# include 指令
用于**引入其他配置文件**，实现配置模块化。

**语法**
```
include 文件 | 通配符;
```

**示例**
```nginx
include /etc/nginx/mime.types;
include /etc/nginx/*.conf;
```

**作用**
- 拆分配置，便于管理
- 主配置 `nginx.conf` 可以只做总入口

---

# listen 指令
指定 Nginx 监听的 **IP + 端口**。

**语法**
```
listen 地址[:端口] [default_server] [ssl] [http2] [reuseport];
```

**示例**
```nginx
listen 80;
listen 80 default_server;
listen 443 ssl;
listen [::]:80;       # IPv4 + IPv6
listen 127.0.0.1:8000;
```

**说明**
- `listen 80`：监听所有 IP 的 80 端口
- `default_server`：默认虚拟主机，无匹配域名时走这里
- `ssl`：开启 HTTPS
- `reuseport`：多进程并行接收连接，提升性能
- `[::]:80`：同时支持 IPv4 和 IPv6

---

# server_name 指令
指定该 server 块**对应哪些域名**，实现**虚拟主机**。

**语法**
```
server_name 字符串 正则 通配符 _ IP;
```

**示例**
```nginx
server_name www.test.com test.com;
server_name *.test.com;       # 泛域名
server_name 192.168.1.1;
server_name _;                # 匹配所有域名（默认主机）
server_name ~^.+\.amazon\.(com|in)$;  # 正则
```

**作用**
一台服务器跑多个网站，靠 `server_name` 区分。

---

# proxy_pass 指令
**反向代理**，把请求转发给后端服务器。

**语法**
```
proxy_pass URL/上游地址;
```

**示例**
```nginx
proxy_pass https://10.0.0.5:8080;
proxy_pass https://backend_server$request_uri;
```

**作用**
- 将请求转发给 upstream（后端集群）
- 实现反向代理、负载均衡、API 网关

---


**（proxy_pass）可以指定一个可选的 URI 路径，用于描述请求如何转发到上游服务器。**
该指令通常用于**反向代理配置**。

proxy_pass 指令**必须包含**：
1. `$scheme`（Nginx 内置变量，表示协议 http 或 https）
2. 完整的 URL **或** 后端 upstream 名称
3. 支持使用 Nginx 变量（通过引用方式传递请求路径片段）

---

## 示例 1：直接代理到 URL
```nginx
location /url/ {
    proxy_pass http://www.test.com/link/;
}
```
访问 `/url/page.html` → 转发到 `http://www.test.com/link/page.html`

---

## 示例 2：代理到 upstream 后端服务器集群
```nginx
# 定义后端集群
upstream backend_server {
    server server1.com:443;
    server server2.com:443;
}

location /url/ {
    proxy_pass http://backend_server;
}
```

---

## 示例 3：正则 + 引用变量转发
```nginx
location ~* "/(001|002|003)" {
    proxy_pass http://backend_server/test/$1;
}
```
访问 `/001` → 转发到 `http://backend_server/test/001`

---

# ✅ 总结：proxy_pass 三大用法
1. **直接转发到具体网址**
2. **转发到 upstream 集群（负载均衡）**
3. **正则捕获 + 路径重写转发**

---

# 超清晰解释：`server_name localhost;` 到底是什么意思

## 1. 直译
**localhost = 本机、本地、当前服务器**

## 2. 作用
当你在配置里写：
```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
}
```

它的意思是：
✅ **这个 server 块只处理访问“本机”的请求**
也就是：
- `http://localhost`
- `http://127.0.0.1`

---

# 3. 什么时候会用？
- 本机开发测试
- Docker 内部访问 Nginx
- 只允许本机打开的页面（如 `/nginx_status`）
- 不想让外网访问的站点

---

# 4. 和 `server_name _;` 的区别
| 配置 | 含义 |
|------|------|
| `server_name localhost;` | 只匹配 localhost |
| `server_name _;` | **匹配所有域名**（默认主机） |

---

# 5. 最关键：多网站示例
```nginx
# 只能本机访问
server {
    listen 80;
    server_name localhost;
    root /local-website;
}

# 外网可访问
server {
    listen 80;
    server_name www.yourdomain.com;
    root /public-website;
}
```

---

# 一句话总结
## `server_name localhost;`
### ✔ 表示：这个网站**只允许本机访问**
### ✔ 不影响外网其他域名的网站
### ✔ 可以和其他 server{} 块共存

---

# 完整翻译 + 超清晰讲解（反向引用、return、rewrite、upstream）
我给你**原汁原味、准确、好懂**的翻译，同时把最难的**Back Referencing（反向引用）** 用最简单的例子讲明白。

---

# 1. Back Referencing 反向引用（Nginx 最核心技巧）
## 翻译
Nginx 的**反向引用**利用正则表达式的**捕获组（Capture Group）**，提取 URL 中的一部分内容，然后在配置里**重复使用**。
它可以实现动态重写、重定向、路由规则。

在例子中，`()` 括号里匹配到的内容 `(001|002|003)` 就叫**捕获组**。
捕获到的值会用在 `proxy_pass` 里，拼接成新的 URL 转发给后端。

- `$1` = 第一个括号里捕获到的值
- `$2` = 第二个括号里捕获到的值

### 例子
```nginx
location ~* "/(001|002|003)" {
    proxy_pass http://backend_server/test/$1;
}
```
- 访问 `/001` → 转发到 `http://backend_server/test/001`
- 访问 `/002` → 转发到 `http://backend_server/test/002`

这个过程就叫 **反向引用**。

---

## 常用正则表达式速查表
| 正则 | 作用 |
|---|---|
| `\w+` | 匹配字母、数字、下划线 |
| `\d+` | 匹配数字 |
| `\D+` | 匹配非数字 |
| `\s+` | 匹配空格 |
| `\S+` | 匹配非空格 |
| `(.*)` | 匹配任意字符（最常用在反向引用） |
| 邮箱正则 | 匹配邮箱 |
| IP 正则 | 匹配 IPv4 |

---

# 2. return 指令（最简单的重定向/返回）
## 翻译
`return` 是 Nginx 最简单的返回指令，**直接返回状态码**，停止后续所有处理。

**语法**
```
return 状态码 [内容];
return 状态码 跳转地址;
```

**例子**
```nginx
return 301 https://新网址$request_uri;
return 503 "维护中";
```

---

# 3. rewrite 指令（URL 重写）
## 翻译
`rewrite` 功能更强，**在请求被处理前修改 URL**。

**语法**
```
rewrite 正则 替换内容 [标记];
```

**例子**
```nginx
rewrite ^/oldpath/(.*)$ /newpath/$1 permanent;
```
- `/oldpath/abc` → `/newpath/abc`

### 4 个标记（必须记住）
- `last`：重写后，重新匹配 location
- `break`：停止重写，继续当前逻辑
- `redirect`：302 临时跳转
- `permanent`：301 永久跳转

---

# 4. return 301 / 302 / 308 区别（面试必考）
## 翻译
- **301 永久跳转**
  浏览器会缓存，搜索引擎更新索引。
  用于域名更换、http→https。

- **302 临时跳转**
  不缓存，搜索引擎保留旧地址。
  用于临时维护、活动页面。

- **308 永久跳转（保留请求方法）**
  和 301 一样，但 **不会把 POST 变成 GET**。
  适合接口、POST 请求。

---

# 5. upstream 指令（后端服务器组 + 负载均衡）
## 翻译
`upstream` 用来**定义一组后端服务器**，实现**负载均衡**。
Nginx 会自动把请求分发给这些服务器。

**例子**
```nginx
upstream backend_server {
    server server1.com:443;
    server server2.com:443;
}
```

然后在 location 里使用：
```nginx
proxy_pass http://backend_server;
```

---

# 6. upstream 里的 server 指令
定义后端服务器地址 + 端口。
```
server 地址:端口;
```
不写端口默认 80。

---

---

# 🔥 本章终极总结（你必须记住）
1. **反向引用 `$1`**
   正则 `()` 捕获 → `$1` 使用
2. **return**
   直接返回、最简单
3. **rewrite**
   改 URL、功能强
4. **301/302/308**
   301 永久、302 临时、308 保留POST
5. **upstream**
   后端服务器组 → 负载均衡

---

# 完整翻译 + 极简讲解（upstream 所有参数 + 缓冲区核心指令）
我把你这段**超级重要的 Nginx 负载均衡 + 缓冲区配置**全部翻译+讲透，全部是**面试 + 生产环境必考**内容！

---

# 一、upstream 服务器参数（负载均衡核心）
## 1. weight 权重
给后端服务器设置**相对权重**，默认 `weight=1`。
Nginx 默认按**轮询（round-robin）**分发请求，权重越高，分到的请求越多。

```nginx
upstream backend_server {
    server server1.com:443 weight=1;
    server server2.com:443 weight=3;
}
```
- 每 **4 个请求**
- 1 个给 server1
- 3 个给 server2

## 2. max_fails 最大失败次数
设置**连续失败多少次**后，标记服务器为 **down（宕机）**。
默认：max_fails=1

```nginx
server server1.com:443 max_fails=2;
```
连续失败 **2 次** → Nginx 暂时不发请求给它。

> max_fails=0 表示**不检查健康状态**，永远不标记宕机。

## 3. fail_timeout 宕机重试时间
服务器被标记 down 后，**暂停多久不发请求**，时间到再重试。

```nginx
server server1.com:443 max_fails=2 fail_timeout=10s;
```
失败 2 次 → 暂停 **10 秒** → 10 秒后重试是否恢复。

## 4. backup 备用服务器
标记为**备用机**。
**只有所有主服务器都挂了，才会启用 backup**。

```nginx
server server3.com:443 backup;
```

## 5. resolve 动态解析 DNS
让 Nginx **运行时自动重新解析域名 IP**。
适合 Docker / K8s 环境（IP 经常变）。

```nginx
server backend1.test.com resolve;
```

## 6. resolver DNS 解析器
配置 Nginx 使用的 **DNS 服务器**，必须配合 resolve 使用。

```nginx
http {
    resolver 8.8.8.8;  # Google DNS
}
```

## 7. slow_start 慢启动
服务器**刚恢复/刚上线**时，**流量慢慢增加**，给服务器预热时间。

```nginx
server server1.com:443 slow_start=5s;
```

## 8. down 永久下线
标记服务器**永久不可用**，直接剔除。

```nginx
server server3.com:443 down;
```

## 9. drain 优雅下线（优雅停机）
- **不接收新请求**
- **已有的请求处理完再下线**
- 不会中断用户连接

### down vs drain
- **down**：立即剔除，断开连接
- **drain**：优雅下线，处理完再停

---

# 二、Nginx 缓冲区指令（性能 + 排错核心）
## 1. client_body_buffer_size
**接收客户端请求体的缓冲区大小**（POST 表单/JSON）。
超过大小 → 写入**临时文件**。

默认：8k/16k

## 2. client_header_buffer_size
**存储客户端请求头的默认缓冲区**。
请求头超过 1k → 报 **400 Bad Request**。

## 3. large_client_header_buffers
**大请求头专用缓冲区**（cookie 特别多时用）。

```
large_client_header_buffers 4 8k;
```
最多 4 块缓冲区，每块 8k。

### 区别总结
- **client_header_buffer_size**：存**正常大小**请求头
- **large_client_header_buffers**：存**超大**请求头

---

# 三、反向代理缓冲区（proxy 相关）
## 1. proxy_buffers
Nginx 从**后端服务器读取响应**的缓冲区。

```
proxy_buffers 8 4k;
```
8 块缓冲区，每块 4k。

## 2. proxy_buffer_size
存储**后端响应头**的缓冲区。
响应头过大 → 报 400 / header too large。

## 3. proxy_busy_buffers_size
限制**正在使用的缓冲区大小**，超过则写入临时文件。

---

# 🔥 极简总结（你必须背下来）
## upstream 负载均衡 9 个参数
1. **weight** 权重
2. **max_fails** 最大失败次数
3. **fail_timeout** 宕机重试时间
4. **backup** 备用机
5. **resolve** 动态解析 DNS
6. **resolver** DNS 服务器
7. **slow_start** 慢启动
8. **down** 强制下线
9. **drain** 优雅下线

## 缓冲区 6 个核心指令
1. client_body_buffer_size（请求体）
2. client_header_buffer_size（请求头）
3. large_client_header_buffers（大请求头）
4. proxy_buffers（代理响应缓冲区）
5. proxy_buffer_size（代理响应头）
6. proxy_busy_buffers_size（繁忙缓冲区限制）

---

# 最后一段完整翻译 + 全网最清晰对比 + 必背总结
我把你这段**终极核心内容**全部翻译、对比、讲透，学完这部分你 Nginx 就算完全通关了！

---

# 1. proxy_buffer_size vs proxy_busy_buffers_size（必考对比）
## 翻译
- **proxy_buffer_size**
  用于**存储后端响应头**的**初始缓冲区**。
  只存响应头，很小。

- **proxy_busy_buffers_size**
  限制**“忙状态”缓冲区的总大小**。
  也就是：已经从后端读到数据，但**还没完全发给客户端**的缓冲上限。
  超过这个大小，Nginx 会把内容写入临时文件。

---

# 2. Nginx 常用 HTTP 模块（超级重要）
## ngx_http_keyval_module
键值存储模块。

## ngx_http_limit_conn_module
限制**同一个 IP 的并发连接数**。

## ngx_http_limit_req_module
限制**请求速率（限流）**，比如 1 秒 10 个请求。

## ngx_http_log_module
日志模块（access_log、error_log）。

## ngx_http_map_module
根据条件创建自定义变量。

## ngx_http_mirror_module
请求镜像（复制流量到测试服务器）。

## ngx_http_rewrite_module
URL 重写（rewrite、return、if）。

## ngx_http_split_clients_module
流量切分（A/B 测试）。

## ngx_http_ssl_module
HTTPS 支持。

## ngx_http_status_module
状态监控页面（stub_status）。

## ngx_http_upstream_module
上游服务器 + 负载均衡。

---

# 3. Mail 模块
代理邮件协议：SMTP、IMAP、POP3。

---

# 4. Stream 模块
处理 **TCP/UDP 流量**（非 HTTP），例如：
- 数据库
- Redis
- MQ
- 自定义 TCP 协议

---

# 5. Nginx 变量（最常用必背）
## 内置变量
- `$scheme`：http / https
- `$host`：请求域名
- `$request_uri`：完整请求地址（带参数）
- `$uri`：请求路径（不带参数）
- `$remote_addr`：客户端 IP
- `$request_method`：GET/POST
- `$status`：响应状态码
- `$upstream_addr`：后端服务器地址
- `$request_time`：请求处理时间
- `$http_user_agent`：浏览器信息

## 自定义变量
```nginx
set $my_var "hello";
```

---

# 🔥 本章终极通关总结（你一定要背）
## 一、upstream 9 大参数
1. **weight** 权重
2. **max_fails** 最大失败次数
3. **fail_timeout** 重试间隔
4. **backup** 备用机
5. **resolve** 动态解析 DNS
6. **resolver** DNS 服务器
7. **slow_start** 慢启动
8. **down** 强制下线
9. **drain** 优雅下线

## 二、缓冲区 6 个核心
1. client_body_buffer_size（请求体）
2. client_header_buffer_size（请求头）
3. large_client_header_buffers（大请求头）
4. proxy_buffers（后端响应缓冲）
5. proxy_buffer_size（后端响应头）
6. proxy_busy_buffers_size（繁忙缓冲上限）

## 三、return 301/302/308
- **301**：永久跳转（会变 GET）
- **302**：临时跳转
- **308**：永久跳转（**保留 POST**）

## 四、Location 匹配优先级
1. `=` 精确匹配
2. `^~` 前缀匹配
3. `~` / `~*` 正则匹配
4. 普通前缀 / 默认 `/`

## 五、反向引用
`()` 捕获 → `$1` 使用

---



