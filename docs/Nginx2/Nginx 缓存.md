# Nginx 缓存（Caching）完整翻译+通俗讲解+考点总结
完全按照你教材原文+披萨比喻，**考试直接背**

---

## 一、全文翻译
我们回到第1章介绍Nginx时用过的**披萨店类比**：

假设你开了一家披萨店，每天有几百个订单。
如果**每来一个订单，你都从头现做披萨**（揉面、酱料、配料），高峰期订单排队，顾客等待时间会非常久。

更好的做法：
提前把热门披萨做好，放在保温炉里保温。
订单来了，直接拿现成的，**不用重新制作**，立刻交付给顾客。

这就是**缓存（Caching）**的本质：
把频繁访问的数据提前保存好、随时可用，
不用每次都去后端应用服务器重新获取、重新生成。

缓存是网站提速最核心的手段之一。
缓存让内容随时可用，大幅缩短加载时间，提供流畅用户体验。

本章我们学习：哪些内容可以缓存、如何在Nginx中有效配置缓存。
学完你将完全理解：缓存对网站速度优化、留住用户的重要作用。

---

## 二、缓存核心通俗原理（必背一句话）
**缓存 = 把后端返回的内容，存在Nginx本地磁盘/内存里。
下次同一个用户再请求，Nginx直接返回本地缓存，不再请求后端服务器。**

好处：
1. 网站加载**极快**
2. **大幅降低后端服务器压力**
3. 节省带宽
4. 提升并发能力

---

## 三、哪些内容适合缓存？（教材重点）
✅ **适合缓存（静态内容）**
HTML、CSS、JS、图片、字体、静态JSON
不经常变化、所有用户看到一样的内容

❌ **绝对不能缓存（动态内容）**
用户个人信息、登录状态、购物车、实时接口、后台接口
每次请求结果都不一样，缓存会造成数据错误

---

## 四、Nginx 缓存核心指令（下一节考点预告）
教材接下来会讲这几个核心指令：
1. `proxy_cache_path` 定义缓存路径、大小、层级、过期时间
2. `proxy_cache_key` 缓存key规则
3. `proxy_cache` 开启/关闭缓存
4. `proxy_cache_valid` 设置不同响应码的缓存时长
5. `proxy_cache_bypass` / `proxy_no_cache` 不缓存条件
6. Cache-Control、Expires 浏览器缓存

---

# Nginx 缓存完整翻译+精简考点背诵版（完全对应教材原文）
## 一、全文翻译
缓存（Caching）是将**频繁访问的数据/文件副本**，存储在临时存储空间（缓存 Cache）的过程。

通过缓存，服务器、浏览器可以保存常用数据，
避免用户每次访问网站都重新下载、重新处理资源。
这极大提升加载速度、优化整体用户体验。

最典型例子：**浏览器缓存**
浏览器会把静态内容保存在用户本地设备，保存一段时间。
用户第一次访问网站：浏览器从服务器下载静态不变资源，并保存到本地缓存。
用户再次访问：浏览器**直接读取本地缓存**，不再请求服务器。
大幅加快加载速度、节省网络流量、减轻服务器压力。

---

## 二、缓存的全部优点（教材完整版，考试简答题直接复制）
1. **更快加载速度 Faster Load Times**
缓存存储高频内容，访问更快，对内容量大的网站效果明显。

2. **降低服务器压力 Reduced Server Load**
不用每次重新生成内容，释放服务器资源，提升处理能力。

3. **节省带宽 Bandwidth Savings**
减少服务器与客户端传输数据量，高流量网站可大幅节约成本。

4. **优化用户体验 Improved User Experience**
响应更快、页面更流畅，降低跳出率、提升用户留存与活跃度。

5. **提升可扩展性 Increased Scalability**
减轻后端压力，高峰期系统不易被打垮，支持更高并发。

6. **降低延迟 Lower Latency**
CDN 就近缓存，全球用户就近获取资源，延迟更低。

7. **优化数据库性能 Optimized Database Performance**
缓存高频数据库查询，减少重复查询，避免数据库瓶颈。

8. **节约成本 Cost Efficiency**
降低服务器、带宽、算力开销，节省运维成本。

