这是一个 **Vue 3 的 `watch`**，用于监听 props 的变化并同步到组件内部状态。

### 代码解析

```ts
watch(
  () => props.modelValue,  // 监听函数，返回要监听的响应式数据
  (val) => {                // 回调函数，val 是新值
    imageUrl.value = val || ''
  }
)
```

### 作用

| 参数 | 说明 |
|------|------|
| `props.modelValue` | 父组件传入的头像 URL（v-model 双向绑定） |
| `imageUrl.value` | 组件内部维护的头像预览 URL |

### 为什么需要这个 watch？

```
父组件传入新头像 URL
        │
        ▼
props.modelValue 变化
        │
        ▼
watch 回调触发
        │
        ▼
imageUrl.value 同步更新
        │
        ▼
UI 自动重新渲染新头像
```

### 使用场景

1. **父组件修改头像**（如上传成功返回新 URL）→ watch 同步更新预览
2. **重置头像**（传入空字符串）→ watch 清空预览

### 对比 computed

`watch` 和 `computed` 都能实现响应式同步，但区别在于：

| | watch | computed |
|---|---|---|
| 用途 | 响应变化执行副作用 | 根据响应式数据派生新值 |
| 例子 | `props.modelValue` 变化 → 同步到 `imageUrl` | `props.modelValue` → 直接返回处理后的值 |
| 同步/异步 | 支持异步 | 只能同步 |

这里用 `watch` 而不是 `computed`，因为 `imageUrl` 不是从 `modelValue` 简单派生，而是需要**响应式同步**以触发 UI 更新。