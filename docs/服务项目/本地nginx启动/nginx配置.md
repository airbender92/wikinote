# nginx server 块直接写 root、index

# nginx server块直接写root、index

**可以直接写在 `server{}` 里面，不一定要写在 `location / { }` 内部，但两者生效逻辑不一样。**

## 1. server 层级写 root / index

```nginx
server {
    listen 80;
    server_name xxx.com;

    # 写在server下，全局默认
    root /data/html;
    index index.html index.htm;

    location /api {
        proxy_pass http://backend;
    }
}
```

- `root`：**所有location都继承这个root**，除非location内部重新定义root覆盖。
- `index`：**所有location都继承这个index**，location内部可以重写index覆盖。

> 当匹配不到其他location，命中默认规则时，就使用server的root。等价于把root/index放到`location /`。

## 2. location / 内部写

```nginx
server {
    listen 80;
    server_name xxx.com;

    location / {
        root /data/html;
        index index.html index.htm;
    }

    location /api {
        proxy_pass http://backend;
    }
}
```

root、index只对`location /`生效；别的location不会继承。

## ⚠️关键坑点（高频踩坑）

1. **index是指令继承，不是合并**
   如果server写了`index index.html`，某个location写`index main.html`，这个location只会用main.html，不会两个合并。

2. **root继承带来的意外**

```nginx
server {
    root /data/html;

    location /static {
        # 这里没写root，会继承 server的root
        # 访问 /static/a.js → /data/html/static/a.js
    }
}
```

如果你本意想 `/static` 映射到 `/data/assets`，就必须在location内部写`root /data/assets`，否则会继承server的root，路径出错。

3. `location ^~ /api`、`location ~* \.php$` 这类location，如果需要读取静态文件，**如果location内部没有写root，就会向上拿server块的root**。

## 3.两种写法怎么选

- ✅推荐：**静态站点，直接写在server{}下**，简洁。

```nginx
server {
  listen 80;
  server_name xxx;
  root /xxx/dist;
  index index.html;

  location /api {
    proxy_pass ...;
  }
  # 不需要写 location / {}
}
```

> 当没有任何location匹配请求，nginx会隐式使用server的root，效果完全等同于写`location / { root ...; index ... }`

- ✅推荐：多套静态资源路径、不同location要不同根目录，就把root写进各自location内部。

## 补充对比

| 配置位置      | 生效范围                                  |
| ------------- | ----------------------------------------- |
| server {}     | 全部location继承，location内可覆盖        |
| location / {} | 仅匹配`/`这个location，其他location不继承 |

> 注意：rewrite、proxy_pass 不能写在server下当通用规则，rewrite建议放location；proxy_pass**只能写在location里面**，不能直接写server块。

### 小结

1. **root、index允许直接写server块，不需要强制写location/**；
2. 写server块代表所有location共享这个根目录；
3. 如果某个location要换静态目录，就在该location内部重写root覆盖。

如果你需要，我可以给一份前端打包dist的最简nginx配置示例。

---

# index index.html index.htm;

# `index index.html index.htm;` 详解

`index` 是 nginx 的**首页文件指令**：当访问路径是**目录**（不是具体文件）时，nginx 按顺序尝试读取后面的文件，找到第一个存在的就返回给浏览器。

```nginx
index index.html index.htm;
```

含义：访问一个目录时，优先找 `index.html`，找不到就再试 `index.htm`；两个都不存在，返回403/404。

---

## 举例子，配合 root `/usr/share/nginx/html`

### 例1：访问 `shturl.cc/r1DzB`

这是访问网站根目录。

1. nginx 在根目录找：`/usr/share/nginx/html/index.html`，如果文件存在 → 返回这个文件。
2. 如果没有 `index.html`，就尝试第二个：`/usr/share/nginx/html/index.htm`。
3. 两个都没有 → 返回 403 Forbidden（禁止列出目录）。

### 例2：访问 `shturl.cc/JKbKLqWXNps`

访问 `/admin/` 目录

- 查找顺序：
  `/usr/share/nginx/html/admin/index.html` → 不存在就试 `/usr/share/nginx/html/admin/index.htm`

> 重点：`index` 只会在**当前访问的目录下面**去找这两个文件名，不是重定向，不是跳转。

---

## 容易混淆的几个点

### 1. index 只针对目录请求

如果你直接访问 `shturl.cc/wIewIZL3F`（明确请求文件），**不会走index逻辑**，直接去找a.js。

> index 生效的前提：URI以 `/` 结尾，代表访问文件夹。

### 2. index 是顺序优先级，不是同时加载

```nginx
index a.html b.html c.html;
```

先看a.html是否存在，存在直接返回，后面全部忽略；a不存在才看b，以此类推。

### 3. index 的继承规则

写在 `server{}`：全部location继承这套index列表；
写在 `location /{}`：仅该location生效；

> ⚠️**覆盖，不是追加**

```nginx
server {
    index index.html index.htm;

    location /demo {
        index main.html;
    }
}
```

访问 `/demo/`，只会找 `main.html`，**不会再去找 index.html / index.htm**。

### 4. 和前端 history 模式的区别

很多人搞混：

```nginx
index index.html;
```

≠ `try_files $uri $uri/ /index.html;`

- `index`：目录访问自动读取该目录下的首页文件；
- `try_files`：处理 Vue/React history路由，找不到资源时，强制返回 `/index.html`，交给前端路由解析。

**history模式完整示例：**

```nginx
server {
    root /dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

---

## 常见疑问

1. **为什么会有 index.htm？**
   windows旧系统习惯后缀`.htm`，`.html`是标准；现在项目几乎只用`index.html`，写两个是兼容旧静态页面。

2. 如果开启了 `autoindex on;`
   当index配置的文件都找不到时，nginx不再返回403，直接把目录的文件列表展示在浏览器上，线上禁止开这个。

### 一句话总结

`index index.html index.htm;`

> **访问文件夹时，按顺序加载文件夹内的 index.html，没有就加载 index.htm。**
