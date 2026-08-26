# `USER root`（Dockerfile指令）

```
USER root
```

作用：**切换镜像的执行用户为 root（超级管理员）**。

## 背景

很多企业定制的私有基础镜像（就是你这个 `182.xx.x.x/nginx`），**默认不是root用户**，会使用普通非root账号运行nginx，提升安全，比如 `nginx` 用户。

- 不写`USER root`：后续`RUN`、容器启动CMD，都以**当前默认用户**执行；
- `USER root`：切换成root身份，后面的指令都用root权限跑。

### 在你的Dockerfile里的作用

```
ARG BASE_IMAGE=182.xx.x.x/nginx
FROM ${BASE_IMAGE}

USER root          # 切到root超级用户

RUN rm -rf /etc/nginx/conf.d/default.conf

COPY docker/setenv.sh /etc/nginx/conf.d/
COPY run.sh /
RUN chmod +x /run.sh

CMD ["/run.sh"]
```

1. 基础镜像默认可能是普通nginx用户，普通用户**没有权限删除 `/etc/nginx/conf.d/` 下面的系统配置文件、修改目录、chmod加执行权限**。
2. 加上`USER root`之后：
   - `RUN rm -rf`：有权限删除系统目录下的配置
   - `RUN chmod +x /run.sh`：有权限修改脚本执行权限
   - 容器启动后 run.sh脚本也是root账号执行，可以读写 `/etc/nginx/conf.d/`，生成`default.conf`配置文件。

> 如果不写`USER root`，使用普通用户去删系统文件，构建阶段直接报权限拒绝 `Permission denied`。

## USER指令两个生效范围

1. **Build构建阶段**：后面所有`RUN`指令，使用该用户执行。
2. **容器运行阶段**：`CMD ["/run.sh"]` 也会以这个用户启动脚本。>

> 这里容器内run.sh、nginx进程都是root运行。

## 语法两种写法

```
USER root
# 或者uid
USER 0
```

root的uid就是0。

## 安全小知识

生产容器**不推荐默认root运行**，但是你这套镜像场景不得已用root：
脚本要动态写 `/etc/nginx/conf.d/default.conf`，这个目录属于系统目录，普通用户无写入权限。

### 常见两种写法对比

#### 写法1：全程root（你当前项目）

```
USER root
RUN xxx
COPY xxx
CMD ["/run.sh"]
```

整个构建+容器运行全部root，简单直接，但是容器进程权限很高。

#### 写法2：build时用root处理文件，运行时切回普通用户（最佳安全实践）

```
# build阶段root处理文件
USER root
RUN rm -rf /etc/nginx/conf.d/default.conf
COPY run.sh /
RUN chmod +x /run.sh

# 构建完成，容器启动的时候切回普通nginx用户
USER nginx
CMD ["/run.sh"]
```

> 但这套动态生成nginx配置的架构一般很难这么做：因为启动脚本要写`/etc/nginx/conf.d/`，普通用户写不进去，所以很多内部业务镜像直接全程USER root。

## 坑点

1. `USER root`只会影响**它后面的指令**，写在FROM之前无效。
   ❌错误

```
USER root
FROM ${BASE_IMAGE}
```

✅正确，写在FROM之后

```
ARG BASE_IMAGE=xxx
FROM ${BASE_IMAGE}
USER root
```

2. 如果基础镜像已经是root，写`USER root`属于多余，但写上也无害。

## 把整条Dockerfile片段汇总，到目前为止全部指令

```
# build构建参数，指定私有仓库基础镜像
ARG BASE_IMAGE=182.xx.x.x/nginx
FROM ${BASE_IMAGE}

# 切换root超级用户，获得系统目录读写权限
USER root

# build阶段删除镜像自带默认nginx配置
RUN rm -rf /etc/nginx/conf.d/default.conf

# 复制变量脚本到镜像内
COPY docker/setenv.sh /etc/nginx/conf.d/

# 复制容器入口脚本
COPY run.sh /
RUN chmod +x /run.sh

# 容器启动执行run.sh
CMD ["/run.sh"]
```

> 运行流程回顾：
>
> 1. build：拉取私有nginx镜像 → 切root → 删除旧conf → 复制sh脚本
> 2. docker run启动容器，root执行run.sh
> 3. run.sh中`source /etc/nginx/conf.d/setenv.sh`加载变量
> 4. 通过`cat >> <<EOF`动态生成 `/etc/nginx/conf.d/default.conf`
> 5. `exec nginx -g "daemon off;"`前台启动nginx。

## 记忆点

1. `USER root`：切换执行身份为超级管理员；解决文件读写权限不足。
2. 很多私有nginx镜像默认是普通nginx账号，删改系统配置会权限报错，必须加这句。
3. 作用于**后续所有RUN、CMD**。
4. 安全角度不建议容器root，但动态写系统配置的场景经常不得不使用root。
