## MenuItem.vue 递归菜单组件解读

```vue
<template>
  <el-sub-menu v-if="menu.children?.length" :index="menu.path">
    <template #title>
      <el-icon v-if="menu.icon"><component :is="menu.icon" /></el-icon>
      <span>{{ menu.title }}</span>
    </template>
    <menu-item
      v-for="child in menu.children"
      :key="child.id"
      :menu="child"
    />
  </el-sub-menu>
  <el-menu-item v-else :index="menu.path">
    <el-icon v-if="menu.icon"><component :is="menu.icon" /></el-icon>
    <template #title>{{ menu.title }}</template>
  </el-menu-item>
</template>

<script setup lang="ts">
defineProps<{
  menu: MenuItem
}>()
</script>
```

---

### 1. 递归组件

```vue
<menu-item
  v-for="child in menu.children"
  :key="child.id"
  :menu="child"
/>
```

**关键点：** 组件自己调用自己，实现无限层级菜单

```
菜单结构：
├─ 用户管理 (el-sub-menu)
│   ├─ 用户列表 (el-sub-menu)
│   │   └─ 用户详情 (el-menu-item)
│   └─ 添加用户 (el-menu-item)
└─ 系统设置 (el-sub-menu)
```

---

### 2. 条件渲染

```vue
<el-sub-menu v-if="menu.children?.length" ...>
  <!-- 有子菜单 -->
</el-sub-menu>
<el-menu-item v-else ...>
  <!-- 无子菜单 -->
</el-menu-item>
```

| 条件 | 渲染 |
|------|------|
| `menu.children?.length > 0` | `el-sub-menu`（可展开的父菜单） |
| 否则 | `el-menu-item`（最终菜单项） |

---

### 3. 动态组件

```vue
<el-icon v-if="menu.icon">
  <component :is="menu.icon" />
</el-icon>
```

**`<component :is="menu.icon" />` 解释：**

```typescript
// menu.icon = 'User'（字符串）
// 等价于
<User />

// 动态渲染 Element Plus 图标组件
```

**为什么用动态组件？**
```typescript
// 不同的菜单有不同图标
{ title: '用户', icon: 'User' }
{ title: '订单', icon: 'Goods' }
{ title: '设置', icon: 'Setting' }
```

---

### 4. Props 定义

```typescript
defineProps<{
  menu: MenuItem
}>()
```

| 语法 | 含义 |
|------|------|
| `defineProps<{...}>()` | TypeScript 类型声明 props |
| `MenuItem` | 菜单项的类型（来自 @/types/menu.d.ts） |

**自动推导：**
```typescript
// 父组件传入
<menu-item :menu="currentMenu" />

// Props 类型自动为 MenuItem
```

---

### 5. 模板逻辑图

```
menu.children 存在且有长度？
    ↓ yes
el-sub-menu（可展开父菜单）
    ├── #title 插槽（显示图标+标题）
    └── menu-item（递归渲染子菜单）
    
    ↓ no
el-menu-item（最终菜单项）
    ├── 显示图标
    └── 显示标题
```

---

### 6. 完整菜单渲染示例

```typescript
// 菜单数据
const menu = {
  title: '系统管理',
  icon: 'Setting',
  children: [
    {
      title: '用户管理',
      icon: 'User',
      children: [
        { title: '用户列表', path: '/users' },
        { title: '添加用户', path: '/users/add' },
      ]
    }
  ]
}
```

**渲染结果：**
```
<ul>
  <li>系统管理 (el-sub-menu)
    <ul>
      <li>用户管理 (el-sub-menu)
        <ul>
          <li>用户列表 (el-menu-item)
          <li>添加用户 (el-menu-item)
        </ul>
      </li>
    </ul>
  </li>
</ul>
```

---

### 7. 为什么用递归？

```vue
<!-- MenuItem.vue 自身调用 -->
<menu-item :menu="child" />
```

**解决的问题：**
- 菜单层级不确定（1级、2级、3级...）
- 递归可以处理任意层级

**如果是 3 层嵌套？**
```
1层: <menu-item /> 
2层: <menu-item /> 
3层: <menu-item /> ← 继续递归调用自己
```

---

### 8. 与 Element Plus 组件对应

| 组件 | 用途 |
|------|------|
| `el-menu` | 菜单容器 |
| `el-sub-menu` | 可展开的父菜单 |
| `el-menu-item` | 最终菜单项 |
| `#title` | 菜单标题插槽 |

---

### 9. script setup 写法

```typescript
defineProps<{
  menu: MenuItem
}>()
```

| 语法 | 说明 |
|------|------|
| `<script setup>` | Vue 3 组合式 API 语法糖 |
| `defineProps` | 编译时宏，自动导入 |
| `MenuItem` | 类型来自全局类型声明（无需 import） |

---

### 10. 总结

| 特性 | 说明 |
|------|------|
| 递归 | 自身调用自身，处理无限层级 |
| 动态组件 | 根据 icon 字符串渲染不同图标 |
| 条件渲染 | 有子菜单用 sub-menu，否则用 menu-item |
| TypeScript | defineProps 泛型定义 |

---

需要继续了解 **路由配置** 吗？