9. **提升应用整体性能 Enhanced Application Performance**
内存缓存比磁盘更快，适合计算密集型业务。

10. **提升服务可用性 Improved Availability**
源站宕机/异常时，缓存内容仍可正常访问，增加系统容错能力。

---

# 🔥 极简必背总结（考试压缩版）
1. **缓存定义**：把高频访问数据存在临时缓存区，不用重复请求后端/下载。
2. **浏览器缓存原理**：首次下载保存本地，再次访问直接读本地缓存。
3. **缓存核心好处**：提速、降服务器压力、省带宽、低延迟、高可用、护数据库、降成本。
4. **缓存适用内容**：静态不变资源（图片、css、js、字体）
5. **禁止缓存内容**：登录态、个人信息、实时动态接口、购物车。

---

![cache](/assets/Nginx2/caching.jpg);

# 分层缓存（Different Types of Cache）完整翻译+图文详解+考点背诵
完全对照你这张架构图+教材原文，考试直接背👇

---
## 一、全文完整翻译
缓存可以应用在**技术栈的各个层级**：操作系统、网络层（CDN、DNS）、Web应用、数据库。
对于问答平台、游戏、媒体分享、社交网络这类**读多写少（Read-heavy）**的业务，缓存对降低延迟、提升IOPS性能至关重要。

缓存的数据可以包括：数据库查询结果、复杂计算结果、API接口响应、HTML/JS/图片等Web静态资源。

下图展示了完整网站架构，缓存可以部署在每一层：
浏览器、应用服务器、中间缓存、CDN、负载均衡/反向代理服务器。

在任意一层开启缓存（尤其是**反向代理/负载均衡Nginx层**），都能大幅提升网站性能。

---
## 二、逐行拆解你这张5层缓存架构图（100%对应）
从上到下完整链路：
`用户终端（移动端/电脑） → 互联网 → Web内容层 → 应用层 → 数据库层`

下面表格是**5层缓存分层详解（考试必背）**

| 缓存层级 Layer | 用途 Use Case | 对应技术 Technologies | 落地解决方案 Solutions |
| ---- | ---- | ---- | ---- |
| **客户端缓存 Client-Side（浏览器缓存）** | 加速浏览器从网站获取Web资源（浏览器/设备本地缓存） | HTTP缓存响应头、浏览器本地缓存 | 浏览器原生缓存机制 |
| **DNS缓存** | 域名解析IP地址（域名→IP解析缓存） | DNS服务器递归/迭代缓存 | Amazon Route 53 DNS服务 |
| **Web层缓存（Nginx反向代理/CDN缓存）** | 加速Web服务器资源读取、管理Web会话（服务端缓存，就是你正在学的Nginx缓存） | HTTP缓存头、CDN、反向代理、Web加速器、键值存储 | CloudFront CDN、Redis、Memcached |
| **应用层缓存 App Cache** | 加速应用服务性能、数据访问速度 | 键值存储、应用本地缓存 | Redis、Memcached、应用框架缓存 |
| **数据库缓存 Database Cache** | 降低数据库查询延迟、优化数据库请求 | 数据库缓冲区、数据库键值存储 | Redis、Memcached数据库缓存 |

---
## 三、5层缓存通俗理解（一句话记住每层）
1. **浏览器缓存**：用户电脑本地，第一次下载资源存在本地，下次不请求服务器
2. **DNS缓存**：域名解析IP的结果缓存，不用每次重新解析域名
3. **Web/Nginx缓存**：**你正在学的重点！** Nginx反向代理缓存后端响应，直接返回，不再请求后端应用
4. **应用缓存**：后端Java/PHP应用缓存计算结果、接口数据
5. **数据库缓存**：缓存SQL查询结果，减轻数据库查询压力

---
## 四、本节核心考点（简答题满分答案）
1. 缓存可以部署在**客户端、DNS、Web(Nginx)、应用、数据库**5个层级
2. 其中**Nginx反向代理/Web层缓存**对性能提升最显著
3. 缓存适合读多写少业务（社交、媒体、问答、游戏）
4. 缓存内容：静态资源、API响应、数据库查询、计算结果
5. 缓存价值：降延迟、提IOPS、降服务器压力、提升并发

