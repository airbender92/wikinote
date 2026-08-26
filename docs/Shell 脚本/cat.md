# cat

`cat` 是 **Linux / Shell（.sh脚本）** 的命令，Windows cmd**原生没有cat**。

## 作用

> cat = concatenate，读取整个文件内容，输出打印到终端

```bash
# 打印整个文件到屏幕
cat error.log

# 把文件内容输出到另一个文件（覆盖）
cat a.txt > b.txt

# 拼接两个文件
cat 1.txt 2.txt > all.txt
```

### 常用示例（Linux）

```bash
# 查看nginx错误日志
cat /var/log/nginx/error.log

# 看配置文件
cat nginx.conf
```

## Windows 对应等价命令

1. **CMD**：`type`

```cmd
:: cmd 等价 cat，打印文件内容
type logs\error.log
```

2. **PowerShell**：`Get‑Content`，别名 `cat`

```powershell
# PowerShell里面可以直接写cat
cat logs\error.log
```

> ⚠注意：只有PowerShell支持cat，普通cmd不识别cat。

## 对比表

| 环境                 | 查看文件全部内容命令                |
| -------------------- | ----------------------------------- |
| Linux Shell / sh脚本 | `cat 文件名`                        |
| Windows CMD          | `type 文件名`                       |
| Windows PowerShell   | `cat 文件名` / `Get‑Content 文件名` |

### 补充几个Linux查看文件命令，教程里经常出现

```bash
cat       # 一次性全部输出，适合小文件
more      # 分页，按空格翻页，q退出
less      # 分页查看，上下键滚动，q退出
tail -f   # 实时跟踪日志（最常用！看nginx、服务动态日志）
```

`tail -f logs/access.log` 实时滚动打印日志，开发调试神器。

> Windows没有tail‑f；PowerShell对应：

```powershell
Get‑Content logs\access.log -Wait
```

## 容易踩坑

网上Nginx、后端部署教程大量写 `cat nginx.conf`，这是**Linux命令**。
你Windows cmd不要敲 `cat nginx.conf`，会报 `'cat' 不是内部或外部命令`。
Windows cmd查看配置用：

```cmd
type conf\nginx.conf
```

### 小结

- `cat`：Linux，输出文件全部内容。
- cmd用 `type`；PowerShell才可以用`cat`。
- 实时看日志 Linux：`tail -f 文件`；PowerShell：`Get‑Content xxx -Wait`。

> 顺带复习前面：
> echo → 打印文字；cat → **打印文件内容**。

如果你需要，我把常见linux命令和windows cmd等价命令整理一张小清单。
