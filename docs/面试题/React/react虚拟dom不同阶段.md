# 手写简易虚拟DOM + Diff + 打补丁demo

> 简化版，模拟React核心逻辑：createElement生成虚拟DOM、diff对比、patch更新真实DOM。
> 不实现Fiber、调度、事件，只理解核心原理。

## 1. 虚拟DOM结构定义

虚拟DOM对象结构：

```
{
  type: string | Function; // 标签名 div/p，组件这里忽略，只处理原生标签
  props: {
    children: [], // 子虚拟DOM数组
    [key: string]: any // className style等属性
  };
  key?: string | number;
}
```

### ① createElement：模拟 React.createElement，生成虚拟DOM

```
/**
 * 创建虚拟DOM
 * @param {string} type 标签
 * @param {object} props 属性
 * @param  {...any} children 子节点
 */
function createElement(type, props, ...children) {
  // 处理children：文本节点包装成对象
  const normalizedChildren = children.map(child => {
    if (typeof child === 'string' || typeof child === 'number') {
      // 文本虚拟节点
      return {
        type: 'TEXT_ELEMENT',
        props: { nodeValue: child }
      }
    }
    return child
  })

  return {
    type,
    props: {
      ...props,
      children: normalizedChildren
    },
    key: props?.key
  }
}
```

使用，等价JSX：`<div class="app"><p>hi</p></div>`

```
const vdom = createElement('div', { className: 'app' },
  createElement('p', null, 'hi')
)
console.log(vdom)
```

## 2. render：虚拟DOM → 生成真实DOM

```
function render(vdom) {
  let dom
  // 文本节点特殊处理
  if (vdom.type === 'TEXT_ELEMENT') {
    dom = document.createTextNode(vdom.props.nodeValue)
  } else {
    // 创建标签元素
    dom = document.createElement(vdom.type)
    // 设置属性，排除children
    Object.keys(vdom.props).forEach(propName => {
      if (propName === 'children') return
      dom.setAttribute(propName, vdom.props[propName])
    })
    // 递归渲染子节点
    vdom.props.children.forEach(child => {
      dom.appendChild(render(child))
    })
  }
  // 在vdom上保存对应的真实dom，diff要用
  dom._vdom = vdom
  return dom
}
```

初次渲染：

```
const container = document.querySelector('#root')
const vdom1 = createElement('div', {className:'app'}, createElement('p',null,'hello'))
container.appendChild(render(vdom1))
```

## 3. diff 算法：对比新旧虚拟DOM，生成补丁

补丁类型：

- `REPLACE`：节点整体替换
- `PROPS`：属性更新
- `TEXT`：文本更新
- `CHILDREN`：子节点发生变化

```
const PATCH_TYPE = {
  REPLACE: 'REPLACE',
  PROPS: 'PROPS',
  TEXT: 'TEXT',
  CHILDREN: 'CHILDREN'
}

function diff(oldVdom, newVdom) {
  const patches = []

  // 1. 节点类型不一样：直接整体替换
  if (oldVdom.type !== newVdom.type) {
    patches.push({ type: PATCH_TYPE.REPLACE, newVdom })
    return patches
  }

  // 2. 文本节点：对比文本内容
  if (newVdom.type === 'TEXT_ELEMENT') {
    if (oldVdom.props.nodeValue !== newVdom.props.nodeValue) {
      patches.push({ type: PATCH_TYPE.TEXT, content: newVdom.props.nodeValue })
    }
    return patches
  }

  // 3. 属性对比
  const oldProps = oldVdom.props
  const newProps = newVdom.props
  const propPatches = {}
  // 新增/修改属性
  Object.keys(newProps).forEach(key => {
    if (key === 'children') return
    if (oldProps[key] !== newProps[key]) {
      propPatches[key] = newProps[key]
    }
  })
  // 删除旧属性
  Object.keys(oldProps).forEach(key => {
    if (key === 'children') return
    if (!newProps.hasOwnProperty(key)) {
      propPatches[key] = null
    }
  })
  if(Object.keys(propPatches).length > 0){
    patches.push({ type: PATCH_TYPE.PROPS, props: propPatches })
  }

  // 4. 子节点diff（简易版，没有完整key列表diff，仅按索引对比）
  const oldChildren = oldVdom.props.children
  const newChildren = newVdom.props.children
  const childPatches = []

  const maxLen = Math.max(oldChildren.length, newChildren.length)
  for(let i = 0; i < maxLen; i++){
    childPatches.push(diff(oldChildren[i], newChildren[i]))
  }
  patches.push({ type: PATCH_TYPE.CHILDREN, children: childPatches })

  return patches
}
```

