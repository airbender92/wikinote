以下根据音频标题 **《5分钟教会你如何本地部署 DeepSeek-R1，无需联网，全程干货，没有一句废话》** 整理为一份参考文档。

> 说明：由于未提取音频原文，本文不是逐字稿，而是根据该主题整理的标准化 DeepSeek-R1 本地部署实践指南，可作为学习和操作参考。

---

# DeepSeek-R1 本地部署参考手册

## 1. 项目简介

### 1.1 什么是 DeepSeek-R1

DeepSeek-R1 是由深度求索（DeepSeek）推出的大语言模型，重点优化了：

* 数学推理能力
* 代码生成能力
* 逻辑分析能力
* 长文本理解能力

本地部署后，可以：

* 不依赖互联网运行
* 数据完全保存在本机
* 保护隐私
* 降低 API 调用成本
* 自定义模型和应用

---

# 2. 本地部署方案选择

目前常见部署方式：

| 方案                  | 适合人群       | 特点        |
| ------------------- | ---------- | --------- |
| Ollama              | 普通用户       | 最简单，命令行部署 |
| LM Studio           | 新手         | 图形化界面     |
| vLLM                | 开发者        | 高性能服务器部署  |
| llama.cpp           | 低配置设备      | CPU/GPU均可 |
| Open WebUI + Ollama | 私有 ChatGPT | 推荐方案      |

推荐：

> Ollama + DeepSeek-R1 + Open WebUI

体验类似 ChatGPT，同时模型运行在本地。

---

# 3. 硬件要求

## 3.1 最低配置

### 小模型（1.5B / 7B）

适合：

* 普通笔记本
* 家用电脑

建议：

```
CPU:
Intel i5 / AMD Ryzen 5+

内存:
16GB+

硬盘:
至少 20GB 空间
```

---

## 3.2 推荐配置

### 14B 模型

```
内存:
32GB+

显存:
12GB+

GPU:
RTX 3060 12GB
RTX 4070
RTX 4080
```

---

## 3.3 大模型

例如：

DeepSeek-R1 32B / 70B

需要：

```
显存:
24GB+

多GPU环境更佳
```

普通电脑不建议运行。

---

# 4. 安装 Ollama

## 4.1 Windows 安装

进入：

Ollama 官网：

[https://ollama.com](https://ollama.com)

下载安装包：

```
OllamaSetup.exe
```

安装完成后打开 PowerShell：

检查：

```bash
ollama --version
```

如果显示版本号：

说明安装成功。

---

# 5. 下载 DeepSeek-R1 模型

## 5.1 查看可用模型

执行：

```bash
ollama list
```

---

## 5.2 下载 DeepSeek-R1

例如：

### 7B版本

```bash
ollama pull deepseek-r1:7b
```

---

### 14B版本

```bash
ollama pull deepseek-r1:14b
```

---

### 32B版本

```bash
ollama pull deepseek-r1:32b
```

---

下载完成后查看：

```bash
ollama list
```

显示：

```
deepseek-r1
```

说明成功。

---

# 6. 启动 DeepSeek-R1

运行：

```bash
ollama run deepseek-r1:7b
```

进入聊天模式：

例如：

```
>>> 请解释量子计算
```

模型会直接回答。

---

# 7. 部署 Web 界面（推荐）

命令行体验有限，可以安装 Open WebUI。

效果：

类似：

ChatGPT网页界面

支持：

* 多模型管理
* 历史聊天
* 文件上传
* 知识库
* 用户管理

---

# 8. 使用 Docker 部署 Open WebUI

## 8.1 安装 Docker Desktop

下载安装：

[https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)

确认：

```bash
docker --version
```

---

## 8.2 启动 Open WebUI

执行：

```bash
docker run -d \
-p 3000:8080 \
--name open-webui \
--restart always \
-v open-webui:/app/backend/data \
ghcr.io/open-webui/open-webui:main
```

---

启动成功后访问：

```
http://localhost:3000
```

即可打开网页聊天界面。

---

# 9. 连接 Ollama

Open WebUI 默认连接：

```
http://host.docker.internal:11434
```

如果没有连接：

进入：

```
设置
 ↓
连接
 ↓
Ollama API
```

填写：

```
http://host.docker.internal:11434
```

保存。

---

# 10. 完全离线运行

如果希望断网使用：

提前准备：

## 模型文件

例如：

```
deepseek-r1:7b
```

下载完成后：

即可关闭网络。

运行：

```
ollama run deepseek-r1:7b
```

不会访问互联网。

---

# 11. 常见问题

## 问题1：显存不足

错误：

```
CUDA out of memory
```

解决：

降低模型：

例如：

```
32B
↓
14B

14B
↓
7B
```

---

## 问题2：运行速度慢

优化：

### 使用GPU

确认：

```bash
nvidia-smi
```

查看显卡状态。

---

### 使用量化模型

例如：

```
Q4_K_M
```

优点：

* 占用更少显存
* 推理速度更快

---

## 问题3：模型删除

查看：

```bash
ollama list
```

删除：

```bash
ollama rm deepseek-r1:7b
```

---

# 12. 推荐部署组合

## 普通电脑

推荐：

```
Windows
+
Ollama
+
DeepSeek-R1 7B
```

---

## 游戏显卡电脑

推荐：

```
RTX 3060/4060/4070

+
DeepSeek-R1 14B
+
Open WebUI
```

---

## 工作站

推荐：

```
Linux

+
vLLM

+
DeepSeek-R1 32B/70B
```

---

# 13. 一键部署流程总结

完整流程：

```
1. 安装 Ollama

↓

2. 下载模型

ollama pull deepseek-r1:7b

↓

3. 测试运行

ollama run deepseek-r1:7b

↓

4. 安装 Docker

↓

5. 部署 Open WebUI

↓

6. 浏览器访问

localhost:3000

↓

7. 断网运行
```

---

# 14. 最终建议

对于大多数个人用户：

推荐配置：

```
Windows 11

16GB以上内存

RTX 3060 12GB 或更高

Ollama

DeepSeek-R1 7B/14B

Open WebUI
```

即可获得一个：

* 私有化 ChatGPT
* 无联网依赖
* 数据不上传
* 免费长期使用

的本地 AI 助手。

---

**文档版本：DeepSeek-R1 本地部署参考 v1.0**
**适用场景：个人电脑、本地 AI 助手、离线知识库、代码辅助**

---

如果需要，我还可以进一步整理成 **“Windows 实战版（逐条复制命令版）”** 或 **“PDF/Word版部署手册”**。