---

# CDN 内容分发网络（Content Delivery Network）完整图文解析+考点背诵
完全对照你这张世界地图原理图+教材原文👇

---

![cdn](/assets/Nginx2/cdn.jpg);


## 一、标题&图注翻译
**Content delivery network 内容分发网络**
CDN 从**源站服务器**缓存内容，到全球分布式CDN缓存节点服务器，让用户更快获取内容。

图例：
- 🟢 USER 用户
- 🟦 CDN SERVER CDN缓存节点服务器
- 🟧 ORIGIN SERVER 你的源站服务器（Nginx网站原始服务器）

---
## 二、图片原理逐行讲解（100%对应架构）
1. 橙色**源站服务器**：你自己的网站原始服务器（部署Nginx、网站、数据库），只有1个/少数几个固定地点
2. 蓝色**CDN节点**：全球各个国家/城市都部署了分布式缓存服务器
3. 绿色用户：全球各地用户访问网站
4. 正常无CDN：全世界所有用户 → 远距离直连唯一源站，延迟极高、源站压力爆炸
5. **CDN工作流程**：
    - CDN提前把源站静态资源（图片、JS、CSS、视频）缓存到全球各地节点
    - 用户请求 → 连接**地理上最近的本地CDN节点**，不直接连远在海外的源站
    - CDN节点直接返回缓存内容，速度极快
    - CDN节点内容过期/不存在，才会回源站拉取最新内容

---
## 三、全文完整翻译
CDN（内容分发网络）是一套**跨全球地理位置分布式部署的服务器网络**，用于交付图片、视频、样式表、JS等Web静态资源。

CDN的核心目标：
通过**距离用户地理位置最近的节点服务器**提供内容，降低网络延迟、提升响应速度。
原理：缩短数据传输的物理距离，同时大幅减轻源站服务器压力，优化终端用户体验。

举例：
你在印度访问网站，孟买本地CDN节点，远比美国德克萨斯源站速度快得多。

案例：
流媒体平台Netflix，使用Akamai全球CDN服务，给全球千万用户交付影视内容。
通过把内容缓存到用户就近节点、优化网络路由，Akamai极大降低延迟，提升用户播放体验。

---
## 四、CDN核心作用&考点（考试必背精简版）
1. **就近访问，极低延迟**：用户连本地节点，不用跨地域连源站
2. **保护源站**：大量静态资源请求由CDN承接，源站压力大幅降低
3. **加速静态资源**：图片、视频、CSS、JS、字体等静态内容
4. **抗并发抗DDoS**：CDN分流，源站不易被流量打垮
5. 工作逻辑：**缓存预热 → 用户就近访问CDN缓存 → 缓存失效才回源站更新**

---
## 五、CDN 和 Nginx 缓存的关系（本节重点）
- CDN = **全球分布式多级Web缓存**（对应你上一张分层缓存里的Web层缓存）
- Nginx proxy_cache = **源站本地反向代理缓存**
- 完整最优架构：
`用户 → 浏览器缓存 → CDN全球缓存 → Nginx源站缓存 → 应用 → 数据库`
五层缓存层层加速

---
# 🔥一句话终极记忆
**CDN = 全球遍地开花的就近缓存节点，用户不走远路连源站，本地CDN直接返回内容，提速、护源站、降延迟**

---

![dns-cache](/assets/Nginx2/dns-cache.jpg);

# DNS 缓存（DNS Caching Flow）完整图文解析+考点背诵
完全对照你这张流程图+教材原文👇

---
## 一、先看懂这张 DNS 缓存流程图（逐段拆解）
链路从上到下：
`Web浏览器 → 本机DNS解析器 → 运营商ISP DNS解析器 → 递归DNS全网查询`

每一级都自带缓存，**从上到下逐级缓存，逐级查找**：
1.  **CLIENT COMPUTER 客户端电脑**
    - Web Browser 浏览器：自带 **Mini Cache 浏览器DNS迷你缓存**
    - DNS resolver 本机DNS解析器：自带 **Local Cache 本地系统DNS缓存**
2.  **INTERNET SERVICE PROVIDER 运营商ISP网络**
    - DNS resolver 运营商DNS解析器：自带 **Local Cache 运营商DNS缓存**
