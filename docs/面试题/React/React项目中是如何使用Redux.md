# React中使用Redux

> 注意：原生Redux本身**和React无关**，Redux是独立状态管理库；通过 `react‑redux` 库把Redux和React连接起来。
> 现在主流两套写法：

1. **旧版：原生Redux（createStore、reducer、action、connect）**，老项目；
2. **新版：Redux Toolkit(RTK)，官方推荐，新项目首选，简化样板代码**。

> 包：

- `redux`：redux核心
- `react‑redux`：react绑定库
- `@reduxjs/toolkit`：RTK工具集（官方推荐）

## 一、核心概念先记牢

1. **store**：唯一仓库，保存全局state，整个应用只有一个store
2. **state**：全局状态对象，只读
3. **action**：普通JS对象，描述“发生了什么”，必须有`type`字段，可携带`payload`数据
4. **reducer**：纯函数 `(state,action)=>newState`，根据action返回新state，**不能修改原state**
5. **dispatch**：store.dispatch(action)，派发action，触发reducer执行
6. react‑redux：
   - `<Provider store={store}>`：把store放到React上下文，后代组件可以拿到store
   - `useSelector`：组件读取state
   - `useDispatch`：组件拿到dispatch函数，派发action

---

# 方式1：Redux Toolkit RTK（现代项目，推荐）

`@reduxjs/toolkit`，内部已经封装createStore、immutable处理，**不用手写action，不用手动拷贝state**。

### 1.安装

```
npm install @reduxjs/toolkit react-redux
```

### 2.创建slice（包含state、reducers、自动生成actions）

`store/counterSlice.js`

```
import { createSlice } from '@reduxjs/toolkit'

const counterSlice = createSlice({
  name: 'counter', // slice名称，action type前缀
  initialState: {
    count: 0
  },
  reducers: {
    // 直接写赋值！RTK内部immer，允许直接“修改”state，底层生成新对象
    add(state, action) {
      state.count += action.payload
    },
    minus(state, action) {
      state.count -= action.payload
    }
  }
})

// 自动生成action
export const { add, minus } = counterSlice.actions

export default counterSlice.reducer
```

### 3.配置store

`store/index.js`

```
import { configureStore } from '@reduxjs/toolkit'
import counterReducer from './counterSlice'

export const store = configureStore({
  reducer: {
    counter: counterReducer
    // 可以放多个slice
  }
})
```

### 4.入口main.jsx，Provider包裹整个应用

```
import React from 'react'
import ReactDOM from 'react-dom/client'
import { Provider } from 'react-redux'
import { store } from './store'
import App from './App'

const root = ReactDOM.createRoot(document.getElementById('root'))
root.render(
  {/* 将store注入全局context */}
  <Provider store={store}>
    <App />
  </Provider>
)
```

### 5.组件内使用 `useSelector / useDispatch`

```
import { useSelector, useDispatch } from 'react-redux'
import { add, minus } from './store/counterSlice'

function Counter() {
  // 读取state，state.切片名.字段
  const count = useSelector(state => state.counter.count)
  const dispatch = useDispatch()

  return (
    <div>
      <div>{count}</div>
      <button onClick={()=>dispatch(add(1))}>+1</button>
      <button onClick={()=>dispatch(minus(1))}>-1</button>
    </div>
  )
}
export default Counter
```

### RTK处理异步（createAsyncThunk）

redux reducer**只能纯同步函数，不能写请求**，异步用`createAsyncThunk`

```
import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'

// 异步action
export const fetchUserInfo = createAsyncThunk(
  'user/fetchUser',
  async (id) => {
    const res = await fetch(`/api/user/${id}`)
    return await res.json()
  }
)

const userSlice = createSlice({
  name:'user',
  initialState:{
    info:null,
    loading:false
  },
  reducers:{},
  extraReducers(builder){
    builder
      .addCase(fetchUserInfo.pending,(state)=>{
        state.loading = true
      })
      .addCase(fetchUserInfo.fulfilled,(state,action)=>{
        state.info = action.payload
        state.loading = false
      })
  }
})
```

组件直接 `dispatch(fetchUserInfo(1001))`

---

# 方式2：原生redux 旧写法（老项目，了解即可）

> 手写action对象、reducer必须返回全新state，不能修改原state

```
npm install redux react-redux
```

1. reducer

```
// reducer.js
const initialState = { count:0 }
export default function counterReducer(state=initialState,action){
  switch(action.type){
    case 'ADD':
      // ❌禁止 state.count++，必须返回新对象
      return {...state, count: state.count + action.payload}
    case 'MINUS':
      return {...state, count: state.count - action.payload}
    default:
      return state
  }
}
```

2. 创建store

```
import { createStore } from 'redux'
import counterReducer from './reducer'
const store = createStore(counterReducer)
export default store
```

3. main.jsx同样用 `<Provider store={store}>`
4. 组件使用（hooks写法，不用connect）

```
import {useSelector,useDispatch} from 'react-redux'

function Demo(){
  const count = useSelector(s=>s.count)
  const dispatch = useDispatch()
  return <>
    <div>{count}</div>
    <button onClick={()=>dispatch({type:'ADD',payload:1})}>+</button>
  </>
}
```

> 类组件老写法：`connect(mapStateToProps,mapDispatchToProps)(Component)`，现在新项目基本不用。

```
// connect 类组件示例（旧）
const mapStateToProps = state => ({ count: state.count })
const mapDispatchToProps = dispatch => ({
  add: ()=>dispatch({type:'ADD',payload:1})
})
export default connect(mapStateToProps,mapDispatchToProps)(Counter)
```

## 高频面试问题

### 1. Provider作用

使用React Context，把store实例放到上下文，所有后代组件可以通过react‑redux的hooks拿到store，不用一层一层props传递。

### 2. useSelector

- 接收回调函数，返回需要的state；state变化组件重渲染。
- **注意：不要直接返回对象字面量 `useSelector(s=>({a:s.a,b:s.b}))`，每次调用返回新对象，会造成不必要重渲染；可以用shallowEqual做浅比较。**

```
import { shallowEqual, useSelector } from 'react-redux'
const {a,b} = useSelector(s=>({a:s.a,b:s.b}), shallowEqual)
```

###3. reducer为什么不能修改原state？
Redux依赖state引用变化判断是否更新；直接修改原state，引用不变，redux无法感知状态变更，UI不会更新。

> RTK用immer库，表面可以直接赋值，底层生成全新state。

###4. Redux为什么异步不能写在reducer？
reducer要求纯函数；异步请求、定时器有副作用，所以用thunk中间件处理异步。RTK内置thunk。

###5. store是单例，整个应用只有一个store，通过reducer组合拆分模块。

## connect 和 hooks(useSelector/useDispatch)对比

1. connect：高阶组件HOC，主要服务类组件；需要写mapState、mapDispatch；
2. useSelector / useDispatch：Hook，函数组件，写法简洁，现代项目主流。

## 极简面试回答

> Redux是独立状态库，react‑redux做桥接。
>
> 1. 定义reducer，创建store；
> 2. 入口用`<Provider store={store}>`注入Context；
> 3. 组件中`useSelector`读取状态，`useDispatch`派发action修改状态；
> 4. reducer接收action，返回全新state更新store；
>    新项目直接用Redux Toolkit，简化样板代码，内置immer、thunk异步中间件。

如果你需要，我可以讲redux中间件原理，redux-thunk、redux‑saga区别。
