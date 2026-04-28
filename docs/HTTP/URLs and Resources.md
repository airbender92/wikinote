这段文字是《HTTP: The Definitive Guide》第 2 章（URLs 和 Resources）的开篇引言。作者用了一个生动的城市类比，来解释 **URL（统一资源定位符）** 的核心作用。

---

## 核心类比：互联网是一座城市

| 现实世界 | 互联网世界 |
|----------|------------|
| 街道地址（博物馆、餐馆、住宅） | **URL** — 资源的具体位置 |
| 电话号码（消防局、秘书、母亲） | 也是一种定位方式，但 URL 更通用 |
| ISBN（书号）、公交线路号、银行账号、社保号 | **URN**（统一资源名称）— 资源的唯一名字，不依赖位置 |
| 机场登机口、地铁站名 | 也是命名/定位机制 |

> URL 就是互联网资源的 **标准化地址**：它告诉你**资源在哪里**（哪台服务器、哪个路径）以及**如何访问它**（用什么协议，如 HTTP、FTP）。

---

## URL 与 URN 的对比

书中本章会详细区分：

- **URL**：强调 **位置**（Location），例如 `http://www.example.com/index.html`  
- **URN**：强调 **名称**（Name），例如 `urn:isbn:0451450523`（一本书的 ISBN），不关心它当前存在哪个服务器上

> 日常我们说的“网址”绝大多数是 URL。URN 尚未普及，但作者会在本章末尾讨论其前景。

---

## 本章剩余内容预告

根据这段导言，本章将涵盖：

1. **URL 语法**（scheme、host、port、path、query、fragment 等组件）
2. **URL 快捷方式**（相对 URL、自动扩展 URL）
3. **URL 编码与字符规则**（如何处理不安全字符、保留字符）
4. **常见的 URL 方案**（`http://`、`https://`、`ftp://`、`mailto:` 等）
5. **URL 的未来**（URN 以及持久性资源命名）

---

![16](/assets/http/16.jpg)

这段文字进一步明确了 **URI、URL 和 URN** 的关系，并拆解了一个典型 HTTP URL 的结构。

---

## 核心概念回顾

- **URI（Uniform Resource Identifier）**：统一资源标识符，一个通用的概念，用于唯一标识一个资源。
- **URL（Uniform Resource Locator）**：统一资源定位符，URI 的子集，通过**描述资源的位置**来标识它。
- **URN（Uniform Resource Name）**：统一资源名称，URI 的另一子集，通过**给资源一个唯一的名字**来标识它，与当前位置无关。

> 在实际的 HTTP 应用中，几乎只使用 URL。所以本书后续虽然可能混用 URI 和 URL 术语，但本质上讨论的都是 URL。

---

## URL 的三部分结构（以 `http://www.joes-hardware.com/seasonal/index-fall.html` 为例）

| 组成部分 | 示例 | 作用 |
|----------|------|------|
| **方案（scheme）** | `http` | 告诉客户端用什么协议访问资源（如 HTTP、FTP、RTSP） |
| **服务器地址（server location）** | `www.joes-hardware.com` | 资源所在的主机名（通过 DNS 解析为 IP） |
| **资源路径（resource path）** | `/seasonal/index-fall.html` | 服务器上该资源的本地路径 |

> 其他协议的例子：
> - `mailto:president@whitehouse.gov`（电子邮件地址）
> - `ftp://ftp.lots-o-books.com/pub/complete-price-list.xls`（FTP 文件）
> - `rtsp://www.joes-hardware.com:554/interview/cto_video`（实时流媒体）

---

## URL 的通用格式

大多数 URL 遵循相同的模式：

```
<scheme>://<host>/<path>
```

这种统一的结构让任何资源（无论类型、无论访问方式）都可以用一个字符串方便地表示和分享。

---

## 历史背景

> 在 URL 出现之前，访问不同协议的资源需要不同的客户端、不同的命令和不同的操作步骤。  
> URL 的出现把这一切统一起来——用户只需要点击链接或输入地址，由浏览器自动选择合适的协议和方式去获取资源。

---

## 与你之前阅读的联系

- 第 1 章已经介绍了 **URI 作为资源标识符** 和 **URL 作为最常见的 URI 形式**。  
- 第 2 章接下来会深入讲解 URL 的各个组成部分（包括端口、用户名/密码、查询参数、片段等），以及相对 URL、URL 编码等内容。

---

Page 45

---

