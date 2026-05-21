## Item 69 详细讲解：当回调函数依赖 `this` 时，为其提供类型

JavaScript 中的 `this` 关键字非常特殊，它的值**不取决于词法作用域**（不像普通变量由代码位置决定），而是取决于**函数是如何被调用的**（即运行时绑定）。这种动态绑定带来了很大的灵活性，但也极易出错。TypeScript 允许你在函数类型中显式声明 `this` 的类型，以便在回调函数场景中提供正确的类型检查。

---

### 1. `this` 动态绑定的问题：方法提取丢失 `this`

```ts
class C {
  vals = [1, 2, 3];
  logSquares() {
    for (const val of this.vals) {
      console.log(val ** 2);
    }
  }
}

const c = new C();
c.logSquares();       // 正常，输出 1, 4, 9

const method = c.logSquares;
method();             // 运行时错误：Cannot read property 'vals' of undefined
```

**原因**：`c.logSquares()` 实际上做了两件事：  
- 调用 `C.prototype.logSquares`  
- 将函数内部的 `this` 绑定到 `c`  

当你提取 `method = c.logSquares` 后，`method()` 只是直接调用函数，没有绑定 `this`（非严格模式下 `this` 成为全局对象，严格模式下为 `undefined`），因此访问 `this.vals` 失败。

**修复**：使用 `bind` 或箭头函数。

---

### 2. 常见场景：DOM 事件回调中的 `this`

许多 JavaScript API（如 DOM 事件监听器、jQuery 等）会**主动设置**回调函数中的 `this` 值。例如：

```ts
document.querySelector('input')?.addEventListener('change', function(e) {
  console.log(this);   // 这里 this 指向触发事件的 input 元素
});
```

这是 API 设计的一部分：回调函数中的 `this` 被绑定了特定的上下文。如果你用 TypeScript 编写这样的库，就需要在类型声明中体现这一点。

---

### 3. 在 TypeScript 中声明带有 `this` 的回调类型

你可以在回调函数的类型签名中**添加一个假的 `this` 参数**，它必须是参数列表的第一个，且名字必须为 `this`。TypeScript 会特殊处理它：它不占用实际参数位置，仅用于类型检查。

```ts
function addKeyListener(
  el: HTMLElement,
  listener: (this: HTMLElement, e: KeyboardEvent) => void
) {
  el.addEventListener('keydown', e => listener.call(el, e));
}
```

- `listener` 的类型是 `(this: HTMLElement, e: KeyboardEvent) => void`  
- 这表示：调用 `listener` 时，必须通过 `.call`、`.apply` 或直接绑定等方式，确保它的 `this` 是 `HTMLElement` 类型。

#### 为什么 `this` 参数是“假的”？

因为调用时你不能像普通参数那样传递一个参数。下面这样会出错：

```ts
function addKeyListener(
  el: HTMLElement,
  listener: (this: HTMLElement, e: KeyboardEvent) => void
) {
  el.addEventListener('keydown', e => {
    listener(el, e);   // 错误：期望 1 个参数，但得到了 2 个
  });
}
```

`listener` 实际上只接受一个参数（`e`），而不是两个。`this` 参数仅仅用于类型检查，并不增加函数参数数量。

---

### 4. TypeScript 如何强制执行正确的 `this`

当你正确使用 `.call` 时，TypeScript 会检查 `this` 的类型是否匹配：

```ts
el.addEventListener('keydown', e => {
  listener(e);
  // 错误：'this' 上下文类型为 'void'，不能赋给 'HTMLElement'
});
```

因为 `listener(e)` 没有指定 `this`，TypeScript 认为 `this` 是 `undefined`（严格模式），而期望的是 `HTMLElement`，所以报错。正确的方式是 `listener.call(el, e)`。

---

### 5. 作为回调的使用者，如何获得类型安全的 `this`

当你调用 `addKeyListener` 并传入一个普通函数（不是箭头函数）时，TypeScript 会正确推断回调内部的 `this` 类型：

```ts
addKeyListener(el, function(e) {
  console.log(this.innerHTML);   // ✅ this 被推断为 HTMLElement
});
```

箭头函数会**捕获外层 `this`**，而不是动态绑定。因此，如果你在类中使用箭头函数作为回调，`this` 可能不是你想要的那个：

```ts
class Foo {
  registerHandler(el: HTMLElement) {
    addKeyListener(el, e => {
      console.log(this.innerHTML);   // 错误：this 是 Foo，没有 innerHTML
    });
  }
}
```

这里箭头函数中的 `this` 是外层 `Foo` 实例，因此访问 `this.innerHTML` 报错。TypeScript 正确捕获了这个错误。

---

### 6. 设计新 API 的建议

- **尽量避免依赖动态 `this` 绑定的回调**。因为箭头函数的广泛使用，现代 JS 中开发者更习惯词法 `this`。如果必须依赖 `this`，请确保类型声明中包含 `this` 参数。
- **优先使用回调参数传递上下文**，而不是依赖 `this`。例如：

```ts
interface Listener {
  (e: KeyboardEvent, target: HTMLElement): void;
}
```

这样用户不需要理解 `this` 的诡异行为。

---

### 7. 总结

- `this` 是动态绑定的，在回调中其值可能由调用者设置。
- 如果你编写的库会改变回调的 `this`，必须在类型声明中通过**假的 `this` 参数**明确指定其类型。
- 用户使用回调时，必须使用普通函数（不是箭头函数）才能获得正确的 `this` 推断。
- TypeScript 会强制要求你通过 `.call` / `.apply` 等方式传入正确的 `this` 上下文。
- 新 API 最好避免依赖动态 `this`，改用显式参数传递上下文。

**记住**：`this` 是 JavaScript 最难懂的部分之一。如果你不得不让回调依赖 `this`，请务必在类型系统中明确标注，否则用户会感到困惑并产生 bug。