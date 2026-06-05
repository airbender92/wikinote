## request.ts Axios 请求封装解读

### 整体结构

```typescript
class Request {
  instance: AxiosInstance      // Axios 实例
  pendingMap: Map<...>        // 防重复请求
  cacheMap: Map<...>          // 请求缓存
  cacheTime: number           // 缓存时间（5分钟）

  constructor() { ... }       // 初始化
  setupInterceptors() { ... } // 拦截器
  addPending/removePending()  // 防重
  handleUnauthorized() { ... } // 401 处理
  get/post/put/delete()       // 请求方法
}
```

---

### 1. 创建 Axios 实例

```typescript
this.instance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 15000,
})
```

| 配置 | 值 | 说明 |
|------|-----|------|
| `baseURL` | `/api` 或环境变量 | API 基础路径 |
| `timeout` | 15000ms | 15秒超时 |

---

### 2. 请求拦截器流程

```typescript
this.instance.interceptors.request.use(
  (config) => {
    // 1. 添加 Token
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // 2. 防重复请求
    this.addPending(config)

    // 3. 请求缓存（仅 GET）
    if (config.method?.toLowerCase() === 'get' && config.cache !== false) {
      // 检查缓存...
    }

    return config
  }
)
```

---

### 3. 防重复请求

```typescript
private addPending(config: CustomAxiosRequestConfig): void {
  const cacheKey = generateCacheKey(config)
  
  // 如果已存在，先取消之前的请求
  if (this.pendingMap.has(cacheKey)) {
    const controller = this.pendingMap.get(cacheKey)
    controller?.abort()
    this.pendingMap.delete(cacheKey)
  }

  const controller = new AbortController()
  config.signal = controller.signal
  this.pendingMap.set(cacheKey, controller)
}
```

**为什么需要防重复？**
```
用户快速点击两次「查询」按钮
    ↓
请求1: GET /api/users?page=1
请求2: GET /api/users?page=1
    ↓
如果没有防重：两个请求都发
如果有防重：第一个请求被取消，只发一个
```

**generateCacheKey：**
```typescript
function generateCacheKey(config): string {
  return `${method}_${url}_${JSON.stringify(params)}_${JSON.stringify(data)}`
}
// 例: "GET_/api/users_{}"_"{}"
```

---

### 4. 请求缓存

```typescript
if (config.method?.toLowerCase() === 'get' && config.cache !== false) {
  const cacheKey = generateCacheKey(config)
  const cached = this.cacheMap.get(cacheKey)
  
  if (cached && cached.expire > Date.now()) {
    // 缓存未过期，取消请求，返回缓存
    this.removePending(config)
    return Promise.reject({ __cached: true, data: cached.data })
  }
}
```

| 配置 | 说明 |
|------|------|
| `cache !== false` | 默认开启缓存 |
| `cacheTime: 5 * 60 * 1000` | 缓存 5 分钟 |

---

### 5. 响应拦截器

```typescript
this.instance.interceptors.response.use(
  (response) => {
    const { data, config } = response
    
    // 1. 移除 pending
    this.removePending(config)
    
    // 2. 缓存 GET 响应
    if (config.method === 'get') {
      cacheMap.set(cacheKey, { data, expire: Date.now() + cacheTime })
    }

    // 3. 业务错误处理
    if (code !== 0 && code !== 200) {
      if (code === 401) this.handleUnauthorized()
      if (code === 403) ElMessage.error('无权限')
      return Promise.reject(new Error(message))
    }

    return data
  },
  (error) => {
    // 处理各种 HTTP 错误
    switch (status) {
      case 401: handleUnauthorized(); break
      case 403: ElMessage.error('无权限'); break
      case 404: ElMessage.error('资源不存在'); break
      case 500: ElMessage.error('服务器错误'); break
    }
  }
)
```

---

### 6. 401 处理

```typescript
private handleUnauthorized(): void {
  removeToken()           // 清除 token
  router.push('/login')    // 跳转登录
  ElMessage.warning('登录已过期')
}
```

---

### 7. 请求方法

```typescript
get<T>(url, config?)
post<T>(url, data?, config?)
put<T>(url, data?, config?)
delete<T>(url, config?)
```

**使用示例：**
```typescript
// GET 请求
const res = await request.get<UserInfo>('/user/info')
const res = await request.get('/user/list', { params: { page: 1 } })

// POST 请求
const res = await request.post<Token>('/login', { username, password })

// 禁用缓存
request.get('/data', { cache: false })
```

---

### 8. 完整请求流程图

```
组件调用 request.get('/api/users')
    ↓
请求拦截器
    ├─ 添加 Token
    ├─ 检查缓存 → 有缓存？→ 返回缓存数据
    ├─ 检查防重 → 重复请求？→ 取消之前的
    └─ 继续发送
    ↓
服务器响应
    ↓
响应拦截器
    ├─ 检查 HTTP 状态码
    ├─ 检查业务 code
    ├─ 缓存 GET 响应
    └─ 返回 data
    ↓
组件收到数据
```

---

### 9. 核心功能总结

| 功能 | 实现方式 | 作用 |
|------|---------|------|
| Token 自动注入 | 请求拦截器 | 携带认证信息 |
| 防重复请求 | Map + AbortController | 避免并发冲突 |
| 请求缓存 | Map + 过期时间 | 减少重复请求 |
| 统一错误处理 | 响应拦截器 | 全局错误提示 |
| 401 自动跳转 | handleUnauthorized | 登录过期处理 |

---

### 10. 与 api/index.ts 的关系

```typescript
// api/index.ts
import { request } from '@/utils/request'

export const getUserInfo = () => request.get('/user/info')

// api/modules/auth.ts
import { request } from '@/utils/request'

export const login = (data) => request.post('/login', data)
```

---

### 11. 缓存 key 生成规则

```typescript
generateCacheKey(config) {
  const { url, method, params, data } = config
  return `${method}_${url}_${JSON.stringify(params)}_${JSON.stringify(data)}`
}

// 例1：GET 无参数
GET_/api/users_{}_{}

// 例2：GET 带参数
GET_/api/users_{"page":1}_{}

// 例3：POST 带数据
POST_/api/login_{}_{"username":"admin"}
```

---

### 12. Promise.reject 带缓存标识

```typescript
// 请求拦截器中返回缓存
return Promise.reject({ __cached: true, data: cached.data })

// 响应拦截器中识别
if (error.__cached) {
  return Promise.resolve(error.data)
}
```

**为什么用 reject + resolve？**
- `reject` 停止当前请求
- `resolve` 让后续 `.then()` 拿到缓存数据

---

需要继续了解 **api/index.ts** 或 **mock/index.ts** 吗？