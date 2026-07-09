# CSS Modules
一句话理解：**CSS Modules 不是新语法，而是一个构建工具（Webpack/Vite）的方案，自动给 CSS 类名加唯一哈希，彻底解决 CSS 全局命名冲突、样式污染问题。**

---

## 核心特点
- **作用域局部化**：默认每个 class 都是**局部作用域**，不会全局污染
- **类名自动哈希**：编译后类名变成类似 `style_box__abc123`
- **纯 CSS 写法**：不用学新语法，正常写 CSS/Less/Sass 都行
- **按需引入**：通过 JS 对象引入类名，不会全局覆盖
- **配合预处理器**：完美兼容 Sass / Less / PostCSS

---

## 基本使用示例（React 最常见）
### 1. 样式文件：`Button.module.css`
```css
/* 正常写 CSS 即可 */
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
}

.primary {
  background: blue;
  color: white;
}
```

### 2. 组件中使用
```jsx
import styles from './Button.module.css';

function Button() {
  return (
    {/* 通过 styles 对象引用类名 */}
    <button className={`${styles.btn} ${styles.primary}`}>
      按钮
    </button>
  );
}
```

### 3. 编译后 DOM 效果
```html
<button class="Button_btn__abc123 Button_primary__def456">
  按钮
</button>
```

---

## 常用语法
### 1. 全局类名（不想被哈希）
```css
/* 局部 */
.title { color: red; }

/* 全局 */
:global(.container) {
  margin: 0 auto;
}
```

### 2. 嵌套 & 配合预处理器
CSS Modules 不限制嵌套，你可以直接搭配 Less/Sass：
```less
// Button.module.less
.wrap {
  padding: 10px;

  .content {
    font-size: 14px;
  }
}
```

### 3.  composes 复用样式（CSS Modules 独有）
```css
.btn {
  padding: 8px 16px;
}

.primary {
  /* 继承 .btn 样式 */
  composes: btn;
  background: blue;
}
```

---

## CSS Modules vs 普通 CSS / CSS-in-JS
| 方式 | 作用域 | 命名冲突 | 写法成本 | 运行时开销 |
|------|--------|----------|----------|------------|
| 普通 CSS | 全局 | 严重 | 低 | 无 |
| CSS Modules | 局部 | 无 | 极低 | 无 |
| CSS-in-JS | 局部 | 无 | 中 | 有 |

**总结：**
- 想要**零运行时开销 + 不污染全局 + 写法简单** → 首选 **CSS Modules**
- 想要**JS 里写样式、动态主题强** → 选 styled-components 等

---

## 与 Sass/Less 的关系
- **Sass/Less：扩展 CSS 语法（变量、嵌套、mixin）**
- **CSS Modules：解决命名冲突、作用域问题**

两者**完全不冲突**，可以一起用：
`index.module.scss` / `page.module.less` 都是合法的。

---

## 快速记忆
- CSS Modules = **局部作用域 CSS**
- 靠**构建工具自动哈希类名**实现
- 正常写 CSS/Less/Sass，通过 `styles.xxx` 引用
- 适合：React/Vue 组件化开发，避免样式互相覆盖

如果你用 React/Vue，我可以给你一套**最佳实践目录结构 + 常用封装示例**。