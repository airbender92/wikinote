## DefaultLayout.vue 完整解析

### 整体结构

```
<template>
  <div class="default-layout">          <!-- 根容器 -->
    <el-container>                     <!-- 布局容器 -->
      <el-aside>                       <!-- 侧边栏 -->
        <div class="logo-wrapper">      <!-- Logo 区域 -->
        <el-menu>                      <!-- 菜单 -->
          <menu-item />                 <!-- 递归菜单 -->
        </el-menu>
      </el-aside>

      <el-container>                  <!-- 主内容区 -->
        <el-header>                    <!-- 顶部导航 -->
          <el-breadcrumb />            <!-- 面包屑 -->
          <el-dropdown />              <!-- 用户下拉 -->
        </el-header>

        <el-main>                      <!-- 内容区 -->
          <router-view />              <!-- 路由出口 -->
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>
```

---

### 模板部分解析

#### 1. 侧边栏区域

```vue
<el-aside :width="sidebarWidth" class="layout-aside">
  <!-- Logo -->
  <div class="logo-wrapper">
    <svg-icon v-if="!collapsed" name="logo" class="logo-icon" />
    <span v-if="!collapsed" class="logo-text">Vue Demo</span>
  </div>

  <!-- 菜单 -->
  <el-menu
    :default-active="activeMenu"
    :collapse="collapsed"
    :collapse-transition="false"
    router
    class="sidebar-menu"
  >
    <menu-item
      v-for="menu in visibleMenus"
      :key="menu.id"
      :menu="menu"
    />
  </el-menu>
</el-aside>
```

| 属性 | 说明 |
|------|------|
| `:width="sidebarWidth"` | 动态宽度（展开220px / 折叠64px） |
| `default-active` | 当前激活菜单 |
| `:collapse="collapsed"` | 是否折叠 |
| `router` | 启用路由模式（点击菜单跳转） |
| `menu-item` | 递归渲染菜单 |

#### 2. 顶部导航

```vue
<el-header class="layout-header" height="56px">
  <div class="header-left">
    <!-- 折叠按钮 -->
    <el-icon class="collapse-btn" @click="toggleSidebar">
      <Fold v-if="!collapsed" />
      <Expand v-else />
    </el-icon>

    <!-- 面包屑 -->
    <el-breadcrumb separator="/">
      <el-breadcrumb-item
        v-for="item in breadcrumbs"
        :key="item.path"
        :to="item.path"
      >
        {{ item.title }}
      </el-breadcrumb-item>
    </el-breadcrumb>
  </div>

  <div class="header-right">
    <!-- 用户下拉 -->
    <el-dropdown trigger="click" @command="handleCommand">
      <div class="user-info">
        <el-avatar :size="28" class="user-avatar">
          {{ username.charAt(0).toUpperCase() }}
        </el-avatar>
        <span class="username">{{ username }}</span>
      </div>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item command="profile">个人中心</el-dropdown-item>
          <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>
</el-header>
```

| 元素 | 说明 |
|------|------|
| `Fold / Expand` | 根据折叠状态切换图标 |
| `breadcrumbs` | 从路由 matched 生成面包屑 |
| `el-dropdown` | 用户下拉菜单 |
| `command="logout"` | 点击触发退出 |

#### 3. 内容区（keep-alive）

```vue
<el-main class="layout-main">
  <router-view v-slot="{ Component }">
    <keep-alive>
      <component :is="Component" />
    </keep-alive>
  </router-view>
</el-main>
```

**为什么用 keep-alive？**

| 效果 | 说明 |
|------|------|
| 缓存组件 | 切换路由时不销毁组件 |
| 保留状态 | 如列表页滚动位置、表单数据 |
| 提升性能 | 避免重复创建组件 |

---

### script setup 部分

```typescript
const router = useRouter()
const route = useRoute()
const appStore = useAppStore()
const menuStore = useMenuStore()
const userStore = useUserStore()
```

#### 计算属性

```typescript
const collapsed = computed(() => appStore.sidebarCollapsed)

const sidebarWidth = computed(() => (collapsed.value ? '64px' : '220px'))

const visibleMenus = computed(() => menuStore.visibleMenus)

const activeMenu = computed(() => route.path)

const username = computed(() => userStore.username)

const breadcrumbs = computed<BreadcrumbItem[]>(() => {
  const matched = route.matched.filter((item) => item.meta?.title)
  return matched.map((item) => ({
    path: item.path,
    title: item.meta.title as string,
  }))
})
```

| 计算属性 | 来源 | 用途 |
|---------|------|------|
| `collapsed` | appStore | 侧边栏折叠状态 |
| `sidebarWidth` | collapsed | 动态宽度 |
| `visibleMenus` | menuStore | 过滤后的菜单 |
| `activeMenu` | route.path | 当前路由 |
| `breadcrumbs` | route.matched | 面包屑数据 |

#### 方法

```typescript
function toggleSidebar() {
  appStore.toggleSidebar()
}

async function handleCommand(command: string) {
  if (command === 'logout') {
    await userStore.logout()
  }
}
```

---

### 样式部分

```scss
.default-layout {
  height: 100vh;           // 占满视口
  overflow: hidden;
}

.layout-aside {
  background-color: #001529; // 深蓝背景（Ant Design 风格）
  transition: width 0.3s;   // 宽度过渡动画

  .logo-wrapper {
    height: $header-height;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.sidebar-menu {
  border-right: none;
  background-color: transparent;

  :deep(.el-menu-item.is-active) {
    background-color: $primary-color;  // Element Plus 蓝色
    color: #fff;
  }
}
```

| 样式特性 | 说明 |
|---------|------|
| `height: 100vh` | 固定高度，不随页面滚动 |
| `transition: width 0.3s` | 侧边栏折叠动画 |
| `:deep()` | 深度选择器，修改 Element Plus 内部样式 |
| SCSS 变量 | `$header-height`、`$primary-color` 等来自 variables.scss |

---

### 布局层级图

```
┌────────────────────────────────────────────┐
│ Header (56px)                              │
│ ┌──────────┬────────────────────────────┐   │
│ │ FoldIcon │ Breadcrumb    [UserAvatar]│   │
│ └──────────┴────────────────────────────┘   │
├────────────────────────────────────────────┤
│ Sidebar       │ Main                       │
│ (220/64px)    │                            │
│ ┌──────────┐  │ ┌────────────────────────┐ │
│ │ Logo     │  │ │                        │ │
│ ├──────────┤  │ │   <router-view>        │ │
│ │ Menu     │  │ │   (页面内容)            │ │
│ │  - item  │  │ │                        │ │
│ │  - item  │  │ │                        │ │
│ │    - sub │  │ │                        │ │
│ └──────────┘  │ └────────────────────────┘ │
│               │                            │
└────────────────────────────────────────────┘
```

---

### 与其他模块的关系

```
userStore → username（用户信息）
menuStore → visibleMenus（菜单列表）
appStore  → collapsed（侧边栏状态）
router    → route.path、breadcrumbs（路由信息）
```

---

需要继续了解 **路由配置** 吗？