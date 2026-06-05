## api.d.ts 类型定义解读

```typescript
// src/types/api.d.ts

/** API 响应结构 */
interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}

/** 登录请求参数 */
interface LoginRequest {
  username: string
  password: string
}

/** 登录响应 */
interface LoginResponse {
  token: string
  refreshToken: string
  expiresIn: number
}

/** 分页响应 */
interface PageResult<T> {
  list: T[]
  total: number
  page: number
  pageSize: number
}
```

---

### 1. 泛型接口

```typescript
interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}
```

| 语法 | 含义 |
|------|------|
| `<T = unknown>` | 泛型参数，默认值为 `unknown` |
| `T` | data 字段的类型，由调用者指定 |

**使用示例：**

```typescript
// 不指定 T，默认用 unknown
const res1: ApiResponse

// 指定 T 为具体类型
const res2: ApiResponse<UserInfo>
const res3: ApiResponse<MenuItem[]>
```

---

### 2. 泛型与具体类型对比

```typescript
// 不使用泛型：每个接口都要写
interface UserResponse {
  code: number
  message: string
  data: UserInfo
}

interface MenuResponse {
  code: number
  message: string
  data: MenuItem[]
}

// 使用泛型：一套搞定
interface ApiResponse<T> {
  code: number
  message: string
  data: T  // T 由调用者决定
}
```

---

### 3. 具体接口定义

```typescript
interface LoginRequest {
  username: string
  password: string
}
```

| 属性 | 类型 | 说明 |
|------|------|------|
| `username` | string | 用户名 |
| `password` | string | 密码 |

```typescript
interface LoginResponse {
  token: string
  refreshToken: string
  expiresIn: number
}
```

| 属性 | 类型 | 说明 |
|------|------|------|
| `token` | string | 访问令牌 |
| `refreshToken` | string | 刷新令牌 |
| `expiresIn` | number | 过期时间（秒） |

---

### 4. 分页响应泛型

```typescript
interface PageResult<T> {
  list: T[]
  total: number
  page: number
  pageSize: number
}
```

**使用示例：**

```typescript
// 用户分页
PageResult<UserInfo>
// 等价于
{
  list: UserInfo[]
  total: number
  page: number
  pageSize: number
}

// 订单分页
PageResult<Order>
// 等价于
{
  list: Order[]
  total: number
  page: number
  pageSize: number
}
```

---

### 5. 类型层级关系

```
ApiResponse<T>           → 最外层响应包装
    ├── code
    ├── message
    └── data: T
            │
            ├── LoginResponse        → 登录接口
            ├── UserInfo             → 用户信息
            ├── MenuItem[]           → 菜单列表
            └── PageResult<T>        → 分页响应
                    └── list: T[]
```

---

### 6. 实际使用场景

```typescript
// 登录接口
POST /api/login
Request:  LoginRequest
Response: ApiResponse<LoginResponse>

// 获取用户信息
GET /api/user/info
Response: ApiResponse<UserInfo>

// 获取用户列表（分页）
GET /api/users?page=1&pageSize=10
Response: ApiResponse<PageResult<UserInfo>>
```

---

### 7. 为什么需要这些类型？

| 类型 | 解决的问题 |
|------|-----------|
| `ApiResponse<T>` | 统一响应格式，data 类型安全 |
| `LoginRequest` | 登录参数类型检查 |
| `LoginResponse` | 登录响应数据访问 |
| `PageResult<T>` | 分页数据通用结构 |

---

### 8. 与其他文件的关系

```typescript
// user.ts 中使用
import type { LoginRequest, LoginResponse } from '@/types/api'

async login(credentials: LoginRequest): Promise<void> {
  const { data } = await loginApi(credentials)
  // data 类型为 LoginResponse
}
```

---

需要继续了解 **路由配置** 吗？