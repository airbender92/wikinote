## utils/storage.ts 存储封装解读

```typescript
// src/utils/storage.ts

const STORAGE_PREFIX = 'vue_demo_'

export function setItem(key: string, value: unknown): void {
  const data = JSON.stringify(value)
  localStorage.setItem(`${STORAGE_PREFIX}${key}`, data)
}

export function getItem<T = unknown>(key: string): T | null {
  const data = localStorage.getItem(`${STORAGE_PREFIX}${key}`)
  if (!data) return null
  try {
    return JSON.parse(data) as T
  } catch {
    return null
  }
}

export function removeItem(key: string): void {
  localStorage.removeItem(`${STORAGE_PREFIX}${key}`)
}

export function clearStorage(): void {
  localStorage.clear()
}
```

---

### 1. 存储前缀

```typescript
const STORAGE_PREFIX = 'vue_demo_'
```

| 作用 | 说明 |
|------|------|
| 命名空间隔离 | 防止与其他项目冲突 |
| 实际存储 | `vue_demo_token`、`vue_demo_userInfo` |

---

### 2. setItem 写入

```typescript
export function setItem(key: string, value: unknown): void {
  const data = JSON.stringify(value)
  localStorage.setItem(`${STORAGE_PREFIX}${key}`, data)
}
```

| 步骤 | 说明 |
|------|------|
| `JSON.stringify` | 对象转 JSON 字符串 |
| `setItem` | 写入 localStorage |

**为什么需要 JSON.stringify？**
```typescript
// localStorage 只支持字符串
localStorage.setItem('user', { name: '张三' })  // ❌ 变成 '[object Object]'
localStorage.setItem('user', JSON.stringify({ name: '张三' }))  // ✅ '{"name":"张三"}'
```

---

### 3. getItem 读取

```typescript
export function getItem<T = unknown>(key: string): T | null {
  const data = localStorage.getItem(`${STORAGE_PREFIX}${key}`)
  if (!data) return null
  try {
    return JSON.parse(data) as T
  } catch {
    return null
  }
}
```

| 步骤 | 说明 |
|------|------|
| `getItem` | 读取字符串 |
| `JSON.parse` | JSON 字符串转对象 |
| `try/catch` | 防止解析失败 |

**为什么需要 try/catch？**
```typescript
// 数据被手动修改或损坏时
const data = localStorage.getItem('vue_demo_user')
// data = 'abc123'（无效 JSON）
JSON.parse('abc123')  // ❌ 抛出异常
```

---

### 4. 泛型默认值

```typescript
getItem<T = unknown>(key: string): T | null
//         ↑
//      默认 unknown
```

| 调用 | T 类型 |
|------|--------|
| `getItem('token')` | `unknown` |
| `getItem<string>('token')` | `string` |
| `getItem<UserInfo>('user')` | `UserInfo` |

---

### 5. removeItem 删除

```typescript
export function removeItem(key: string): void {
  localStorage.removeItem(`${STORAGE_PREFIX}${key}`)
}
```

**注意：** 只删除指定的 key，不影响其他数据。

---

### 6. clearStorage 清空

```typescript
export function clearStorage(): void {
  localStorage.clear()
}
```

**危险！** 会删除 localStorage 中的**所有数据**。

---

### 7. 完整流程

```
存储对象 userInfo
    ↓
setItem('userInfo', userInfo)
    ↓
JSON.stringify → '{"name":"张三","age":18}'
    ↓
localStorage.setItem('vue_demo_userInfo', '{"name":"张三","age":18}')
    ↓
读取
    ↓
localStorage.getItem('vue_demo_userInfo') → '{"name":"张三","age":18}'
    ↓
JSON.parse → { name: '张三', age: 18 }
    ↓
返回对象
```

---

### 8. 为什么封装而不是直接用 localStorage？

| 方面 | 直接用 | 封装后 |
|------|--------|--------|
| Key 前缀 | 每次手动加 | 自动添加 |
| JSON 序列化 | 每次手动处理 | 自动处理 |
| 异常处理 | 每次 try/catch | 内部处理 |
| 换存储介质 | 改所有地方 | 只改这里 |

---

### 9. 潜在问题

```typescript
// 1. 存储大小限制（约 5MB）
setItem('largeData', hugeObject)  // 可能失败

// 2. 无法存储函数、undefined
setItem('fn', () => {})  // 函数被转成 undefined
setItem('u', undefined)   // 存储为 null

// 3. 同步操作
localStorage 是同步的，大量数据会阻塞主线程
```

---

### 10. auth.ts 如何使用

```typescript
// auth.ts
import { setItem, getItem, removeItem } from './storage'

setItem(TOKEN_KEY, token)      // 写入
getItem<string>(TOKEN_KEY)      // 读取
removeItem(TOKEN_KEY)          // 删除
```

---

需要继续了解 **request.ts（请求封装）** 吗？