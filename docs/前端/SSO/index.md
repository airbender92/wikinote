toolName: view_files
            
status: success
          
            
filePath: d:\wybD\Codes\demos\frontend\vue-demo\src\views\login\index.vue
          

        
            
toolName: view_files
            
status: success
          
            
filePath: d:\wybD\Codes\demos\frontend\vue-demo\src\views\login\index.vue
          
让我再看一下 `userStore.ssoLogin` 的实现来完整理解 SSO 流程。

        
            
toolName: search_by_regex
            
status: success
          
query: ssoLogin
          

        
            
toolName: search_by_regex
            
status: success
          
query: ssoLogin
          
## SSO 流程解释

### 1. 为什么在 `onMounted` 执行 SSO 检查

因为 SSO 是**外部鉴权系统回调**的流程。当用户完成 SSO 登录后，鉴权系统会通过 **redirect** 跳回当前项目，并在 URL 中带上 `sso_token` 参数。所以页面加载时必须立即检查这个参数。

### 2. SSO 完整逻辑

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   当前项目      │      │   SSO 鉴权系统   │      │   后端 API      │
│  (vue-demo)     │      │                 │      │                 │
└────────┬────────┘      └────────┬────────┘      └────────┬────────┘
         │                        │                        │
         │  1. 点击SSO登录         │                        │
         │───────────────────────>│                        │
         │                        │                        │
         │  2. 跳转到SSO登录页面    │                        │
         │<───────────────────────│                        │
         │                        │                        │
         │  3. 用户在SSO系统登录    │                        │
         │                        │                        │
         │  4. redirect回来        │                        │
         │   ?sso_token=xxx        │                        │
         │<───────────────────────│                        │
         │                        │                        │
         │  5. onMounted检测到     │                        │
         │   sso_token             │                        │
         │────────────────────────>│  6. 验证token          │
         │                        │───────────────────────>│
         │                        │                        │
         │  7. 返回项目自己的token  │                        │
         │<───────────────────────│<───────────────────────│
         │                        │                        │
         │  8. 登录成功，跳转首页   │                        │
```

### 3. 关键代码

**用户点击 SSO 登录** ([第120行](file:///d:\wybD\Codes\demos\frontend\vue-demo\src\views\login\index.vue#L120-L123)):
```ts
function handleSSOLogin() {
  const ssoUrl = `${import.meta.env.VITE_API_BASE_URL}/sso/login?redirect=${encodeURIComponent(window.location.href)}`
  window.location.href = ssoUrl
}
```

**SSO 回调处理** ([第125-140行](file:///d:\wybD\Codes\demos\frontend\vue-demo\src\views\login\index.vue#L125-L140)):
```ts
async function handleSSOCallback() {
  const ssoToken = route.query.sso_token as string
  if (!ssoToken) return

  loading.value = true
  try {
    await userStore.ssoLogin(ssoToken)  // 用 ssoToken 换取项目自己的 token
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch (error) {
    // 处理失败
  }
}
```

**Store 中的 SSO 验证** ([第44-49行](file:///d:\wybD\Codes\demos\frontend\vue-demo\src\store\modules\user.ts#L44-L49)):
```ts
async ssoLogin(ssoToken: string): Promise<void> {
  const { data } = await ssoVerifyApi(ssoToken)  // 调用后端验证 SSO token
  this.token = data.token  // 后端返回项目自己的 token
  setToken(data.token)
  await this.fetchUserInfo()
}
```

### 4. 回答你的问题

**是的，鉴权系统会 redirect 回当前项目**。流程是：
1. 用户在当前项目点击 SSO 登录
2. 跳转到 SSO 鉴权系统的登录页面（同一个浏览器的 Session 下，SSO 系统可能直接认证通过）
3. 认证完成后，**redirect 回到当前项目**的 login 页面，URL 带有 `?sso_token=xxx` 参数
4. 当前项目用这个 `sso_token` 调用后端验证，换取项目自己的 `token`