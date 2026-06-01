![4](/assets/docker/4.jpg)

我帮你把这段搭建 Docker 应用栈的内容，做了**结构化梳理+步骤拆解+原理说明**，帮你一次性吃透这个案例👇

---

# 2.3.2 第一个 Docker 应用栈（完整解读）
## 一、应用栈整体架构
这是一个典型的 6 节点容器化 Web 应用，结构如下：


| 层级 | 节点 | 数量 | 作用 |
| :--- | :--- | :--- | :--- |
| 接入层 | HAProxy | 1 | 负载均衡代理，对外提供访问入口 |
| 应用层 | App（Django） | 2 | Python + Django 写的 Web 应用，处理业务逻辑 |
| 数据层 | Redis-Master | 1 | 主数据库，负责写操作 |
| 数据层 | Redis-Slave | 2 | 从数据库，负责读操作，实现读写分离 |

---

## 二、第一步：获取所有依赖镜像
首先需要从 Docker Hub 拉取基础镜像，命令和结果如下：
```bash
# 拉取基础镜像
sudo docker pull ubuntu
sudo docker pull django
sudo docker pull haproxy
sudo docker pull redis

# 查看已下载的镜像
sudo docker images
```
输出示例：
| REPOSITORY | TAG | IMAGE ID | CREATED | VIRTUAL SIZE |
| :--- | :--- | :--- | :--- | :--- |
| redis | latest | 3b7234aa3098 | 9 days ago | 110.8MB |
| haproxy | latest | 380557f8f7b3 | 9 days ago | 97.91MB |
| django | latest | 8b9d8caadod9 | 9 days ago | 885.8MB |
| ubuntu | latest | 8eaa4ff06b53 | 2 weeks ago | 188.3 MB |

---

## 三、核心原理：`--link` 容器互联
Docker 早期通过 `--link` 参数实现容器间的单向通信，核心原理：
1.  被连接的容器 IP 会被写入到连接容器的 `/etc/hosts` 文件中。
2.  容器内可以直接通过**容器别名**访问对方，无需手动配置 IP。
3.  它是**单向**的：A `--link` B 只能让 A 访问 B，B 无法直接访问 A。

示例命令：
```bash
# 启动 redis-slave1 容器，并连接到 redis-master（别名设为 master）
sudo docker run -it --name redis-slave1 --link redis-master:master redis /bin/bash
```
在 `redis-slave1` 容器内查看 `/etc/hosts`，会看到类似：
```
172.17.0.5 master
172.17.0.6 08df6a2cb468
127.0.0.1 localhost
```
容器内通过 `master` 就能解析到 `redis-master` 的 IP `172.17.0.5`，实现通信。

---

## 四、关键：容器启动顺序与连接关系
根据 `--link` 单向通信的特点，启动顺序必须从底层到上层：
1.  **redis-master**（最先启动，因为所有从节点和应用都要连它）
2.  **redis-slave1 / redis-slave2**（连接到 redis-master）
3.  **App1 / App2**（连接到 redis-master）
4.  **HAProxy**（最后启动，连接到两个 App 节点，并对外暴露端口）

对应的连接关系：
- `redis-slave` → `redis-master`
- `App` → `redis-master`
- `HAProxy` → `App1` + `App2`

---

## 五、完整搭建流程（简化版）
### 1. 启动 redis-master
```bash
sudo docker run -d --name redis-master redis
```

### 2. 启动 redis-slave
```bash
# slave1
sudo docker run -d --name redis-slave1 --link redis-master:master redis
# slave2
sudo docker run -d --name redis-slave2 --link redis-master:master redis
```

### 3. 启动 App 节点（Django 应用）
```bash
sudo docker run -d --name app1 --link redis-master:master django
sudo docker run -d --name app2 --link redis-master:master django
```

### 4. 启动 HAProxy 并对外暴露端口
```bash
sudo docker run -d --name haproxy --link app1:app1 --link app2:app2 -p 80:80 haproxy
```
- `-p 80:80`：将容器的 80 端口映射到宿主机的 80 端口
- 访问 `http://宿主机IP:80` 即可通过 HAProxy 访问整个应用栈

---

## 六、这个案例的核心意义
1.  **理解容器互联**：通过 `--link` 理解容器间如何通信，为后续学习 Docker 网络（Bridge、Overlay、CNI）打下基础。
2.  **体会分层架构**：从数据库 → 应用 → 负载均衡的三层架构，是典型的分布式应用设计。
3.  **掌握容器编排的雏形**：手动控制启动顺序和依赖关系，正是后续 Kubernetes 编排调度的基础思想。

---

💡 补充说明：`--link` 是 Docker 早期的容器互联方式，现在已经不推荐使用了，现代 Docker 更推荐使用 **自定义 Bridge 网络** 来实现容器互联，更安全、更灵活。

---

# 3. 应用栈容器节点启动 + 4. 应用栈容器节点配置（完整精简总结）
这部分是**全书第一个完整实战案例**，核心是：**用6个容器搭一套可访问的 Web 应用栈**，包含 Redis 主从、Django Web、HAProxy 负载均衡。

---

