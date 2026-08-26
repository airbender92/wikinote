# `nginx -g "daemon off;"`

这是 **Docker容器跑Nginx的标准固定写法**，几乎所有nginx镜像的入口脚本最后都是这句。

## 拆解命令

```
nginx -g "daemon off;"
```

1. `nginx`：启动nginx主程序
2. `-g`：nginx参数，**临时执行全局指令**，生效范围是本次启动，不用修改nginx.conf文件
3. `daemon off;`
   - 默认nginx：`daemon on`，后台守护进程模式；master进程脱离终端，放到后台运行。
   - `daemon off`：**关闭守护进程，前台运行**，nginx master进程绑定当前shell终端，占据前台。

---

## 为什么Docker里面必须写 `daemon off;`

> Docker容器规则：**容器存活，依赖PID 1进程前台运行**。PID1进程退出 → 容器直接停止。

### 如果写普通的 `start nginx`（daemon on，后台模式）

1. shell脚本执行 `nginx`，nginx master跑到后台。
2. shell脚本执行完毕，shell（PID1）直接退出。
3. PID1结束，Docker认为程序全部结束 → **容器立刻停止退出**，即使nginx后台还在跑，容器照样死掉。

### 使用 `nginx -g "daemon off;"`

1. nginx master进程留在**前台，接管PID1**。
2. shell脚本执行这句之后，**这里会阻塞，不会往下执行，不会退出脚本**。
3. nginx进程存活，容器就保持运行。
4. 如果nginx异常崩溃退出，PID1消失 → 容器跟着退出，符合docker设计。

> Windows的nginx不要写这个；Windows直接`start nginx`后台跑。`daemon off`在Windows也能用，但cmd一关nginx就结束。

## sh脚本完整的典型结尾

```
# 前面cat <<EOF动态生成配置……

# 校验配置
nginx -t

# 前台启动nginx，阻塞在这里，脚本不会跑完退出
exec nginx -g "daemon off;"
```

### 额外：`exec` 关键字

经常看到：

```
exec nginx -g "daemon off;"
```

`exec` 的作用：**用nginx进程直接替换当前shell进程（PID1直接变成nginx）**，不再保留shell进程。

- 不加exec：PID1是bash，nginx是子进程；bash如果收到信号，转发可能有问题。
- 加exec：PID1直接是nginx master，容器信号（stop/kill）直接交给nginx，优雅关闭生效。>

> Docker最佳实践，推荐带上`exec`。

## 完整流程复盘（Docker nginx入口脚本）

```
CMD ["/run.sh"]
```

run.sh：

1. 读取Docker环境变量 `$BACKEND_URL`
2. `cat >> <<EOF` 渲染生成nginx配置，注意nginx变量要写`\$host`转义
3. `nginx -t`校验配置语法
4. `exec nginx -g "daemon off;"` 前台启动，**脚本阻塞在这里，不会结束**

### 两个daemon模式对比

| 模式         | 命令                     | 适用场景                          | 效果                         |
| ------------ | ------------------------ | --------------------------------- | ---------------------------- |
| 守护后台模式 | `nginx`(默认daemon on)   | 物理机/虚拟机Linux，Windows nginx | 放到后台，终端可以继续敲命令 |
| 前台模式     | `nginx -g "daemon off;"` | **Docker容器**                    | 占用前台，PID1，容器不会退出 |

## 容易踩坑

1. 如果你在普通虚拟机Linux直接敲 `nginx -g "daemon off;"`，当前终端被占死，按`Ctrl+C`，nginx直接停止。
2. 脚本中 `daemon off;` **分号不能丢**，属于nginx配置语法。
3. Windows不要照搬 `-g "daemon off;"`，本地开发直接用`start nginx`。

## 串联你前面全部知识点

1. Docker启动执行CMD的sh脚本
2. sh读取docker环境变量`$BACKEND_URL`（shell变量）
3. `cat >> <<EOF`，bash替换shell变量；nginx内置`\$host`转义，原样写入conf
4. 生成完成nginx配置文件
5. `nginx -t`校验
6. `exec nginx -g "daemon off;"` 前台启动nginx作为PID1，容器保持运行。

> 区分记忆：
>
> - shell脚本里：`$VAR` shell变量，`\$host` 转义输出`$host`文本给nginx
> - nginx conf文件内：`$host` nginx内置变量，请求阶段求值
> - docker：必须`daemon off`前台运行；物理机：默认后台daemon on。

如果你需要我可以写一份最小可运行的完整Dockerfile+run.sh示例。
