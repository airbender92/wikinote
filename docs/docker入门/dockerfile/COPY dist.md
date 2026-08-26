```
COPY dist/* /usr/share/nginx/html/
```

## 作用

把**构建上下文本地 `dist` 目录下所有文件**，复制到镜像内 nginx 静态页面目录：`/usr/share/nginx/html/`。

> `dist` 就是前端项目打包输出目录（vue/react执行build之后产出的静态资源：index.html、js、css、图片）。

### 细节拆解

1. `dist/*`：`*`代表通配，复制dist下面**全部内容**，不复制dist文件夹本身。
2. 目标路径末尾带 `/`：代表是目录。
   最终效果：

```
/usr/share/nginx/html/
├─ index.html
├─ js/
├─ css/
└─ 各种静态资源
```

nginx默认静态站点根目录就是 `/usr/share/nginx/html`，访问nginx就会返回这里的`index.html`。

## 两种COPY写法的区别（高频踩坑）

```
# 写法1：COPY dist/*  /usr/share/nginx/html/
# 将dist里面的全部文件，直接放到html下（你现在这行）

# 写法2：COPY dist  /usr/share/nginx/html
# 把整个dist文件夹复制过去，结果变成 /usr/share/nginx/html/dist/index.html，访问不到页面，错误！
```

> ✅你的写法 `COPY dist/* /usr/share/nginx/html/` 是前端镜像标准写法。

## 时机

`COPY` 属于 **docker build 构建阶段执行**，打包进镜像。
镜像做好之后，容器启动不需要再打包前端文件，nginx直接读取镜像内的静态文件。

## 结合你整套Dockerfile

```
ARG BASE_IMAGE=182.xx.x.x/nginx
FROM ${BASE_IMAGE}

USER root

RUN rm -rf /etc/nginx/conf.d/default.conf

# 复制前端打包产物dist
COPY dist/* /usr/share/nginx/html/

COPY docker/setenv.sh /etc/nginx/conf.d/
RUN chmod 644 /etc/nginx/conf.d/setenv.sh

COPY run.sh /
RUN chmod +x /run.sh

CMD ["/run.sh"]
```

### 完整业务逻辑串起来

1. 本地前端执行build，输出dist（index.html、js、css）
2. `docker build`：
   - 拉取私有nginx基础镜像
   - 切root，删除镜像自带nginx配置
   - **COPY把dist前端静态资源打进镜像**
   - 复制shell脚本 setenv.sh、run.sh
3. `docker run`启动容器，执行run.sh
   1. `source setenv.sh` 加载环境变量
   2. `cat >> <<EOF` 动态生成 nginx `default.conf`配置
   3. `exec nginx -g "daemon off;"`前台启动nginx
4. nginx：
   - 静态页面从 `/usr/share/nginx/html/` 返回（前端页面）
   - `/api/` 请求代理转发给后端服务

## 常见坑

1. **构建上下文问题**
   执行build命令的当前目录，必须能看到`dist`文件夹；如果dist不在当前目录，会报找不到文件。
2. .dockerignore
   如果 `.dockerignore` 文件写了 `dist/`，会忽略dist目录，COPY复制不到任何前端文件，页面空白。
3. root权限复制
   这里`USER root`，复制过来的文件属主是root；如果未来改为普通用户运行容器，注意html目录读权限。
4. history模式依赖nginx配置

> 前端history路由刷新404，正好就是你之前看到的

```
location / {
    try_files $uri $uri/ /index.html;
}
```

这一段是在run.sh脚本动态写入default.conf，**不是build阶段写死在镜像里面**。

## 总结记忆

- `COPY dist/* /usr/share/nginx/html/`：**build阶段把前端打包静态资源打进镜像**。
- `/usr/share/nginx/html`：nginx默认静态资源根目录。
- 前端页面文件是镜像固化的；nginx代理配置是**容器启动sh脚本动态生成**。
