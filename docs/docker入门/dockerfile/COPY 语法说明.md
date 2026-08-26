```
COPY docker/setenv.sh /etc/nginx/conf.d/
```

### COPY语法说明

`COPY 宿主机源路径 镜像内目标路径`

- 构建上下文（你本地机器）：`docker/setenv.sh`，项目文件夹下 `docker` 子目录里面的 `setenv.sh` 文件
- 复制到镜像容器内部路径：`/etc/nginx/conf.d/`

> 目标路径末尾带斜杠 `/`：代表复制到这个**目录下面**，文件名保持不变。
> 最终镜像内文件完整路径：`/etc/nginx/conf.d/setenv.sh`

⚠️重点：**`/etc/nginx/conf.d/` 是nginx读取`.conf`配置文件的目录！**
nginx只会加载这个目录下后缀为 `.conf` 的文件；
`.sh` shell脚本nginx**不会解析它**，仅仅只是把脚本文件放在这个文件夹，不会当成配置。

---

## setenv.sh 是干什么的？

结合你前面整套架构：

1. Docker build阶段 `COPY` 将脚本打进镜像，放在 `/etc/nginx/conf.d/setenv.sh`
2. 它不是nginx配置，是**shell脚本**。
3. 在你的入口 `run.sh` 里面大概率会有类似：

```
# 加载执行这个脚本
source /etc/nginx/conf.d/setenv.sh
```

`source`（等价 `.`）执行sh脚本，把脚本内部定义的变量导入当前shell环境。

两种常见内容：

1. setenv.sh内部写死各种默认环境变量

```
#!/bin/bash
NGINX_LISTEN_PORT=80
BACKEND_SERVICE=http://node:3000
```

run.sh `source` 之后，就可以直接使用 `$NGINX_LISTEN_PORT`、`$BACKEND_SERVICE`，再配合 `cat >> <<EOF` 渲染nginx配置。

2. 也可能脚本里面做环境变量兜底逻辑：如果容器没有传入ENV，就给默认值。

```
#!/bin/bash
# 如果变量为空，赋予默认值
[ -z "${BACKEND_URL}" ] && BACKEND_URL="http://127.0.0.1:3000"
```

---

## 容易踩坑

1. 不要误以为放到 `conf.d` 下面nginx就会读取！

```
/etc/nginx/conf.d/
├─ default.conf   ✅ nginx加载（后缀conf）
└─ setenv.sh     ❌ nginx完全忽略，只是shell脚本
```

2. COPY只是复制文件，**不会自动加执行权限**。
   如果这个脚本需要执行，有两种处理：

```
# 复制之后追加RUN给执行权限
COPY docker/setenv.sh /etc/nginx/conf.d/
RUN chmod +x /etc/nginx/conf.d/setenv.sh
```

或者用 `source` 加载脚本，source不需要文件有x执行权限。

3. 区分时机

- `COPY`：**docker build镜像构建阶段复制，文件打进镜像层，永久保存在镜像**。
- `source /xxx/setenv.sh`：**容器run启动阶段，在run.sh里面执行，把变量导入shell**。

---

## 整合到你完整Dockerfile片段

```
ARG BASE_IMAGE=182.xx.x.x/nginx
FROM ${BASE_IMAGE}

# 删除镜像自带默认配置
RUN rm -rf /etc/nginx/conf.d/default.conf

# 复制shell变量脚本到镜像内 conf.d目录
COPY docker/setenv.sh /etc/nginx/conf.d/

COPY run.sh /
RUN chmod +x /run.sh

CMD ["/run.sh"]
```

run.sh内部逻辑示例：

```
#!/bin/bash
# 加载setenv.sh，读取里面的变量
source /etc/nginx/conf.d/setenv.sh

# 此时 $BACKEND_URL $NGINX_PORT 就拿到了
cat > /etc/nginx/conf.d/default.conf <<EOF
server {
    listen ${NGINX_PORT};
    location /api/ {
        proxy_pass ${BACKEND_URL};
        proxy_set_header Host \$host;
    }
}
EOF

exec nginx -g "daemon off;"
```

> 变量优先级：
> 容器启动时 `‑e` 传入的环境变量 > setenv.sh脚本里面设置的默认值。

### 小结

1. `COPY docker/setenv.sh /etc/nginx/conf.d/`：build阶段把shell脚本复制进镜像，不是nginx配置。
2. `/etc/nginx/conf.d`只是存放位置，nginx不会处理sh；由入口脚本`source`加载读取变量。
3. source加载后，sh脚本的变量可以给到 `cat >> <<EOF`，动态生成nginx的`default.conf`。
