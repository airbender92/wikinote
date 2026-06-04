# 前端架构设计文档（Vue3 + TS 方案）

## 一、技术栈选型
- 框架：**Vue 3**
- 开发语言：**TypeScript**
- 构建工具：**Vite**
- 状态管理：**Pinia**
- 路由：**Vue Router**
- UI 组件库：**Element Plus**
- CSS 方案：**SCSS + Tailwind CSS**
- 请求库：**Axios**

## 二、项目结构规划
```
src/
├── api/               # 接口请求封装与业务接口
├── assets/            # 静态资源
├── components/        # 公共组件
├── hooks/             # 组合式函数
├── layouts/           # 布局组件（Layout、空布局等）
├── router/            # 路由配置、路由守卫
├── store/             # Pinia 状态管理
├── styles/            # 全局样式、变量、mixin
├── types/             # TS 类型声明
├── utils/             # 工具函数
├── views/             # 页面组件
│   ├── login/         # 登录页
│   └── dashboard/     # 控制台页
├── App.vue
└── main.ts
```

## 三、请求封装设计（axios）

### 3.1 核心能力
- 请求/响应拦截器
- 请求缓存机制
- 防重复请求
- 统一错误处理
- 401/403 自动重定向登录
- 支持单点登录票据传递

### 3.2 实现要点
```typescript
// utils/request.ts
class Request {
  instance: AxiosInstance;
  pendingMap: Map<string, AbortController>; // 防重复
  cacheMap: Map<string, { data: any; expire: number }>; // 请求缓存

  constructor() {
    this.instance = axios.create({ baseURL, timeout });
    this.pendingMap = new Map();
    this.cacheMap = new Map();
    this.setupInterceptors();
  }

  // 请求拦截：token、防重复、缓存
  // 响应拦截：数据解析、错误码处理、登录跳转
}

export const request = new Request();
```

## 四、路由与鉴权体系

### 4.1 路由守卫逻辑
- 全局前置守卫判断登录状态与权限
- 未登录 → 重定向至登录页
- 登录过期/无权限 → 清除 token → 跳转登录
- 支持单点登录回调处理

### 4.2 菜单权限控制
- 后端返回权限码/路由表
- 前端动态生成菜单与可访问路由
- 页面级权限 + 按钮级权限指令
- 左侧菜单根据权限动态渲染

## 五、状态管理（Pinia）
- `userStore`：用户信息、token、登录状态、单点登录信息
- `menuStore`：菜单列表、权限码、当前激活菜单
- `appStore`：全局配置、主题、多标签页、加载状态

## 六、TypeScript 规范
- 统一在 `types/` 目录管理全局类型：
  - `user.d.ts`
  - `menu.d.ts`
  - `api.d.ts`
  - `common.d.ts`
- 接口返回值、props、store state 均需显式声明
- 禁止隐式 any，严格开启 TS 校验

## 七、样式规范
- 全局布局使用 Tailwind CSS 快速搭建
- 组件复杂样式使用 SCSS 变量、mixin、嵌套
- 主题色、间距统一在 `styles/variables.scss` 定义
- 避免样式污染，使用 scoped 或 CSS Modules

## 八、默认页面实现
1. **登录页**
   - 账号密码登录
   - 支持单点登录跳转/回调
   - 表单校验、loading 状态
2. **Dashboard 控制台**
   - 布局：Header + Sidebar + Main
   - 侧边栏菜单（权限控制）
   - 面包屑、用户信息展示
   - 路由出口渲染子页面

## 九、权限与安全
- 路由级鉴权：未登录禁止访问
- 接口级鉴权：请求头携带 token
- 菜单权限：动态过滤无权限菜单
- 单点登录：统一票据验证与过期处理
- 敏感路由使用守卫拦截，防止越权访问

## 十、工程化与规范
- ESLint + Prettier 代码规范
- Git 提交规范
- 环境变量区分 dev/test/prod
- 自动导入：components、hooks、API 等（可选）

需要我把这份架构直接生成**可直接复制到项目的完整目录结构 + 关键文件代码模板**吗？