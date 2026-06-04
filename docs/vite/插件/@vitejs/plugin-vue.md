# @vitejs/plugin-vue 完整中文解读
`@vitejs/plugin-vue` 是 **Vite 官方提供的 Vue 单文件组件（SFC，即 `.vue` 文件）编译插件**，负责在 Vite 中解析、编译 `<template>` / `<script>` / `<style>`，让 Vue 3 项目能正常运行。

下面逐段把官方说明翻译成易懂的工程解读：

---

## 一、基础说明
> Note: as of vue 3.2.13+ and @vitejs/plugin-vue 1.9.0+, @vue/compiler-sfc is no longer required as a peer dependency.

- **Vue 3.2.13+、插件 1.9.0+ 以后**
- 不再需要手动安装 `@vue/compiler-sfc` 作为对等依赖
- 插件内部已经自动处理，项目依赖更简洁

### 最简配置
```js
// vite.config.js
import vue from '@vitejs/plugin-vue'

export default {
  plugins: [vue()],
}
```
只需要引入并放入 `plugins` 数组，Vite 就能识别 `.vue` 文件。

### JSX / TSX 支持
如果要在 Vue 中写 JSX/TSX，必须额外安装：
```bash
npm install @vitejs/plugin-vue-jsx -D
```

---

## 二、插件配置项（Options）
完整 TS 类型定义，下面只讲**常用 & 关键配置**：

### 1. include / exclude
- 匹配哪些文件被当作 Vue SFC 处理
- 默认：处理所有 `.vue` 文件
- 支持字符串、正则、数组

### 2. isProduction
手动指定是否为生产环境，一般**不需要配置**，Vite 会自动判断。

### 3. features（v5.1.0+ 新增）
这是新版集中的功能开关，非常重要：

#### propsDestructure
- 开启 `defineProps` **响应式解构**
- Vue 3.4+ 支持，3.4 默认 `false`（实验），3.5+ 默认 `true`

#### customElement
- 把 Vue SFC 编译为**原生自定义元素（Web Components）**
- 默认：只处理 `*.ce.vue` 结尾的文件
- 设为 `true`：所有 `.vue` 都按自定义元素编译
- 也支持正则/路径匹配哪些文件编译为 Custom Element

#### optionsAPI
- 是否保留 Vue **选项式 API（Options API）**
- 默认 `true`
- 设为 `false` 可在生产构建中剔除相关代码，**减小打包体积**

#### prodDevtools
- 生产环境是否开启 Devtools 支持
- 默认 `false`
- 开启会略微增大体积

#### prodHydrationMismatchDetails
- 生产环境是否开启**水合不匹配详细报错**
- 服务端渲染（SSR）/ 静态站点有用
- 默认 `false`

#### componentIdGenerator
- 组件 ID 生成策略，用于热更新、作用域 CSS
- 开发默认按文件路径 hash
- 生产默认按文件路径 + 源码 hash，更稳定

---

### 4. script / template / style
更底层的编译配置，直接透传给 `@vue/compiler-sfc`：
- `script`：脚本编译选项
- `template`：模板编译、编译优化、资源处理
- `style`：样式编译、CSS 模块化、预处理器

一般项目**很少改**，多用于深度定制编译行为。

### 5. compiler
指定自定义的 `@vue/compiler-sfc` 实例，用于强制某个版本或打补丁。

### 6. customElements（已废弃）
已迁移到 `features.customElement`。

---

## 三、资源 URL 处理（Asset URL handling）
插件编译 `<template>` 时，**自动把静态资源路径转为 ESM 导入**。

例如：
```html
<img src="../image.png" />
```
会被编译成：
```js
import _imports_0 from '../image.png'
```
```html
<img :src="_imports_0" />
```

### 默认处理的标签 & 属性
```js
{
  video: ['src', 'poster'],
  source: ['src'],
  img: ['src'],
  image: ['xlink:href', 'href'],
  use: ['xlink:href', 'href']
}
```

- 只有**静态字符串**会被自动转换
- 动态绑定（如 `:src="img"`）需要手动 `import`

### 自定义资源转换规则
```js
vue({
  template: {
    transformAssetUrls: {
      // 自定义你的标签和属性
    }
  }
})
```

---

## 四、自定义块（Custom Blocks）示例
插件支持解析 `.vue` 里的**自定义块**，比如 `<i18n>`、`<docs>` 等，配合 Vite 插件做额外处理。

官方示例是 **Vue i18n 自定义语言块**：
1. 写一个 Vite 插件处理 `type=i18n`
2. 解析 YAML 并挂载到组件实例
3. 在组件中直接使用 `Comp.i18n`

```vue
<i18n lang="yaml">
message: 'world'
</i18n>
```

这是做**组件本地化、文档块、自定义业务块**的标准方案。

---

## 五、把 SFC 用作原生自定义元素（Custom Elements）
- 要求：Vue 3.2+、插件 1.4.0+
- 文件命名：`*.ce.vue`
- 特点：
  - `<style>` 不会抽离成 CSS 文件
  - 会被编译成**内联 CSS 字符串**
  - 自动注入到 Custom Element 的 Shadow DOM
  - 不需要 `<style scoped>`，天然样式隔离

使用方式：
```js
import { defineCustomElement } from 'vue'
import Example from './Example.ce.vue'

customElements.define('my-example', defineCustomElement(Example))
```

可通过 `customElement` 配置批量开启该模式。

---

## 六、总结（一句话版）
`@vitejs/plugin-vue` 就是 **Vite 环境下 Vue 3 的 `.vue` 文件编译器**，负责模板编译、脚本处理、样式处理、资源路径转换、自定义块、Web Component 模式，是 Vue3 + Vite 项目**必装核心插件**。

如果你需要，我可以按你的项目场景（是否 TS、是否 SSR、是否 Web Components）给你一份**最优 vite.config.js 配置**。