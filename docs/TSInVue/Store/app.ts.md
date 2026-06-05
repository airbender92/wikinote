## app.ts 中的 TypeScript 语法详解

### 1. 接口定义 State 类型

```typescript
interface AppState {
  sidebarCollapsed: boolean
  loading: boolean
}
```

**为什么需要接口？**

| 写法 | 类型安全 | 代码提示 |
|------|---------|---------|
| `{ sidebarCollapsed: false }` | ❌ 无类型约束 | ❌ 无提示 |
| `: AppState` 接口约束 | ✅ 严格类型 | ✅ 完整提示 |

---

### 2. 箭头函数返回类型

```typescript
state: (): AppState => ({
  sidebarCollapsed: false,
  loading: false,
})
```

拆解：

```typescript
(): AppState => { ... }
 ↑
 ↓
(state 是一个函数，返回 AppState 类型)
```

完整展开：

```typescript
state: (): AppState => {
  return {
    sidebarCollapsed: false,
    loading: false,
  }
}

// 或不用箭头函数
state function(): AppState {
  return {
    sidebarCollapsed: false,
    loading: false,
  }
}
```

---

### 3. 方法的返回类型

```typescript
toggleSidebar(): void {
  this.sidebarCollapsed = !this.sidebarCollapsed
}
```

| 部分 | 含义 |
|------|------|
| `toggleSidebar` | 方法名 |
| `(): void` | 返回值类型（void = 无返回值） |
| `this.sidebarCollapsed` | Pinia 自动绑定到 state |

---

### 4. 参数类型约束

```typescript
setSidebarCollapsed(collapsed: boolean): void
```

```typescript
// 等价于
setSidebarCollapsed = (collapsed: boolean): void => {
  this.sidebarCollapsed = collapsed
}
```

---

### 5. Pinia 的泛型推断

```typescript
export const useAppStore = defineStore('app', {
  // ...
})
```

| 写法 | 推断效果 |
|------|---------|
| `defineStore('app', {...})` | store 实例有完整类型 |
| `useAppStore()` | 返回值自动推断 state 和 actions |

**效果示例：**

```typescript
const appStore = useAppStore()

appStore.sidebarCollapsed  // ✅ boolean 类型
appStore.toggleSidebar()   // ✅ 方法签名正确
```

---

### 6. 完整类型推导

```typescript
// 定义时
interface AppState {
  sidebarCollapsed: boolean
  loading: boolean
}

// state 返回 AppState
state: (): AppState => ({...})

// actions 中 this 自动为 AppState 类型
actions: {
  toggleSidebar(): void {
    this.sidebarCollapsed  // ✅ boolean
    this.loading           // ✅ boolean
  }
}
```

---

### 7. 与普通 JS 的对比

**JavaScript 版本：**
```javascript
export const useAppStore = defineStore('app', {
  state: () => ({
    sidebarCollapsed: false,
    loading: false,
  }),
  actions: {
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed
    },
  },
})
```

**TypeScript 版本：**
```typescript
interface AppState {
  sidebarCollapsed: boolean
  loading: boolean
}

export const useAppStore = defineStore('app', {
  state: (): AppState => ({
    sidebarCollapsed: false,
    loading: false,
  }),
  actions: {
    toggleSidebar(): void {
      this.sidebarCollapsed = !this.sidebarCollapsed
    },
  },
})
```

| 增强点 | JS | TS |
|--------|----|----|
| state 属性 | ❌ 无提示 | ✅ 完整提示 |
| 参数类型 | ❌ 无检查 | ✅ 编译检查 |
| 返回值 | ❌ 无检查 | ✅ 类型约束 |

---

### 总结

| TS 语法 | 作用 |
|---------|------|
| `interface` | 定义 state 结构 |
| `(): AppState` | 箭头函数返回类型 |
| `: void` | 方法返回值 |
| `: boolean` | 参数类型 |
| `this` 绑定 | Pinia 隐式推断 this 类型 |

---

需要继续了解 **user store** 吗？