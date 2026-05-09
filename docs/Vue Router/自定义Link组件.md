## 自定义 Link 组件：继承 RouterLink 并重写行为

在实际项目中，UI 组件库的按钮、菜单项等通常有自己的样式和交互规范，直接使用 `<RouterLink>` 可能无法完美融入。通过**封装/继承 `RouterLink`**，我们可以创建完全符合设计系统要求的自定义导航链接组件，同时保留路由跳转的全部能力。

---

### 1. 基础封装：保留原生 `RouterLink` 功能

最简单的方式是创建一个包装组件，使用 `v-bind="$attrs"` 透传所有属性和事件给内部的 `<RouterLink>`。

```vue
<!-- CustomLink.vue -->
<template>
  <RouterLink v-bind="$attrs">
    <slot />
  </RouterLink>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>
```

这样使用时，所有 `to`、`replace`、`active-class` 等原生属性都能正常工作。在此基础上可以叠加自定义样式。

```vue
<template>
  <CustomLink to="/about" class="my-link">关于</CustomLink>
</template>
```

---

### 2. 添加 UI 库标准化样式（例如 Element Plus 按钮）

很多 UI 库的按钮组件需要特定的类名或属性。我们可以将 `<RouterLink>` 渲染为库所期望的 DOM 结构或类。

**示例：让链接显示为 Element Plus 按钮**

```vue
<template>
  <RouterLink
    :to="to"
    :class="['el-button', { 'is-plain': plain, 'is-disabled': disabled }]"
    :disabled="disabled"
    v-bind="$attrs"
  >
    <i v-if="icon" :class="icon"></i>
    <span><slot /></span>
  </RouterLink>
</template>

<script setup>
const props = defineProps({
  to: { required: true },
  plain: Boolean,
  disabled: Boolean,
  icon: String
})
</script>
```

现在 `<CustomLink to="/home" plain icon="el-icon-home">首页</CustomLink>` 会被渲染为 Element Plus 风格的按钮式链接。

---

### 3. 重写导航行为：拦截点击添加自定义逻辑

有时需要在跳转前执行额外操作（如埋点、弹窗确认、动态权限检查）。可以通过**组合式 API 获取内部导航方法**或自己调用 `router.push` 实现。

#### 方法一：直接使用 `useRouter` 并自定义点击

```vue
<template>
  <div @click="handleClick">
    <slot />
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  to: { type: [String, Object], required: true },
  replace: Boolean
})

const router = useRouter()

const handleClick = (event) => {
  // 自定义逻辑，例如埋点
  console.log('导航触发', props.to)
  // 可选：阻止默认事件
  event.preventDefault()
  
  // 执行跳转
  if (props.replace) {
    router.replace(props.to)
  } else {
    router.push(props.to)
  }
}
</script>
```

这种方法完全重写了行为，但不支持 `active-class` 等 `RouterLink` 内置特性。适合纯自定义交互。

#### 方法二：继承原生 `RouterLink` 并扩展方法

Vue 3 中无法直接“继承”单文件组件，但可以通过**高阶组件**或**组合式函数**混入行为。

```vue
<template>
  <RouterLink ref="linkRef" :to="to" v-bind="$attrs" @click="onClick">
    <slot />
  </RouterLink>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import { ref } from 'vue'

const props = defineProps(['to'])
const linkRef = ref()

const onClick = (event) => {
  // 在原生 RouterLink 的点击处理之前执行自定义逻辑
  console.log('即将跳转到', props.to)
  // 不阻止事件，让 RouterLink 继续处理
}
</script>
```

> 注意：`RouterLink` 内部已经绑定了 `click` 事件，我们添加的 `@click` 会与其一起触发。如果不希望重复，可以控制事件顺序或使用 `event.stopPropagation`。

---

### 4. 添加高亮状态自定义（覆盖 active 类）

`RouterLink` 默认会根据当前路由自动添加 `router-link-active` 和 `router-link-exact-active` 类。我们可以直接利用这些类名编写 CSS，或者通过 `active-class` 属性指定自定义类名。

