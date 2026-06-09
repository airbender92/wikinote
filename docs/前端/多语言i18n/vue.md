# Vue I18n 完整使用示例（Vue2 + Vue3 区分，包含基础/组件/模板/JS/TS/动态切换/复数/日期货币等）
## 一、环境区分
### Vue3 + Vue I18n v9（组合式API 主流）
### Vue2 + Vue I18n v8（选项式API）
下面优先 Vue3 示例，附带 Vue2 差异说明

## 1. 安装 & 初始化（Vue3 + Vite）
### 1.1 安装
```bash
npm install vue-i18n@9
# or yarn/pnpm
pnpm add vue-i18n@9
```

### 1.2 新建语言文件
`src/locales/en.json`
```json
{
  "hello": "Hello world",
  "msg": {
    "title": "System Title",
    "welcome": "Welcome {name}"
  },
  "count": "You have {n} apple | You have {n} apples",
  "money": "Price: {amount, currency}",
  "date": "Today is {date, date}"
}
```

`src/locales/zh-CN.json`
```json
{
  "hello": "你好世界",
  "msg": {
    "title": "系统标题",
    "welcome": "欢迎 {name}"
  },
  "count": "你有一个苹果 | 你有 {n} 个苹果",
  "money": "价格：{amount, currency}",
  "date": "今天是 {date, date}"
}
```

### 1.3 创建 i18n 实例 `src/i18n/index.ts`
```typescript
import { createI18n } from 'vue-i18n'
import zh from '../locales/zh-CN.json'
import en from '../locales/en.json'

const messages = {
  'zh-CN': zh,
  'en': en
}

const i18n = createI18n({
  legacy: false, // Vue3 组合式必须false
  locale: 'zh-CN', // 默认语言
  fallbackLocale: 'en', // 缺失文案兜底英文
  messages,
  numberFormats: {
    'zh-CN': {
      currency: { style: 'currency', currency: 'CNY' }
    },
    en: {
      currency: { style: 'currency', currency: 'USD' }
    }
  },
  datetimeFormats: {
    'zh-CN': {
      date: { year: 'numeric', month: 'long', day: 'numeric' }
    },
    en: {
      date: { year: 'numeric', month: 'short', day: 'numeric' }
    }
  }
})

export default i18n
```

### 1.4 main.ts 挂载
```typescript
import { createApp } from 'vue'
import App from './App.vue'
import i18n from './i18n'

const app = createApp(App)
app.use(i18n)
app.mount('#app')
```

---

# 二、模板中各种用法（最常用）
## 2.1 基础文案 $t(key)
```vue
<template>
  <!-- 单层key -->
  <div>{{ $t('hello') }}</div>

  <!-- 嵌套对象key -->
  <h1>{{ $t('msg.title') }}</h1>
</template>
```

## 2.2 插值传参（占位符）
### 单个参数
```vue
<div>{{ $t('msg.welcome', { name: '张三' }) }}</div>
```

### 多参数
语言：`"userInfo": "姓名：{name}，年龄：{age}"`
```vue
<div>{{ $t('userInfo', { name: '李四', age: 20 }) }}</div>
```

## 2.3 复数/单复数选择 | 分隔
语言：`"count": "1个苹果 | {n}个苹果"`
```vue
<!-- n=1 显示第一条 -->
<p>{{ $t('count', 1) }}</p>
<!-- n=5 显示第二条 -->
<p>{{ $t('count', 5) }}</p>

<!-- 传对象写法 -->
<p>{{ $t('count', { n: 10 }) }}</p>
```

## 2.4 数字/货币格式化 $n
```vue
<!-- 货币 -->
<p>{{ $n(99.99, 'currency') }}</p>
<!-- 普通数字千分位 -->
<p>{{ $n(123456) }}</p>
```

## 2.5 日期格式化 $d
```vue
<p>{{ $d(new Date(), 'date') }}</p>
```

## 2.6 v-t 指令（推荐，性能更好）
```vue
<!-- 基础 -->
<span v-t="'hello'"></span>
<!-- 传参 -->
<span v-t="['msg.welcome', { name: '小明' }]"></span>
```

## 2.7 HTML 富文本翻译（v-html + $t）
语言：`"tip": "请点击 <a href='/login'>登录</a>"`
```vue
<div v-html="$t('tip')"></div>
```
> 安全提醒：不要渲染用户可控内容，防止XSS

## 2.8 语言切换按钮 $i18n.locale
```vue
<button @click="$i18n.locale = 'zh-CN'">中文</button>
<button @click="$i18n.locale = 'en'">English</button>
```

## 2.9 语言响应式绑定
```vue
<!-- 切换语言自动更新 -->
<div>{{ $t('hello') }}</div>
```

---

# 三、组合式API setup 中使用（useI18n）
## 3.1 基础使用
```vue
<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t, n, d, locale } = useI18n()

// 普通文案
console.log(t('hello'))
// 传参
console.log(t('msg.welcome', { name: 'setup用户' }))
// 切换语言
locale.value = 'en'
</script>

<template>
  <p>{{ t('hello') }}</p>
</template>
```

