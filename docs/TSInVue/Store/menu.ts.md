## menu.ts 中的 TypeScript 语法详解

### 1. 接口引用未导入的类型

```typescript
interface MenuState {
  menus: MenuItem[]       // MenuItem 未在此文件导入
  permissions: string[]
  activeMenu: string
}
```

**`MenuItem` 从哪来？**

```typescript
// 应该在 @/types/menu.d.ts 或其他类型文件中定义
// 这里直接使用，因为全局类型声明或自动导入
```

---

### 2. 泛型数组类型

```typescript
menus: MenuItem[]        // MenuItem 类型的数组
permissions: string[]    // string 类型的数组
```

等同于：

```typescript
menus: Array<MenuItem>
permissions: Array<string>
```

---

### 3. Getter 的类型标注

```typescript
getters: {
  visibleMenus: (state) => state.menus.filter((menu) => !menu.hidden)
}
```

| 位置 | 类型 |
|------|------|
| `(state)` | 隐式推断为 `MenuState` |
| `visibleMenus` | 自动推断为 `MenuItem[]` |
| `(menu)` | 隐式推断为 `MenuItem` |

---

### 4. 异步 Action 的返回类型

```typescript
async fetchMenus(): Promise<void> {
  const { data } = await getUserMenus()
  this.menus = data
}
```

| 部分 | 含义 |
|------|------|
| `async` | 异步方法 |
| `: Promise<void>` | 返回 Promise，不返回值 |

---

### 5. 解构赋值的类型

```typescript
const { data } = await getUserMenus()
```

**为什么能解构？**

```typescript
// getUserMenus() 返回的是 Axios 响应
interface AxiosResponse<T> {
  data: T
  status: number
  message: string
}

// 所以可以 { data } 解构
// data 的类型由泛型决定
```

---

### 6. 方法的 boolean 返回类型

```typescript
hasPermission(permission: string): boolean {
  if (this.permissions.includes('*')) return true
  return this.permissions.includes(permission)
}
```

| 返回值 | 类型 |
|--------|------|
| `return true` | boolean |
| `return false` | boolean |
| `includes()` 返回值 | boolean |

---

### 7. this 的类型

```typescript
actions: {
  setPermissions(permissions: string[]): void {
    this.permissions = permissions   // this → MenuState
  }
}
```

**Pinia 自动推断 `this` 类型：**

```
defineStore('menu', {...})
        ↓
this 自动类型化为 Store<MenuState>
        ↓
this.permissions 类型为 string[]
```

---

### 8. 与 app.ts 的 TS 区别

| 特性 | app.ts | menu.ts |
|------|--------|---------|
| 接口 | `AppState` | `MenuState` |
| Getter | ❌ 无 | ✅ 有 |
| 异步 Action | ❌ 无 | ✅ `fetchMenus` |
| 联合类型逻辑 | ❌ 无 | ✅ `includes('*')` |

---

### 9. 完整类型流程

```typescript
// 1. 定义 State 类型
interface MenuState {
  menus: MenuItem[]
  permissions: string[]
  activeMenu: string
}

// 2. state 返回值类型标注
state: (): MenuState => ({...})

// 3. actions 中 this 自动推断为 MenuState
actions: {
  setPermissions(p: string[]): void {
    this.permissions  // → string[]
  }
}

// 4. getter 自动推断返回类型
getters: {
  visibleMenus: (state) => state.menus.filter(...)
  // → MenuItem[]
}
```

---

需要继续了解 **user store** 吗？