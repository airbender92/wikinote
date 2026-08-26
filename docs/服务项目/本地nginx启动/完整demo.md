[真实demo地址](../../../demos/node-nginx/)

- `/api/getData` 走接口返回json
- 其他路径可以不用管（静态已经交给Nginx托管了，Node只负责接口）>

> Nginx：80端口，托管www静态页面
> Node：3000端口，**只提供接口，不再处理html页面**

## 修改后的 node server.js

```
const http = require('http');
const port = 3000;

const server = http.createServer((req, res) => {
    // 设置跨域头（本地调试需要，经过nginx反向代理后可以删掉）
    res.setHeader('Access‑Control‑Allow‑Origin', '*');
    res.setHeader('Content‑Type', 'application/json;charset=utf‑8');

    // 接口： /api/getData
    if (req.url === '/api/getData' && req.method === 'GET') {
        const result = {
            code: 200,
            msg: "来自node后端接口的数据",
            data: [11,22,33,44]
        };
        res.writeHead(200);
        res.end(JSON.stringify(result));
        return;
    }

    // 其他路径返回404，因为静态全部由nginx处理
    res.writeHead(404, { 'Content-Type':'text/plain;charset=utf-8' });
    res.end("node：该接口不存在");
});

server.listen(port, () => {
    console.log(`node接口服务启动 http://127.0.0.1:${port}`);
});
```

运行node：

```
node server.js
```

直接访问node接口测试：`http://127.0.0.1:3000/api/getData`

---

## Nginx配置（你已经托管静态，只加/api反向代理）

```
server {
    listen       80;
    server_name  localhost;

    # 你的www静态目录，改成你真实绝对路径
    root   D:/wybD/appInstaller/nginx/www;
    index  index.html index.htm;

    # 所有 /api/ 的请求转发给 node:3000
    location /api/ {
        proxy_pass http://127.0.0.1:3000/api/;

        proxy_set_header Host $host;
        proxy_set_header X‑Real‑IP $remote_addr;
        proxy_set_header X‑Forwarded‑For $proxy_add_x_forwarded_for;
    }

    # history路由模式，刷新404
    location / {
        try_files $uri $uri/ /index.html;
    }

    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   html;
    }
}
```

校验+重载nginx

```
nginx -t
nginx -s reload
```

## 完整访问链路

1. 浏览器访问 `http://localhost`
   👉 Nginx直接读取 `www/index.html`，**不走node**
2. 前端页面里面ajax/fetch请求：`/api/getData`
   👉 请求到nginx(80端口)，nginx匹配`/api/`，反向代理转发给 `127.0.0.1:3000/api/getData`
   👉 node处理接口返回json，再原路返回浏览器

> ✨重点：前端js写请求直接写 `/api/getData`，**不要写127.0.0.1:3000**，全部走nginx80端口。

### 前端www/index.html示例，测试接口

```
<!DOCTYPE html>
<html>
<body>
<h1>nginx托管页面，调用nginx反向代理node接口</h1>
<button onclick="fetchApi()">请求接口</button>
<div id="res"></div>

<script>
async function fetchApi(){
    const resp = await fetch('/api/getData');
    const json = await resp.json();
    document.getElementById('res').innerText = JSON.stringify(json);
}
</script>
</body>
</html>
```

## 本地调试流程

1. cmd1：启动node `node server.js`
2. cmd2：nginx已经启动
3. 浏览器打开 `http://localhost`，点按钮，接口经过nginx转发到node

### 常见坑

1. node没启动 → nginx代理返回502 Bad Gateway
2. proxy_pass路径末尾斜杠：`/api/` 斜杠不能乱删
3. 前端不要写完整 `http://127.0.0.1:3000/api/getData`，要写相对路径 `/api/getData`，才能走nginx反向代理。

> 经过nginx代理后，**前端不需要跨域头**，生产环境可以把node代码里的Access‑Control‑Allow‑Origin删掉。本地调试直接保留即可。
