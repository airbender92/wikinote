我给你**逐行逐函数、逐模块彻底拆解**，不跳步、不省略，保证你完全看懂这个 user store 到底在干嘛、为什么这么写。

# 整体定位
这是一个 **Vue3 + Pinia + TS 后台管理系统的用户状态中心**，负责：
- 登录令牌（token）管理
- 用户信息存储、格式化、兼容后端各种奇葩结构
- 权限解析
- 登出、重置登录态
- 路由权限联动
- 未登录跳转配置
- 支持在非组件（路由守卫、axios）中使用
- 自动持久化

---

# 0. 先看导入部分
```ts
import { defineStore } from 'pinia'
import { store } from '../index'          // 你上一段发的 Pinia 实例
import { UserLoginType, UserType } from '@/api/login/types' // 接口类型
import { ElMessageBox } from 'element-plus' // 登出确认框
import { useI18n } from '@/hooks/web/useI18n' // 国际化
import { getCurrentUserInfoApi, loginOutApi } from '@/api/login' // 登录相关接口
import { getParamValueByCodeApi } from '@/api/systemSetting/param' // 后端取未登录跳转地址
import { useTagsViewStore } from './tagsView' // 标签页 store
import router, { resetRouter } from '@/router' // 路由 + 重置路由方法
import { usePermissionStoreWithOut } from './permission' // 权限 store
import { useLockStoreWithOut } from './lock' // 锁屏 store
import { getLoginRedirectHref } from '@/axios/service' // 登录跳转地址工具
```
作用：引入依赖、接口、其他 store、工具方法。

---

# 1. 常量定义
```ts
const BEARER_TOKEN_PREFIX = 'Bearer '
const NUMERIC_KEY_REGEXP = /^\d+$/
const UN_AUTH_REDIRECT_CACHE_KEY = 'UN_AUTH_REDIRECT'
```
- `Bearer `：token 标准前缀
- `/^\d+$/`：过滤纯数字 key（防止后端返回异常对象结构）
- `UN_AUTH_REDIRECT`：sessionStorage 里存“未登录要跳去哪”

---

# 2. 工具函数（核心！整个 store 的健壮性全靠它们）

## 2.1 normalizeAuthToken —— 统一 token 格式
```ts
const normalizeAuthToken = (token: unknown) => {
  const normalizedToken = pickStringValue(token)

  if (!normalizedToken) {
    return ''
  }

  if (normalizedToken.toLowerCase().startsWith(BEARER_TOKEN_PREFIX.toLowerCase())) {
    return `${BEARER_TOKEN_PREFIX}${normalizedToken.slice(BEARER_TOKEN_PREFIX.length).trim()}`
  }

  return `${BEARER_TOKEN_PREFIX}${normalizedToken}`
}
```
作用：
- 无论后端返不返回 `Bearer`，最终都统一成 `Bearer xxxx`
- 防止接口因为格式不对 401
- 兼容大小写、多余空格

## 2.2 pickStringValue —— 安全取值
```ts
const pickStringValue = (...values: unknown[]) => {
  for (const value of values) {
    if (typeof value === 'string') {
      const trimmed = value.trim()
      if (trimmed) {
        return trimmed
      }
    }
    if (typeof value === 'number') {
      return String(value)
    }
  }
  return ''
}
```
作用：
- 传入多个候选值，自动找**第一个有效字符串/数字**
- 自动去空格
- 后端字段不统一（username / userName / account）时非常有用

## 2.3 normalizePermissions —— 统一权限格式
```ts
const normalizePermissions = (value: unknown): string[] => {
  if (Array.isArray(value)) {
    return value
      .map((item) => (typeof item === 'string' ? item.trim() : String(item ?? '').trim()))
      .filter(Boolean)
  }
  if (typeof value === 'string') {
    const trimmed = value.trim()
    if (!trimmed) {
      return []
    }
    try {
      const parsed = JSON.parse(trimmed)
      return Array.isArray(parsed) ? normalizePermissions(parsed) : []
    } catch {
      return trimmed
        .split(',')
        .map((item) => item.trim())
        .filter(Boolean)
    }
  }
  return []
}
```
作用：
- 兼容数组
- 兼容 JSON 字符串数组
- 兼容逗号分隔字符串（`"user:add,user:edit"`）
- 最终一定返回干净字符串数组
- 权限指令、按钮控制全靠它

