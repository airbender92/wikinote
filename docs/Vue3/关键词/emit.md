## Vue 3 TypeScript Props 和 Emits 类型定义

### 代码解析

```ts
// 1. 定义 Props 的类型接口
interface Props {
  visible: boolean  // 弹窗显示/隐藏
}

// 2. 定义 Emits 的类型接口（声明可抛出的事件）
interface Emits {
  (e: 'update:visible', value: boolean): void  // 关闭弹窗时通知父组件
}

// 3. 使用 defineProps 接收父组件传入的 Props
const props = defineProps<Props>()

// 4. 使用 defineEmits 定义组件可抛出的事件
const emit = defineEmits<Emits>()
```

### Props（父→子数据传递）

```
父组件                          子组件 (ChangePasswordDialog)
  │                                   │
  │──── visible={true} ────────────> │  接收：props.visible
  │                                   │
  │                                   │
  │<──── emit('update:visible', false) │  触发：关闭弹窗
  │                                   │
  ▼                                   ▼
```

### Emits（子→父事件通知）

```ts
// 触发方式
emit('update:visible', false)

// 父组件使用 v-model:visible 接收
// <ChangePasswordDialog v-model:visible="dialogVisible" />
```

### 为什么用 `interface` 而不是对象语法？

| 方式 | 语法 | 适用场景 |
|------|------|----------|
| interface（推荐） | `defineProps<Props>()` | 需要类型提示和校验 |
| 对象字面量 | `defineProps({ visible: Boolean })` | 简单场景，无需类型 |

### `update:visible` 的 Vue 3 命名约定

`update:xxx` 是 Vue 3 **v-model 参数**的命名规范：

```vue
<!-- 父组件 -->
<ChangePasswordDialog v-model:visible="dialogVisible" />

<!-- 子组件触发 -->
emit('update:visible', false)  // 相当于父组件的 dialogVisible = false
```

这种模式让父组件用 `v-model` 双向绑定子组件的状态，实现弹窗的显示/隐藏控制。