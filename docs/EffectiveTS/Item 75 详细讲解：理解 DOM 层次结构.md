## Item 75 详细讲解：理解 DOM 层次结构

在浏览器中编写 TypeScript 代码时，你会频繁操作 DOM 元素和事件。JavaScript 的 DOM API 是动态且灵活的，但 TypeScript 提供了严格的类型层次结构。理解 `EventTarget`、`Node`、`Element`、`HTMLElement` 以及具体元素类型（如 `HTMLDivElement`）之间的区别，以及 `Event` 与 `MouseEvent` 等事件类型的差异，是避免类型错误、写出健壮代码的关键。

---

### 1. 问题示例：拖拽处理程序中的类型错误

下面的代码试图实现一个简单的拖拽效果，但在添加类型注解后出现了大量类型错误：

```ts
function handleDrag(eDown: Event) {
  const targetEl = eDown.currentTarget;
  targetEl.classList.add('dragging');               // 错误：targetEl 可能为 null，且没有 classList
  const dragStart = [eDown.clientX, eDown.clientY]; // 错误：Event 没有 clientX/Y
  const handleUp = (eUp: Event) => {
    targetEl.classList.remove('dragging');          // 同类错误
    targetEl.removeEventListener('mouseup', handleUp);
    const dragEnd = [eUp.clientX, eUp.clientY];
    // ...
  };
  targetEl.addEventListener('mouseup', handleUp);
}

const surfaceEl = document.getElementById('surface');
surfaceEl.addEventListener('mousedown', handleDrag); // 错误：surfaceEl 可能为 null
```

错误根源在于对 DOM 类型层次结构理解不足。

---

### 2. DOM 类型层次结构（从最通用到最具体）

| 类型 | 说明 | 包含内容 | 典型方法/属性 |
|------|------|----------|----------------|
| `EventTarget` | 最顶层的接口，可以添加/移除事件监听器、派发事件 | `window`, `XMLHttpRequest`, 所有 `Node` | `addEventListener`, `removeEventListener`, `dispatchEvent` |
| `Node` | 表示树形结构中的一个节点（可以是元素、文本、注释等） | `document`, `Text`, `Comment`, `Element` | `childNodes`, `parentNode`, `nodeType`, `textContent` |
| `Element` | 文档中的一个元素（有标签名，可能包含属性） | 所有 HTML 元素和 SVG 元素 | `tagName`, `children`, `getAttribute`, `classList` |
| `HTMLElement` | 所有 HTML 元素（不包括 SVG） | `HTMLElement`, `HTMLDivElement`, `HTMLSpanElement` 等 | `style`, `innerHTML`, `click`, `focus` |
| 具体元素类型 | 特定标签对应的接口，如 `HTMLDivElement`, `HTMLButtonElement` | `<div>`, `<button>`, `<input>` 等 | 特有属性：`value` (input), `src` (img), `href` (a) |

**关键点**：
- `EventTarget` 非常原始，**没有 `classList`**，也没有 `childNodes` 等属性。
- `Node` 有 `childNodes`，但**没有 `classList`**。
- `Element` 有 `classList`，但可能不是 `HTMLElement`（例如 SVG 元素）。
- `HTMLElement` 是所有 HTML 元素的基类，拥有布局和样式相关的属性（如 `offsetWidth`、`style`）。

---

### 3. 事件类型层次结构

类似地，事件也有层次结构：

| 类型 | 说明 | 包含信息 |
|------|------|----------|
| `Event` | 最通用的事件 | `type`, `target`, `currentTarget`, `preventDefault()` |
| `UIEvent` | 用户界面事件 | `view`, `detail` |
| `MouseEvent` | 鼠标事件 | `clientX`, `clientY`, `button`, `ctrlKey` 等 |
| `KeyboardEvent` | 键盘事件 | `key`, `code`, `shiftKey` 等 |
| `TouchEvent` | 触摸事件 | `touches`, `targetTouches` |

