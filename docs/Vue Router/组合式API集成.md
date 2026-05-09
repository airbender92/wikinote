## 组合式 API 集成：现代化路由守卫与自定义链接

Vue 3 + Vue Router 4 深度拥抱组合式 API，提供了与组件生命周期更紧密的守卫钩子，以及用于构建自定义导航链接的底层工具 `useLink`。

---

### 1. 组合式 API 风格的路由守卫

在 `<script setup>` 中，不能直接使用选项式 API 的 `beforeRouteEnter`、`beforeRouteUpdate`、`beforeRouteLeave`。取而代之的是 **`onBeforeRouteUpdate`** 和 **`onBeforeRouteLeave`** 两个辅助函数（`beforeRouteEnter` 没有直接替代品，因为组件实例在进入时尚未创建；如果需要用到，仍需使用选项式 API 或配合 `next` 回调）。

#### `onBeforeRouteLeave`：离开组件前的守卫

- **触发时机**：用户即将离开当前组件对应的路由时。
- **常见用途**：阻止未保存编辑的意外跳转、清理定时器等。

```vue
<script setup lang="ts">
import { onBeforeRouteLeave } from 'vue-router'
import { ref } from 'vue'

const hasUnsavedChanges = ref(true)

onBeforeRouteLeave((to, from, next) => {
  if (hasUnsavedChanges.value) {
    const confirm = window.confirm('有未保存的更改，确定离开吗？')
    confirm ? next() : next(false)
  } else {
    next()
  }
})
</script>
```

> ⚠️ 与选项式 API 一样，必须调用 `next()`，否则导航会挂起。

#### `onBeforeRouteUpdate`：复用组件时响应参数变化

- **触发时机**：当同一个组件被复用（例如从 `/user/1` 跳转到 `/user/2`）且路由参数变化时。
- **常见用途**：根据新参数重新获取数据、更新页面内容。

```vue
<script setup lang="ts">
import { onBeforeRouteUpdate } from 'vue-router'
import { ref } from 'vue'
import { fetchUser } from '@/api'

const userData = ref(null)
const route = useRoute()

// 首次加载获取数据
fetchUser(route.params.id).then(data => userData.value = data)

// 参数变化时再次获取
onBeforeRouteUpdate(async (to, from, next) => {
  userData.value = await fetchUser(to.params.id)
  next()   // 必须调用
})
</script>
```

> 对比：在选项式 API 中，你需要分别处理 `beforeRouteUpdate` 和 `watch`；组合式 API 让逻辑更加集中。

#### 为什么没有 `onBeforeRouteEnter`？

`beforeRouteEnter` 守卫在组件实例尚未创建时调用，无法访问 `this` 或组合式 API 变量。Vue Router 4 没有提供组合式 API 版本的 `onBeforeRouteEnter`，因为它的用法天然依赖 `next` 回调来获取组件实例。若确实需要，可以混用选项式 API，或使用 `setup` 函数与 `getCurrentInstance()` 手动处理，但通常不推荐。

---

### 2. `useLink`：获取底层导航属性，构建自定义链接

`<RouterLink>` 组件是一个封装好的完整链接，但有时你需要完全控制渲染的 DOM 结构（例如按钮、自定义标签、带图标的混合元素）。这时可以使用 **`useLink`** 组合式函数，它返回 `RouterLink` 内部使用的响应式状态和方法。

#### `useLink` 返回值

| 属性/方法        | 类型                               | 说明                                                         |
| ---------------- | ---------------------------------- | ------------------------------------------------------------ |
| `route`          | `RouteLocationRaw`                 | 解析后的路由位置对象（基于传入的 `to`）                      |
| `href`           | `ComputedRef<string>`              | 生成的实际 URL（可用于普通 `<a>` 的 `href`）                 |
| `isActive`       | `ComputedRef<boolean>`             | 当前路由是否匹配该链接                                       |
| `isExactActive`  | `ComputedRef<boolean>`             | 是否精确匹配（路径完全一致）                                 |
| `navigate`       | `() => Promise<void>`              | 执行导航的方法，可绑定到点击事件                             |

#### 基础示例：自定义按钮式链接

```vue
<script setup lang="ts">
import { useLink } from 'vue-router'

const props = defineProps<{ to: any }>()
const { href, navigate, isActive, isExactActive } = useLink(props)
</script>

<template>
  <button
    :class="{ active: isActive, 'exact-active': isExactActive }"
    @click="navigate"
  >
    <slot />
    <!-- 自定义显示激活状态 -->
    <span v-if="isActive">🔘</span>
  </button>
</template>
```

使用该组件：
```vue
<CustomLink to="/about">关于我们</CustomLink>
```

#### 高级示例：仿 Ant Design 的 `a` 标签 + 高亮

```vue
<template>
  <a
    :href="href"
    :class="['custom-link', { 'router-link-active': isActive }]"
    @click="navigate"
  >
    <slot name="prefix" />
    <slot />
    <slot name="suffix" />
  </a>
</template>

<script setup>
import { useLink } from 'vue-router'
const props = defineProps({ to: { type: [String, Object], required: true } })
const { href, navigate, isActive } = useLink(props)
</script>
```

#### 何时使用 `useLink` vs 直接使用 `RouterLink`？

- **简单场景**：直接使用 `<RouterLink>`，它已经处理了 `active` 类、滚动行为、无障碍属性。
- **需要完全自定义渲染**（如按钮、卡片、`li` 元素等）或需要拦截导航逻辑时，使用 `useLink` 自行构建。
- **在非组件模板代码中手动触发导航**：使用 `router.push` / `router.replace`，不需要 `useLink`。

---

### 3. 组合式 API 与选项式 API 混用注意

- **`onBeforeRouteLeave` / `onBeforeRouteUpdate` 只能在 `setup` 或 `<script setup>` 中调用**，若组件使用了选项式 API，应使用对应的 `beforeRouteLeave` 等选项。
- 同一个组件中可以同时存在组合式守卫和选项式守卫，它们都会触发（执行顺序：组合式先注册的先执行）。但建议只使用一种风格，避免混乱。

---

### 4. 完整示例：结合守卫 + useLink 的自定义链接组件

```vue
<!-- UserNav.vue -->
<script setup>
import { onBeforeRouteLeave, useLink } from 'vue-router'
import { ref } from 'vue'

const props = defineProps({ to: Object })
const { isActive, navigate } = useLink(props)

const editing = ref(false)

onBeforeRouteLeave((to, from, next) => {
  if (editing.value) {
    const ok = window.confirm('编辑未保存，确定离开？')
    ok ? next() : next(false)
  } else {
    next()
  }
})
</script>

<template>
  <div
    class="user-nav-item"
    :class="{ active: isActive }"
    @click="navigate"
  >
    <slot />
  </div>
</template>
```

---

### 总结

| 组合式 API 工具          | 对应功能                         | 适用场景                           |
| ------------------------ | -------------------------------- | ---------------------------------- |
| `onBeforeRouteLeave`     | 组件离开守卫                     | 阻止未保存的修改离开页面           |
| `onBeforeRouteUpdate`    | 参数更新守卫                     | 同一组件复用且参数变化时重新加载   |
| `useLink`                | 暴露 `RouterLink` 内部状态和方法 | 构建完全自定义的导航链接           |

通过组合式 API，你可以将路由守卫和导航逻辑与组件的响应式状态紧密结合，同时利用 `useLink` 创造出更灵活的 UI 组件，而不再受限于 `<RouterLink>` 的内置结构。