`slot`（插槽）是 Vue 中一个非常强大的内容分发机制，它让你可以像在 HTML 标签里写子元素一样，向组件内部传递结构化的内容。

简单理解：**组件把一部分渲染的“占位符”暴露出来，由父组件来决定这块区域具体渲染什么**。

---

## 一、为什么需要插槽？

假如你写一个 `<Card>` 组件，希望它的样子是：

```
┌───────────────┐
│  标题（可定制） │
│  内容（可定制） │
│  底部按钮（可选）│
└───────────────┘
```

如果没有插槽，你可能需要传很多 `props`（`title`、`content`、`buttonText`…），还要支持 HTML 结构，非常麻烦。用插槽，父组件直接写：

```vue
<Card>
  <h2>我的标题</h2>
  <p>这部分是内容，可以放任何东西</p>
  <template #footer>
    <button>确认</button>
  </template>
</Card>
```

Card 组件内部通过 `<slot>` 标签决定这些内容渲染的位置。

---

## 二、基础用法（默认插槽）

**子组件 Card.vue：**

```vue
<template>
  <div class="card">
    <div class="header">
      <!-- 如果有标题插槽就显示，没有就显示默认文字 -->
      <slot name="header">默认标题</slot>
    </div>
    <div class="body">
      <!-- 默认插槽：不带 name -->
      <slot>这里是没有传入内容时的默认内容</slot>
    </div>
    <div class="footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>
```

**父组件使用：**

```vue
<Card>
  <template #header>
    <h1>自定义标题</h1>
  </template>
  
  这是放在默认插槽里的文本（会替换默认内容）
  
  <template #footer>
    <button>操作按钮</button>
  </template>
</Card>
```

---

## 三、具名插槽 (named slots)

每个 `<slot>` 可以通过 `name` 属性起一个名字。使用 `v-slot:header` 或缩写 `#header` 来指定内容放到哪个插槽。

```vue
<!-- 子组件 -->
<slot name="header"></slot>
<slot name="main"></slot>
<slot name="footer"></slot>
```

```vue
<!-- 父组件 -->
<MyComponent>
  <template #header>顶部内容</template>
  <template #main>中间内容</template>
  <template #footer>底部内容</template>
</MyComponent>
```

注意：**没有名字的 `<slot>` 就是默认插槽，隐含 `name="default"`**。可以同时使用默认插槽和具名插槽。

---

## 四、作用域插槽 (scoped slots)

**它是插槽的高级用法**：子组件可以把内部的一些数据传给父组件，让父组件决定如何展示。

例如一个 `<DataTable>` 组件，它循环数据并希望由外部决定每一行怎么渲染：

```vue
<!-- DataTable.vue -->
<template>
  <table>
    <tr v-for="item in data" :key="item.id">
      <td>
        <!-- 把 item 传递给父组件的作用域插槽 -->
        <slot name="row" :row="item"></slot>
      </td>
    </tr>
  </table>
</template>

<script setup>
defineProps(['data'])
</script>
```

**父组件使用：**

```vue
<DataTable :data="users">
  <template #row="{ row }">
    <!-- 拿到子组件传过来的 row 对象 -->
    <span>{{ row.name }} - {{ row.age }}岁</span>
  </template>
</DataTable>
```

这里的 `#row="{ row }"` 就是接收子组件暴露的 `row` 属性。你也可以解构，也可以直接用 `slotProps` 对象。

---

## 五、动态插槽名（Vue 3）

允许用变量来决定使用哪个具名插槽：

```vue
<template #[dynamicSlotName]>
  ...
</template>
```

```js
const dynamicSlotName = ref('header')
```

---

## 六、渲染作用域

父组件模板里的插槽内容，**只能访问父组件的数据**，不能访问子组件的数据（除非使用作用域插槽，子组件暴露数据）。

- **正确**：插槽里的 `{{ message }}` 来自父组件的 `message`
- **需要通过作用域插槽**才能拿到子组件的 `row.item`

---

## 七、在组合式 API 中访问插槽 (`useSlots()`)

如果你需要在 `<script setup>` 中获取插槽的内容或判断某个插槽是否存在，可以使用 `useSlots()`：

```vue
<script setup>
import { useSlots } from 'vue'
const slots = useSlots()
console.log(slots.header)  // 是否存在 header 插槽的函数
</script>
```

`useSlots()` 返回的对象等同于 `this.$slots`（选项式 API）。

---

## 八、与之前主题的关联

在之前讨论的 `app.config.errorHandler` 或 `provide/inject` 中，插槽并不直接相关，但它们是构建可复用组件库的核心。例如一个全局的 `<ErrorBoundary>` 组件就可以利用默认插槽：

```vue
<ErrorBoundary>
  <!-- 这里放任何可能出错的组件 -->
  <SomeBuggyComponent />
</ErrorBoundary>
```

ErrorBoundary 内部用 `<slot />` 渲染子组件，并配合 `onErrorCaptured` 捕获错误并展示 fallback UI。

---

## ✅ 总结表

| 类型 | 写法（父组件） | 子组件定义 | 适用场景 |
|------|--------------|-----------|----------|
| **默认插槽** | `<Comp>内容</Comp>` | `<slot>` | 单一内容替换 |
| **具名插槽** | `<template #header>...` | `<slot name="header">` | 多个独立位置 |
| **作用域插槽** | `<template #row="{ row }">` | `<slot :row="item">` | 子组件数据由父组件决定渲染方式 |

**一句话记忆**：插槽是 Vue 的“内容投射”机制，让组件更灵活、更可定制；作用域插槽则让子组件能“反向传递数据”给父组件。