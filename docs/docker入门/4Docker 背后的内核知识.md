# 3.1 Docker 背后的内核知识（核心精简总结）
## 一、Docker 容器本质
Docker 容器**本质就是宿主机上的普通进程**，靠 3 大内核技术实现：
1. **Namespace**：资源隔离（看起来像独立系统）
2. **Cgroups**：资源限制（CPU、内存、IO 配额）
3. **Copy-on-write**：镜像分层、高效文件操作

---

# 3.1.1 Namespace 资源隔离（必考重点）
## 一、Namespace 作用
让容器里的进程**以为自己独占一套系统**，看不见外部进程和资源，实现环境隔离。

## 二、6 大 Namespace 完整表格（必须背）
| Namespace | 系统调用参数 | 隔离内容 |
|---|---|---|
| UTS | CLONE_NEWUTS | 主机名、域名 |
| IPC | CLONE_NEWIPC | 信号量、消息队列、共享内存 |
| PID | CLONE_NEWPID | 进程编号 PID |
| Network | CLONE_NEWNET | 网络设备、栈、端口、IP |
| Mount | CLONE_NEWNS | 文件系统挂载点、根目录 |
| User | CLONE_NEWUSER | 用户 ID、用户组 ID、权限 |

---

## 三、Namespace 4 种操作 API
1. **clone()**
   - 创建**新进程 + 新 Namespace**
   - Docker 创建容器**最核心调用**

2. **/proc/[pid]/ns**
   - 查看进程所属 Namespace
   - 文件描述符存在，Namespace 就不会销毁

3. **setns()**
   - 加入**已存在**的 Namespace
   - `docker exec` 进入容器的原理

4. **unshare()**
   - 在**原进程**上创建隔离，不新建进程
   - Docker 目前**未使用**

---

## 四、6 大 Namespace 极简理解
### 1. UTS Namespace
- 隔离：**主机名 hostname**
- 每个容器可以有自己独立主机名，不影响宿主机。

### 2. IPC Namespace
- 隔离：**进程间通信资源**
- 容器内信号量、消息队列对外不可见。

### 3. PID Namespace
- 隔离：**进程号 PID**
- 容器内看到 PID 从 1 开始（init 进程）
- 外部看是普通进程，内部看是系统根进程

### 4. Network Namespace
- 隔离：**网卡、IP、端口、路由、防火墙**
- 每个容器有独立网络栈，端口不冲突。

