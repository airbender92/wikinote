## menu.ts 完整解读

### 1. 整体结构

```typescript
export const useMenuStore = defineStore('menu', {
  state: (): MenuState => ({...}),   // 状态
  getters: {...},                    // 计算属性
  actions: {...},                    // 方法
})
```

### 2. State 定义

```typescript
interface MenuState {
  menus: MenuItem[]        // 菜单列表
  permissions: string[]    // 权限列表 ['user:add', 'user:delete']
  activeMenu: string       // 当前激活菜单的路径
}
```

### 3. Getters（计算属性）

```typescript
getters: {
  visibleMenus: (state) => state.menus.filter((menu) => !menu.hidden)
}
```

| 特点 | 说明 |
|------|------|
| `visibleMenus` | 过滤掉 `hidden: true` 的菜单 |
| 响应式 | 当 `menus` 变化时自动重新计算 |

### 4. Actions（方法）

```typescript
actions: {
  async fetchMenus(): Promise<void> {
    const { data } = await getUserMenus()
    this.menus = data
  },
  
  setPermissions(permissions: string[]): void {...},
  
  hasPermission(permission: string): boolean {...},
  
  resetMenuState(): void {...}
}
```

| 方法 | 作用 | 调用时机 |
|------|------|---------|
| `fetchMenus()` | 从后端获取菜单 | 登录成功后 |
| `setPermissions()` | 设置权限列表 | 登录成功后 |
| `hasPermission()` | 检查权限 | 路由守卫、按钮权限 |
| `resetMenuState()` | 清空菜单状态 | 退出登录时 |

### 5. hasPermission 权限逻辑

```typescript
hasPermission(permission: string): boolean {
  if (this.permissions.includes('*')) return true  // 超级管理员
  return this.permissions.includes(permission)
}
```

```
用户权限: ['user:add', 'user:edit']
检查: 'user:delete'

包含 '*' ?  → 否
包含 'user:delete' ? → 否
返回 false ❌ 无权限
```

```
用户权限: ['*']
检查: 'user:delete'

包含 '*' ?  → 是
返回 true ✅ 有权限
```

### 6. 与其他模块的关系

```
user store (登录)
    ↓ 登录成功后
menu store (获取菜单和权限)
    ↓
router (动态生成路由)
    ↓
layout (渲染菜单)
    ↓
directive (按钮权限 v-permission)
```

### 7. 使用示例

```typescript
const menuStore = useMenuStore()

// 获取菜单
await menuStore.fetchMenus()

// 在模板中使用 getter
menuStore.visibleMenus  // 自动过滤隐藏菜单

// 权限判断
if (menuStore.hasPermission('user:delete')) {
  // 显示删除按钮
}

// 退出时重置
menuStore.resetMenuState()
```

---

需要继续了解 **user store** 吗？