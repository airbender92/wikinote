# 一：检查本地是否安装 Nginx

## Windows

### 方式1：命令行

打开 cmd / PowerShell

```powershell
nginx -v
```

- 输出版本号 → 已安装
- `'nginx' 不是内部或外部命令` → 没装，或者没加到环境变量

---

### 二：Windows查看Nginx在哪个目录

1. **CMD终端 → where**（等价linux which）

```cmd
where nginx
```

> 只搜 `PATH环境变量` 里面的程序，**没加到环境变量的nginx查不到**（绝大多数Windows解压版nginx查不到）。

---

# 三：进入nginx根目录

nginx.exe路径：`D:\wybD\appInstaller\nginx\nginx.exe`
👉 **nginx根目录就是：`D:\wybD\appInstaller\nginx`**
配置文件就在根目录下 `conf\nginx.conf`

进入nginx根目录
打开 cmd / PowerShell

```powershell
cd D:\wybD\appInstaller\nginx
```

---

# 四：列出目录文件：

PowerShell / CMD：

```powershell
cd D:\wybD\appInstaller\nginx
dir
```

PowerShell 也可以用 ls（linux风格别名）

```powershell
cd D:\wybD\appInstaller\nginx
ls
```

执行后你会看到这些关键文件夹：

- conf 👉 **配置文件夹，nginx.conf在这里**
- html 默认静态页面目录
- logs 日志 access.log error.log
- nginx.exe 主程序

接下来打开配置：

```powershell
notepad conf\nginx.conf
```

改完务必校验：

```powershell
nginx -t
```

成功再 reload

```powershell
nginx -s reload
```

---

# 五：Nginx常用命令

# Windows Nginx 常用命令

> 注意：**CMD 需要先切换到 nginx根目录 `D:\wybD\appInstaller\nginx`**；PowerShell可直接cd完整路径执行

## 基础操作

```powershell
# 启动nginx
start nginx

# 优雅重载配置（不中断现有连接，修改配置后用，必须先 nginx -t校验）
nginx -s reload

# 快速停止（强制关闭，立刻断开连接）
nginx -s stop

# 优雅停止，处理完现有连接再关闭
nginx -s quit
```

## 配置检查、查看配置

```powershell
# 校验配置语法，同时打印当前生效配置文件路径【必执行！】
nginx -t

# 大写T，输出合并展开全部配置(所有include引入的子配置全部打印)，排错神器
nginx -T

# 查看nginx版本
nginx -v
nginx -V #大写V，查看编译参数
```

## 进程排查

```powershell
# CMD查看nginx进程
tasklist | findstr nginx

# PowerShell查看nginx进程
Get-Process nginx
```

## 文件操作（在nginx根目录）

```powershell
# 查看目录
dir

#记事本打开主配置
notepad conf\nginx.conf

# 查看错误日志
notepad logs\error.log

# 查看访问日志
notepad logs\access.log
```

## Windows踩坑要点

1. CMD环境，**cd D:\xxx不会切换盘符，要先输入 D:**
2. 修改配置后，**一定要 nginx -t，成功再 reload**；语法错误reload会直接启动失败
3. windows配置里路径用 `/` 斜杠，不要 `\` 反斜杠，会转义报错

```nginx
root D:/wybD/test; # ✔正确
root D:\wybD\test; # ❌错误
```

4. `nginx -s reload` 需要nginx已经处于运行状态，如果进程没启动，reload会报错，直接用`start nginx`启动

## 完整实操流程模板

```powershell
#1.进入目录
cd D:\wybD\appInstaller\nginx
#2.编辑配置
notepad conf\nginx.conf
#3.校验语法
nginx -t
#4.重载生效
nginx -s reload
```

### 常见报错

- `nginx: error while loading configuration file` → 配置语法错误，看报错行号去修改
- `[error] CreateFile() "xxx\nginx.pid" failed` → nginx没有启动，不要用reload，执行start nginx
- 端口占用：看error.log，`bind() to 0.0.0.0:80 failed`，80端口被别的程序占用，改监听端口或者关闭占用程序。

---

# Windows Nginx （cmd执行 start nginx）

> 注意：cmd**必须以管理员运行**，否则容易启动静默失败，没报错但是进程起不来

## 1. 启动

```cmd
# 进入nginx解压根目录
cd D:\nginx
start nginx
```

## 2. 判断是否启动成功（3种方法）

### 方法1：查看进程（最常用）

```cmd
tasklist | findstr nginx
```

✅成功：输出2个进程

```
nginx.exe      1234 Console                    1     12,345 K
nginx.exe      5678 Console                    1      8,900 K
```

> master主进程 + worker工作进程，两个才正常。
> 如果**什么都没有输出=启动失败**

### 方法2：访问页面

浏览器打开：`http://127.0.0.1`
出现 Nginx 欢迎页面，代表完全正常。

