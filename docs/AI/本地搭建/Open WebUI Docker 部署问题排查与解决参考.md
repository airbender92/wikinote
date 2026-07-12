下面整理成一份可保存的参考文档，记录这次 **Open WebUI Docker 部署无法访问问题及解决方法（包含 Hugging Face Token 配置方法）**。

---

# Open WebUI Docker 部署问题排查与解决参考

## 一、问题现象

使用 Docker 部署：

```text
ghcr.io/open-webui/open-webui:main
```

容器启动日志显示正常：

```text
INFO: Started server process [1]
INFO: Waiting for application startup.
```

Embedding 模型开始加载：

```text
Loading SentenceTransformer model
sentence-transformers/all-MiniLM-L6-v2
```

但是浏览器访问：

```
http://localhost:3000
```

无法打开 Open WebUI 页面。

---

# 二、问题排查过程

## 1. 查看 Docker 容器状态

执行：

```powershell
docker ps
```

发现：

错误端口映射：

```
PORTS

0.0.0.0:3000->7860/tcp
```

说明：

```
Windows 主机:
3000

↓

Docker 容器:
7860
```

但是 Open WebUI 默认 Web 服务端口不是 7860。

---

## 2. 检查容器环境变量

执行：

```powershell
docker inspect open-webui --format='{{json .Config.Env}}'
```

发现：

```
PORT=8080
```

说明 Open WebUI 实际监听：

```
8080
```

因此端口关系应该：

```
浏览器
 |
 | localhost:3000
 |
Docker
 |
容器:8080
```

而不是：

```
容器:7860
```

---

# 三、解决方法

## 重新创建 Docker 容器

### 1. 停止旧容器

```powershell
docker stop open-webui
```

---

### 2. 删除旧容器

```powershell
docker rm open-webui
```

注意：

删除的是容器，不会删除 Docker Volume 数据。

如果之前使用：

```
-v open-webui:/app/backend/data
```

则以下数据仍然保留：

* 用户账号
* 聊天记录
* 设置
* 知识库数据

---

### 3. 使用正确端口重新启动

```powershell
docker run -d `
  -p 3000:8080 `
  -v open-webui:/app/backend/data `
  --name open-webui `
  --restart always `
  ghcr.io/open-webui/open-webui:main
```

---

## 4. 验证端口

执行：

```powershell
docker ps
```

正确结果：

```
PORTS

0.0.0.0:3000->8080/tcp
```

说明：

```
宿主机3000
       |
       |
容器8080
```

---

# 四、启动后的 Hugging Face 模型问题

启动日志：

```
HTTP Request:
GET https://huggingface.co/api/models/
sentence-transformers/all-MiniLM-L6-v2
HTTP/1.1 200 OK
```

说明：

* Open WebUI 可以访问 Hugging Face
* 正在下载 Embedding 模型
* 网络正常

出现：

```
Warning:
You are sending unauthenticated requests to the HF Hub.
Please set a HF_TOKEN
```

原因：

当前使用匿名访问 Hugging Face。

影响：

| 项目           | 是否影响 |
| ------------ | ---- |
| Open WebUI启动 | 否    |
| 模型下载         | 可以   |
| RAG功能        | 可以   |
| 下载速度         | 可能较慢 |
| 请求限制         | 较低   |

---

# 五、方法一：配置 Hugging Face Token（推荐）

## 1. 创建 Hugging Face Token

访问：

```
https://huggingface.co/settings/tokens
```

登录账号。

创建 Token：

权限：

```
Read
```

生成：

例如：

```
hf_xxxxxxxxxxxxxxxxx
```

复制保存。

---

## 2. 添加 HF_TOKEN 到 Docker

删除旧容器：

```powershell
docker stop open-webui

docker rm open-webui
```

重新启动：

```powershell
docker run -d `
  -p 3000:8080 `
  -v open-webui:/app/backend/data `
  -e HF_TOKEN=你的token `
  --name open-webui `
  --restart always `
  ghcr.io/open-webui/open-webui:main
```

---

## 3. 验证

查看日志：

```powershell
docker logs open-webui --tail 50
```

不再出现：

```
unauthenticated requests
```

---

# 六、RAG 功能说明

当前环境：

```
ENABLE_RAG=false
```

表示：

RAG 功能关闭。

如果需要：

* PDF 文件问答
* Word 文档分析
* 知识库搜索
* 企业资料库

需要修改：

```
ENABLE_RAG=true
```

---

# 七、最终正确部署状态

检查：

```powershell
docker ps
```

应该看到：

```
IMAGE:
ghcr.io/open-webui/open-webui:main


PORTS:
0.0.0.0:3000->8080/tcp


STATUS:
healthy
```

浏览器：

```
http://localhost:3000
```

即可进入 Open WebUI。

---

# 八、本次问题总结

| 问题                   | 原因               | 解决                |
| -------------------- | ---------------- | ----------------- |
| localhost:3000 无法访问  | Docker 映射错误      | 7860 改为 8080      |
| Open WebUI日志正常但网页打不开 | 服务端口不匹配          | 修改 `-p 3000:8080` |
| HuggingFace警告        | 未登录HF            | 设置 `HF_TOKEN`     |
| RAG不可用               | ENABLE_RAG=false | 开启RAG             |

---

**核心记忆点：**

Open WebUI Docker 默认：

```
容器端口：8080
```

推荐映射：

```
Windows:3000 → Container:8080
```

启动参数：

```bash
-p 3000:8080
```

这是本次故障的关键。
