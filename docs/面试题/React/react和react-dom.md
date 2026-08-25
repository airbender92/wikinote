# React 和 react‑dom 的关系

> React18 以前是一套包，后来做了拆分：**`react` 是核心库，`react‑dom` 是浏览器渲染适配器**

## 1、react 包（核心）

职责：**只负责逻辑、组件、虚拟DOM、状态、Hooks**，和浏览器无关。

- 定义组件、`useState`、`useEffect`、`useContext`、`createElement`（JSX编译后就是这个）
- 生成**虚拟DOM（React元素）**，描述页面长什么样
- 不知道怎么把虚拟DOM画到浏览器页面上，它不操作真实DOM

> 它是跨平台的：同样一份react代码，可以跑浏览器、RN、SSR。

## 2、react‑dom 包（浏览器渲染层）

职责：**把react产出的虚拟DOM，翻译成浏览器真实DOM，挂载到页面上**，是浏览器专属。

- `ReactDOM.createRoot(document.getElementById('root')).render(<App/>)`
- 负责diff算法，对比新旧虚拟DOM，最小化更新真实DOM
- 处理DOM事件、属性、生命周期的DOM副作用

> 如果是 React Native，就不用 react‑dom，换成 `react‑native` 渲染器，渲染原生APP控件。

## 3、JSX编译过程

```
<div>hello</div>
```

babel编译 → `react.createElement('div', null, 'hello')` → 返回虚拟DOM对象
→ **交给 react‑dom**，把虚拟DOM变成浏览器真实DOM节点插入页面。

## 4、版本变化重点（React18）

```
// React17及更早
import React from 'react'
import ReactDOM from 'react-dom'

// React18
import React from 'react'
import { createRoot } from 'react-dom/client' // API迁移到react‑dom
```

## 简单类比记忆

- **react：设计师，画图纸（虚拟DOM），只描述长啥样**
- **react‑dom：施工队，拿着图纸去浏览器盖真实房子（真实DOM）**

## 补充其他渲染器

- `react‑dom`：浏览器web
- `react‑native`：手机App
- `react‑dom/server`：服务端SSR渲染HTML字符串

### 一句话总结

**react负责业务逻辑与虚拟DOM描述；react‑dom负责对接浏览器DOM API，完成页面渲染更新，二者必须成对使用。**

如果你需要，我可以顺带讲下：`react‑dom/client` / `react‑dom/server` 的区别。