3.  最后才会向外发起 RECURSIVE DNS SEARCH 全网递归DNS查询

DNS查询规则：**先查本地缓存，缓存命中直接返回；缓存不存在，才向下一级请求查询**

---
## 二、全文完整翻译
DNS缓存服务器是一类DNS服务器，它会**临时缓存域名解析结果（域名→IP）**，提升后续DNS查询的效率与速度。

当DNS服务器把域名（例如 `example.com`）解析成IP地址（例如 `192.0.2.1`）后，会把这条解析结果缓存起来。
下次再查询同一个域名时，直接返回缓存结果，**不用从头重新递归解析整个域名**，速度极快。

Unbound 是一款流行的开源DNS缓存服务器+递归解析器，安全、快速解析DNS并缓存结果。
被运营商、企业、个人广泛使用，用来加速DNS解析、提升隐私安全性。

---
## 三、DNS缓存完整工作流程（考试必背步骤）
1. 用户浏览器请求访问域名
2. 先查**浏览器DNS迷你缓存** → 命中直接返回IP
3. 没命中，查**本机系统DNS本地缓存** → 命中直接返回IP
4. 没命中，请求运营商DNS服务器，查**运营商DNS缓存** → 命中直接返回IP
5. 都没命中，才向外发起全网递归DNS查询，从根域名→顶级域名→权威服务器拿到IP
6. 解析结果逐级缓存到每一级缓存里，下次查询直接命中

---
## 四、DNS缓存核心考点（简答题满分）
1.  **DNS缓存作用**：缓存域名→IP解析结果，避免重复递归解析，大幅加快域名解析速度、降低网络压力
2.  **缓存层级**：浏览器缓存 → 本机系统缓存 → 运营商ISP缓存 → 权威DNS服务器缓存
3.  **查询逻辑**：就近优先查找缓存，缓存命中直接返回，未命中才向下一级查询
4.  **开源代表**：Unbound 开源DNS缓存递归服务器

---
## 五、结合之前学的全链路缓存总结（完整5层缓存+DNS/CDN）
完整网站访问全链路缓存（从上到下）：
1.  浏览器缓存（HTTP资源缓存+DNS迷你缓存）
2.  DNS分层缓存（本机→运营商→递归DNS）
3.  CDN全球就近缓存
4.  Nginx反向代理Web缓存（你正在学的重点）
5.  应用层缓存
6.  数据库缓存

---
# 🔥一句话终极记忆
**DNS缓存 = 各级服务器缓存「域名对应IP」，先查本地缓存，不用每次全网重新解析域名，解析更快**

---

![nginx-caching](/assets/Nginx2/nginx-caching.jpg);

# Nginx 反向代理缓存（proxy_cache）完整图文解析+考点背诵版
完全对照你这张架构图+教材全部指令，**考试直接背、直接写答案**👇

---
## 一、先看懂这张 Nginx 缓存架构图（100%对应原文）
链路：
`Client客户端 → 互联网 → Nginx（缓存+负载均衡+反向代理） → 后端App应用服务器 + Nginx本地磁盘Cache缓存`

核心原理：
Nginx 作为反向代理，把**后端应用服务器返回的响应**，存在本地磁盘Cache里。
下次客户端再请求相同内容：
Nginx **直接返回本地缓存，不再请求后端应用服务器**，完全绕过源站。
效果：大幅提速、极大降低后端应用服务器压力。

---
## 二、全文完整翻译
Nginx 提供全套完善的缓存功能。
缓存服务器位于客户端与源站（应用服务器）之间，会保存过往请求的内容副本。
当客户端请求已经缓存过的内容时，缓存服务器直接返回内容，**绕过后端源站**。
这既提升了性能（缓存离用户更近），又避免后端服务器每次重新生成页面，大幅降低应用服务器压力。

---
# 三、Nginx proxy_cache 全部指令（教材原版+极简考点版）
按重要程度排序，全部是考试必考简答题

## 1. proxy_cache 开关指令
```nginx
proxy_cache mycache;  # 开启缓存，使用mycache内存区域
proxy_cache off;      # 关闭缓存
```
作用：开启/关闭反向代理缓存，指定缓存共享内存区域，所有worker进程共享缓存元数据。
默认：`off`