## 2.4 normalizeStoredUserInfo —— 最强兼容解析用户信息
```ts
const normalizeStoredUserInfo = (userInfo: unknown): UserType | undefined => {
  if (userInfo == null) return undefined

  if (typeof userInfo === 'string') {
    try {
      return normalizeStoredUserInfo(JSON.parse(userInfo))
    } catch {
      return undefined
    }
  }

  if (Array.isArray(userInfo) || typeof userInfo !== 'object') {
    return undefined
  }

  // 过滤纯数字 key
  const normalizedUserInfo = Object.fromEntries(
    Object.entries(userInfo as Record<string, unknown>).filter(
      ([key]) => !NUMERIC_KEY_REGEXP.test(key)
    )
  )

  // 兼容多种用户名字段
  const username = pickStringValue(
    normalizedUserInfo.username,
    normalizedUserInfo.userName,
    normalizedUserInfo.account
  )

  if (!username) return undefined

  return {
    ...normalizedUserInfo,
    username,
    account: pickStringValue(normalizedUserInfo.account) || username,
    permissions: normalizePermissions(normalizedUserInfo.roleIds) // 从 roleIds 转权限
  }
}
```
作用：
- 后端返对象、JSON 字符串都能解析
- 自动过滤异常数字 key
- 兼容 `username / userName / account`
- 自动把 `roleIds` 转成标准 `permissions` 数组
- 没有用户名直接返回 undefined，避免错误用户态

---

# 3. 内部控制变量
```ts
let isRedirectingToLogin = false
let ensureUserInfoPromise: Promise<boolean> | undefined
```
- `isRedirectingToLogin`：防止重复跳转到登录页
- `ensureUserInfoPromise`：防止重复请求用户信息（请求合并）

---

# 4. State 类型与初始值
```ts
interface UserState {
  userInfo?: UserType
  tokenKey: string
  token: string
  roleRouters?: string[] | AppCustomRouteRecordRaw[]
  rememberMe: boolean
  loginInfo?: UserLoginType
  redirectUrl?: string
  homeCommandDialogShown: boolean
}

state: () => ({
  userInfo: undefined,
  tokenKey: 'Authorization',
  token: '',
  roleRouters: undefined,
  rememberMe: true,
  loginInfo: undefined,
  redirectUrl: '/login',
  homeCommandDialogShown: false
})
```
标准用户状态，不多解释。

---

# 5. Getters —— 快捷读取
```ts
getTokenKey
getToken
getUserInfo
getRoleRouters
getRememberMe
getLoginInfo
getPermissions       // 权限列表
getRedirectUrl
getIsAdmin           // 判断是否 admin
getHomeCommandDialogShown
```
全是只读计算属性，规范用法。

---

# 6. Actions —— 业务核心

## 6.1 setTokenKey / setToken / setUserInfo …
就是赋值，**但会自动走格式化**，外部不用处理格式。

## 6.2 logoutConfirm() —— 登出确认框
```ts
ElMessageBox.confirm(...).then(async () => {
  await loginOutApi(...)
  this.reset()
})
```
点确认 → 调用登出接口 → 重置登录态

## 6.3 reset() —— 真正的“登出核心”
```ts
reset() {
  const permissionStore = usePermissionStoreWithOut()
  const tagsViewStore = useTagsViewStore()
  const lockStore = useLockStoreWithOut()

  // 清空本 store
  this.setToken('')
  this.setTokenKey('Authorization')
  this.setUserInfo(undefined)
  this.setRoleRouters([])
  // ...

  // 清空其他 store
  permissionStore.resetPermissionState()
  tagsViewStore.delAllViews()
  lockStore.resetLockInfo()

  // 重置路由
  resetRouter()

  // 跳转到登录页
  window.location.href = getLoginRedirectHref()
}
```
作用：
- 清空所有登录相关状态
- 重置路由（防止权限残留）
- 清除标签页、锁屏状态
- 强制跳转登录页，保证安全

## 6.4 logout()
直接调用 reset()，不弹框。

## 6.5 setRedirect()
```ts
getParamValueByCodeApi('UN_AUTH_REDIRECT').then(redirectUrl => {
  this.redirectUrl = ...
  sessionStorage.setItem(UN_AUTH_REDIRECT_CACHE_KEY, ...)
})
```
从后端配置中读取“未登录应该跳去哪”，存在本地。

## 6.6 ensureUserInfo() —— 路由守卫必用的“保活函数”
```ts
async ensureUserInfo(force = false) {
  if (!force && this.getUserInfo) return true

  if (!ensureUserInfoPromise) {
    ensureUserInfoPromise = getCurrentUserInfoApi()
      .then(res => {
        const userInfo = res.data?.userInfo || res.data || res
        this.setUserInfo(userInfo)
        this.setRedirect()
        return Boolean(this.getUserInfo)
      })
      .catch(() => false)
      .finally(() => {
        ensureUserInfoPromise = undefined
      })
  }
  return ensureUserInfoPromise
}
```
这是**整个系统最关键的方法之一**：
- 没有 userInfo 就自动去后端拉取
- 多次调用只会发一次请求（防重复）
- 拉取失败自动清空用户态
- 路由守卫里用它保证“一定有用户信息”

