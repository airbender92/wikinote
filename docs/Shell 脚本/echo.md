# echo

`echo` 是**终端输出打印命令**，不同环境都有echo，但语法略有区别。

## 1、Linux / shell(.sh脚本) 里的 echo

作用：打印文字到控制台。

```bash
echo "hello world"
echo 12345
```

运行输出：

```
hello world
12345
```

sh脚本示例 test.sh

```bash
#!/bin/bash
echo "===开始启动服务==="
echo "当前时间: $(date)"
```

### shell echo常用

```bash
# 打印变量
name="张三"
echo $name

# 输出到文件（覆盖）
echo "内容" > a.txt

# 追加写入文件
echo "追加内容" >> a.txt
```

## 2、Windows CMD 里面的 echo（你现在用的环境）

cmd也有echo命令，功能一样。

```cmd
echo hello world
echo 123
```

cmd：

```cmd
@echo off          # 关闭命令本身回显，bat脚本第一行经常写
echo 测试输出 > test.txt
echo 追加文本 >> test.txt
```

> 注意：cmd里面变量用 `%var%`，不是`$var`

```cmd
set name=abc
echo %name%
```

## 3、Node.js 里面没有 echo

node中打印用 `console.log()`，**不是echo**

```javascript
console.log("输出日志");
```

## 4、Nginx 配置里没有echo！

> nginx.conf **不能直接写 echo**。
> nginx想要输出文本，用 `return`，比如调试location：

```nginx
location /debug {
    return 200 "remote_addr=$remote_addr";
}
```

## 快速区分记忆

| 环境               | 打印输出             | 变量符号       |
| ------------------ | -------------------- | -------------- |
| Linux shell / .sh  | `echo "xxx"`         | `$变量`        |
| Windows cmd / .bat | `echo xxx`           | `%变量%`       |
| Node js            | `console.log("xxx")` | `let a` js语法 |
| Nginx conf         | `return 200 "text"`  | `$变量`        |

### 实操小例子

#### linux‑sh

```bash
echo "启动nginx"
nginx -t
```

#### windows‑bat（等价功能）

```bat
@echo off
echo 启动nginx
nginx -t
pause
```

> 你之前看的 nginx linux教程大量出现 `echo`，那是shell脚本，Windows cmd也有echo，但写法不完全通用。

如果你需要，我给你写一个 windows的 start.bat，一键启动nginx+node。
