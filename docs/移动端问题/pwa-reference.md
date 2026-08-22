# PWA 接入与真机验证参考手册

> 适用项目：容灾管理平台移动端 V2.0（F:\codes\AIMobile）
> 技术栈：Vite 8 + React 18 + vite-plugin-pwa 1.3.0 + antd-mobile
> 最后更新：2026-08-22（PWA 接入完成）

---

## 0. 一句话总览

**PWA = 构建产物（dist）+ HTTPS 服务（自签证书）+ 手机信任 CA**。代码配置一次完成，日常开发只需：`pnpm build` → `pnpm preview --host` → 手机访问 `https://电脑IP:4173`。

---

## 1. PWA 代码配置（已完成，勿重复操作）

### 1.1 依赖

```bash
# 注意：必须在自己的终端执行（WorkBuddy 沙箱会拦截 pnpm 的删除操作）
pnpm add -D vite-plugin-pwa
```

### 1.2 vite.config.ts 关键配置

```ts
import { readFileSync } from 'node:fs'
import { VitePWA } from 'vite-plugin-pwa'

const httpsOptions = {
  key: readFileSync('F:/tools/certs/server.key'),
  cert: readFileSync('F:/tools/certs/server.crt'),
}

// plugins 里追加：
VitePWA({
  registerType: 'autoUpdate',          // 发布新版本自动更新，无需用户手动刷新
  includeAssets: ['favicon.svg', 'icons.svg'],
  manifest: {
    name: '容灾管理平台移动端',
    short_name: '容灾管理',
    description: '容灾管理平台移动端 V2.0',
    lang: 'zh-CN',
    display: 'standalone',
    start_url: '/',
    theme_color: '#1677ff',
    background_color: '#ffffff',
    icons: [
      { src: 'pwa-192x192.png', sizes: '192x192', type: 'image/png' },
      { src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png' },
      { src: 'pwa-maskable-192x192.png', sizes: '192x192', type: 'image/png', purpose: 'maskable' },
      { src: 'pwa-maskable-512x512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
    ],
  },
  workbox: {
    globPatterns: ['**/*.{js,css,html,svg,png,ico,woff2}'],
    cleanupOutdatedCaches: true,
    clientsClaim: true,
    skipWaiting: true,
  },
  devOptions: { enabled: false },      // dev 模式不注册 SW，避免干扰开发
})

// server 保持 http（dev 开发用）；preview 启用 https（真机 PWA 验证用）：
preview: {
  https: httpsOptions,
}
```

### 1.3 index.html 已补充的 meta

```html
<link rel="apple-touch-icon" href="/pwa-192x192.png" />
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta
  name="apple-mobile-web-app-status-bar-style"
  content="black-translucent"
/>
<meta name="apple-mobile-web-app-title" content="容灾管理" />
```

### 1.4 PWA 图标（public/ 下）

| 文件                                                    | 用途                  |
| ------------------------------------------------------- | --------------------- |
| `pwa-192x192.png` / `pwa-512x512.png`                   | 常规图标（紫底白 DR） |
| `pwa-maskable-192x192.png` / `pwa-maskable-512x512.png` | 自适应图标（全出血）  |

> 重新生成图标：脚本在 `F:\tmp\gen_pwa_icons.py`（PIL 生成，可改色/文字后重跑）

---

## 2. 本地 HTTPS 证书（已生成，如需重建）

证书位置：`F:\tools\certs\`（ca.crt / server.key / server.crt / ca.key / ext.cnf）

重建命令（git bash 或终端，需已安装 openssl）：

```bash
cd F:/tools/certs
# 1) CA 根证书（手机要装的）
openssl req -x509 -newkey rsa:2048 -nodes -keyout ca.key -out ca.crt -days 3650 -subj "/CN=AIMobile Local Dev CA"
# 2) 服务器私钥 + 签名请求
openssl req -newkey rsa:2048 -nodes -keyout server.key -out server.csr -subj "/CN=192.168.1.3"
# 3) ext.cnf 内容（IP 变了要改这里）：
#    subjectAltName=DNS:localhost,IP:192.168.1.3
#    extendedKeyUsage=serverAuth
# 4) 用 CA 签发服务器证书（有效期 ≤825 天）
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 825 -extfile ext.cnf
```

**⚠️ 电脑 IP 变化时**：改 `ext.cnf` 里的 IP → 重跑第 2~4 步 → 重启 preview。

---

## 3. 构建与启动

```bash
# 构建（产出 dist/sw.js、manifest.webmanifest、workbox-*.js、registerSW.js）
pnpm build

