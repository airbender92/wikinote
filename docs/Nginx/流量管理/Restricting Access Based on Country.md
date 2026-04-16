# 3.3 基于国家限制访问 · 最通俗解释
我给你**超简单、不绕弯、一看就懂**的讲解👇

# 核心一句话
**用 GeoIP2 + map 变量，实现：只允许某个国家的人访问，其他国家直接返回 403 拒绝。**

---

# 1. 这段配置在干嘛？
一共就两步：
1. **判断用户来自哪个国家**
2. **不是美国 → 直接拒绝访问（403）**

---

# 2. 逐段超通俗解释

## 第一步：加载 GeoIP2 模块
```nginx
load_module modules/ngx_http_geoip2_module.so;
```
→ 让 Nginx 能识别用户 IP 来自**哪个国家**。

---

## 第二步：定义国家 → 权限映射
```nginx
map $geoip2_data_country_code $country_access {
    default 1;   # 其他国家 = 1（禁止）
    "US"    0;   # 美国     = 0（允许）
}
```
- `$geoip2_data_country_code`：国家代码（CN、US、JP…）
- `$country_access`：自己定义的变量
  - 0 = 允许
  - 1 = 拒绝

---

## 第三步：拦截非美国用户
```nginx
if ($country_access = '1') {
    return 403;  # 拒绝访问
}
```
- 如果用户**不是美国** → 返回 403 禁止访问
- 如果是美国 → 正常访问

---

# 3. 整体逻辑（超简单）
```
用户访问 → Nginx 识别国家
→ 美国 → 允许
→ 其他 → 403 拒绝
```

---

# 4. 你可以轻松改成：
- 只允许**中国**访问：
  ```nginx
  map $geoip2_data_country_code $country_access {
      default 1;
      "CN" 0;
  }
  ```
- 允许多个国家：
  ```nginx
  map $geoip2_data_country_code $country_access {
      default 1;
      "CN" 0;
      "US" 0;
      "JP" 0;
  }
  ```

---

# 5. 用途非常广
- 合规要求（只允许本国访问）
- 版权限制
- 防攻击、防爬虫
- 业务区域限制

---

# 超精简总结（必须记住）
**GeoIP2 识别国家 → map 定义允许/禁止 → if 判断拦截
一行配置，实现按国家允许/屏蔽访问！**

你现在是不是彻底懂了？
我可以继续带你学 **3.4 速率限制（限流）** 啦！