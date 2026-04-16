# 错误：ps命令不存在
```
root@96cd791bddd7:/# ps -ef | grep nginx
bash: ps: command not found
root@96cd791bddd7:/#

```
我来告诉你**为什么报错 + 怎么解决 + 以后怎么用**，10 秒搞定！

# 问题原因
你现在在 **Docker 官方纯净版 Nginx 容器里**
这个镜像**极度精简**，**没有预装 `ps` 命令**，所以报错。

---

# 解决方法（直接复制运行）
在这个 `root@xxx:/#` 提示符下，直接运行：

```bash
apt update && apt install -y procps
```

等待安装完成，再运行你的命令：
```bash
ps -ef | grep nginx
```
就**正常显示**了 ✅

---

# 更简单的方法（不用装任何东西）
Docker 里**查看 Nginx 进程**，官方推荐用这个命令：
```bash
nginx -V
```
或者直接看进程：
```bash
ps aux
```

---

# 你现在只需要做
1. 输入
```bash
apt update && apt install -y procps
```
2. 再输入
```bash
ps -ef | grep nginx
```
就能看到 Nginx 正在运行了。

---

### 小总结
- Docker Nginx 镜像**精简无 ps** → 装个工具就好
- 一条命令就能修复，不影响你学习这本书
- 接下来你可以**正常练配置、负载均衡、缓存**等所有内容

需要我继续带你往下学 Nginx 配置吗？