# 启动 HTTPS 预览（监听 0.0.0.0:4173，局域网可访问）
pnpm preview --host
```

构建成功的标志（build 输出尾部）：

```
PWA v1.3.0
mode      generateSW
precache  XX entries (XXX KiB)
files generated
  dist/sw.js
  dist/workbox-*.js
```

---

## 4. 电脑验证（最快）

1. **信任 CA**（一次性）：双击 `F:\tools\certs\ca.crt` → 安装证书 → 本地计算机 → 受信任的根证书颁发机构
2. Chrome 打开 `https://localhost:4173`
3. F12 → **Application** 面板：
   - **Manifest**：显示名称/图标/主题色 = 配置正确
   - **Service workers**：显示 `activated and is running` = SW 生效
   - **Cache Storage**：有 precache 缓存 = 离线能力就绪

---

## 5. 手机验证

### 5.1 前置：防火墙放行 4173（管理员 cmd）

```cmd
netsh advfirewall firewall add rule name="Vite Preview 4173" dir=in action=allow protocol=TCP localport=4173
```

### 5.2 手机安装 CA（完整 PWA 必须）

**鸿蒙 HarmonyOS**：

```
设置 → 安全 → 更多安全设置 → 加密与凭据 → 安装证书 → CA 证书
```

- 前置：需先设置锁屏密码
- 传输：微信文件传输助手 / 数据线 / 网盘，发 `F:\tools\certs\ca.crt`

**Android**：

```
设置 → 安全 → 加密与凭据 → 安装证书 → CA 证书
```

**iOS**：

```
打开 ca.crt（邮件/浏览器）→ 安装描述文件（设置→通用→VPN与设备管理）
→ 设置→通用→关于本机→证书信任设置→开启完全信任
```

### 5.3 访问与添加到主屏幕

1. 手机浏览器打开 `https://192.168.1.3:4173`（无警告 = CA 生效）
2. 浏览器菜单 → **添加到主屏幕**
3. 桌面图标点击打开，首次联网加载后**离线可用**

### 5.4 不装 CA 的降级情况

| 设备         | 表现                                                           |
| ------------ | -------------------------------------------------------------- |
| 鸿蒙/Android | 可点「继续访问」看页面，但 **SW 不注册** → 无法添加主屏幕/离线 |
| iOS          | 直接拒绝，无法访问                                             |

### 5.5 免装 CA 的临时方案（Cloudflare 隧道）

```bash
# 需要先下载 cloudflared（winget install Cloudflare.cloudflared 或 GitHub 下载）
cloudflared tunnel --url http://127.0.0.1:4173
# 得到一个 https://xxx.trycloudflare.com 公网地址，手机直接访问，PWA 完整
# 注意：地址每次启动会变；走公网，敏感数据慎用
```

---

## 6. 常见坑速查

| 症状                                                          | 原因                              | 解决                                           |
| ------------------------------------------------------------- | --------------------------------- | ---------------------------------------------- |
| `npm` 报 `Cannot read properties of null (reading 'matches')` | npm 不兼容 pnpm 目录结构          | **本项目禁用 npm，一律用 pnpm**                |
| `ERR_PNPM_VIRTUAL_STORE_DIR_MAX_LENGTH_DIFF`                  | node_modules 用不同 pnpm 配置创建 | 先 `pnpm i` 重建 node_modules                  |
| `EPERM: unlink ...rolldown-binding...node`                    | dev/preview 进程占用原生模块      | 先停掉所有 dev/preview 进程再安装              |
| WorkBuddy 沙箱报 `safe-delete 操作失败`                       | 沙箱拦截 pnpm 删除 node_modules   | **装依赖在用户自己的终端跑**                   |
| 安装极慢                                                      | 网络对 npm registry 不友好        | 加 `--registry https://registry.npmmirror.com` |
| 手机访问 4173 打不开                                          | 防火墙未放行                      | 见 5.1                                         |
| 手机 HTTPS 警告 / SW 不生效                                   | CA 未安装                         | 见 5.2                                         |
| 电脑 IP 变了手机连不上                                        | 证书 SAN 是旧 IP                  | 更新 ext.cnf → 重签证书 → 重启 preview         |

---

## 7. 日常操作速查（记住这三条）

```bash
# 1. 构建 + 启动 HTTPS 预览
pnpm build && pnpm preview --host

# 2. 电脑验证
#    Chrome 打开 https://localhost:4173 → Application 面板

# 3. 手机验证（前提：已装 CA、已放行 4173）
#    浏览器打开 https://192.168.1.3:4173 → 添加到主屏幕
```

> 小贴士：preview 是长驻进程，重启电脑后需重新 `pnpm preview --host`。
