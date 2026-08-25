# 同一链接PC访问Web、手机访问H5

核心思路：**一套URL，服务端/前端判断设备类型，PC跳转Web端，移动端跳转H5端**，域名链接保持不变，只是内部分发不同页面。

> 两种方案：**服务端判断（推荐，性能好）**、**前端JS判断（简单，有闪烁）**

## 方案1：服务端设备识别（生产优先推荐）

同一个URL，服务器拿到http请求头，识别是PC还是手机，返回不同页面。

### 原理

读取请求头 `User‑Agent`，解析客户端设备：

- PC浏览器 → 返回PC Web页面
- 手机浏览器 → 返回H5页面

### Nginx配置示例（最常用）

```
server {
    listen 80;
    server_name demo.test.com;

    # UA匹配移动端
    if ($http_user_agent ~* "(Android|iPhone|iPad|iPod|Mobile)") {
        # 渲染H5页面，h5目录放h5打包产物
        root /data/h5;
    }
    # 默认PC端页面
    root /data/pc;
    index index.html;
}
```

> 优点：请求阶段就分发，无页面闪烁；搜索引擎友好；用户地址栏URL始终不变。
> 缺点：Nginx/Apache需要配置，前后端两套打包产物分开存放。

### SpringBoot/Node后端实现逻辑

收到请求，解析User‑Agent：

1. 判断是移动端，返回H5的index.html
2. 判断是PC端，返回PC Web的index.html

## 方案2：前端JS判断（简单快速，适合静态页面）

> 注意：页面会先加载，再跳转，会有短暂闪烁，不适合高并发生产。
> 同一入口index.html，JS检测屏幕宽度 / userAgent，做内部跳转。

```
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
</head>
<body>
<script>
// 判断是否移动端
function isMobile() {
    return /Android|iPhone|iPod|iPad/.test(navigator.userAgent) || window.innerWidth < 768;
}
if(isMobile()){
    // 渲染H5应用，可以hash路由切换，不改变浏览器地址
    location.hash="#/h5"
}else{
    location.hash="#/pc"
}
</script>
</body>
</html>
```

### SPA项目（Vue/React）实现方式

**同一个项目，路由层做分发，URL完全不变**
访问 `https://xxx.com/`

- PC环境：路由自动导向 `/pc/home`
- 手机环境：路由自动导向 `/h5/home`

> 地址栏链接不变，只是内部路由切换。
> ⚠️缺点：HTML已经下载完成才执行判断，会闪屏；爬虫抓取容易识别异常。

## 方案3：两套独立站点，302重定向（不推荐）

`demo.test.com`

- 手机访问302跳转到 `demo.test.com/h5`
- PC访问302跳转到 `demo.test.com/pc`>

> ❗浏览器地址栏URL会发生变化，**不符合你“同一个链接”的需求**，不选这个。

## 重要区分：2种业务形态

1. **两套代码（PC一套Web、H5一套）**：Nginx/后端根据UA返回不同index.html，**推荐，维护清晰**
2. **一套代码自适应（响应式）**：只写一套页面，CSS媒体查询适配PC/手机，不需要分发跳转；但交互差异巨大的业务不适合。

## 踩坑点

1. iPad平板UA会被识别成移动端，需要单独做适配逻辑
2. JS判断会有闪屏，正式业务优先服务端Nginx处理
3. SPA部署时，Nginx要配置history模式try_files，防止刷新404
4. 微信内置浏览器UserAgent特殊，识别规则要兼容微信

## 选型建议

| 方案            | 优点                     | 缺点                 | 适用场景           |
| --------------- | ------------------------ | -------------------- | ------------------ |
| Nginx服务端分发 | 无闪烁，URL不变，SEO友好 | 需要服务器配置       | 生产环境首选       |
| 前端JS路由分发  | 无需改服务器，快速实现   | 页面闪烁，不利于爬虫 | 内部系统、原型演示 |
| 响应式一套代码  | 只维护一套程序           | 交互差异大时体验差   | 简单展示页面       |

如果你用的是Vue3/Vite，我可以直接给你完整可复制的路由层代码。如果是Nginx部署，我可以给你完整可直接粘贴的配置。
