# React Context 避免消费组件整棵树不必要重渲染问题

## 现象

当 `Context.Provider` 的 `value` 更新时，**所有消费该 Context 的组件，不管实际有没有用到变化的字段，都会触发重渲染**；并且会向下传导，导致子树重新render。

> 根源：

1. Provider 的 `value` 如果是对象字面量 `value={{a,b}}`，每次父组件render都会生成全新对象引用；
2. Context是**整体更新**：只要value引用变化，全部 `useContext`、`Consumer` 消费组件全部触发渲染，**不会做字段粒度的筛选**。

示例（坑代码）

```
// ❌ 父组件每次渲染，value都是新对象引用，所有消费组件无脑重渲染
<ThemeContext.Provider value={{ theme, setTheme, userInfo }}>
  <App />
</ThemeContext.Provider>
```

## 解决方案（4种方案，按常用程度排序）

### 方案1：拆分多个细粒度 Context（最推荐）

**不要把一堆不经常一起变化的状态塞到同一个Context里面。**

- 把高频变化状态、低频变化状态拆成不同Context。

例如：

- `ThemeContext`：主题（可能频繁切换）
- `UserContext`：用户信息（登录后基本不变）

```
<ThemeContext.Provider value={themeObj}>
  <UserContext.Provider value={userObj}>
    <App />
  </UserContext.Provider>
</ThemeContext.Provider>
```

> 效果：只有对应Context变化，才会触发对应消费组件渲染；只消费UserContext的组件，theme变化不会重渲染。

---

### 方案2：useMemo 缓存 Provider 的 value 对象引用

如果必须放在同一个Context，**不要直接写对象字面量**，用 `useMemo` 缓存value，只有依赖项真正改变，才生成新对象。

```
// ✅ 缓存value引用
const contextValue = useMemo(() => ({
  theme,
  setTheme,
  userInfo
}), [theme, setTheme, userInfo])

return (
  <ThemeContext.Provider value={contextValue}>
    <App/>
  </ThemeContext.Provider>
)
```

> 注意：`setTheme` 如果是 `useState` 返回的 dispatch，引用永远稳定，可以不用放依赖。

⚠️ 这一步**只能解决父组件无关渲染导致value引用无故变化**；
只要 `contextValue` 引用真的变了，**所有消费组件依旧全部重渲染**。useMemo不能做到“只更新用到某个字段的组件”。

---

### 方案3：使用 selector 模式：use‑context‑selector 库

> React内置 `useContext` 不支持selector；只要context value变，组件就render，不管组件只用其中哪个属性。

第三方库 `use‑context‑selector`，允许组件只订阅context里面的某一部分数据；只有**选中的那部分发生变化，当前组件才重渲染**。

安装：

```
npm install use-context-selector
```

用法要点：

1. 创建context使用库提供的 `createContext`；
2. 消费使用 `useContextSelector(context, state => state.theme)`

```
import { createContext, useContextSelector } from 'use-context-selector'

const AppContext = createContext()

// Provider
const AppProvider = ({children})=>{
  const [theme, setTheme] = useState('light')
  const [user, setUser] = useState({name:'xxx'})

  const value = useMemo(()=>({theme, setTheme, user, setUser}),[theme, user])
  return <AppContext.Provider value={value}>{children}</AppContext.Provider>
}

// 组件A：只订阅theme，user变化不会重渲染
const CompA = ()=>{
  const theme = useContextSelector(AppContext, v=>v.theme)
  return <div>{theme}</div>
}

// 组件B：只订阅user，theme变化不会重渲染
const CompB = ()=>{
  const user = useContextSelector(AppContext, v=>v.user)
  return <div>{user.name}</div>
}
```

> 这是同一个大Context下做细粒度更新的标准方案。

---

### 方案4：容器组件 + memo，拆分消费与渲染（隔离重渲染范围）

把消费context的逻辑提升到外层容器组件；内层UI组件用 `React.memo`，**不直接消费context，通过props接收数据**。
让重渲染只发生在很薄的容器组件，内部大子树不受影响。

```
// 内层纯UI组件，memo，不碰context
const InnerUI = React.memo(({theme})=>{
  return <div>{theme}</div>
})

// 外层容器负责消费context
const Wrapper = ()=>{
  const {theme} = useContext(AppContext)
  return <InnerUI theme={theme}/>
}
```

> 代价：需要写很多包装组件；适合局部优化。

## 常见误区

1. ❌以为给消费组件包 `React.memo` 就能阻止context引起的重渲染

> `memo` 只拦截props变化；**context变化不受memo控制**，依旧会重渲染。memo拦不住context更新。

2. ❌只缓存Provider value就万事大吉
   useMemo(value)只是防止无意义引用变更；一旦value真的更新，全部消费组件依然执行render。想要粒度控制，需要拆分context或者 use‑context‑selector。
3. ❌把大量不相关状态全部塞进一个Context。这是性能问题根源。

## 选型总结

1. **优先：拆分多个细粒度Context**，简单无第三方依赖；状态按变更频率拆分。
2. 状态耦合度高不方便拆分：使用 `use‑context‑selector` 做selector细粒度订阅。
3. Provider对象务必 `useMemo` 缓存，避免每次父渲染产生新引用。
4. React.memo不能阻止context带来的重渲染。

## 面试简答

> Context的问题：Provider的value引用发生变化时，所有消费该Context的组件会全部重渲染，内置useContext不支持按字段筛选更新。

1. **拆分细粒度Context**：将变化频率不同的状态拆分为多个Context，避免不相关状态变更互相影响，优先使用该方案。
2. Provider的value对象使用 `useMemo` 缓存引用，防止父组件render时生成全新对象，造成不必要的context更新。注意这只能避免无故更新，无法实现字段级按需渲染。
3. 使用 `use‑context‑selector` 库，支持selector订阅context中的部分状态，只有组件订阅的那部分数据变化，组件才重渲染。
4. 将context消费提升到外层容器，内层UI组件memo，通过props传值，缩小重渲染范围。>

> 注意：`React.memo` 只能对props生效，**无法阻止context更新触发重渲染**。

> 额外：React18 没有内置context selector，官方推荐优先拆分context；复杂场景引入use‑context‑selector。
