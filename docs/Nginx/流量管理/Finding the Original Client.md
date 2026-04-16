# 3.4 找到真实客户端 IP · 超通俗终极解释
我用**最简单、最直白、不绕弯**的话，一次性把这段讲得明明白白👇

# 核心一句话
**当 Nginx 前面还有一层代理（如云厂商 LB、CDN、防火墙）时，Nginx 拿到的 IP 是代理的，不是用户真实 IP。
这两个指令就是让 Nginx 穿透多层代理，找到**最原始、真实的用户 IP**，给 GeoIP2 使用。**

---

# 1. 为什么需要这个？
正常情况：
`用户 → Nginx` → Nginx 拿到真实 IP

但**云环境/多层代理**下是这样：
`用户 → CDN/LB/云代理 → Nginx`
→ Nginx 拿到的是 **LB 的 IP**，不是用户 IP
→ GeoIP 定位就错了！

---

# 2. 两个关键指令（必须懂）
## ① `geoip2_proxy 10.0.16.0/26;`
**告诉 Nginx：这个网段是“可信代理”**
当请求来自这个网段时，Nginx 就知道：
“这是代理发过来的，我要去请求头里找真实 IP。”

真实 IP 藏在请求头：**`X-Forwarded-For`**

## ② `geoip2_proxy_recursive on;`
**开启递归查找真实 IP**
如果前面有**多层代理**（比如：用户 → LB1 → LB2 → Nginx）
Nginx 会一层层往前找，直到拿到**最原始的用户 IP**

---

# 3. 配置整体作用
```nginx
geoip2_proxy 10.0.16.0/26;    # 信任这个网段的代理
geoip2_proxy_recursive on;    # 穿透多层代理找真实IP
```

效果：
✅ Nginx 不再拿代理 IP
✅ 拿到**用户真实 IP**
✅ GeoIP2 定位国家/城市 100% 准确

---

# 4. 哪些场景必须用？
- AWS ELB
- Google Cloud LB
- Azure LB
- 阿里云/腾讯云负载均衡
- CDN 后面挂 Nginx
- 公司内部多层代理

---

# 5. 超精简总结（最重要）
**geoip2_proxy = 告诉 Nginx 谁是可信代理
geoip2_proxy_recursive = 穿透代理找真实用户IP
目的：让 GeoIP 定位准确不误判**

你现在是不是彻底通透了？
我可以继续带你学 **3.5 速率限制（限流）** 啦！