```vue
<template>
  <RouterLink
    :to="to"
    active-class="my-custom-active"
    exact-active-class="my-custom-exact-active"
  >
    <slot />
  </RouterLink>
</template>

<style>
.my-custom-active {
  color: red;
  font-weight: bold;
}
</style>
```

如果希望根据激活状态渲染不同的子内容（如显示图标变体），可以使用组合式 API 的 `useLink`：

```vue
<script setup>
import { useLink } from 'vue-router'

const props = defineProps(['to'])
const { isActive, isExactActive, href, navigate } = useLink(props)
</script>

<template>
  <a :href="href" @click="navigate" :class="{ active: isActive }">
    <span v-if="isActive">🔘</span>
    <slot />
  </a>
</template>
```

`useLink` 提供了原始的响应式状态，让你完全控制渲染内容，这是最灵活的方式。

---

### 5. 适配 UI 库的菜单组件（如 Ant Design Vue 的 `a-menu`）

Ant Design Vue 的菜单要求使用 `<a-menu-item>` 并通过 `key` 标识路由。我们可以封装一个组件将 `RouterLink` 的能力注入到菜单项中。

```vue
<!-- RouterMenuItem.vue -->
<template>
  <a-menu-item :key="to.path" @click="navigate">
    <slot />
  </a-menu-item>
</template>

<script setup>
import { useLink } from 'vue-router'

const props = defineProps({ to: { type: Object, required: true } })
const { navigate } = useLink(props)
</script>
```

使用：
```vue
<a-menu>
  <RouterMenuItem :to="{ path: '/dashboard' }">仪表盘</RouterMenuItem>
  <RouterMenuItem :to="{ path: '/settings' }">设置</RouterMenuItem>
</a-menu>
```

---

### 6. 完整的自定义 Link 组件示例（结合所有特性）

```vue
<!-- CustomRouterLink.vue -->
<template>
  <component
    :is="tag"
    :href="href"
    :class="[
      'custom-link',
      { 'custom-link--active': isActive, 'custom-link--exact': isExactActive },
      customClass
    ]"
    @click="handleClick"
  >
    <slot name="prefix" />
    <slot />
    <slot name="suffix" />
  </component>
</template>

<script setup>
import { useLink } from 'vue-router'
import { computed } from 'vue'

const props = defineProps({
  to: { type: [String, Object], required: true },
  tag: { type: String, default: 'a' },
  customClass: String,
  disabled: Boolean
})

const { href, isActive, isExactActive, navigate } = useLink(props)

const handleClick = (event) => {
  if (props.disabled) {
    event.preventDefault()
    return
  }
  // 执行自定义逻辑，比如埋点
  console.log('导航到:', props.to)
  
  // 调用 useLink 提供的导航方法
  navigate(event)
}
</script>

<style scoped>
.custom-link--active {
  color: #409eff;
  font-weight: bold;
}
.custom-link--exact {
  text-decoration: underline;
}
</style>
```

使用示例：
```vue
<CustomRouterLink to="/home" tag="div" customClass="menu-item">
  <template #prefix>🏠</template>
  首页
</CustomRouterLink>
```

---

### 7. 总结

| 需求                                 | 推荐方案                                     |
| ------------------------------------ | -------------------------------------------- |
| 保留 `RouterLink` 所有功能，仅改样式 | 用 `<RouterLink>` 加自定义类名或 `active-class` |
| 需要与 UI 库按钮/菜单结合            | 封装组件，透传属性和事件，设置合适样式类名   |
| 需要添加点击前的自定义逻辑（埋点/确认） | 使用 `useLink` 获取 `navigate` 方法并包装    |
| 需要完全控制渲染的 DOM 结构和激活状态 | 使用 `useLink` 解构响应式状态，自行渲染      |
| 需要阻止导航（如权限不足）           | 在自定义 `click` 中判断条件，不调用 `navigate` |

通过封装 `RouterLink` 或使用 `useLink`钩子，你可以创造出既符合设计系统规范又具备完整路由功能的自定义导航组件，提升项目的复用性和可维护性。