**关键点**：`clientX` / `clientY` 只存在于 `MouseEvent` 和 `TouchEvent` 中，不存在于 `Event` 或 `UIEvent` 中。

---

### 4. 错误分析与修复

#### 4.1 `eDown` 的类型太宽

`addEventListener('mousedown', handler)` 中的 `handler` 参数实际上是一个 `MouseEvent`，而不是普通的 `Event`。因此应该将参数类型声明为 `MouseEvent`（或者让 TypeScript 通过上下文推断）。

#### 4.2 `currentTarget` 的类型是 `EventTarget | null`

`eDown.currentTarget` 的类型是 `EventTarget | null`，没有 `classList` 属性。但在 `mousedown` 事件中，`currentTarget` 就是添加监听器的元素（这里是一个 `HTMLElement`）。我们可以通过类型断言或类型守卫将其转换为 `HTMLElement`，或者更简单地，直接使用外部变量 `el`（因为我们在 `addDragHandler` 中已经有一个 `el` 参数）。

#### 4.3 元素可能为 `null`

`document.getElementById` 返回 `HTMLElement | null`，因此需要处理 `null` 的情况（例如 `if (surfaceEl)` 或使用非空断言 `surfaceEl!`）。

---

### 5. 修复后的正确版本

```ts
function addDragHandler(el: HTMLElement) {
  el.addEventListener('mousedown', (eDown: MouseEvent) => {
    const dragStart = [eDown.clientX, eDown.clientY];
    const handleUp = (eUp: MouseEvent) => {
      el.classList.remove('dragging');
      el.removeEventListener('mouseup', handleUp);
      const dragEnd = [eUp.clientX, eUp.clientY];
      console.log('dx, dy = ', [0, 1].map(i => dragEnd[i] - dragStart[i]));
    };
    el.classList.add('dragging');
    el.addEventListener('mouseup', handleUp);
  });
}

const surfaceEl = document.getElementById('surface');
if (surfaceEl) {
  addDragHandler(surfaceEl);
}
```

**改进点**：
- 使用 `el`（`HTMLElement`）而不是 `eDown.currentTarget`，避免了 `EventTarget` 问题。
- 明确参数类型为 `MouseEvent`，可以直接访问 `clientX`、`clientY`。
- 处理了 `surfaceEl` 可能为 `null` 的情况。

---

### 6. 常见 DOM 类型实践建议

- **获取元素时尽量使用 `as` 断言到具体类型**：如果你知道 `id` 对应的元素类型，可以写 `document.getElementById('my-btn') as HTMLButtonElement`。但仅在你确信存在时才使用。
- **使用 `instanceof` 进行运行时检查**：`if (el instanceof HTMLInputElement) { ... }` 可以安全地收窄类型。
- **利用 TypeScript 的上下文推断**：将回调函数内联（而不是预先定义）可以让 TypeScript 自动推断参数类型，例如 `el.addEventListener('click', e => { ... })` 中的 `e` 会被推断为 `MouseEvent`。
- **考虑使用 `querySelector` 与具体标签选择器**：`document.querySelector('div#my-id')` 返回的类型是 `HTMLDivElement | null`，比 `getElementById` 更精确。

---

### 7. 总结

- **DOM 类型层次**：`EventTarget` → `Node` → `Element` → `HTMLElement` → 具体元素。越往下，可用的属性和方法越多。
- **事件类型层次**：`Event` → `UIEvent` → `MouseEvent`/`KeyboardEvent`/`TouchEvent`。根据事件类型选择正确的参数类型。
- **处理 `null`**：始终检查 `getElementById`、`querySelector` 等方法的返回值，或者使用非空断言（仅当你确信元素存在时）。
- **优先使用上下文推断**：内联事件处理函数，让 TypeScript 自动推断事件类型，减少手动注解。

掌握这些层次关系后，你就能自信地编写浏览器 TypeScript 代码，并理解为什么某些操作需要类型断言或类型守卫。