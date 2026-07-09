# CSS-in-JS
一句话：**把 CSS 写在 JS 代码里**，通过 JS 库生成样式，自动实现组件级隔离、动态样式、主题、逻辑复用。

---

## 核心概念
- 不是把 CSS 字符串塞进 style 属性
- 而是用 JS 语法描述样式，库会自动生成唯一 class 并插入 `<style>`
- 自带**局部作用域**，不会全局污染
- 天然支持 JS 变量、条件、循环、函数

常见库：
- **styled-components**（最流行）
- **Emotion**（更快、更小，支持 css prop）
- **Linaria**（零运行时，编译时生成 CSS）

---

## 基本示例（styled-components）
```jsx
import styled from 'styled-components';

// 用 JS 写样式
const Button = styled.button`
  padding: 8px 16px;
  background: ${props => props.primary ? 'blue' : 'gray'};
  color: white;
  border: none;
  border-radius: 4px;

  &:hover {
    opacity: 0.9;
  }
`;

function App() {
  return (
    <div>
      <Button>普通按钮</Button>
      <Button primary>主要按钮</Button>
    </div>
  );
}
```

特点：
- 样式直接绑定组件
- 支持**props 动态样式**
- 支持嵌套、& 父选择器
- 自动生成唯一类名，无冲突

---

## CSS-in-JS 解决了什么
1. **真正的组件样式隔离**
   不用 BEM、不用 CSS Modules、不用手动命名
2. **动态样式极其方便**
   主题、深色模式、响应式、权限样式，直接用 JS 变量
3. **样式可以复用、逻辑化**
   函数、循环、条件、共享常量
4. **删除组件=自动删除样式**
   不会残留无用全局 CSS

---

## 优点
- 作用域天然局部
- 动态样式体验最好
- 组件化更彻底（JSX + 样式写一起）
- 支持自动前缀、关键帧、模板字符串嵌套
- 主题系统非常成熟（ThemeProvider）

## 缺点
- **运行时开销**：解析样式 → 生成 CSS → 插入样式标签
- 服务端渲染需要额外配置（hydration 样式闪烁）
- 打包体积略大
- 调试不如原生 CSS 直观
- 对熟悉 CSS 工作流的人有一定习惯成本

---

# 三者放在一起对比（最清晰）
## 1. Less / Sass
- 作用：**扩展 CSS 语法**（变量、嵌套、mixin、运算）
- 本质：**预编译**，最终还是普通 CSS
- 作用域：**全局**，需要手动避免命名冲突

## 2. CSS Modules
- 作用：**局部作用域 + 避免冲突**
- 本质：**构建工具给 class 加哈希**
- 写法：还是 CSS/Less/Sass
- 特点：**零运行时开销**，性能最好

## 3. CSS-in-JS
- 作用：**JS 控制样式 + 极致动态化**
- 本质：JS 运行时生成样式
- 写法：JS 里写样式
- 特点：动态最强，但有运行时成本

---

## 怎么选（前端面试高频）
- 追求**性能、稳定、轻量** → CSS Modules + Less/Sass
- 追求**组件化、动态主题、复杂交互样式** → CSS-in-JS
- 中后台系统、传统项目 → Less + CSS Modules 最稳妥
- 组件库、高交互 UI 库 → CSS-in-JS 更舒服

---

如果你需要，我可以给你一段**面试专用精简版总结**，背会就能直接说。