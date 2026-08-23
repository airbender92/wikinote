# useCallback + React.memo Demo
核心要点：
1. `React.memo`：包裹子组件，**对 props 做浅对比**，props 不变就跳过渲染，对标类组件 `PureComponent`
2. `useCallback(fn, deps)`：缓存函数引用，依赖不变时，函数引用地址不变；专门解决**把函数作为 props 传给 memo 子组件**时，父组件更新导致子组件无效重渲染

> ⚠️注意：只靠 `React.memo` 没用，父组件每次渲染都会生成新函数，props 函数引用变了，memo 依然会触发子组件重渲染，需要 `useCallback` 稳住函数引用。

```tsx
import React, { useState, useCallback } from 'react';

// 子组件：用 React.memo 做 props 浅比较
const Child = React.memo(({ onClick, count }: { onClick: () => void; count: number }) => {
  console.log('👉子组件渲染');
  return (
    <div style={{ border: '1px solid #ccc', padding: 10 }}>
      <p>子组件count: {count}</p>
      <button onClick={onClick}>子组件按钮</button>
    </div>
  );
});

export default function Parent() {
  const [parentNum, setParentNum] = useState(0);
  const [childCount, setChildCount] = useState(0);

  console.log('🚀父组件渲染');

  // useCallback：缓存函数，依赖[childCount]不变，函数引用就不变
  const handleChildClick = useCallback(() => {
    setChildCount(prev => prev + 1);
  }, [childCount]);

  return (
    <div style={{ padding: 10 }}>
      <h3>父组件</h3>
      <p>父组件状态：{parentNum}</p>
      {/* 修改父组件状态，父组件会重新render */}
      <button onClick={() => setParentNum(p => p + 1)}>修改父组件state</button>

      {/* 传给memo子组件：使用useCallback缓存后的函数 */}
      <Child onClick={handleChildClick} count={childCount} />
    </div>
  );
}
```

## 运行现象
1. 点击【修改父组件state】：
   - 控制台打印 `🚀父组件渲染`
   - **不会打印 `👉子组件渲染`**
   > 原因：`handleChildClick` 被 `useCallback` 缓存，引用不变；`count` props 也没变；`React.memo` 浅对比 props 全部相等，子组件跳过重渲染。

2. 点击【子组件按钮】：
   - 修改 `childCount`，`useCallback` 依赖变化 → 生成新函数引用
   - props `count` 也变化，子组件正常重新渲染。

## ❌反面示例（不使用useCallback）
如果直接写，不用`useCallback`：
```tsx
// 父组件内，每次父渲染都会生成全新函数引用
const handleChildClick = () => {
  setChildCount(prev => prev + 1);
};
```
此时哪怕子组件包了`React.memo`，**每次父组件更新，子组件也会跟着重渲染**，因为函数 props 的引用地址每次都是新对象，浅比较判定 props 发生变化。

## 补充注意点
1. `useCallback` 不是万能优化，有极小的内存与判断开销，不要所有函数无脑包；适合：传给`memo`子组件、作为其他hook依赖（useEffect、useMemo）。
2. `React.memo`只是**浅比较**，如果 props 传对象/数组字面量 `xxx={{a:1}}`，每次都是新引用，memo依然失效，对象需要配合`useMemo`缓存。
3. 类组件对比：
   - `React.memo(函数组件)` ≈ `PureComponent`
   - `useCallback` 负责稳住函数引用；`useMemo` 负责稳住对象/数组值引用。

### 配套useMemo小例子（对象props场景）
```tsx
const info = useMemo(() => ({ name: 'test' }), []);
<ChildMemo info={info} />
```
> 如果直接写`<ChildMemo info={{ name:'test' }}>`，每次父渲染对象都是新引用，memo失效。

如果你需要，我可以再写一个对比版本，把「用useCallback」和「不用useCallback」两个版本放在同一个文件，方便你复制到项目直接看控制台日志对比效果。