## RouterView 插槽高级用法：精细控制组件渲染

Vue Router 4 为 `<RouterView>` 组件提供了**作用域插槽**（scoped slot），让你能够完全掌控路由组件的渲染过程。通过插槽，你可以访问到当前匹配的**组件定义**、**路由信息**等，从而实现比普通 `<router-view />` 更复杂的逻辑，例如：

- 为不同路由动态包裹不同的布局组件（如带侧边栏的布局 vs 全屏布局）。
- 在渲染前后添加过渡动画 + `keep-alive` 的精细组合。
- 实现路由级的权限校验或错误边界。
- 为异步组件展示加载状态。

---

### 1. 基础语法与插槽参数

```vue
<RouterView v-slot="{ Component, route }">
  <component :is="Component" />
</RouterView>
```

**插槽 Props**：

| 属性        | 类型                                      | 说明                                                         |
| ----------- | ----------------------------------------- | ------------------------------------------------------------ |
| `Component` | `VNode` 或 `Component` 类型               | 当前路由匹配到的组件（可直接用于 `<component :is="...">`）   |
| `route`     | `RouteLocationNormalized`                 | 当前激活的路由对象（包含 `params`、`query`、`meta` 等）      |

如果使用 `<KeepAlive>` 或 `<Transition>`，你需要自己包装 `Component`。

---

### 2. 典型高级用法

#### 2.1 动态布局：根据路由 `meta` 切换不同的外层结构

许多后台管理系统需要不同页面使用不同的布局（例如登录页无需侧边栏，工作台需要头部+菜单）。利用插槽可以轻松实现：

```vue
<!-- App.vue -->
<template>
  <RouterView v-slot="{ Component, route }">
    <component :is="route.meta.layout || 'DefaultLayout'">
      <component :is="Component" />
    </component>
  </RouterView>
</template>

<script setup>
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import BlankLayout from '@/layouts/BlankLayout.vue'
</script>
```

路由配置：
```javascript
const routes = [
  { path: '/login', component: Login, meta: { layout: 'BlankLayout' } },
  { path: '/dashboard', component: Dashboard, meta: { layout: 'DefaultLayout' } }
]
```

> 注意：需要全局注册这些布局组件，或使用异步组件。

#### 2.2 组合 `Transition` 和 `KeepAlive` 并保留动画

普通用法中 `<Transition>` 和 `<KeepAlive>` 包裹 `<RouterView>` 可能无法灵活控制某些细节（例如根据路由决定是否缓存、不同的过渡效果）。插槽方式让你把控制权完全拿回手中：

```vue
<RouterView v-slot="{ Component, route }">
  <transition :name="route.meta.transition || 'fade'" mode="out-in">
    <keep-alive :include="cachedViews">
      <component :is="Component" :key="route.fullPath" />
    </keep-alive>
  </transition>
</RouterView>
```

- 你可以根据路由 `meta` 动态设置过渡名称。
- 可以同时使用 `:key` 强制重新渲染（符合预期时）。
- `cachedViews` 数组可以根据权限或用户操作动态调整。

#### 2.3 渲染前的权限校验或重定向

在插槽中，你可以获取到 `route` 对象，并决定是否渲染该组件。比如无权限时渲染一个错误组件而不是目标页面：

```vue
<RouterView v-slot="{ Component, route }">
  <component :is="hasPermission(route) ? Component : Forbidden" />
</RouterView>
```

或者在渲染前执行异步检查（例如动态加载权限配置）：

```vue
<RouterView v-slot="{ Component, route }">
  <Suspense>
    <component :is="await checkAuthAndGetComponent(route, Component)" />
  </Suspense>
</RouterView>
```

> 注意：这种方式会将异步逻辑前置到渲染过程，通常更推荐在路由守卫中处理权限，但插槽方式提供了另一种“渲染时防御”的可能性。

#### 2.4 包裹错误边界（Error Boundary）

为每个页面组件包裹一个错误边界组件，捕获子组件的错误：

```vue
<RouterView v-slot="{ Component, route }">
  <ErrorBoundary :key="route.fullPath">
    <component :is="Component" />
  </ErrorBoundary>
</RouterView>
```

错误边界组件可以利用 Vue 的 `errorCaptured` 生命周期或者官方库 `vue-error-boundary`。

#### 2.5 渲染加载状态 + 异步组件

如果路由组件是异步加载的（懒加载），在 `Component` 解析完成前，`Component` 会是 `undefined`。你可以在插槽中展示加载指示器：

```vue
<RouterView v-slot="{ Component }">
  <Suspense>
    <template #default>
      <component :is="Component" />
    </template>
    <template #fallback>
      <div>Loading...</div>
    </template>
  </Suspense>
</RouterView>
```

---

### 3. 注意事项

- **`Component` 的值在路由未匹配时是 `undefined`**，需要做防御性处理（例如渲染 `null` 或 404 组件）。
- **插槽内推荐使用 `key`**：如果你根据路由参数变化希望强制重建组件（而不是复用），可以给 `<component :is="Component">` 添加 `:key="route.fullPath"`。
- **性能**：插槽方式不会引入额外开销，因为 `Component` 已经是 Vue 内部解析好的虚拟节点。
- **与嵌套路由的组合**：如果存在嵌套 `<RouterView>`，内层的 `<RouterView>` 同样可以使用插槽，并不会冲突。

---

### 4. 完整示例：支持布局、缓存、过渡的动态渲染器

```vue
<!-- RouterViewSlot.vue 可复用组件 -->
<template>
  <RouterView v-slot="{ Component, route }">
    <component :is="route.meta.layout || 'DefaultLayout'">
      <transition :name="route.meta.transition || 'fade'" mode="out-in">
        <keep-alive :include="keepAliveIncludes">
          <component
            :is="Component"
            :key="route.meta.keepComponentKey ? route.fullPath : undefined"
          />
        </keep-alive>
      </transition>
    </component>
  </RouterView>
</template>

<script setup>
import { computed } from 'vue'
import { useStore } from 'vuex'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import BlankLayout from '@/layouts/BlankLayout.vue'

const store = useStore()
const keepAliveIncludes = computed(() => store.state.cache.cachedViews)
</script>
```

---

### 5. 与传统用法的对比

| 特性                     | 普通 `<router-view />`                  | 插槽高级用法                            |
| ------------------------ | --------------------------------------- | --------------------------------------- |
| 包裹动态布局             | 需要额外嵌套组件，或通过路由守卫替换     | 直接在插槽内根据 `route.meta` 决定      |
| 组合 `transition` 和 `keep-alive` | 写法固定，无法动态调整               | 完全可控，可针对不同路由使用不同行为    |
| 访问当前路由对象         | 需在组件内使用 `useRoute()`             | 插槽内直接提供 `route` 属性             |
| 渲染前做额外逻辑         | 只能通过守卫                            | 可以在插槽内同步或异步处理              |
| 代码可读性               | 简单直观                                | 更灵活但略微复杂                        |

---

### 总结

`RouterView` 的插槽机制将路由组件的渲染控制权完全交还给了开发者。通过它，你可以：

- 实现**动态布局**（不同路由套不同外壳）。
- 精细控制**过渡动画和缓存**（根据路由元信息动态切换）。
- 在渲染层进行**权限校验**或**错误隔离**。
- 优雅处理**异步组件加载状态**。

这比传统的 `<router-view />` 加全局配置的方式更加灵活，尤其适合大型应用的设计系统或需要高度定制渲染流程的场景。掌握这种高级用法，可以让你的路由架构更加清晰和强大。