### 方法3：查看监听端口

```cmd
netstat -ano | findstr :80
```

看到nginx的PID占用80端口就是正常。

## 3. 配置校验（启动失败必执行）

```cmd
nginx -t
```

- `test is successful`：配置没问题
- 报红色：conf配置写错，按提示修改

## 4. Windows nginx常用命令（在nginx根目录执行）

```cmd
start nginx          # 启动
nginx -s stop        # 快速停止（强制杀掉进程）
nginx -s quit        # 优雅停止，处理完现有连接再退出
nginx -s reload      # 修改conf后重载配置，不用重启服务
nginx -t             # 测试配置文件语法
```

## 5. 启动失败去哪里看报错

日志路径：`nginx目录\logs\error.log`
常见坑：

1. **80端口被别的程序占用（如IIS、迅雷、其他web）** → error.log会报 bind() to 0.0.0.0:80 failed
2. cmd没管理员权限，start nginx执行完无任何输出，但进程没起来
3. conf里面路径写反斜杠 `\` 需要转义写成 `\\` 或者用 `/`

---

# 五. 修改nginx配置

## 关键点

nginx 的 `root` 指令写**完整绝对路径**就可以，Windows路径用**正斜杠 `/`**，不要反斜杠`\`。

举例：你的项目在

```
D:\code\web-demo\www
        └ index.html
```

那么 nginx.conf 里面 root 直接写：

```nginx
root   D:/code/web-demo/www;
```

> ⚠ Windows nginx坑：路径不要写 `D:\code\web-demo\www`，`\` 在配置文件是转义字符，会解析错乱。统一用 `/`。

### 完整server示例，项目不在nginx目录

```nginx
server {
    listen       80;
    server_name  localhost;

    # 静态目录：指向你自己项目的www，不在nginx文件夹内
    root   D:/code/web-demo/www;
    index  index.html index.htm;

    # /api 反向代理转发给 node 3000
    location /api/ {
        proxy_pass http://127.0.0.1:3000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # history路由，刷新404
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

### 修改配置之后必做两步（管理员cmd，进入nginx安装目录执行）

```cmd
nginx -t
nginx -s reload
```

## 两种路径写法都合法

1. 绝对路径（推荐，项目放任意位置）

```nginx
root D:/code/web-demo/www;
```

2. 相对路径：**相对nginx程序所在目录**，不推荐Windows使用，很容易搞混。

> 比如写 `root ./html;`，这个`./`指的是**nginx.exe所在目录**，不是conf目录。

## 举个现实例子

- Nginx安装位置：`D:\soft\nginx`
- 你的前端项目：`D:\workspace\demo\www\index.html`

conf里面直接写：

```nginx
root D:/workspace/demo/www;
```

跟 D:\soft\nginx 完全互不干涉。

## 排错：报403 Forbidden

Windows偶尔出现403：

1. 文件夹权限问题，文件夹不要放在需要管理员保护的目录，比如`C:\Windows`；放D盘普通目录最稳。
2. 确认 `root` 路径是到**www这一层**，不是到index.html。
   ✅正确：`root D:/workspace/demo/www;`
   ❌错误：`root D:/workspace/demo/www/index.html;`

> root指向**文件夹**，不是html文件。index指令指定默认文件index.html。

---
