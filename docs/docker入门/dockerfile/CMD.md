> 注意语法：Dockerfile 里面必须是**双引号** `""`，单引号 `''` 属于错误语法，会直接报错。

```
# ❌错误，单引号
CMD ['/etc/nginx/conf.d/setenv.sh']

# ✅正确
CMD ["/etc/nginx/conf.d/setenv.sh"]
```

---

## 核心问题：不能把 `setenv.sh` 直接作为 CMD

回顾两个脚本分工：

1. **`setenv.sh`**：只是**变量配置脚本**，职责：定义/赋值环境变量；它执行完就直接退出，**不会启动 nginx**。
2. **`run.sh`**：真正的容器入口脚本：
   - `source setenv.sh` 加载变量
   - `cat >> <<EOF` 动态生成 nginx conf
   - `exec nginx -g "daemon off;"` 前台拉起 nginx，维持容器不退出

如果你写：

```
CMD ["/etc/nginx/conf.d/setenv.sh"]
```

容器启动执行 `setenv.sh`：

1. setenv.sh 里面只是变量赋值，脚本跑完，进程直接结束。
2. PID1 进程退出 → **Docker容器立刻停止退出**，nginx根本不会启动。

> `setenv.sh` 只适合被 `source` 加载，**不适合直接作为容器CMD入口**。

### source 和直接执行 ./setenv.sh 的巨大区别

1. `source /etc/nginx/conf.d/setenv.sh`（在run.sh内部执行）
   在**当前shell进程里面执行脚本**，变量导入当前shell环境；执行完继续往下跑run.sh剩余逻辑，最后启动nginx。
2. `/etc/nginx/conf.d/setenv.sh` 直接运行（CMD这样写）
   会**新开一个子shell进程**执行脚本；变量只存在子进程，执行结束子进程销毁，父进程完全拿不到变量，并且脚本结束容器直接死亡。

---

## 正确写法（你项目原本的设计）

```
# CMD执行真正入口 run.sh，run.sh内部再source setenv.sh
CMD ["/run.sh"]
```

run.sh内部：

```
#!/bin/bash
# 加载变量脚本，把变量导入当前shell环境
source /etc/nginx/conf.d/setenv.sh

# 动态渲染nginx配置
cat > /etc/nginx/conf.d/default.conf <<EOF
server {
    listen ${NGINX_PORT};
    location / {
        try_files \$uri \$uri/ /index.html;
    }
    location /api/ {
        proxy_pass ${BACKEND_URL};
        proxy_set_header Host \$host;
    }
}
EOF

# 前台启动nginx，接管PID1，容器保持运行
exec nginx -g "daemon off;"
```

---

## 小结重点

1. Dockerfile `CMD` 指定的程序，必须是**长期驻留不退出的进程**（nginx、run.sh这种）；不能是执行完就退出的配置脚本。
2. `setenv.sh` 是变量配置脚本，**职责是被source加载，不能直接当做容器CMD**。
3. `source`：在当前进程加载变量；直接运行脚本：新开子进程，变量不生效，执行完就退出。
4. Dockerfile JSON数组格式必须使用**双引号**，单引号语法非法。

### 整套完整汇总版 Dockerfile

```
ARG BASE_IMAGE=182.xx.x.x/nginx
FROM ${BASE_IMAGE}

USER root

RUN rm -rf /etc/nginx/conf.d/default.conf

# 复制前端dist静态资源
COPY dist/* /usr/share/nginx/html/

# 复制变量脚本
COPY docker/setenv.sh /etc/nginx/conf.d/
RUN chmod 644 /etc/nginx/conf.d/setenv.sh

# 复制主入口脚本
COPY run.sh /
RUN chmod +x /run.sh

# 入口是 run.sh，不是 setenv.sh
CMD ["/run.sh"]
```

执行链路：
`docker run` → `/run.sh` 运行 → `source setenv.sh` 读取变量 → 动态生成default.conf → `exec nginx -g "daemon off;"`。
