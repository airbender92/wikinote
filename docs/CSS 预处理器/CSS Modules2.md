# 核心结论先讲清楚
正常默认规则（Vite/Webpack）：
1. **`xxx.module.less`**：开启 **CSS Modules**，类名自动哈希、局部作用域，必须 `import styles from './xxx.module.less'` 用 `styles.xxx`
2. **普通 `xxx.less`**：默认**全局样式**，类名不会哈希，直接 `import './xxx.less'` 就全局生效，**不能 `import styles from './xxx.less'`**

你看到项目里 `import styles from './xxx.less'`（不带 `.module`）还能正常导出类名对象，只有两种根本原因：
## 一、构建工具强制全局开启 CSS Modules（Webpack 自定义配置）
### 原理
`css-loader` 配置里把 `modules: true` 全局打开，**所有 less/css 文件全部当成 CSS Modules**，不再区分 `.module` 后缀约定。
### Webpack 配置示例
```js
{
  test: /\.less$/,
  use: [
    'style-loader',
    {
      loader: 'css-loader',
      options: {
        // 全局开启所有css/less为CSS Modules
        modules: true, 
        localIdentName: '[name]__[local]__[hash:6]'
      }
    },
    'less-loader'
  ]
}
```
此时：
- 不管文件名是 `index.less` 还是 `index.module.less`，都会编译导出类名对象
- 组件统一 `import styles from './index.less'`
- 所有类名自动哈希，全局无冲突

### 缺点
想写**全局公共样式**（重置、主题）会很麻烦，必须手动用 `:global()` 包裹。

## 二、Vite 自定义匹配规则，不依赖 `.module` 后缀
Vite 默认只把 `/\.module\./` 文件识别为 CSS Modules，但可以手动修改 `css.modules.regexp`，匹配所有 `.less` 文件，全部启用模块化：
```js
// vite.config.js
export default defineConfig({
  css: {
    modules: {
      // 匹配所有less文件，全部走CSS Modules
      regexp: /\.less$/i
    }
  }
})
```
效果同上：任意 `.less` 导入都得到 `styles` 对象。

## 三、另一种场景：Vue 项目 <style module>（和文件后缀无关）
Vue 单文件组件不用拆分 `.less` 文件，直接在 `<style module lang="less">` 写样式，模板用 `$style.xxx`，完全不需要 `xxx.module.less` 文件：
```vue
<template>
  <div :class="$style.box">测试</div>
</template>
<style module lang="less">
.box { color: red; }
</style>
```
这种是**组件内 CSS Modules**，不是外部独立 less 文件，和你说的 `import styles from './xxx.less'` 是两套方案。

## 四、补充：两种完全不同的「无module后缀」项目写法区分
### 情况A：全局开启 CSS Modules（你问的场景）
文件：`Button.less`
```less
.btn { padding: 8px; }
```
组件：
```jsx
import styles from './Button.less'
<button className={styles.btn} />
```
编译后 `.btn` → `.Button__btn__a1b2c3`，隔离样式。

### 情况B：纯全局less（默认配置，不能import styles）
文件：`global.less`
```less
.btn { padding: 8px; }
```
组件只能引入生效，拿不到对象：
```jsx
import './global.less' // 直接全局注入，无导出
<button className="btn" />
```
这里如果写 `import styles from './global.less'` 会报错。

## 五、为什么大部分项目保留 `.module` 约定？
1. **区分全局/局部**：`global.less` 全局，`page.module.less` 组件局部，不用到处写 `:global()`
2. **配置更干净**：不用修改 `modules.regexp`，脚手架开箱即用
3. **可读性强**：看文件名就知道是否哈希隔离，新人上手快

## 快速记忆
- 能 `import styles from './xxx.less'`（不带module）= **构建配置全局开启了CSS Modules**
- 只能 `import './xxx.less'` 不能取styles对象 = 默认全局样式
- `.module.less` 是行业**约定标识**，不是语法强制，配置可以改掉这个规则