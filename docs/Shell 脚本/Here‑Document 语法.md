# `cat >> <<EOF`

这是 **Shell（bash）的 Here‑Document 语法**，只在 `.sh` / Linux 环境使用，Windows cmd**完全不支持**。

## 完整格式

```
cat >> 输出文件名 <<EOF
这里写多行文本
第二行
第三行
EOF
```

### 拆解每一部分

1. `cat`：读取输入
2. `>>`：**追加**到文件（> 是覆盖，>> 追加）
3. `<<EOF`：**Here‑Doc 开始标记**，EOF只是约定标记名字，可以换成别的如 `END`
4. 中间所有行，原样写入文件，支持换行
5. 单独一行 `EOF`：结束标记，**顶格写，前面不能有空格**

> ⚠结束的 `EOF` 必须独占一行，前面不能空格，否则识别不到结束。

## 示例1：追加内容到 nginx.conf

```
cat >> nginx.conf <<EOF
server {
    listen 8080;
}
EOF
```

含义：把 `server{...}` 这段配置**追加写到 nginx.conf 文件末尾**。

## 示例2：覆盖（把 >> 改成 >）

```
cat > test.txt <<EOF
第一行
第二行
EOF
```

`cat >`：**覆盖原有文件**，文件旧内容全部清空再写入。

## 变量替换

默认会解析shell变量：

```
port=3000
cat > app.conf <<EOF
port=$port
EOF
```

生成文件内容：`port=3000`

如果不想解析变量，原样输出 `$`，给开始标记加引号 `'EOF'`

```
cat > app.conf <<'EOF'
port=$port
EOF
```

文件原样保存 `port=$port`，不做变量替换。

## 常见真实场景

自动化脚本一键生成配置文件。
linux一键写nginx配置、写systemd服务文件经常看到这一套。

```
# 脚本示例 create_nginx.sh
#!/bin/bash
cat > /etc/nginx/conf.d/app.conf <<EOF
server {
    listen 80;
    location /api/ {
        proxy_pass http://127.0.0.1:3000;
    }
}
EOF
nginx -t
nginx -s reload
```

## ⚠对你 Windows 的提示

- `cat >> <<EOF` **Windows cmd不支持**，不要复制到cmd运行。
- Windows 如果要多行写入文件，用bat或者powershell。

PowerShell等价实现类似 Here‑Doc：

```
@'
server {
  listen 80;
}
'@ | Out‑File app.conf -Append
```

## 易混点小结

| 语法                | 作用                         |
| ------------------- | ---------------------------- |
| `cat >> file <<EOF` | **追加**多行文本到文件       |
| `cat > file <<EOF`  | **覆盖**，重建文件写入多行   |
| `<<'EOF'`           | 关闭变量解析，原样输出$符号  |
| 结尾`EOF`           | 必须独占一行顶格，不能有空格 |

> 很多网上部署教程用这个语法一键生成nginx配置，这是linux脚本技巧，**Windows Nginx不能照搬这一套**。Windows就手动编辑conf文件。

如果你需要，我可以整理一份高频shell符号速记：`> >> << < | $ '' "" `。
