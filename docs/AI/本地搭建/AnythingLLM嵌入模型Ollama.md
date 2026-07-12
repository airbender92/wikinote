从你的截图看，**DeepSeek-R1.md 已经进入 AnythingLLM 工作区，但是“保存并嵌入（Embed）”一直停在 0%**。这通常不是文档问题，而是 **Embedding（向量化）环节没有正常工作**。

AnythingLLM 的流程：

```
上传文档
   ↓
解析 Markdown/PDF
   ↓
切片 Chunk
   ↓
Embedding模型生成向量  ← 你卡在这里
   ↓
写入向量数据库
   ↓
可以问答
```

现在卡在第 4 步。

---

## 先检查 1：Embedding 模型是否配置

进入：

```
AnythingLLM
↓
设置 Settings
↓
Embedding Preference
```

看你的配置。

如果你是之前搭建的：

```
DeepSeek R1 + Ollama + AnythingLLM
```

那么需要注意：

**DeepSeek R1 不是 Embedding 模型**

它只能聊天推理。

你还需要一个向量模型，例如：

推荐：

```
nomic-embed-text
```

或者中文效果更好的：

```
bge-m3
```

---

## 如果使用 Ollama

打开 CMD：

检查：

```cmd
ollama list
```

应该看到类似：

```
deepseek-r1
nomic-embed-text
```

如果没有：

安装：

```cmd
ollama pull nomic-embed-text
```

或者：

```cmd
ollama pull bge-m3
```

---

然后 AnythingLLM：

设置：

```
Embedding Model
```

选择：

```
ollama
```

模型：

```
nomic-embed-text
```

保存。

---

## 检查 2：Ollama 是否运行

CMD：

```cmd
ollama ps
```

正常：

```
NAME              STATUS
deepseek-r1       running
```

如果 Ollama 服务没启动：

```cmd
ollama serve
```

保持窗口不要关闭。

---

## 检查 3：查看 AnythingLLM 日志

右上角：

```
设置
 ↓
开发者设置
 ↓
查看日志
```

或者：

打开：

```
C:\Users\你的用户名\AppData\Roaming\anythingllm-desktop\storage\logs
```

重点看：

类似：

```
Embedding failed
Cannot connect Ollama
Model not found
```

---

## 检查 4：你的文档是否太大

你的文件：

```
DeepSeek-R1.md
```

如果是从教程生成的 Markdown：

可能包含：

* 大量代码块
* 图片链接
* HTML
* 特殊字符

测试：

新建一个：

```
test.md
```

内容：

```
DeepSeek R1 是一个大语言模型。
AnythingLLM 可以构建本地知识库。
```

上传。

如果秒完成：

说明原文件解析问题。

---

## 检查 5：C盘空间问题

你前面提到 AnythingLLM 占 C盘。

如果：

```
C盘剩余 <5GB
```

Embedding 可能直接失败。

检查：

```
C:\Users\用户名\AppData\Roaming\anythingllm-desktop\storage
```

大小。

---

## 根据你的情况，我优先怀疑：

你现在环境：

```
Windows
+
Ollama
+
DeepSeek-R1
+
AnythingLLM Desktop
```

最可能原因：

### ① 没有安装 Embedding 模型（概率最高）

解决：

```cmd
ollama pull bge-m3
```

然后 AnythingLLM：

```
Embedding Provider:
Ollama

Embedding Model:
bge-m3
```

重新嵌入。

---

### ② Ollama 地址错误

AnythingLLM：

```
LLM Provider:
Ollama

地址:
http://localhost:11434
```

不要写：

```
127.0.0.1:11434/api
```

---

你可以再发一张：

**AnythingLLM → 设置 → Embedding Preference 页面截图**

我可以直接判断是哪一步配置错。你现在这个状态不是文件问题，基本是 Embedding 模型链路没有通。