---
## 2. proxy_cache_path 缓存根配置（最重要！http块配置）
```nginx
proxy_cache_path /data/nginx/cache 
levels=1:2 
keys_zone=my_cache:10m 
max_size=10g 
inactive=60m 
use_temp_path=off;
```
逐参数解释（教材原版定义）：
| 参数 | 作用（考试背诵版） |
|------|-------------------|
| `/data/nginx/cache` | 缓存文件**磁盘存储目录** |
| `levels=1:2` | 缓存目录分级，避免单目录文件过多；哈希第1位建一级目录、后2位建二级目录 |
| `keys_zone=my_cache:10m` | 定义共享内存区域my_cache，分配10MB内存，存放缓存key、过期时间等元数据 |
| `max_size=10g` | 缓存磁盘最大总大小；超出自动LRU淘汰最久未使用内容 |
| `inactive=60m` | 缓存60分钟未被访问，自动删除过期缓存 |
| `use_temp_path=off` | 关闭临时目录，直接写入缓存目录，减少磁盘IO |

---
## 3. proxy_cache_key 缓存唯一Key
```nginx
proxy_cache_key "$scheme$host$request_uri";
```
默认值，定义缓存的唯一标识；相同key命中同一份缓存。
可自定义：带上cookie、请求头实现用户独立缓存。

---
## 4. proxy_cache_valid 缓存过期时间（按响应码）
```nginx
proxy_cache_valid 200 302 10m;  # 200/302状态码缓存10分钟
proxy_cache_valid 404 1m;       # 404缓存1分钟
proxy_cache_valid any 1m;      # 所有状态码缓存1分钟
```
默认：不指定状态码时，默认缓存 `200/301/302`

---
## 5. proxy_cache_use_stale 后端异常使用过期缓存
```nginx
proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;
```
作用：后端服务器报错、超时、不可用时，Nginx**直接返回旧过期缓存**，保证服务可用，提升高可用。

---
## 6. proxy_no_cache / proxy_cache_bypass 跳过缓存
- `proxy_no_cache`：满足条件**不缓存本次响应**（写入缓存跳过）
  ```nginx
  proxy_no_cache $http_cookie $http_authorization;
  ```
  登录态、授权请求不缓存
- `proxy_cache_bypass`：满足条件**直接绕过缓存请求后端**（读取缓存跳过）

---
## 7. proxy_cache_lock 缓存锁（防止缓存击穿/惊群效应）
```nginx
proxy_cache_lock on;
proxy_cache_lock_timeout 5s;
```
作用：大量并发请求同时访问**未缓存资源**时，只放行1个请求去后端回源，其他请求等待缓存生成；
防止后端被瞬间打垮（惊群问题Thundering herd）。

---
## 8. proxy_cache_min_uses 最少访问次数才缓存
```nginx
proxy_cache_min_uses 3;
```
请求至少被访问3次才缓存，避免缓存低频冷门资源。默认1次。

---
## 9. proxy_cache_methods 缓存允许的请求方法
```nginx
proxy_cache_methods GET HEAD;
```
默认只缓存GET/HEAD安全幂等请求，不缓存POST；可手动开启POST缓存。

---
# 四、Nginx 标准完整缓存配置（教材最终版，直接背）
```nginx
http {
    # 定义缓存路径、内存、大小、过期
    proxy_cache_path /data/nginx/cache 
    levels=1:2 
    keys_zone=my_cache:10m 
    max_size=10g 
    inactive=60m 
    use_temp_path=off;

    server {
        listen 80;
        server_name example.com;

        location / {
            proxy_cache my_cache; # 开启缓存
            proxy_cache_key "$scheme$host$request_uri";
            proxy_cache_valid 200 10m; # 200缓存10分钟
            proxy_cache_valid 404 1m;
            proxy_cache_use_stale error timeout http_502 http_503; # 后端异常用旧缓存
            proxy_cache_lock on; # 防止缓存击穿
            proxy_no_cache $http_cookie; # 带cookie登录用户不缓存

            # 反向代理转发后端
            proxy_pass http://app_servers;
        }
    }
}
```

