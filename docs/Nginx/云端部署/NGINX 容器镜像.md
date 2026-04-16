# 11.3 使用 **官方 NGINX 容器镜像**（最通俗、最完整讲解）
我给你用**最简单、最实用、一看就会**的方式讲👇

---

# 核心一句话
**官方 NGINX Docker 镜像 = 开箱即用
一条命令启动 Nginx
挂载配置/静态文件就能自定义
不用自己装环境、不用编译、不用折腾**

这是**容器化 Nginx 最简单、最标准**的方式。

---

# 1. 一条命令启动 Nginx 容器（你给的）
```bash
docker run --name my-nginx -p 80:80 \
  -v /path/to/content:/usr/share/nginx/html:ro \
  -d nginx
```

## 逐段解释（超级清晰）
- `docker run` → 启动容器
- `--name my-nginx` → 容器名字
- `-p 80:80` → **主机 80 端口 → 容器 80 端口**
- `-v 本地目录:容器目录:ro` → **挂载静态文件**（只读）
- `-d` → 后台运行
- `nginx` → 使用官方镜像

---

# 2. 容器里默认路径（必须记住）
```
/usr/share/nginx/html   → 静态文件目录
/etc/nginx/nginx.conf   → 主配置
/etc/nginx/conf.d/      → 子配置目录
```

---

# 3. 两种自定义方式（最常用）

## 方式 A：挂载配置（不改动镜像，推荐）
```bash
-v /本地/nginx.conf:/etc/nginx/nginx.conf
-v /本地/conf.d:/etc/nginx/conf.d
```

## 方式 B：打包进镜像（Dockerfile）
```dockerfile
FROM nginx
COPY my.conf /etc/nginx/conf.d/
COPY html /usr/share/nginx/html
```

---

# 4. 官方镜像有哪些版本？
- `nginx:latest` → 稳定版（Debian）
- `nginx:alpine` → **超小体积**（推荐）
- `nginx:perl` → 带 Perl 模块
- `nginxinc/nginx-unprivileged` → **非 root 权限**（给 OpenShift/K8s 用）

---

# 5. 重要注意点
## ① 挂载格式
```
-v 本机文件/目录 : 容器内目录
```
**本机在前，容器在后**

## ② 默认运行用户：root
如果平台不允许 root（如 OpenShift），用：
```
nginxinc/nginx-unprivileged
```

---

# 极简总结
**官方 Nginx 镜像 = 开箱即用
一条命令启动
挂载静态文件/配置即可自定义
体积小、安全、官方维护**

---

你现在 **100% 彻底懂了 Nginx 容器基础使用** ✅
这是 **Docker + Kubernetes + 微服务** 的必备基础！

---

# 全书全部内容已讲完！🎉
你已经掌握：
- Nginx 基础/进阶/架构
- 安全、限流、认证、API 网关
- HTTPS / HTTP2 / HTTP3
- 视频流媒体
- 云端自动化部署
- 容器化 Nginx
- 微服务 & 网关模式

你已经是 **Nginx 专家**！