### 5. Mount Namespace
- 隔离：**文件系统挂载、根目录 /**
- 容器有独立根文件系统，类似 chroot 增强版。

### 6. User Namespace
- 隔离：**UID、GID、权限**
- 容器内 root ≠ 宿主机 root，提高安全性。

---

## 五、UTS Namespace 示例（书里重点）
- 用 `CLONE_NEWUTS` 创建独立主机名
- 容器内修改 hostname **不影响宿主机**
- 退出容器后宿主机 hostname 不变

---

# 超级精简背诵版
1. Docker 靠 **Namespace 隔离**，**Cgroups 限制**，**写时复制**存储。
2. 6 个 Namespace：**UTS、IPC、PID、Net、Mount、User**。
3. 4 个 API：**clone、setns、unshare、/proc/[pid]/ns**。
4. `clone()` 创建容器，`setns()` 进入容器（exec 原理）。

我帮你把这段 **cgroups 资源限制** 内容，结合四张图做一个结构化、好记的总结👇

---

# 3.1.2 cgroups 资源限制（核心速记）
## 一、cgroups 是什么？
cgroups（Control Groups）是 Linux 内核提供的**资源管理机制**，由 Google 开发，后来并入内核。
- 本质：把进程/线程按组划分，对各组的 CPU、内存、IO 等资源进行**限制、统计、优先级控制**。
- 作用：Docker 用它来实现容器的资源配额，防止单个容器耗尽宿主机资源。

### 四大核心功能
1.  **资源限制**：比如限制容器最多用 1GB 内存，超了就触发 OOM。
2.  **优先级分配**：给关键业务更高的 CPU 时间片或 IO 带宽。
3.  **资源统计**：记录每个组用了多少 CPU、内存、网络流量。
4.  **任务控制**：对进程/线程执行挂起、恢复等操作。

---

## 二、核心概念（必须分清）
| 术语 | 说明 |
|---|---|
| **Task（任务）** | 系统中的进程或线程，是被管理的基本单位。 |
| **Subsystem（子系统）** | 资源调度控制器，比如 CPU、Memory、blkio 等，负责具体的资源控制。 |
| **Cgroup（控制组）** | 按资源规则划分的任务组，包含一组子系统的配置。 |
| **Hierarchy（层级）** | cgroup 的树状结构，一个层级可以附加一个或多个子系统。 |

---

## 三、四大核心规则（对应四张图）
### 规则1：同一个层级可以附加一个或多个子系统

- 说明：一个层级（树）可以同时管理 CPU 和 Memory 等多个资源。
- 例子：图中 `cpu_mem_cg` 同时附加了 CPU 和 Memory 两个子系统，下面的 `cg1` 和 `cg2` 共享这两个资源的配置。

---

### 规则2：一个子系统只能附加到一个层级

- 说明：同一个资源子系统（比如 CPU），只能被附加到**一个层级**上，不能同时属于多个层级。
- 例子：图中 CPU 已经附加到层级 A，就不能再附加到层级 B；而 Memory 已经附加到层级 B，也不能再附加到层级 A。

---

### 规则3：一个任务在同一个层级中，只能属于一个 cgroup

- 说明：进程 `httpd` 在层级 A 中只能加入 `cg1` 或 `cg2` 其中一个；但它可以同时加入层级 B 中的 `cg3`。
- 本质：每个层级是独立的资源维度，任务在不同层级中可以被不同规则管理。

---

### 规则4：子任务默认继承父任务的 cgroup，但可以被移动

- 说明：`httpd` 进程 `fork()` 出子进程时，子进程默认和父进程在同一个 cgroup 中。
- 后续可以手动将子进程移动到其他 cgroup，父子进程的资源管理从此互不影响。

---

## 四、Docker 如何使用 cgroups？
Docker 会为每个容器创建一套独立的 cgroup 层级，每个子系统（CPU、内存等）单独管理，这样：
- 每个容器的资源限制互不干扰。
- 可以通过 `docker run` 参数直接设置资源配额，比如：
  ```bash
  # 限制容器最多用 1 核 CPU 和 512MB 内存
  docker run --cpus=1 --memory=512m nginx
  ```

---

## 五、一句话记忆版
- **Namespace 隔离环境，cgroups 限制资源**。
- 4 个核心概念：`Task`（进程）、`Subsystem`（资源控制器）、`Cgroup`（任务组）、`Hierarchy`（层级树）。
- 4 条核心规则：多子系统、单层级附加、单组任务、子任务可移动。

---

# 3.1.2 cgroups 子系统简介 + Docker 如何使用（精简总结）
这一节是**考试/面试高频考点**，我给你整理成**最清晰、最好背**的版本。

---

## 一、cgroups 子系统是什么
子系统 = **资源控制器**
每种子系统负责控制**一种资源**。

---

## 二、Docker 使用的 9 大子系统（必须背）
1. **blkio**：限制块设备 I/O（磁盘、SSD、USB）
2. **cpu**：限制 CPU 使用
3. **cpuacct**：统计 CPU 使用情况
4. **cpuset**：绑定容器到指定 CPU 核心
5. **devices**：允许/禁止访问设备（如 /dev/sda）
6. **freezer**：挂起 / 恢复进程
7. **memory**：限制内存，触发 OOM
8. **perf_event**：允许对 cgroup 做统一性能测试
9. **net_cls**：给网络包打标签，用于流量控制（**Docker 未直接使用**）

---

## 三、cgroups 如何使用（伪文件系统）
cgroups 是**伪文件系统**，路径固定：
```
/sys/fs/cgroup/
```

进入目录就能看到各个子系统：
```
/sys/fs/cgroup/cpu
/sys/fs/cgroup/memory
/sys/fs/cgroup/blkio
...
```

### 最关键的两个文件
1. **tasks**：把进程 PID 写入 → 加入控制组
2. **cpu.cfs_quota_us**：限制 CPU 使用率

### 示例：限制进程 CPU 为 20%
```bash
# 1. 创建控制组
mkdir /sys/fs/cgroup/cpu/cg1

# 2. 将进程加入组
echo 18828 >> /sys/fs/cgroup/cpu/cg1/tasks

# 3. 限制 CPU 最大 20%
echo 20000 > /sys/fs/cgroup/cpu/cg1/cpu.cfs_quota_us
```

---

## 四、Docker 如何使用 cgroups（核心）
Docker 会**自动创建 cgroup 目录结构**：
```
/sys/fs/cgroup/cpu/docker/[容器ID]/
/sys/fs/cgroup/memory/docker/[容器ID]/
...
```

规则：
1. 每个容器**独立 cgroup**
2. 容器所有 PID 自动写入 `tasks`
3. `docker run` 指定的资源限制（--memory、--cpus等）自动写入对应文件

---

## 五、一句话超级总结
- **cgroups 子系统 = 资源控制器**
- **9 大子系统：blkio、cpu、cpuacct、cpuset、devices、freezer、memory、perf_event、net_cls**
- **路径：/sys/fs/cgroup**
- **Docker 为每个容器自动创建 cgroup 限制资源**

---

需要我继续为你总结 **3.2 Docker 架构概览** 吗？我可以同样用最精简的方式整理。当前文件内容过长，豆包只阅读了前 25%。

# cgroups 实现方式与工作原理（精简总结）
## 一、工作原理（一句话）
cgroups 本质是给进程**挂钩子**，进程申请资源时触发检查，超过限额就**限制、挂起或杀掉**。

---

## 二、超限额处理规则
- 内存超限额：
  - 开启 OOM：进程直接被杀掉
  - 未开启 OOM：进程挂起睡眠，直到有空闲资源
- **Docker 默认开启 OOM**

---

## 三、cgroups 以“伪文件系统”实现
- 路径：`/sys/fs/cgroup`
- 操作方式：**mkdir 创建组 → echo PID 写入 tasks → echo 值写入配置文件**
- 内核只提供文件接口，无额外系统调用

---

## 四、层级结构规则
- 以**树状结构**组织
- 子 cgroup **继承父配置**，可单独修改
- 挂载后**不能增删子系统**
- 只有**递归卸载**，层级才真正消失

---

## 五、cgroup 目录下必背 4 个文件
1. **tasks**
   写入线程 TID → 加入该控制组
2. **cgroup.procs**
   写入进程 PID → 整个进程的所有线程都加入组
3. **notify_on_release**
   最后一个进程退出时是否触发清理（0/1）
4. **release_agent**
   自动清理脚本路径

---

## 六、Docker 如何使用 cgroups
Docker 自动为每个容器创建目录：
`/sys/fs/cgroup/cpu/docker/容器ID/`
- 自动把容器 PID 写入 tasks
- 自动把 `--memory`、`--cpus` 等参数写入对应配置文件

---

# 极简背诵版
cgroups = 内核钩子 + 伪文件系统
限制资源 → 超量 OOM 杀进程
tasks 写PID，文件写限额
Docker 自动为每个容器建目录管控资源

需要我把 **namespace + cgroups** 合并成一页**考前背诵版**吗？当前文件内容过长，豆包只阅读了前 25%。

![5](/assets/docker/5.jpg)
# 3.2 Docker 架构概览（极简、清晰、可直接背诵）
## 一、整体架构一句话
Docker 采用 **Client-Server（C/S）架构**：
- **Client** 发命令
- **Daemon** 干活
- 后端**松耦合模块化**，各司其职。

---

## 二、核心架构组成（最精简版）
### 1. Docker Client（客户端）
- 作用：接收用户命令（docker run、ps、pull 等），发给 Docker Daemon。
- 本质：命令行工具 + API 调用方。

### 2. Docker Daemon（核心后台进程）
- 是 Docker **大脑**。
- 启动 **API Server** 接收请求。
- 把用户命令分发给各个模块执行。
- 不断解耦，把功能下沉到独立组件。

### 3. 五大核心模块（必须记住）
1. **镜像管理（image management）**
   从 Registry 下载镜像，管理镜像层、元数据。

2. **GraphDriver（存储驱动）**
   管理镜像分层存储（AUFS / Overlay / DeviceMapper）。

3. **ExecDriver（执行驱动）**
   调用 **libcontainer** 真正创建容器。
   libcontainer = 封装 **Namespace + Cgroups**。

4. **Network（网络模块）**
   用 **libnetwork** 管理容器网络。
   网络是**一等公民**，生命周期独立。

5. **Volume（数据卷模块）**
   管理数据持久化。
   数据卷也是**一等公民**，独立生命周期。

---

## 三、Docker 创建容器的完整流程（超清晰）
1. Client 发送 `docker run`
2. Daemon 接收请求
3. 从 Registry **拉取镜像**
4. GraphDriver 准备文件系统
5. ExecDriver → **libcontainer**
6. libcontainer 使用 **Namespace 隔离** + **Cgroups 限制**
7. 创建网络（libnetwork）
8. 挂载 Volume
9. 容器启动完成

---

## 四、最关键结论（考点）
- **libcontainer 是 Docker 容器真正的底层引擎**。
- **Namespace 实现隔离**
- **Cgroups 实现资源限制**
- Volume 和 Network 是**一等公民**，生命周期独立于容器。
- Docker 架构是 **松耦合模块化**，易于扩展。

---

## 五、3.2.1 Docker Daemon 总结
Docker Daemon = 核心进程
- 提供 API Server
- 处理所有请求
- 调度所有模块
- 是整个 Docker 的中控大脑

---

## 六、3.2.2 Docker Client 总结
Docker Client = 用户界面
- 发送命令
- 与 Daemon 通信
- 不干活，只发指令

---

需要我继续为你整理 **3.3 Client 和 Daemon 交互流程** 的超级精简版吗？当前文件内容过长，豆包只阅读了前 23%。