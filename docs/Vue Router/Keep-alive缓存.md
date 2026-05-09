## 性能优化核心：`<keep-alive>` 缓存组件

在 Vue Router 应用中，每次切换路由默认会**销毁**离开的组件、**创建**进入的组件。如果某些页面含有复杂的表单、图表或大量数据，反复创建/销毁会导致性能下降、状态丢失（如滚动位置、输入内容）。通过 `<keep-alive>` 包裹 `<router-view>` 可以**缓存不活动的组件实例**，避免重复渲染和状态重置。

---

### 1. 为什么需要缓存？

| 场景                     | 无缓存（默认行为）                     | 有缓存（`<keep-alive>`）                |
| ------------------------ | -------------------------------------- | --------------------------------------- |
| 列表页 → 详情页 → 回列表 | 列表页重新加载数据、滚动位置重置       | 列表页保持原状态（筛选条件、滚动位置）  |
| 多标签页切换             | 每次切换都重新渲染，频繁触发接口       | 仅激活/停用，数据不丢失，接口不重复调用 |
| 包含复杂图表、富文本     | 重复初始化，CPU 开销大，可能卡顿       | 一次渲染后复用，交互流畅                |

---

### 2. 基本用法

```vue
<template>
  <div>
    <keep-alive>
      <router-view />
    </keep-alive>
  </div>
</template>
```

包裹后，所有通过 `<router-view>` 渲染的路由组件都将被缓存。

---

### 3. 精细化控制：`include` / `exclude` / `max`

#### 按组件名称缓存/排除
- `include`：只有名称匹配的组件会被缓存。
- `exclude`：名称匹配的组件不会被缓存。

> ⚠️ **必须为组件配置 `name` 选项**，否则无法匹配。

```vue
<keep-alive include="UserList,ProductList" exclude="UserDetail">
  <router-view />
</keep-alive>
```

组件中定义 `name`（选项式或组合式均可）：
```vue
<script>
export default { name: 'UserList' }
</script>
```

组合式 `<script setup>` 中需要单独定义：
```vue
<script>
export default { name: 'UserList' }
</script>
<script setup>
// 组合式逻辑
</script>
```

或者使用 `vite-plugin-vue-setup-extend` 等插件简化。

#### 限制最大缓存实例数量
```vue
<keep-alive :max="10">
  <router-view />
</keep-alive>
```
当缓存实例超过 `max` 时，最久未访问的实例会被销毁，释放内存。

---

### 4. 缓存与路由元信息结合的最佳实践

通过 `meta` 字段动态决定哪些路由需要缓存，避免硬编码 `include`。

```javascript
// router/index.js
const routes = [
  {
    path: '/list',
    component: () => import('@/views/List.vue'),
    meta: { keepAlive: true }   // 标记需要缓存
  },
  {
    path: '/detail/:id',
    component: () => import('@/views/Detail.vue'),
    meta: { keepAlive: false }  // 不需要缓存
  }
]
```

然后在根组件中根据 `$route.meta.keepAlive` 动态决定是否使用 `<keep-alive>`：

```vue
<template>
  <keep-alive>
    <router-view v-if="$route.meta.keepAlive" />
  </keep-alive>
  <router-view v-if="!$route.meta.keepAlive" />
</template>
```

或者使用两个 `<router-view>` 配合 `key` 进行更精细的控制（见第 6 节）。

---

### 5. 缓存组件的生命周期变化

被 `<keep-alive>` 缓存的组件，生命周期行为发生变化：

| 钩子                | 首次进入               | 再次进入（从缓存激活） | 离开（停用）           | 缓存满被销毁      |
| ------------------- | ---------------------- | ---------------------- | ---------------------- | ----------------- |
| `onMounted`         | 执行                   | **不再执行**           | -                      | -                 |
| `onUnmounted`       | -                      | -                      | **不再执行**           | 执行（真正销毁）  |
| `onActivated`       | 执行（`mounted` 后）   | 执行                   | -                      | -                 |
| `onDeactivated`     | -                      | -                      | 执行                   | -                 |

