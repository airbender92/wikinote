# Dockerfile ARG BASE_IMAGE=182.xx.x.x/nginx

```
ARG BASE_IMAGE=182.xx.x.x/nginx
FROM ${BASE_IMAGE}
```

## ARG是什么

`ARG` = **构建参数（Build‑arg）**，只在**镜像构建阶段（docker build）生效**，容器运行的时候不存在。

- `ARG BASE_IMAGE=182.xx.x.x/nginx`：定义构建变量 `BASE_IMAGE`，给一个**默认值**私有镜像仓库地址。
- 后面 `FROM ${BASE_IMAGE}`，引用这个ARG变量，作为基础镜像。

> 和 `ENV` 的核心区别：

1. **ARG：构建阶段有效，build的时候用；容器run起来环境里看不到这个变量。**
2. **ENV：镜像内部环境变量，build + 容器运行时都存在，容器内sh脚本可以直接读取$XXX。**

### 拆解这两行

```
# 定义构建参数BASE_IMAGE，默认镜像地址是私有仓库 182.xx.x.x/nginx
ARG BASE_IMAGE=182.xx.x.x/nginx

# 使用变量的值作为基础镜像
FROM ${BASE_IMAGE}
```

1. 默认构建，不传递参数：

```
docker build -t my-nginx .
```

实际等价：

```
FROM 182.xx.x.x/nginx
```

会拉取你公司内网私有镜像仓库的nginx镜像，不是官方dockerhub的nginx。

2. build时可以**覆盖ARG默认值**，用 `--build-arg`

```
# 构建的时候替换基础镜像，切换成官方nginx
docker build --build-arg BASE_IMAGE=nginx:alpine -t my-nginx .
```

此时 `${BASE_IMAGE}` 就变成 `nginx:alpine`，`FROM nginx:alpine`。

> ARG变量**只在build构建过程使用**；容器启动后，进入容器执行 `env`，**看不到BASE_IMAGE这个环境变量**。sh脚本里面不能直接读取 `$BASE_IMAGE`。

## 位置坑（高频踩坑）

> ARG必须写在**使用它的FROM之前**！

❌错误写法（不起作用）

```
FROM ${BASE_IMAGE}
ARG BASE_IMAGE=182.xx.x.x/nginx
```

✅正确

```
ARG BASE_IMAGE=182.xx.x.x/nginx
FROM ${BASE_IMAGE}
```

> 在多阶段构建中，每个FROM块会重置ARG；FROM前面的ARG是全局构建参数。

## 和你前面整套链路串起来

```
# --------构建阶段（build）--------
ARG BASE_IMAGE=182.xx.x.x/nginx
FROM ${BASE_IMAGE}

# ENV：这个会打进镜像，容器运行时sh脚本可以读取 $BACKEND_URL
ENV BACKEND_URL=http://node:3000

COPY run.sh /
RUN chmod +x /run.sh

# 容器启动阶段（run）执行sh脚本
CMD ["/run.sh"]
```

- `ARG BASE_IMAGE`：**仅build构建镜像的时候用**，用来选择从哪个仓库拉nginx基础镜像。容器运行时sh拿不到这个变量。
- `ENV BACKEND_URL`：镜像环境变量，**容器启动后run.sh脚本可以直接$BACKEND_URL读取**，配合`cat >> <<EOF`动态生成nginx配置。

## 私有镜像地址说明

`182.xx.x.x/nginx` 是**企业内部私有镜像仓库**地址。

- 公网Docker Hub是 `nginx`
- 公司搭建内部harbor镜像仓库，地址是IP，存放内部镜像，内网机器才能pull。>

> 本机不在内网的话，直接build会报错pull失败。

## ARG与ENV对比速记

| 指令           | 生效时机                      | 容器内是否可见   | sh脚本能否读取          |
| -------------- | ----------------------------- | ---------------- | ----------------------- |
| `ARG NAME=val` | docker build **构建镜像阶段** | ❌容器运行不存在 | ❌sh脚本读不到          |
| `ENV NAME=val` | build + 容器run运行时         | ✅env命令可看到  | ✅sh脚本直接`$NAME`使用 |

### 小技巧：ARG转成ENV，让容器内脚本可以读到

如果你希望把构建参数ARG的值，在容器运行时给sh脚本使用，需要赋值给ENV：

```
ARG VERSION=1.0
ENV APP_VERSION=${VERSION}
```

容器内sh就可以 `echo $APP_VERSION`。

## 完整回顾整条链路

1. `docker build --build-arg BASE_IMAGE=xxx .` → ARG生效，拉取私有仓库nginx基础镜像
2. 镜像内置 `ENV BACKEND_URL=xxx`
3. `docker run -e BACKEND_URL=http://127.0.0.1:3000` 启动容器，可覆盖ENV
4. 容器启动执行CMD `run.sh`
5. sh读取环境变量`$BACKEND_URL`（ENV来的，不是ARG）
6. `cat >> <<EOF` 动态渲染nginx配置，nginx内置变量注意`\$host`转义
7. `exec nginx -g "daemon off;"`前台启动nginx，PID1保持容器存活。

> 关键点区分：**ARG管构建镜像；ENV管容器运行时脚本变量，两者不要混淆。**