---

# 7. 持久化 & 非组件调用
```ts
persist: true
```
整个 user store 自动 localStorage 持久化。

```ts
export const useUserStoreWithOut = () => {
  return useUserStore(store)
}
```
用于：
- 路由守卫
- axios 拦截器
- 工具函数
用法：
```ts
const userStore = useUserStoreWithOut()
```

---

# 一句话总结（最精髓）
这个 user store 是一个**高度健壮、兼容后端各种结构、自带格式化、自带防重请求、自动持久化、能联动路由/权限/标签页/锁屏**的企业级用户状态中心。

你如果告诉我你**具体哪一段看不懂**（比如正则、权限解析、reset 逻辑、ensureUserInfo），我可以再单独给你拆开讲。

----

我用最直白、最本质的话给你讲清楚：
**因为这两个变量，是用来控制「整个模块行为」的，不属于某个 store 实例，也不属于某一次组件渲染。**

如果把它们放进 `state` 里，反而会出 BUG，甚至导致页面死循环、重复请求、重复跳转。

---

# 1. 先看这两个变量是干嘛的

## ① `isRedirectingToLogin = false`
```ts
let isRedirectingToLogin = false
```
作用：
**防止多次、重复跳转到登录页**

你在 `reset()` 里能看到：
```ts
if (isRedirectingToLogin) {
  return
}

isRedirectingToLogin = true
window.location.href = '...login'
isRedirectingToLogin = false
```

如果不加这个锁：
- 路由守卫多次触发
- 多个地方同时调用 logout
- 异步逻辑并发执行
就会出现：
**连续多次跳转登录页 → 页面疯狂刷新、卡死、报错**

---

## ② `ensureUserInfoPromise: Promise<boolean> | undefined`
```ts
let ensureUserInfoPromise: Promise<boolean> | undefined
```
作用：
**防止同一时间多次请求用户信息接口**

在 `ensureUserInfo()` 里：
```ts
if (!ensureUserInfoPromise) {
  ensureUserInfoPromise = getCurrentUserInfoApi().then(...)
}
return ensureUserInfoPromise
```

如果不加这个：
- 页面刚进入时，多个组件同时用 `await ensureUserInfo()`
- 路由守卫 + 导航栏 + 菜单 同时调用
就会：
**瞬间发 N 个一模一样的 /getUserInfo 请求**
浪费接口、造成竞态 bug、后端压力变大

---

# 2. 为什么必须定义在 `defineStore` 外面？

## 关键点 1：它们不是「状态」，是「运行时控制标记」
- `state` 里放的是：需要持久化、需要响应式、需要页面共享的数据
  - token
  - userInfo
  - permissions
- 而这两个只是：
  - 跳转锁
  - 请求合并锁

**它们不需要持久化，不需要响应式，不需要被组件访问。**

## 关键点 2：store 是单例，但变量要「模块级唯一」
Pinia 的 store 本身是单例，但：
- 如果你把锁放进 state
- 它会被持久化
- 会被 devtools 追踪
- 会被其他代码意外修改
- 还会变成响应式，带来不必要开销

而定义在**模块顶层**（文件最外面）：
- 整个应用生命周期里**只有一份**
- 任何地方调用这个 store，都共用同一把锁
- 不会被序列化、不会被持久化
- 外部无法访问，安全、干净、纯粹做控制

## 关键点 3：如果放 state 里会出 BUG
举个最典型的：

### 锁放 state 里 → 跳转锁失效
```ts
state: () => ({
  isRedirectingToLogin: false
})
```
结果：
- 异步流程中，多次触发 reset
- 多个地方同时判断 `if (!this.isRedirectingToLogin)`
- 全部通过，同时执行跳转
→ **页面多次刷新、死循环**

### 请求锁放 state 里 → 无法真正合并请求
因为 Promise 不能被 JSON 序列化，放进 state 会直接异常或丢失。

---

# 3. 一句话总结（最核心）
```ts
let isRedirectingToLogin = false
let ensureUserInfoPromise: Promise<boolean> | undefined
```

它们是：
**模块级的锁变量，用来控制并发、防止重复执行，
不属于用户状态，不需要响应式，不需要持久化，
所以必须定义在 defineStore 外部，作为模块私有变量。**

---

# 4. 类比一下你就彻底懂了
- `token / userInfo` → 相当于**你的身份证、房间钥匙**
  → 存在 state，要保存、要共享

- `isRedirectingToLogin` → 相当于**厕所门上的“有人/无人”锁**
  → 谁都不能带走，用完就消失，只用来防止多人同时进去

- `ensureUserInfoPromise` → 相当于**排队叫号机**
  → 一堆人同时来，只让一个人去办事，其他人等他结束

这就是为什么它们必须写在外面。