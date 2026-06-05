## views/login/index.vue 登录页面解读

### 整体结构

```
login/index.vue
├── <template>
│   ├── .login-container (背景容器)
│   │   └── .login-card (登录卡片)
│   │       ├── .login-header (标题区)
│   │       ├── <el-form> (登录表单)
│   │       └── .login-footer (底部链接)
│   └── <script setup> (逻辑)
└── <style scoped> (样式)
```

---

### 模板结构

```vue
<div class="login-container">
  <div class="login-card">
    <!-- 标题 -->
    <div class="login-header">
      <h1>Vue Demo</h1>
      <p>企业级管理后台</p>
    </div>
    
    <!-- 表单 -->
    <el-form :model="loginForm" :rules="rules">
      <el-form-item prop="username">
        <el-input v-model="loginForm.username" ... />
      </el-form-item>
      <el-form-item prop="password">
        <el-input v-model="loginForm.password" type="password" ... />
      </el-form-item>
      <el-form-item>
        <el-checkbox v-model="rememberMe">记住我</el-checkbox>
      </el-form-item>
      <el-form-item>
        <el-button :loading="loading" @click="handleLogin">登 录</el-button>
      </el-form-item>
    </el-form>
    
    <!-- 底部 -->
    <div class="login-footer">
      <el-link>单点登录</el-link>
    </div>
  </div>
</div>
```

---

### script setup 逻辑

#### 1. 数据定义

```typescript
const formRef = ref<FormInstance>()     // 表单引用
const loading = ref(false)              // 加载状态
const rememberMe = ref(false)           // 记住我

const loginForm = reactive<Credentials>({
  username: '',
  password: '',
})
```

#### 2. 表单验证规则

```typescript
const rules = reactive<FormRules>({
  username: [
    { required: true, message: '请输入账号', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6位', trigger: 'blur' },
  ],
})
```

#### 3. 记住账号功能

```typescript
// 页面加载时读取记住的账号
const savedUsername = localStorage.getItem('vue_demo_saved_username')
if (savedUsername) {
  loginForm.username = savedUsername
  rememberMe.value = true
}
```

#### 4. 登录处理

```typescript
async function handleLogin() {
  const form = formRef.value
  if (!form) return

  // 表单验证
  await form.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      // 调用 store 登录
      await userStore.login(loginForm)
      
      // 记住账号
      if (rememberMe.value) {
        localStorage.setItem('vue_demo_saved_username', loginForm.username)
      } else {
        localStorage.removeItem('vue_demo_saved_username')
      }
      
      ElMessage.success('登录成功')
      
      // 跳转到来源页或首页
      const redirect = (route.query.redirect as string) || '/'
      router.push(redirect)
      
    } catch (error) {
      ElMessage.error(err.message || '登录失败')
    } finally {
      loading.value = false
    }
  })
}
```

#### 5. SSO 单点登录

```typescript
function handleSSOLogin() {
  const ssoUrl = `${import.meta.env.VITE_API_BASE_URL}/sso/login?redirect=${encodeURIComponent(window.location.href)}`
  window.location.href = ssoUrl
}
```

---

### 登录流程图

```
用户输入账号密码
    ↓
点击登录按钮
    ↓
form.validate() 表单验证
    ↓
├─ 验证失败 → 提示错误，不提交
└─ 验证成功 → 继续
    ↓
userStore.login(loginForm)
    ↓
├─ 成功 → 保存账号 → 提示成功 → 跳转来源页/首页
└─ 失败 → 提示错误信息
    ↓
finally → loading = false
```

---

### 样式特点

```scss
.login-container {
  // 渐变背景
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  
  // 毛玻璃效果
  .login-card {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
  }
}
```

| 效果 | 技术 |
|------|------|
| 渐变背景 | `linear-gradient` |
| 毛玻璃 | `backdrop-filter: blur(10px)` |
| 阴影 | `box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3)` |

---

### 与 store 的交互

```typescript
// 调用 userStore.login()
await userStore.login(loginForm)

// 内部调用链：
user.login(loginForm)
    ↓
loginApi(loginForm)  // 发送登录请求
    ↓
setToken(token)      // 保存 token
    ↓
fetchUserInfo()      // 获取用户信息
    ↓
登录完成
```

---

### 记住账号的安全考虑

```typescript
// 只保存用户名，不保存密码
localStorage.setItem('vue_demo_saved_username', loginForm.username)

// 密码永远不会本地存储
```

---

### redirect 参数的作用

```
用户访问 /dashboard（需要权限）
    ↓
未登录，重定向到 /login?redirect=/dashboard
    ↓
登录成功后
    ↓
router.push('/dashboard')  → 回到原页面
```

---

需要继续了解 **dashboard/index.vue** 或 **mock/index.ts** 吗？