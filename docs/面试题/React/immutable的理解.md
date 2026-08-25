# Immutable 理解

## 什么是不可变（immutable）

> **不可变：数据一旦创建，就不能直接修改原数据；要修改，必须生成一份全新的数据，原对象保持原样。**

JS 默认对象、数组是**可变(mutable)**：

```js
const obj = { a: 1 };
obj.a = 2; // ✅直接修改原对象，原地变更
```

这就是可变，原引用没变，内容改了。

不可变写法，不改动原来obj，返回新对象：

```js
const obj = { a: 1 };
const newObj = { ...obj, a: 2 }; // 新对象，obj原封不动
```

---

## 为什么Redux要求reducer必须immutable

Redux靠**引用是否变化**判断状态有没有更新：

```js
// ❌错误，原地修改，引用不变，redux感知不到，UI不会更新
function reducer(state, action) {
  state.count++;
  return state;
}

// ✅正确，返回全新对象，引用改变
function reducer(state, action) {
  return { ...state, count: state.count + 1 };
}
```

> 如果直接修改state，对象引用不变，`useSelector`对比引用，认为数据没变，组件不会重渲染。

### 原生JS实现不可变的痛点

1. 简单对象：`{...obj}` 展开还行
2. **嵌套深层对象，写起来非常痛苦**

```js
// state.user.info.name 修改，多层展开
return {
  ...state,
  user: {
    ...state.user,
    info: {
      ...state.user.info,
      name: "newName",
    },
  },
};
```

嵌套越深，代码爆炸，容易漏写一层，不小心修改原state。

> 于是出现两类方案：Immutable.js、Immer

---

## 1. Immutable.js（第三方库，老项目）

Facebook出品，全新一套数据结构 `Map、List`，不是普通js对象。

```js
import { Map } from "immutable";
const state = Map({ count: 0 });
// set 返回新的Map实例，不会修改原state
const newState = state.set("count", 10);
```

特点：

- 真正不可变，所有操作返回新实例；
- 数据不是原生JS对象，需要 `.get()`、`.toJS()` 取值，写法繁琐；
- 和普通JS混用很别扭，现在新项目基本不用。

缺点：

- 学习成本高；
- 大量toJS转换，有性能开销；
- 类型TS支持麻烦。

> 现在企业很少用 Immutable.js。

## 2. Immer（现在主流，RTK内置！）⭐

> **Immer核心：produce函数**
> 允许你**表面写直接修改的代码**，内部帮你生成全新不可变对象。

```js
import { produce } from "immer";

const baseState = {
  user: {
    info: { name: "张三" },
  },
};

const nextState = produce(baseState, (draft) => {
  // ✅这里可以直接修改draft，只是代理对象，不会改动原baseState
  draft.user.info.name = "李四";
});
```

- `draft`：代理草稿对象，你随便改；
- produce返回一份全新的state，原始`baseState`完全不变。

### Redux‑Toolkit 内部就集成了Immer

所以在 `createSlice` 的reducers里面，可以直接写赋值：

```js
const slice = createSlice({
  name: "user",
  initialState: { name: "张三" },
  reducers: {
    changeName(state, action) {
      // 看似原地修改，实际是immer代理，生成新state
      state.name = action.payload;
    },
  },
});
```

> ⚠️注意：**只能在RTK的reducer里面这么写！普通原生redux reducer不能直接修改state。**

### immer不能做的事

不要直接返回 `draft`，不要把draft赋值给外部变量；不要解构draft。

---

# 核心区分

1. **Immutable.js：全新数据类型 Map/List，老方案，现在少用**
2. **Immer：基于原生JS对象，代理劫持，写可变语法产出不可变数据，RTK内置，现代首选**

## 为什么需要不可变，完整收益

1. ✅Redux/Vuex状态库：靠引用变化判断状态更新；
2. ✅方便做时间旅行调试（redux‑devtools），记录每一份state快照；
3. ✅方便做比较、缓存；React.memo、useSelector靠引用对比；
4. ✅避免副作用，防止多处共享同一个对象意外互相篡改。

## 坑点：什么叫“浅不可变”

```js
const state = { user: { name: "张三" } };
const newState = { ...state };
newState.user.name = "李四";
```

> `...state` 只拷贝第一层，**user依旧是原来对象的引用**，直接改里面的属性，还是修改原数据。
> 这就是**浅拷贝，不能解决嵌套对象不可变**，这也是immer解决的痛点。

## 面试题：手写简答

> Immutable不可变，指数据不能原地修改，修改要返回全新数据。
> Redux的reducer要求不可变，因为redux通过引用对比判断状态变更，原地修改引用不变UI不会更新。
> 原生JS嵌套对象展开写法繁琐；老方案Immutable.js提供Map、List专用数据结构；现在主流Immer，通过produce生成代理draft，可以像写可变代码一样，内部自动生成全新不可变对象，Redux‑Toolkit内置Immer。
> 注意对象展开只是浅拷贝，嵌套对象依旧会原地修改。

### 高频追问：RTK里面既然有immer，那我可以直接修改state吗？

> 只能修改produce/RTK reducer给你的draft代理对象；外部原始state依旧不能直接修改。

如果你需要，我可以对比：`immer`、`immutable.js`、`toJS`、`structuredClone`深拷贝的区别。
