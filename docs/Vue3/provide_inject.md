在 Vue 中，`provide` 和 `inject` 是一对用于 **跨层级组件通信** 的 API，能够绕过层层 `props` 传递，让祖先组件直接向任意后代组件提供数据或方法。

## 一、核心作用

- **避免 prop drilling**：解决爷孙组件、隔多代组件之间传参繁琐的问题。
- **适用于插件、主题、全局配置、共享状态**（但不是响应式状态管理，除非配合响应式数据）。

## 二、基本用法

### 选项式 API

```js
// 祖先组件
export default {
  provide() {
    return {
      theme: 'dark',
      updateTheme: (newTheme) => { this.theme = newTheme }
    }
  },
  data() {
    return { theme: 'dark' }
  }
}

// 后代组件
export default {
  inject: ['theme', 'updateTheme'],
  mounted() {
    console.log(this.theme) // 'dark'
    this.updateTheme('light')
  }
}
```

### 组合式 API (Vue 3 推荐)

```vue
<!-- 祖先组件 App.vue -->
<script setup>
import { provide, ref } from 'vue'
const theme = ref('dark')
const toggleTheme = () => theme.value = theme.value === 'dark' ? 'light' : 'dark'
provide('theme', theme)          // 提供响应式数据
provide('toggleTheme', toggleTheme)
</script>

<!-- 后代组件 DeepChild.vue -->
<script setup>
import { inject } from 'vue'
const theme = inject('theme')           // 自动解包 ref，得到响应式对象
const toggleTheme = inject('toggleTheme')
</script>

<template>
  <div :class="theme">当前主题</div>
  <button @click="toggleTheme">切换主题</button>
</template>
```

## 三、与响应式数据的配合

**重要**：默认 `provide` 提供的值**不是响应式的**。如果希望后代组件能响应祖先数据的变化，必须提供响应式数据（`ref` / `reactive`）。

```js
// 正确：提供响应式数据
const count = ref(0)
provide('count', count)   // 后代 inject 得到 count，修改 count.value 会触发更新

// 错误：提供普通值
provide('count', 0)       // 后代无法感知变化
```

如果需要将祖先的响应式数据**只读**传给后代，可以使用 `readonly` 包装：

```js
provide('count', readonly(count))
```

## 四、注入默认值和类型声明

### 设置默认值（避免找不到 provide 时报错）

```js
// 组合式
const theme = inject('theme', 'light')   // 第二个参数是默认值

// 选项式
inject: {
  theme: {
    from: 'theme',      // 如果找不到 'theme'，使用下面的 default
    default: 'light'
  }
}
```

### TypeScript 类型声明

```ts
import type { InjectionKey, Ref } from 'vue'

// 定义注入 key 的类型
export const themeKey: InjectionKey<Ref<string>> = Symbol('theme')

provide(themeKey, theme)

// 后代注入
const theme = inject(themeKey) // 类型自动推导为 Ref<string> | undefined
```

## 五、典型应用场景

| 场景 | 说明 |
|------|------|
| **主题/皮肤切换** | 顶层 provide 主题变量，所有组件 inject 并应用样式 |
| **语言/国际化** | 顶层 provide 当前 locale，后代组件 inject 后配合 i18n 使用 |
| **全局配置** | 例如 provide 一个 `$http` 实例或 `eventBus` |
| **表单组件库** | 表单容器 provide 校验规则、表单值，内部输入项 inject 并使用 |
| **依赖注入替代全局变量** | 避免污染 `globalProperties`，且支持 TypeScript 类型安全 |

## 六、注意事项

1. **调试困难**：因为数据来源不明确，如果组件层级过多且随意使用 `inject`，会降低代码可读性。建议**集中管理注入的 key**（用常量或 Symbol）。

2. **不推荐作为响应式状态管理**：如果需要在多个不相关的组件间共享状态，应使用 Pinia / Vuex。`provide/inject` 更适合**由特定祖先提供、仅后代需要使用**的数据。

3. **与 `app.config.globalProperties` 的区别**：
   - `globalProperties`：全局所有组件都能访问，更像“全局变量”。
   - `provide/inject`：只能在**提供者的后代组件**中注入，作用域受控，更利于组件复用和隔离。

4. **组合式 API 中注入默认值**：可以传入工厂函数，但要注意不要在工厂函数中执行副作用（如调用 API），因为那会每次注入都执行。

## 七、与之前讨论的 `$toast` 如何结合？

如果你希望 Toast 方法可以在整个应用中调用（包括 setup、errorHandler），有两种推荐方式：

- **独立模块**（我之前建议的）：直接导出 `toast` 对象，在任何地方导入调用。
- **provide/inject**：在根组件 provide 一个 `toast` 对象，但在 `errorHandler` 中无法直接使用（因为不在组件实例内）。所以不适用于全局错误处理。

因此，`provide/inject` 更适用于**模板或组件逻辑中**的跨层级传值；而真正的全局工具（如 toast、http）保留模块化导入更简单清晰。

## 八、总结一句话

> **`provide` 在祖先组件里提供数据/方法，`inject` 在后代组件里接收，配合响应式数据和类型 key，就能优雅地解决跨层级通信问题。**