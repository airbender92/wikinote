# CSS 预处理器：Sass & Less 核心对比
CSS 预处理器是用一套**类 CSS 语法**写样式，最终编译成标准 CSS 的工具，能大幅提升样式开发效率，最主流的就是 **Sass** 和 **Less**。

---

## 一、共同点（为什么要用预处理器）
- 支持**变量**：统一管理颜色、尺寸、字体等
- 支持**嵌套**：层级结构更清晰，不用重复写选择器
- 支持**混合（Mixin）**：复用样式片段
- 支持**运算**：加减乘除计算宽高、颜色
- 支持**模块化**：拆分文件、导入合并

---

## 二、Sass vs Less 核心区别
### 1. 语法与文件后缀
- **Sass**
  - 两种语法：`.sass`（缩进）、`.scss`（大括号，更常用）
  - 语法更接近原生 CSS，学习成本低
- **Less**
  - 后缀 `.less`
  - 语法几乎和 CSS 一致，上手最快

### 2. 编译环境
- **Sass**
  - 基于 Ruby，后来有 **Dart Sass**（主流）
  - 需 Node 环境编译
- **Less**
  - 基于 JavaScript
  - 既可 Node 编译，也可浏览器端直接运行

### 3. 功能强弱
- **Sass 更强**
  - 支持 **if / for / each 循环逻辑**
  - 强大的函数系统、继承（`@extend`）
  - 社区生态更成熟（Bootstrap 5+ 改用 Sass）
- **Less 够用**
  - 逻辑能力弱，无完整循环、复杂函数
  - 满足中小型项目完全没问题

### 4. 生态与流行度
- **Sass**：现代前端主流，Vue/React 项目标配
- **Less**：早期非常火（Bootstrap 3/4 使用），现在仍大量用于老项目、后台管理系统

---

## 三、简单语法示例
### 1. 变量
```scss
// Sass
$color: #ff4400;
.box { color: $color; }
```

```less
// Less
@color: #ff4400;
.box { color: @color; }
```

### 2. 嵌套
```scss
.container {
  width: 100%;
  .item {
    font-size: 14px;
    &:hover { color: red; }
  }
}
```
Less 写法完全一样。

### 3. 混合（Mixin）
```scss
// Sass
@mixin flex-center {
  display: flex;
  justify-content: center;
  align-items: center;
}
.box { @include flex-center; }
```

```less
// Less
.flex-center() {
  display: flex;
  justify-content: center;
  align-items: center;
}
.box { .flex-center(); }
```

---

## 四、怎么选？
- **新项目、工程化、复杂系统** → 选 **Sass（SCSS）**
- **老项目维护、快速上手、轻量需求** → 选 **Less**
- 两者学会一个，另一个几乎无缝切换

如果你需要，我可以给你一份**可直接复制的 Sass + Less 常用语法速查表**。