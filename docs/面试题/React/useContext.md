# useContext

`useContext` 是 React Hook，用于消费 **Context 上下文**，解决**跨多层组件传参（props层层透传，props drilling）**问题。

> 流程：

1. `createContext()` 创建上下文容器
2. 上层组件 `<MyContext.Provider value={数据}>` 提供数据
3. 下层任意组件 `useContext(MyContext)` 获取value

> ⚠️注意：**useContext拿到的是整个context对象，不是传字符串！不能传字符串key。**

## 基础完整示例

```
import { createContext, useContext, useState } from 'react'

// 1. 创建上下文，可以设置默认值（Provider不提供时才生效）
const CountContext = createContext(0)

// 父组件
function Parent() {
  const [count, setCount] = useState(100)
  return (
    {/* Provider提供value，所有后代组件可以读取 */}
    <CountContext.Provider value={count}>
      <Child />
    </CountContext.Provider>
  )
}

// 深层子组件，不需要props一层层传递
function Child() {
  // 2. 消费context
  const count = useContext(CountContext)
  return <div>{count}</div>
}
```

## 传递对象（同时传状态+修改方法）

实际业务经常把state和修改函数一起丢进context：

```
const UserContext = createContext(null)

function App() {
  const [user, setUser] = useState({name:'张三'})
  return (
    <UserContext.Provider value={{ user, setUser }}>
      <Page />
    </UserContext.Provider>
  )
}

function Page() {
  const { user, setUser } = useContext(UserContext)
  return (
    <div>
      {user.name}
      <button onClick={()=>setUser({name:'李四'})}>修改</button>
    </div>
  )
}
```

## 核心更新机制（面试重点）

> **当Provider的`value`发生引用变化，所有调用`useContext(该Context)`的组件，全部会重新渲染！**

### 大坑：value直接写字面量对象，造成无意义渲染

```
// ❌ 每次父组件render，value都是全新{}对象，引用永远变，所有消费组件全部重渲染
<MyContext.Provider value={{a:1, b:2}}>
```

修复：用`useMemo`缓存value对象，只有依赖变化才生成新引用

```
const value = useMemo(()=>({user, setUser}), [user])
<MyContext.Provider value={value}>
```

> 对比Redux useSelector：
>
> - `useSelector`：内部做返回值对比，**全局state变，组件不一定更新**
> - `useContext`：只要Provider的value引用变，**所有消费该context的组件全部无条件重渲染，没有内置筛选**。
>   ✨这是 useContext 和 redux最大区别。

## 如何解决useContext全量渲染问题

1. **useMemo缓存Provider的value**（基础）
2. **拆分多个Context**：不要把所有变量塞同一个context，变化频率不同的数据分开
3. Context + useReducer组合：把状态逻辑抽reducer，适合中型全局状态
4. 复杂全局状态，直接上Redux/Zustand，不要硬扛useContext

## useContext + useReducer 组合（替代简易redux）

```
const CountContext = createContext()

function reducer(state, action){
  switch(action.type){
    case 'ADD': return {count: state.count+1}
    default: return state
  }
}

function ProviderWrapper({children}){
  const [state, dispatch] = useReducer(reducer, {count:0})
  const value = useMemo(()=>({state, dispatch}),[state])
  return <CountContext.Provider value={value}>{children}</CountContext.Provider>
}

// 子组件
function Demo(){
  const {state, dispatch} = useContext(CountContext)
  return <div onClick={()=>dispatch({type:'ADD'})}>{state.count}</div>
}
```

## createContext默认值什么时候生效？

> **只有组件不在对应Provider包裹内，才使用createContext传入的默认值。**
> 如果被Provider包裹，默认值完全忽略。

```
const Ctx = createContext(100)

// 没有Provider，读取到100
function A(){
  const v = useContext(Ctx) //100
}

// 有Provider，value为200，默认值作废
<Ctx.Provider value={200}>
  <A/> {/* v=200 */}
</Ctx.Provider>
```

## 类组件对应API

```
static contextType = MyContext
this.context // 获取值
```

或者 `<MyContext.Consumer>` render props写法，现在基本被useContext替代。

## useContext 不适合做什么

1. **不适合大型全局状态**，一旦value变化所有消费组件全部渲染，性能不好；
2. 不要把所有业务状态全部塞进一个Context；
3. 不要当做简单全局变量，适合跨层级透传主题、配置、登录用户信息这类。

## 面试背诵总结

> useContext用来消费createContext创建的上下文，解决props层层透传；上层通过Provider提供value，后代组件useContext获取。
> 关键点：Provider的value引用一旦改变，**所有useContext消费该上下文的组件全部重渲染，没有过滤机制**；
> 直接写对象字面量会造成频繁渲染，需要useMemo缓存value；
> createContext的默认值仅在没有Provider包裹时生效；
> 可以搭配useReducer实现简易全局状态；复杂全局状态建议使用Redux/Zustand，避免useContext性能问题。

### 高频追问

useContext 和 useSelector区别？

> useContext：只要Provider value引用变，全部消费组件更新；
> useSelector：store变化后，对比selector返回值，只有返回值引用改变才更新组件。

如果你需要，我可以讲Zustand，轻量状态库，对比redux。
