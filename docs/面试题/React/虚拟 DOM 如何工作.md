# React 虚拟DOM 是如何工作的

虚拟DOM本质就是**JS对象**，用来描述真实DOM的结构，不是浏览器真正DOM节点。React 核心流程：**生成虚拟DOM → Diff对比新旧虚拟DOM → 最小化更新真实DOM**。

## 1. 虚拟DOM长什么样

JS对象，标签、属性、子节点都用对象字段表达。

```
<div className="box">
  <p>hello</p>
</div>
```

编译后得到虚拟DOM（ReactElement）：

```
{
  type: 'div',
  props: {
    className: 'box',
    children: [
      { type:'p', props:{children:'hello'} }
    ]
  }
}
```

> 注意：React17之前用`React.createElement`生成；React17+ JSX自动导入`jsx()`函数。

## 2. 完整工作流程

### ① 初次渲染

1. 组件执行，返回JSX，转换成**新虚拟DOM树**
2. 根据虚拟DOM，全部创建真实DOM，渲染到页面。

### ② state/props 更新触发重渲染

1. `setState` / props改变，组件重新执行，**生成一份全新的虚拟DOM树**>

> ⚠️重点：不是修改旧虚拟DOM，是直接生成新树。

2. **Diff算法**：对比新虚拟DOM 和 上一次旧虚拟DOM，找出差异
3. 根据diff结果，只把差异部分更新到真实DOM，而不是整体重绘整个DOM树。

> 目的：DOM操作开销大，JS对象运算很快，用JS计算差异，减少DOM操作次数。

## 3. Diff算法核心规则（React的diff策略）

React不会做完整树递归对比（复杂度O(n³)性能太差），做了3条假设，时间复杂度降到O(n)

1. **同层比较，不跨层级移动节点**
   只对比同一层级节点；如果节点层级变了，直接销毁重建，不会挪位置。

```
旧：div > p
新：div > span
👉 p销毁，新建span
```

2. **type不同直接销毁重建**
   同一位置，type不一样（div→p），直接删掉旧DOM，新建DOM，不尝试复用。
3. **key用来列表diff（最重要）**
   数组循环渲染列表，必须给`key`。

- key作为节点唯一标识，在同一层根据key找旧节点，**尽量复用DOM节点，只修改属性**
- ❌不要用index当key：数组增删时index会错乱，导致节点复用错误，出现渲染bug。

> key只在兄弟节点之间做对比，不需要全局唯一。

### diff做三件事

- 新增：旧树没有，新树有 → 创建DOM
- 删除：旧树有，新树没有 → 删除DOM
- 更新：key&type相同，只是props/children变了 → 更新DOM属性，复用原有DOM节点

## 4. 两个容易混淆概念：虚拟DOM vs Fiber

> React16之后，虚拟DOM底层换成Fiber架构

- **ReactElement：JS对象，就是我们常说虚拟DOM（描述UI）**
- **Fiber：内部工作单元，是React运行时内部对象，用来实现可中断的diff、时间切片**
  平时写代码接触的是ReactElement虚拟DOM；Fiber是底层调度用。

## 5. 举个简单例子

state从`{name:'A'}`变成`{name:'B'}`

1. 组件重新运行，生成新虚拟DOM，里面文本变成B
2. diff对比新旧虚拟DOM，发现只有文本子节点变化
3. 只执行真实DOM的`textContent = 'B'`，不会重建整个div。

## 6. 误区澄清

1. ❌虚拟DOM不是直接提升渲染速度：**不是虚拟DOM比原生DOM快**，而是它**减少不必要DOM操作次数**；频繁少量更新场景收益最大。
2. ❌虚拟DOM不会跳过渲染：setState后组件依然会执行、生成新虚拟DOM；diff之后才决定要不要改真实DOM。
3. ❌diff不会移动跨层级节点，跨层级就直接销毁重建。

## 极简总结口诀

> JSX转对象(虚拟DOM) → 状态变化生成新虚拟DOM → Diff对比新旧树，借助key找差异 → 只把差异打补丁到真实DOM。

如果你需要，我可以再讲：render阶段、commit阶段，diff发生在哪一步；或者手写简易虚拟DOM+diff小demo。