## 一、容器节点启动（命令 + 顺序 + 说明）
### 启动顺序（必须严格按这个来，因为 --link 单向依赖）
1. **redis-master**
2. **redis-slave1 / redis-slave2**
3. **APP1 / APP2**
4. **HAProxy**（最后启动，对外暴露端口）

### 启动命令汇总
```bash
# 1. 启动 Redis 主节点
docker run -it --name redis-master redis /bin/bash

# 2. 启动 Redis 从节点（连接主库）
docker run -it --name redis-slave1 --link redis-master:master redis /bin/bash
docker run -it --name redis-slave2 --link redis-master:master redis /bin/bash

# 3. 启动 Django 应用（挂载目录 + 连接 Redis）
docker run -it --name APP1 --link redis-master:db \
  -v ~/Projects/Django/App1:/usr/src/app django /bin/bash

docker run -it --name APP2 --link redis-master:db \
  -v ~/Projects/Django/App2:/usr/src/app django /bin/bash

# 4. 启动 HAProxy（连接两个APP + 端口映射 + 挂载目录）
docker run -it --name HAProxy \
  --link APP1:APP1 --link APP2:APP2 \
  -p 6301:6301 \
  -v ~/Projects/HAProxy:/tmp haproxy /bin/bash
```

### 关键说明
- 全部用 `/bin/bash` 启动，方便进入容器交互配置。
- `--link`：容器间单向通信，自动写入 hosts，不用写死 IP。
- `-v`：宿主机与容器目录共享，**在宿主机编辑文件，容器内直接生效**。
- `-p 6301:6301`：HAProxy 对外暴露端口，外部可访问。

---

## 二、容器节点配置（分四部分，最核心步骤）
### 1）Redis Master 配置
1. 查看数据卷路径：
```bash
docker inspect --format "{{ .Volumes }}" redis-master
```
2. 在宿主机编辑 `redis.conf`：
```ini
daemonize yes
pidfile /var/run/redis.pid
```
3. 复制到容器并启动：
```bash
cd /data
cp redis.conf /usr/local/bin
redis-server redis.conf
```

### 2）Redis Slave 配置
与主库几乎一样，只多一行：
```ini
slaveof master 6379
```
- `master` 来自 `--link redis-master:master`，自动解析 IP。

### 3）Redis 主从测试
```bash
# 主库写入
redis-cli set master hello

# 从库读取（能读到表示主从同步成功）
redis-cli get master
```

---

### 4）APP（Django）节点配置
1. 容器内安装 Redis 依赖：
```bash
pip install redis
```
2. 创建 Django 项目：
```bash
django-admin.py startproject redisweb
python manage.py startapp helloworld
```
3. 在宿主机修改代码（利用 `-v` 共享目录）：
- `views.py`：连接 Redis、读写数据、返回页面
- `settings.py`：注册 `helloworld` 应用
- `urls.py`：绑定 URL `/helloworld` 到视图

4. 初始化 Django：
```bash
python manage.py migrate
python manage.py syncdb
```

5. 启动 Web 服务：
```bash
# APP1 用 8001，APP2 用 8002
python manage.py runserver 0.0.0.0:8001
```

---

### 5）HAProxy 配置（负载均衡）
1. 在宿主机编辑 `haproxy.cfg`：
- 监听 `6301`
- 后端转发到 `APP1:8001`、`APP2:8002`
- 开启统计页面 `/haproxy-stats`

2. 容器内启动：
```bash
cp /tmp/haproxy.cfg /usr/local/sbin/
haproxy -f haproxy.cfg
```

---

## 三、访问方式（最终效果）
1. **外部访问应用（通过 HAProxy）**
```
http://宿主机IP:6301/helloworld
```
2. **HAProxy 监控页面**
```
http://宿主机IP:6301/haproxy-stats
```
3. 自动负载均衡到 APP1 / APP2。

---

## 四、你提供的两个报错说明（无法访问页面）
- `http://0.0.0.0:8001/`
- `http://172.17.0.9:6301/haproxy-stats`

报错：**网页解析失败**
原因：
1. 这是书里**早期老旧版本**的案例（Docker 1.10 + Django 1.7 + 老 HAProxy），环境不兼容。
2. 现在的系统/浏览器无法直接解析这种旧式 HTTP 响应。
3. 容器网络、端口映射、服务是否正常启动都会导致无法访问。

✅ **重点不在跑通页面，而在掌握这套流程**：
`镜像 → 容器启动顺序 → --link 互联 → volume 共享文件 → 主从配置 → 应用部署 → 负载均衡`

---

## 五、极简记忆版（考试/复习专用）
1. **6 容器**：1主2从Redis + 2个Django + 1个HAProxy
2. **顺序**：Redis主 → 从 → APP → HAProxy
3. **互联**：--link 容器名:别名，自动写 hosts
4. **共享文件**：-v 宿主机目录:容器目录，在外面改文件
5. **作用**：Redis 主从同步 + Django Web + HAProxy 负载均衡
6. **入口**：宿主机 6301 端口访问整个应用栈

需要我把这一节整理成**一页纸背诵版**吗？当前文件内容过长，豆包只阅读了前 28%。