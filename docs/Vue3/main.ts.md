## main.ts 完整解读

```typescript
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'
import pinia from './store'
import { setupGuards } from './router/guards'
import { permission } from './directives/permission'

import './styles/global.scss'

const app = createApp(App)

// 注册 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 注册自定义指令
app.directive('permission', permission)

// 使用插件
app.use(pinia)
app.use(router)
app.use(ElementPlus, {
  locale: zhCn,
})

// 设置路由守卫
setupGuards(router)

app.mount('#app')
```

### 执行顺序图

```
1. 创建应用
       ↓
2. 注册全局资源（图标、指令）
       ↓
3. 安装插件（pinia、router、ElementPlus）
       ↓
4. 设置路由守卫
       ↓
5. 挂载到 DOM
```

### 逐段解析

#### 第一部分：导入依赖

```typescript
import { createApp } from 'vue'           // Vue 核心
import ElementPlus from 'element-plus'    // UI 组件库
import 'element-plus/dist/index.css'     // Element Plus 样式
import zhCn from 'element-plus/es/locale/lang/zh-cn'  // 中文语言包
import * as ElementPlusIconsVue from '@element-plus/icons-vue'  // 图标库
```

#### 第二部分：创建应用实例

```typescript
const app = createApp(App)
```

这行代码的意思是：

```
createApp(App) 创建一个应用实例
        ↓
app 是一个 Vue 应用对象
        ↓
app 上有 .use() .component() .directive() .mount() 等方法
```

#### 第三部分：注册全局组件（图标）

```typescript
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}
```

这段代码的作用是：

```
ElementPlusIconsVue 包含所有图标：
{
  "User": IconUserComponent,
  "Lock": IconLockComponent,
  "Home": IconHomeComponent,
  ... 共 70+ 个图标
}
        ↓
遍历并全局注册
        ↓
模板中可以直接用 <el-icon><User /></el-icon>
```

#### 第四部分：注册自定义指令

```typescript
app.directive('permission', permission)
```

注册后，模板中可以使用 `v-permission` 指令：

```vue
<button v-permission="'user:delete'">删除</button>
```

#### 第五部分：安装插件

```typescript
app.use(pinia)       // 状态管理
app.use(router)      // 路由管理
app.use(ElementPlus, { locale: zhCn })  // UI + 中文
```

| 插件 | 全局注入内容 |
|------|------------|
| `pinia` | `this.$store` / `useStore()` |
| `router` | `this.$router` / `useRouter()` |
| `ElementPlus` | 所有 UI 组件 + 中文语言 |

#### 第六部分：路由守卫

```typescript
setupGuards(router)
```

在路由切换前进行权限校验（如检查登录状态）。

#### 第七部分：挂载

```typescript
app.mount('#app')
```

```
<div id="app"></div>  ← index.html 中的容器
        ↓
Vue 应用渲染到这个 div 中
```

---

### 完整生命周期

```
用户打开页面
    ↓
浏览器下载 index.html
    ↓
执行 <script type="module" src="/src/main.ts">
    ↓
┌─────────────────────────────┐
│       main.ts 执行           │
│  1. createApp(App)          │
│  2. 注册图标、指令、插件      │
│  3. 设置路由守卫            │
│  4. mount('#app')           │
└─────────────────────────────┘
    ↓
App.vue 组件开始渲染
    ↓
<router-view> 渲染对应页面
```

---

### 为什么顺序很重要？

| 顺序 | 必须先执行 | 原因 |
|------|----------|------|
| `app.use(pinia)` 在前 | ✅ | 路由守卫中需要用到 Pinia Store |
| `app.use(router)` 在前 | ✅ | Element Plus 内部可能用到路由 |
| `setupGuards(router)` 在后 | ✅ | 路由安装完成后才能设置守卫 |
| `app.mount()` 最后 | ✅ | 所有配置完成后才能渲染 |

---

需要继续了解 **路由配置** 吗？