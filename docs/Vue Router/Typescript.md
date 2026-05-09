## TypeScript 支持：强类型路由配置

在基于 TypeScript 的 Vue 3 项目中使用 Vue Router，不仅能享受代码提示和类型检查，还能通过**强类型路由配置**大幅提升项目的可维护性——避免手写字符串路径、参数名错误，以及导航时传错参数类型等问题。

---

### 1. 基础类型：`RouteRecordRaw`

创建路由时，官方提供了 `RouteRecordRaw` 类型来约束路由配置：

```typescript
// router/index.ts
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/user/:id',
    name: 'user',
    component: () => import('@/views/UserView.vue'),
    props: true
  },
  {
    path: '/about',
    name: 'about',
    component: () => import('@/views/AboutView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
```

`RouteRecordRaw` 会自动提示 `path`、`name`、`component`、`children` 等字段，防止拼写错误。

---

### 2. 类型安全的导航：为 `useRouter()` 增强类型

Vue Router 内置的类型系统对 `push`、`replace` 的参数做了基础类型约束，但无法自动关联**路由名称与参数类型**。不过我们可以通过**模块增强**（Module Augmentation）手动建立路由名称 → 参数类型的映射。

#### 定义路由参数类型映射

```typescript
// router/types.ts 或直接在 router/index.ts 中
import 'vue-router'

declare module 'vue-router' {
  interface RouteNamedMap {
    'user': {      // 路由名称必须与 routes 中的 name 一致
      params: { id: string | number }   // 注意：实际 params 中 id 会是 string
      query?: { tab?: string; page?: number }
    }
    'about': {
      params: {}   // 没有参数
      query?: {}
    }
    // 可以继续添加其他路由...
  }
}
```

**注意**：Vue Router 底层实际会把 `params.id` 解析为字符串，但上述类型可以让你在编码时获得提示。

#### 使用时获得参数类型提示

```vue
<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

// 现在调用 push 时，如果 name 为 'user'，会自动要求 params 中包含 id
function goToUser(id: number) {
  router.push({
    name: 'user',
    params: { id }   // 类型安全，必须提供 id
    // query: { page: 1 }   // 可选，但会被类型检查
  })
}
</script>
```

> 上述模块增强需要手动维护，社区方案如 `unplugin-vue-router` 可以自动从文件结构生成类型，但官方推荐的方式仍是显式声明。

---

### 3. 组合式 API 中的类型安全：`useRoute` + 泛型

`useRoute()` 返回的 `RouteLocationNormalized` 类型本身已经包含 `params` 和 `query` 的基础类型（`Record<string, string | string[]>`）。我们可以通过**泛型**或**类型断言**来获得精确的类型：

#### 方法一：自定义 Hook 封装

```typescript
// composables/useTypedRoute.ts
import { useRoute } from 'vue-router'
import type { RouteNamedMap } from '@/router/types'

export function useTypedRoute<T extends keyof RouteNamedMap>() {
  const route = useRoute()
  return {
    params: route.params as RouteNamedMap[T]['params'],
    query: route.query as RouteNamedMap[T]['query']
  }
}
```

使用：
```vue
<script setup lang="ts">
const { params, query } = useTypedRoute<'user'>()
console.log(params.id)   // 类型为 string | number
</script>
```

#### 方法二：直接使用类型断言（简单场景）

```vue
<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
const userId = route.params.id as string
</script>
```

---

### 4. 更先进的方案：`vue-router/auto` 实验性类型生成

Vue Router 官方实验性支持从 `pages/` 目录自动推断路由类型。安装 `unplugin-vue-router` 后，可以自动生成 `typed-router.d.ts`，实现全自动类型安全。

```bash
npm install -D unplugin-vue-router
```

配置 `vite.config.ts`：
```typescript
import VueRouter from 'unplugin-vue-router/vite'

export default {
  plugins: [
    VueRouter({
      routesFolder: 'src/pages'
    }),
    // ...其他插件
  ]
}
```

之后 `$router` 和 `$route` 会自动获得完整的路由类型提示，无需手动声明映射。

---

### 5. 利用 `defineProps` 接收路由参数（`props: true` 时）

当在路由中开启 `props: true`，组件可以通过 `defineProps` 直接接收 `params`，此时 TypeScript 可以完美推断类型：

```typescript
// UserView.vue
const props = defineProps<{
  id: string   // 与路由配置中的 :id 对应
}>()
```

然后在路由配置中开启 `props: true`，路由参数会自动注入为组件 props。

---

### 6. 总结：强类型路由的收益

| 场景                     | 常见的运行时错误                          | TypeScript 解决方案                              |
| ------------------------ | ----------------------------------------- | ------------------------------------------------ |
| 跳转时写错路由名称       | 页面空白，控制台报 `No match found`       | 模块增强后，`name: 'usr'` 直接报错不存在         |
| `params` 参数名拼写错误  | 组件中取到 `undefined`                    | 类型提示 `params: { id: string }` 强制你写 `id`  |
| `query` 类型错误（传数字）| URL 变成 `?page=%5Bobject%20Object%5D`    | 编译时报错，要求转换为字符串                     |
| 重构路由路径             | 全局搜索字符串路径，容易遗漏              | 使用 `name` 进行跳转，路径修改只影响配置         |

通过上述方法，可以将路由配置的潜在错误从**运行时**提前到**编译时**，尤其在大型项目中显著提升协作效率和代码健壮性。建议小型项目至少使用 `RouteRecordRaw` 约束配置，中大型项目则引入模块增强或自动生成方案。