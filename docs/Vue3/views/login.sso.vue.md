## 单点登录（SSO）逻辑

在 `login/index.vue` 中确实只是一个**跳转占位**：

```typescript
function handleSSOLogin() {
  const ssoUrl = `${import.meta.env.VITE_API_BASE_URL}/sso/login?redirect=${encodeURIComponent(window.location.href)}`
  window.location.href = ssoUrl
}
```

---

### 实际逻辑流程

```
用户点击「单点登录」
    ↓
跳转到 SSO 授权页面
window.location.href = 'http://后端/sso/login?redirect=当前页面'
    ↓
用户在 SSO 系统完成登录
    ↓
SSO 系统回调到前端，带上 token
    ↓
前端解析 token，完成登录
```

---

### 为什么这里没有完整实现？

| 原因 | 说明 |
|------|------|
| SSO 由后端实现 | 登录页面只是跳转入口 |
| 回调地址由后端指定 | 本项目只是拼接 URL |

---

### 实际项目中 SSO 的完整流程

```typescript
// 方式一：URL 参数传递 token（当前项目的思路）
window.location.href = '/sso/login?redirect=当前页'

// SSO 登录成功后回调：
// http://前端/login?sso_token=xxx&redirect=/dashboard
```

```typescript
// 或者在后端完成登录后重定向
// http://前端/login?token=xxx&redirect=/dashboard
```

---

### 登录页面需要的补充逻辑

如果后端采用 **URL 参数回调** 方式，登录页还需要处理：

```typescript
// 从 URL 解析 SSO token
onMounted(() => {
  const ssoToken = route.query.sso_token as string
  if (ssoToken) {
    // 换取正式 token 或直接登录
    handleSSOLoginCallback(ssoToken)
  }
})

async function handleSSOLoginCallback(ssoToken: string) {
  try {
    // 调用后端接口，用 SSO token 换取正式 token
    const { data } = await ssoLoginApi(ssoToken)
    userStore.setToken(data.token)
    await userStore.fetchUserInfo()
    router.push(route.query.redirect as string || '/')
  } catch (error) {
    ElMessage.error('SSO 登录失败')
  }
}
```

---

### 当前代码的问题

```typescript
function handleSSOLogin() {
  // 只做了跳转，没有回调处理
  window.location.href = ssoUrl
}
```

**缺失的部分：** SSO 登录成功后，**回调回来时的处理逻辑**。

---

### 如果要完善 SSO

```typescript
// 1. 跳转到 SSO
function handleSSOLogin() {
  const redirect = encodeURIComponent(window.location.origin + '/login')
  const ssoUrl = `${import.meta.env.VITE_API_BASE_URL}/sso/login?redirect=${redirect}`
  window.location.href = ssoUrl
}

// 2. 处理回调（需要在页面加载时检查）
onMounted(async () => {
  const token = route.query.token as string
  if (token) {
    // SSO 回调携带了 token
    await userStore.loginBySSOToken(token)
  }
})
```

---

### 总结

| 项目 | 当前状态 | 说明 |
|------|---------|------|
| 跳转 | ✅ 已实现 | 跳转到 SSO 授权页 |
| 回调处理 | ❌ 未实现 | 需要根据后端回调方式补充 |

SSO 逻辑需要**前后端配合**，前端只是跳转到后端，真正的登录认证在后端完成。

---

需要继续了解 **mock/index.ts** 吗？