这是 **AnythingLLM Desktop 版的正常现象**。它默认把大量数据放在 **C盘用户目录**，不是安装目录，所以即使软件安装很小，后续导入文档、向量化、模型缓存后，C盘会快速膨胀。AnythingLLM 本身是本地运行模式，聊天记录、文档、向量数据库等都会保存在本机。([AnythingLLM][1])

Windows 默认位置一般是：

```
C:\Users\你的用户名\AppData\Roaming\anythingllm-desktop\
```

其中最占空间的是：

```
storage\
 ├── documents          文档解析文件
 ├── lancedb            向量数据库
 ├── vector-cache       embedding缓存
 ├── models             模型文件（如果使用内置模型）
 └── anythingllm.db     数据库
```

([Restackio][2])

## 方法一（推荐）：把 AnythingLLM 数据迁移到 D盘

例如迁移到：

```
D:\AI\AnythingLLM\
```

### 1. 关闭 AnythingLLM

确认任务栏托盘也退出。

---

### 2. 找到数据目录

打开：

```
Win + R
```

输入：

```
%APPDATA%
```

进入：

```
anythingllm-desktop
```

复制整个文件夹。

例如复制：

```
C:\Users\你的用户名\AppData\Roaming\anythingllm-desktop
```

到：

```
D:\AI\
```

变成：

```
D:\AI\anythingllm-desktop
```

---

### 3. 删除 C盘原目录

确认 D盘复制完整后：

删除：

```
C:\Users\你的用户名\AppData\Roaming\anythingllm-desktop
```

---

### 4. 创建目录链接（关键）

以管理员身份打开 CMD：

开始菜单 → 搜索 cmd → 右键 → 管理员运行

执行：

```cmd
mklink /J "C:\Users\你的用户名\AppData\Roaming\anythingllm-desktop" "D:\AI\anythingllm-desktop"
```

成功会显示：

```
为 ... 创建的联接
```

之后：

* AnythingLLM 仍认为数据在 C盘
* 实际文件全部写入 D盘

这是 Windows 处理大型应用数据迁移最稳定的方法。

---

## 方法二：重新安装时修改位置

如果你还没有开始使用：

1. 卸载 AnythingLLM
2. 删除：

```
C:\Users\用户名\AppData\Roaming\anythingllm-desktop
```

3. 安装到：

```
D:\Applications\AnythingLLM
```

但是注意：

**安装位置 ≠ 数据位置**

Desktop版本的数据仍可能进入 AppData，所以单纯改安装目录不能完全解决。([Restackio][2])

---

## 方法三（更适合搭建本地知识库）：使用 Docker 版

如果你的目标是：

* DeepSeek R1
* Ollama
* AnythingLLM
* 本地知识库
* 大量PDF/代码/资料

我更推荐 Docker。

可以直接指定：

```
D:\AI\anythingllm-storage
```

作为数据目录。

官方 Docker 示例也是通过挂载 storage 目录控制数据位置。([GitHub][3])

结构：

```
D:
 └── AI
     ├── models
     ├── ollama
     └── anythingllm-storage
```

这样以后：

* DeepSeek模型 → D盘
* Embedding → D盘
* 知识库 → D盘
* C盘只放系统

---

## 如果你的C盘已经被占满

可以先检查：

打开：

```
C:\Users\你的用户名\AppData\Roaming\anythingllm-desktop\storage
```

看大小。

如果：

* 几百 MB → 正常
* 几 GB → 有大量文档
* 十几 GB～几十 GB → 通常是模型或向量库

---

结合你之前在搭建 **DeepSeek R1 + AnythingLLM 本地知识库**，我建议直接采用：

```
D:\AI\
 ├── Ollama\
 │    └── models
 │
 ├── AnythingLLM\
 │    └── storage
 │
 └── Documents\
      └── KnowledgeBase
```

这样以后导入几千份PDF也不会污染C盘。

如果你现在已经安装并导入了一些知识库，我建议不要重装，直接做 **迁移 + mklink**，数据不会丢。

[1]: https://anythingllm.com/desktop?utm_source=chatgpt.com "Download AnythingLLM for Desktop"
[2]: https://d2wozrt205r2fu.cloudfront.net/p/anything-llm-answer-file-locations-cat-ai?utm_source=chatgpt.com "Anything-llm File Location Guide | Restackio"
[3]: https://github.com/BlueLabelLabs/bll-anything-llm/blob/master/docker/HOW_TO_USE_DOCKER.md?utm_source=chatgpt.com "bll-anything-llm/docker/HOW_TO_USE_DOCKER.md at master · BlueLabelLabs/bll-anything-llm · GitHub"