---
# 🔥 本节终极考试必背总结
1. Nginx proxy_cache 是**反向代理Web层缓存**，缓存后端响应，直接本地返回，不请求后端应用服务器
2. 核心指令：`proxy_cache_path`（定义缓存）、`proxy_cache`（开关）、`proxy_cache_valid`（过期时间）
3. 作用：提速、降后端压力、提升并发、后端异常降级可用
4. 只缓存静态/公开内容，**登录态、私有内容必须 proxy_no_cache 不缓存**
5. `proxy_cache_lock` 解决缓存惊群击穿问题
6. `proxy_cache_use_stale` 后端故障降级返回过期缓存

---

# Nginx 缓存进程 + 缓存清理（Purge）**超级精简背诵版**
我完全按照你这页教材给你整理，**考试直接默写**👇

---

# 一、Nginx 缓存涉及的两个进程（必背）
Nginx 缓存有两个**专门的后台进程**负责管理：

## 1. Cache Manager（缓存管理器）
- **作用**：定期运行
- **任务**：检查缓存大小是否超过 `max_size`
- **策略**：超过就删除 **LRU（最近最少使用）** 的缓存
- **特点**：缓存可以**暂时超过大小**，但最终会被拉回限制内

## 2. Cache Loader（缓存加载器）
- **作用**：Nginx **启动 / 重启 / 重载**时运行
- **任务**：把缓存元数据（key、路径、过期时间）加载到共享内存
- **特点**：为了不卡服务器，会**分段、分批加载**，使用：
  - `loader_threshold`
  - `loader_files`
  - `loader_sleep`

---

# 二、教材里的完整缓存配置（4 步核心）
```nginx
http {
    # 1. 定义缓存路径和内存区域
    proxy_cache_path /var/cache/nginx keys_zone=my_cachezone:10m;

    server {
        listen 8080;

        # 2. 开启缓存
        proxy_cache my_cachezone;

        location / {
            proxy_pass http://backend-server;

            # 3. 缓存key
            proxy_cache_key $scheme://$host$uri$is_args$args;

            # 4. 缓存过期时间
            proxy_cache_valid 200 10m;
        }
    }
}
```

---

# 三、proxy_cache_bypass（手动绕过缓存）
作用：满足条件时**不读缓存，直接回源**

例：cookie 里有 bypasscache 就绕过
```nginx
proxy_cache_bypass $cookie_bypasscache;
```

---

# 四、proxy_cache_use_stale（后端挂了继续用旧缓存）
作用：**后端宕机、超时、5xx 错误时，继续返回旧缓存**
保证网站不断服！

```nginx
proxy_cache_use_stale 
    error 
    timeout 
    http_500 
    http_502 
    http_503 
    http_504 
    http_429;
```

---

# 五、缓存清理 Purging Content（考试必考）
## 为什么要清理缓存？
1. 内容更新了
2. 缓存了敏感数据
3. 排查问题

## 清理指令：**proxy_cache_purge**
- 方法：使用 `PURGE` 请求方法
- 成功返回：**204 No Content**

## 配置步骤
```nginx
map $request_method $purge_method {
    PURGE   1;
    default 0;
}

server {
    location / {
        proxy_cache cache_zone;
        proxy_cache_purge $purge_method;
    }
}
```

## 清理命令
```bash
curl -X PURGE http://yourdomain.com/some/path
```

---

# 六、限制 Purge 权限（只允许信任IP清理）
用 **geo 指令** 允许指定IP清理缓存，防止别人恶意清空缓存

```nginx
geo $purge_allowed {
    default 0;
    10.0.0.1 1;
    192.168.0.0/24 1;
}

map $request_method $purge_method {
    PURGE   $purge_allowed;
    default 0;
}
```

---

# 🔥 考试必背一句话总结
1. **Cache Manager** 控制缓存大小，删旧缓存
2. **Cache Loader** 启动时加载缓存元数据，分段加载不卡机
3. **proxy_cache_use_stale** 后端挂了用旧缓存，提高可用性
4. **proxy_cache_bypass** 条件绕过缓存
5. **proxy_cache_purge** 清理缓存，返回 204
6. 必须用 geo 限制**允许清理缓存的IP**

---