> **注意**：使用组合式 API 时，需要从 `vue` 中导入 `onActivated` 和 `onDeactivated`。

```vue
<script setup>
import { onActivated, onDeactivated } from 'vue'

onActivated(() => {
  // 组件被激活时：刷新数据、恢复定时器
  fetchData()
})

onDeactivated(() => {
  // 组件停用时：清除定时器、取消请求
  clearTimer()
})
</script>
```

---

### 6. 解决缓存导致的“数据不更新”问题

如果路由带参数（如 `/user/1` 和 `/user/2`）且组件被缓存，由于组件实例被复用，`onMounted` 不会再次执行，导致页面显示旧数据。解决方案有三种：

#### 方案一：监听 `$route` 变化
```vue
<script setup>
import { watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
watch(() => route.params.id, (newId) => {
  fetchUser(newId)
}, { immediate: true })
</script>
```

#### 方案二：使用 `onBeforeRouteUpdate` 守卫
```vue
<script setup>
import { onBeforeRouteUpdate } from 'vue-router'

onBeforeRouteUpdate(async (to, from, next) => {
  await fetchUser(to.params.id)
  next()
})
</script>
```

#### 方案三：给 `<router-view>` 添加 `key` 强制刷新
```vue
<keep-alive>
  <router-view :key="$route.fullPath" />
</keep-alive>
```
这样每次路径完全变化时（包括查询参数），会强制重建组件，但会失去缓存复用实例的好处，**不推荐**与 `keep-alive` 同时使用。

---

### 7. 性能优化建议与陷阱

| 建议                                                         | 原因                                                         |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| **只为需要缓存的组件开启**（使用 `include` 或 `meta` 标记）  | 无差别缓存会占用更多内存，且增加组件逻辑复杂度               |
| **合理设置 `max`**                                           | 对于无限列表页，缓存过多实例会导致内存持续增长               |
| **在 `onDeactivated` 中清理副作用**（定时器、WebSocket、全局事件） | 组件未销毁但停用，不清除会导致重复注册或内存泄露             |
| **避免在 `<keep-alive>` 内使用 `v-if` 导致多个子节点**        | `<keep-alive>` 要求只有一个子节点（通常是 `<router-view>`）  |
| **不要滥用**：对永远只访问一次的页面（如提交成功页）关闭缓存 | 浪费内存且没有实际收益                                       |

---

### 8. 完整示例：标签页导航 + 缓存

```vue
<!-- Layout.vue -->
<template>
  <div class="tabs">
    <button v-for="tab in tabs" :key="tab.name" @click="currentTab = tab.name">
      {{ tab.label }}
    </button>
  </div>
  <keep-alive :include="cachedViews">
    <router-view />
  </keep-alive>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const cachedViews = ref(['List'])   // 默认缓存列表页

const tabs = [
  { name: 'List', label: '列表', path: '/list' },
  { name: 'Detail', label: '详情', path: '/detail' }
]

const currentTab = ref(route.name)

watch(currentTab, (tabName) => {
  router.push({ name: tabName })
  // 动态添加需要缓存的组件
  if (!cachedViews.value.includes(tabName)) {
    cachedViews.value.push(tabName)
  }
})
</script>
```

---

### 总结

- **`<keep-alive>` 是提升路由切换体验的核心工具**，尤其适合需要保留用户操作状态的场景。
- 配合 `include`/`exclude` 或 `meta.keepAlive` 标记，实现精细化缓存策略。
- 使用 `onActivated` / `onDeactivated` 处理缓存组件的激活/停用逻辑。
- 注意监听路由参数变化，避免缓存导致的数据不更新问题。

合理使用 `<keep-alive>`，可以让你的单页应用既保持 SPA 的流畅性，又拥有接近原生 App 的状态保留能力。