# 判断 A DOM 元素是否是 B 的子/后代元素

> 注意：**子元素 directChild**（直接一层孩子） 和 **后代元素 descendant**（任意深度子子孙孙）是两个概念。

## 1. 判断是否为【后代元素】（任意深度，最常用）

### 方法1：`element.contains()` ✅推荐，浏览器原生API

```
// 判断 a 是否是 b 的后代（包含直接子元素、多层嵌套）
const isDescendant = b.contains(a)
```

- 返回布尔 `true / false`
- 特殊：`b.contains(b)` → **true，元素自己包含自己**

示例：

```
<div id="box">
  <div id="child">
    <span id="span"></span>
  </div>
</div>
```

```
const box = document.querySelector('#box')
const span = document.querySelector('#span')

console.log(box.contains(span)) // true，span是box后代
console.log(box.contains(box))  // true，自己包含自己
```

> 业务场景：点击外部关闭弹窗，判断点击的target是否在弹窗容器内部。

### 如果需要排除“自己等于自己”

```
// a 是 b 的后代，但 a !== b
function isDescendantNotSelf(parent, child) {
  return parent !== child && parent.contains(child)
}
```

## 2. 判断是否只是【直接子元素】（仅一层，不包含孙子）

不能用contains，contains会匹配所有后代。
两种写法：

```
// 方式A：parentNode 判断
const isDirectChild = a.parentNode === b
```

```
// 方式B：children 集合查找
const isDirectChild = Array.from(b.children).includes(a)
```

## 3. 兼容边界情况

- 如果 `a` 或者 `b` 为 `null / undefined`，调用`.contains()`会报错，先做空判断

```
function isDescendant(parent, child) {
  if (!parent || !child) return false
  return parent.contains(child)
}
```

- 如果两个元素不在同一个文档（比如在iframe里面），`contains` 返回 false，iframe内DOM不能和外部DOM互相contains。

## 4. 旧浏览器备选：`compareDocumentPosition`（了解）

`contains`底层就是基于这个API，返回数字掩码：

```
// 20 = 0b10100 → child 在 parent 内部
const res = b.compareDocumentPosition(a)
const isDescendant = (res & Node.DOCUMENT_POSITION_CONTAINED_BY) !== 0
```

> 一般业务直接用 `contains`，可读性更好。

## 5. 实际业务经典场景：点击页面空白关闭弹窗

```
const popup = document.querySelector('.popup')
document.addEventListener('mousedown', (e) => {
  // 如果点击目标不是弹窗的后代，就关闭弹窗
  if (!popup.contains(e.target)) {
    popup.style.display = 'none'
  }
})
```

## 总结

1. ✅**任意深度后代（孙子、重孙子）：`parent.contains(child)`**，最常用。注意：元素自己contains自己返回true。
2. ✅**仅直接一级子元素：`child.parentNode === parent`**。
3. 记得做空值判断；iframe中DOM不能跨frame使用contains。

### 快速记忆

- `b.contains(a)`：**a是不是落在b的内部（包含自己）**。