## 3.2 复数、数字、日期在JS中
```typescript
const { t, n, d } = useI18n()

// 复数
t('count', 3)
// 货币格式化
n(199.9, 'currency')
// 日期
d(new Date(), 'date')
```

## 3.3 函数内动态翻译（接口返回提示文案）
```typescript
function showToast() {
  const msg = t('msg.welcome', { name: '游客' })
  alert(msg)
}
```

---

# 四、选项式API 用法（Vue3 legacy:true / Vue2）
## Vue2 / Vue3 legacy 模式
### 初始化 i18n 时 `legacy:true`
```typescript
const i18n = createI18n({
  legacy: true,
  locale: 'zh-CN',
  messages
})
```

### 组件内直接 this.$t
```vue
<script>
export default {
  mounted() {
    console.log(this.$t('hello'))
    this.$i18n.locale = 'en' // 切换语言
  }
}
</script>

<template>
  <div>{{ $t('msg.title') }}</div>
</template>
```

---

# 五、高级场景示例
## 5.1 动态语言包（异步加载语言，分包优化）
### i18n/index.ts
```typescript
import { createI18n, useI18n } from 'vue-i18n'

const i18n = createI18n({
  legacy: false,
  locale: 'zh-CN',
  fallbackLocale: 'zh-CN',
  messages: {} // 初始空
})

// 封装异步加载语言函数
export async function loadLocale(lang: string) {
  const msg = await import(`../locales/${lang}.json`)
  i18n.global.setLocaleMessage(lang, msg.default)
  i18n.global.locale.value = lang
}

export default i18n
```

### 页面切换语言时懒加载
```vue
<script setup>
import { loadLocale } from '@/i18n'
async function changeLang(lang) {
  await loadLocale(lang)
}
</script>
<template>
  <button @click="changeLang('en')">英文</button>
</template>
```

## 5.2 全局TS/工具函数中使用 i18n（非组件文件）
工具文件 `utils/msg.ts`
```typescript
import i18n from '@/i18n'

export function getWelcome(name: string) {
  return i18n.global.t('msg.welcome', { name })
}
```

## 5.3 枚举/常量结合i18n
```typescript
// const.ts
export const STATUS = {
  SUCCESS: 'status.success',
  FAIL: 'status.fail'
}

// 组件
const { t } = useI18n()
const text = t(STATUS.SUCCESS)
```

语言配置：
```json
{
  "status": {
    "success": "操作成功",
    "fail": "操作失败"
  }
}
```

## 5.4 消息插值带默认值、缺失key兜底
当key不存在时自动走 fallbackLocale
```vue
<!-- 不存在key test.xxx 会显示英文兜底 -->
{{ $t('test.xxx') }}
```

## 5.5 自定义格式化函数
i18n实例中注册全局格式化：
```typescript
i18n.global.formatter('percent', (val) => `${val * 100}%`)
```
语言文件：
```json
"rate": "转化率：{num, percent}"
```
使用：
```vue
{{ $t('rate', { num: 0.85 }) }}
```

## 5.6 Element Plus / UI库 结合i18n
```typescript
import ElementPlus from 'element-plus'
import zhEl from 'element-plus/dist/locale/zh-cn.mjs'
import enEl from 'element-plus/dist/locale/en.mjs'

const elLocales = {
  'zh-CN': zhEl,
  en: enEl
}

// 切换语言同时切换UI库语言
async function changeLang(lang) {
  await loadLocale(lang)
  app.use(ElementPlus, { locale: elLocales[lang] })
}
```

---

# 六、Vue2 i18n v8 关键差异小结
1. 导入：`import VueI18n from 'vue-i18n'`
2. 实例：`new VueI18n({ locale, messages })`
3. 无 `useI18n`，只能 `this.$t`
4. 无 `legacy` 配置，默认选项式
5. 全局翻译：`i18n.t()`

## Vue2 简单初始化示例
```js
import Vue from 'vue'
import VueI18n from 'vue-i18n'
Vue.use(VueI18n)

const i18n = new VueI18n({
  locale: 'zh-CN',
  messages: {
    'zh-CN': require('./locales/zh-CN.json'),
    en: require('./locales/en.json')
  }
})

new Vue({ i18n, render: h => h(App) })
```

---

# 七、常用API速查表
| 写法 | 场景 |
|------|------|
| `$t('key')` / `t('key')` | 基础翻译 |
| `$t('key', { x: 1 })` | 占位传参 |
| `$t('key', number)` | 单复数 |
| `$n(num, format)` | 数字/货币格式化 |
| `$d(date, format)` | 日期格式化 |
| `v-t="'key'"` | 指令翻译（推荐） |
| `$i18n.locale` | 读写当前语言 |
| `useI18n()` | setup组合式获取t/locale |
| `i18n.global.t()` | js/ts全局文件翻译 |
| `setLocaleMessage` | 动态追加语言包 |

需要我给你一份可直接复制的**完整Vue3 Vite i18n最小可运行模板**（含页面切换语言、复数、货币、异步加载）吗？

