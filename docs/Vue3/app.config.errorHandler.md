在真实的大型 Vue 项目中，`app.config` 是一个非常实用但容易被忽视的入口。它提供了一些应用级别的配置选项，让你能够统一控制整个 Vue 应用的行为。你提到的 `errorHandler` 就是其中最典型、最常用的一项。

## 1. `app.config.errorHandler` —— 全局错误处理

在大型应用中，组件数量多、逻辑复杂，不可能在每个组件里都写 `try/catch` 或 `errorCaptured` 钩子。通过设置全局错误处理器，可以：

- **统一收集错误**：所有组件、指令、渲染函数、侦听器中抛出的未捕获错误都会汇集到这里。
- **上报到监控系统**：将错误信息、组件栈、用户操作路径发送到 Sentry、BugSnag 或自研的日志服务。
- **友好的用户提示**：避免白屏或卡死，可以降级展示备用 UI 或弹窗提示“系统开小差，请稍后重试”。
- **区分环境**：开发环境打印详细错误堆栈，生产环境只记录并优雅降级。

```js
// main.js
import { createApp } from 'vue'
import App from './App.vue'

const app = createApp(App)

app.config.errorHandler = (err, instance, info) => {
  // 上报到日志服务
  logErrorToService({
    error: err.stack,
    component: instance?.$options.name || 'anonymous',
    lifecycle: info, // 例如 'render function', 'v-on handler' 等
    url: window.location.href,
    user: getUserInfo()
  })

  // 开发环境打印完整错误
  if (process.env.NODE_ENV === 'development') {
    console.error('[Global Error]', err, info)
  }

  // 可选：触发全局 Toast 提示
  app.config.globalProperties.$toast?.error('操作失败，请重试')
}
```

> **注意**：`errorHandler` 本身捕获不到异步任务（如 `setTimeout`，`Promise` 未处理的 rejection），需要配合 `window.onerror` 和 `unhandledrejection` 一起使用。

## 2. 其他实用的 .config 选项

大型项目中以下选项也常被用到：

### `app.config.globalProperties`

向所有组件实例添加全局属性，避免在每个组件里重复导入工具函数或第三方库。

```js
// 注入全局工具
app.config.globalProperties.$http = axios
app.config.globalProperties.$dayjs = dayjs
app.config.globalProperties.$filters = {
  formatDate: (val, format = 'YYYY-MM-DD') => dayjs(val).format(format)
}
```

在模板或 Options API 中直接使用：
```vue
<template>
  <div>{{ $filters.formatDate(date) }}</div>
</template>

<script>
export default {
  mounted() {
    this.$http.get('/api/user')
  }
}
</script>
```

但在 Composition API 中推荐用 `provide/inject` 或模块导入，避免依赖隐式全局变量。

### `app.config.performance`

开启后会在浏览器 DevTools 的性能面板中记录组件初始化、渲染、更新等耗时标记，适合在开发阶段排查性能瓶颈。

```js
if (process.env.NODE_ENV === 'development') {
  app.config.performance = true
}
```

### `app.config.optionMergeStrategies`

自定义选项的合并策略，主要用于混入（mixins）或插件开发。比如你希望所有组件都支持一个自定义字段 `myAsyncData`，并规定父组件的值覆盖子组件：

```js
app.config.optionMergeStrategies.myAsyncData = (parent, child) => {
  return child ?? parent
}
```

## 3. 真实项目中的最佳实践

### ① 环境差异化配置

创建 `config` 模块，根据 `NODE_ENV` 动态设置：

```js
// config/app.config.js
export function setupAppConfig(app) {
  // 错误处理器
  app.config.errorHandler = (err, vm, info) => {
    if (import.meta.env.PROD) {
      // 生产上报
      window.Sentry?.captureException(err, { extra: { info, component: vm?.$options.name } })
    } else {
      console.group(`[Global Error] ${info}`)
      console.error(err)
      console.groupEnd()
    }
  }

  // 性能标记仅在开发启用
  if (import.meta.env.DEV) {
    app.config.performance = true
  }

  // 注入全局属性（谨慎数量，避免命名冲突）
  app.config.globalProperties.$dayjs = dayjs
}
```

### ② 结合错误边界组件

`errorHandler` 是最后一道防线，但无法做 UI 降级。你可以同时封装一个 `<ErrorBoundary>` 组件，利用 `onErrorCaptured` 钩子实现组件粒度的 fallback UI：

```vue
<!-- ErrorBoundary.vue -->
<script setup>
import { ref, onErrorCaptured } from 'vue'
const error = ref(null)
onErrorCaptured((err, instance, info) => {
  error.value = err
  // 阻止错误继续向上传播
  return false
})
</script>

<template>
  <div v-if="error" class="error-fallback">
    出错了，<button @click="error = null">重试</button>
  </div>
  <slot v-else />
</template>
```

### ③ 避免过度使用 `globalProperties`

在 Composition API + TypeScript 项目中，全局属性会失去类型提示（除非声明模块扩展）。而且依赖全局对象会让代码的依赖关系不清晰。优先推荐：

- 工具函数直接 `import`
- 第三方库的实例通过模块单例获取（例如 `axios` 自己导出一个实例）
- 需要跨组件共享的数据或方法使用 `provide/inject`

当你需要在模板中频繁调用某个格式化函数时，再考虑挂到 `globalProperties` 上，并补充类型声明：

```ts
// shims-vue.d.ts 或 main.ts 中
declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $dayjs: typeof dayjs
  }
}
```

## 4. 总结

在真实大型项目里，`app.config` 是应用初始化的“控制中心”：
- `errorHandler` 必不可少，用于统一错误监控和兜底。
- `globalProperties` 可以按需注入少量高频使用的工具。
- `performance` 帮助定位性能问题。
- 结合环境变量、类型声明和错误边界，能构建出健壮、可维护的前端架构。

理解并善用这些配置，可以让团队在迭代过程中保持一致的行为准则，同时降低排错成本。