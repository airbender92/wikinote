```
RUN rm -rf /etc/xxxx/default.conf
```

## 命令拆解（Dockerfile 的 RUN，镜像构建阶段执行）

`RUN`：**构建镜像的时候执行，打包进镜像；容器运行时不会再跑这行**。

```
rm      # 删除文件
-r      # 递归（删文件夹用）
-f      # force，强制删除；文件不存在也不报错
rm -rf  # 强制删除文件/目录，不抛异常
```

作用：**删掉基础镜像自带的默认 nginx 配置文件**。

### 为什么要删除 default.conf

你这套镜像逻辑：

1. 基础私有nginx镜像自带 `/etc/nginx/conf.d/default.conf`（默认站点配置）
2. 我们是靠 `run.sh` 脚本，容器**启动的时候**用 `cat >> <<EOF` 动态生成一份全新的 default.conf
3. 如果不删掉原始默认配置：两份配置同时存在，nginx会同时加载，发生冲突、出现意外虚拟主机。

所以构建镜像阶段直接把模板旧配置清理掉：

```
RUN rm -rf /etc/nginx/conf.d/default.conf
```

> 构建镜像就把旧文件删掉，容器启动之后目录是空的，再由sh脚本生成全新配置。

### 容易混淆两个时机

1. **RUN rm -rf xxx** → `docker build` 构建镜像阶段执行，写进镜像层。镜像打包完，这个文件就永久没了。
2. 如果写在 `run.sh`（容器启动脚本）里面的 `rm -rf xxx` → 容器每次启动的时候才删除。

两种都可以实现删除，区别：

- RUN（build阶段删）：一次执行，镜像内永久干净，容器启动脚本更轻量。
- sh脚本内rm：每次容器起来删一次；适合某些场景。

## 坑点

1. 文件名拼写错误 `default.cong`，会因为找不到文件，`rm -f` 不会报错，构建不会失败，但是旧配置实际还留在镜像里面，后续出现诡异问题。一定要核对后缀：`.conf`。
2. `-rf` 威力很大，路径写错会删坏镜像系统文件，生产要小心。

## 结合你完整整套流程串联

```
# build阶段
ARG BASE_IMAGE=182.xx.x.x/nginx
FROM ${BASE_IMAGE}

# 构建镜像就删除镜像自带默认站点配置
RUN rm -rf /etc/nginx/conf.d/default.conf

ENV BACKEND_URL=http://node:3000
COPY run.sh /
RUN chmod +x /run.sh

CMD ["/run.sh"]
```

容器启动之后：

1. 执行 `run.sh`
2. `cat >> <<EOF` → **动态生成全新 /etc/nginx/conf.d/default.conf**
3. nginx -t 校验
4. exec nginx -g "daemon off;"

> build阶段把旧的删掉，run的时候脚本生成新的，保证只有一份我们自己的nginx配置，不会和镜像自带的模板冲突。

### 小补充

nginx会加载 `/etc/nginx/conf.d/*.conf`，目录下**所有以.conf结尾的文件全部加载**，多份文件就多个server块，容易冲突。所以要清理掉镜像自带的模板。