> ⚠️这里子节点是简易版本：按索引对比，没有实现key的移动复用；真实React diff会做key映射，处理列表增删移位。

## 4. patch：把补丁应用到真实DOM

```
function patch(dom, patches) {
  patches.forEach(patch => {
    switch(patch.type){
      case PATCH_TYPE.REPLACE:{
        const newDom = render(patch.newVdom)
        dom.parentNode.replaceChild(newDom, dom)
        break
      }
      case PATCH_TYPE.TEXT:{
        dom.nodeValue = patch.content
        break
      }
      case PATCH_TYPE.PROPS:{
        Object.entries(patch.props).forEach(([k, v])=>{
          if(v === null){
            dom.removeAttribute(k)
          }else{
            dom.setAttribute(k, v)
          }
        })
        break
      }
      case PATCH_TYPE.CHILDREN:{
        const childNodes = dom.childNodes
        patch.children.forEach((childPatches, idx)=>{
          if(childNodes[idx]){
            patch(childNodes[idx], childPatches)
          }
        })
        break
      }
    }
  })
}
```

## 5. 完整运行示例

```
<!DOCTYPE html>
<div id="root"></div>
<script>
// 把上面 createElement render diff patch PATCH_TYPE 全部复制进来

// 1.初次渲染
let oldVdom = createElement('div', {className:'box'},
  createElement('h1', null, '标题'),
  createElement('p', null, '原始文本')
)
const root = document.querySelector('#root')
root.appendChild(render(oldVdom))

// 2.状态变化，生成新虚拟DOM
setTimeout(()=>{
  const newVdom = createElement('div', {className:'box active'},
    createElement('h1', null, '标题'),
    createElement('p', null, '更新后的文本')
  )
  // 得到差异补丁
  const patches = diff(oldVdom, newVdom)
  // 打补丁更新真实DOM
  patch(root.firstChild, patches)
  // 更新旧vdom引用
  oldVdom = newVdom
}, 2000)
</script>
```

> 2秒之后：div新增active属性，p标签文本更新，**不会重建整个div，只修改差异部分**。

## 和真实React的差距

1. 上面子节点diff只是按索引，**没有实现key的移动复用逻辑**；真实React会建立key→节点map，处理数组新增、删除、排序。
2. 没有Fiber、时间切片、可中断渲染；这个是同步递归diff。
3. 没有组件、hooks、合成事件、ref。
4. 属性处理简陋，没有style对象、事件(onClick)。

## 接下来讲：React render阶段 & commit阶段

React16+ 整个更新分为两大阶段：

1. **Render阶段（可中断）**
   执行组件、生成Fiber树（新版虚拟DOM）、执行diff，**纯JS计算，不碰真实DOM**。
   可以被高优先级任务打断。
2. **Commit阶段（不可中断，同步执行）**
   拿到diff后的副作用，一次性操作真实DOM：增删改DOM、执行生命周期、ref赋值。

> 我们手写demo里`diff`就是render阶段；`patch`就是commit阶段。

### 关键知识点

- setState不会立刻修改state，触发调度，进入render构建新Fiber树；
- render阶段只算，不更新页面；所有DOM修改全部集中在commit阶段执行。

如果你想，我可以再补一份**带key列表diff实现**，或者梳理一张流程图；或者讲为什么fiber要把递归改成链表。
