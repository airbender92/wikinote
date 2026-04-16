# 2.5 Sticky Cookie 会话黏连（仅 Nginx Plus 商业版）
## 一句话解释
让**同一个用户**，在一段时间内**永远访问同一台后端服务器**，靠 Cookie 实现“会话黏连”。

---

## 这段配置在干嘛？
```nginx
upstream backend {
    server backend1.example.com;
    server backend2.example.com;

    sticky cookie
        affinity
        expires=1h
        domain=.example.com
        httponly
        secure
        path=/;
}
```

逐行翻译成人话：
- `sticky cookie`：开启 Cookie 会话黏连
- `affinity`：给这个 Cookie 起名叫 `affinity`
- `expires=1h`：Cookie 有效期 1 小时
- `domain=.example.com`：在该域名下生效
- `httponly`：JS 不能读取，更安全
- `secure`：只在 HTTPS 下传输
- `path=/`：全站有效

---

## 工作流程
1. 用户第一次访问
2. Nginx Plus 选一台后端服务器
3. 给用户种下一个 Cookie，记录这台服务器
4. 后续请求带上这个 Cookie
5. Nginx 识别 Cookie → 一直转发到同一台服务器

---

## 关键要点
- **只在 Nginx Plus 商业版才有**
- **只工作在 HTTP 环境**（因为依赖 Cookie）
- 作用：保证会话不丢失，用户不用重复登录
- 和 `ip_hash` 类似，但更精准、更灵活

---

## 超精简总结
**sticky cookie = 给用户种个 Cookie，让他一直黏在同一台服务器上，实现会话保持。**