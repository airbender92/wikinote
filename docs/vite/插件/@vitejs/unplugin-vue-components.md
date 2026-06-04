# unplugin-vue-components
**Vue 组件 & 指令按需自动导入插件**，和 `unplugin-auto-import` 是黄金搭档。

---

## 核心作用
- 不用手动写 `import` 和 `components` 注册
- 组件在模板里直接写标签就生效
- 支持第三方 UI 库（Element Plus、Naive UI、Vant 等）自动导入
- 支持自定义组件、指令自动导入

```vue
<!-- 以前 -->
<template>
  <ElButton />
</template>
<script setup>
import { ElButton } from 'element-plus'
</script>

<!-- 现在 → 直接用，自动导入 -->
<template>
  <ElButton />
</template>
```

---

## 安装
```bash
npm i -D unplugin-vue-components
```

---

## Vite 完整示例（最常用）
```ts
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  plugins: [
    vue(),
    // API 自动导入
    AutoImport({
      resolvers: [ElementPlusResolver()],
    }),
    // 组件自动导入
    Components({
      // 自动导入 UI 组件
      resolvers: [ElementPlusResolver()],
      // 自动生成 components.d.ts 给 TS
      dts: true,
    }),
  ],
})
```

---

## 常用配置说明
```ts
Components({
  // 要扫描的组件目录
  dirs: ['src/components'],

  // 组件名称扩展名
  extensions: ['vue'],

  // 是否生成 TS 类型文件
  dts: 'src/components.d.ts',

  // UI 库解析器
  resolvers: [
    ElementPlusResolver(),
    // NaiveUiResolver(),
    // VantResolver(),
    // AntDesignVueResolver(),
  ],

  // 是否导入目录作为命名空间
  // components/foo/Button.vue → <FooButton />
  directoryAsNamespace: false,

  // 全局包含自定义指令
  directives: true,
})
```

---

## 支持的 UI 库（内置 resolver）
- Element Plus
- Naive UI
- Vant
- Ant Design Vue
- Vuetify
- Headless UI
- Prime Vue
- Inkline
- Element UI (Vue2)
- Arco Design

---

## 搭配 unplugin-auto-import
这俩一般**一起用**：
- `unplugin-auto-import`：自动导入 API（ref / computed / useRouter 等）
- `unplugin-vue-components`：自动导入组件和指令

---

## TypeScript
生成 `components.d.ts` 后，TS 会自动识别全局组件，不会报错。

---

## ESLint
如果出现 `no-undef`，在 `.eslintrc` 中加入：
```json
"globals": {
  "defineProps": "readonly",
  "defineEmits": "readonly"
}
```
或直接用 `unplugin-auto-import` 生成的 eslint 配置。

需要我给你一份**Vue3 + Element Plus/Naive UI/Vant** 可直接复制的成品配置吗？