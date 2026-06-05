## common.d.ts 类型定义解读

```typescript
// src/types/common.d.ts

/** 通用选项 */
interface SelectOption {
  label: string
  value: string | number
  disabled?: boolean
}

/** 分页参数 */
interface PageParams {
  page: number
  pageSize: number
}

/** 排序方向 */
type SortOrder = 'ascending' | 'descending' | null

/** 表单规则 */
type FormRules = Record<string, unknown[]>
```

---

### 1. SelectOption（通用下拉选项）

```typescript
interface SelectOption {
  label: string          // 显示文本
  value: string | number // 选项值
  disabled?: boolean     // 是否禁用（可选）
}
```

**使用场景：**

```typescript
// Element Plus 下拉框
const options: SelectOption[] = [
  { label: '选项1', value: 1 },
  { label: '选项2', value: 2, disabled: true },
]
```

---

### 2. PageParams（分页参数）

```typescript
interface PageParams {
  page: number      // 当前页码
  pageSize: number  // 每页条数
}
```

**使用场景：**

```typescript
// 请求用户列表
const params: PageParams = {
  page: 1,
  pageSize: 10,
}
```

---

### 3. SortOrder（排序类型）

```typescript
type SortOrder = 'ascending' | 'descending' | null
```

| 值 | 含义 |
|-----|------|
| `'ascending'` | 升序 |
| `'descending'` | 降序 |
| `null` | 无排序 |

**使用场景：**

```typescript
// 表格排序
interface TableColumn {
  prop: string
  order: SortOrder
}

const col: TableColumn = {
  prop: 'createTime',
  order: 'descending',
}
```

---

### 4. FormRules（表单验证规则）

```typescript
type FormRules = Record<string, unknown[]>
```

**`Record<K, V>` 语法：**

```typescript
Record<string, unknown[]>
//    ↑    ↑
//  key类型  value类型
```

**等价的普通写法：**

```typescript
interface FormRules {
  [key: string]: unknown[]
}
```

**使用场景：**

```typescript
// Element Plus 表单验证
const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 10, message: '长度在 3 到 10 个字符' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
  ],
}
```

---

### 5. 类型别名 type vs 接口 interface

```typescript
interface SelectOption { ... }
type SortOrder = 'ascending' | 'descending' | null
```

| 对比 | interface | type |
|------|-----------|------|
| 扩展 | `extends` | `&` 交叉类型 |
| 声明合并 | ✅ 支持 | ❌ 不支持 |
| 对象结构 | ✅ 适合 | ✅ 适合 |
| 联合类型 | ❌ 不适合 | ✅ 适合 |
| 工具类型 | ❌ 不支持 | ✅ `Record<string, T>` 等 |

---

### 6. 三种文件类型对比

| 文件 | 职责 |
|------|------|
| `api.d.ts` | API 相关类型（请求、响应） |
| `common.d.ts` | 通用类型（分页、选项、规则） |
| `user.d.ts` / `menu.d.ts` | 业务类型（用户、菜单） |

---

### 7. Record 工具类型

```typescript
Record<string, unknown[]>
// 等价于
{
  [key: string]: unknown[]
}
```

**常用工具类型：**

| 工具类型 | 含义 |
|---------|------|
| `Record<K, V>` | 键值对 |
| `Partial<T>` | 所有属性变可选 |
| `Required<T>` | 所有属性变必选 |
| `Pick<T, K>` | 选取部分属性 |
| `Omit<T, K>` | 排除部分属性 |

---

## 实际项目中 SelectOption 的扩展方案

### 问题

实际业务中，`SelectOption` 可能有更多属性：

```typescript
// 级联选择
interface SelectOption {
  label: string
  value: string | number
  children?: SelectOption[]  // 级联子选项
  disabled?: boolean
}

// 或者带图标
interface SelectOption {
  label: string
  value: string | number
  icon?: string
  description?: string
  tagType?: 'primary' | 'success' | 'warning' | 'danger'
}
```

---

### 方案对比

| 方案 | 写法 | 优点 | 缺点 |
|------|------|------|------|
| **可选属性堆叠** | `disabled?`, `children?` | 简单 | 接口膨胀，不相关属性混在一起 |
| **继承扩展** | `extends` | 相关属性分组 | 层级变深 |
| **泛型** | `<T>` | 灵活，类型安全 | 稍复杂 |
| **多个专用接口** | `SelectOption` / `CascaderOption` | 职责清晰 | 可能冗余 |

---

### 方案一：可选属性（当前项目做法）

```typescript
interface SelectOption {
  label: string
  value: string | number
  disabled?: boolean
  children?: SelectOption[]     // 级联用
  icon?: string                  // 图标用
  [key: string]: unknown        // 允许扩展
}
```

**缺点：** 不相关属性混在一起，可能有 `icon` 但不是所有选项都有

---

### 方案二：继承扩展（推荐）

```typescript
// 基础选项
interface BaseOption {
  label: string
  value: string | number
  disabled?: boolean
}

// 级联选项
interface CascaderOption extends BaseOption {
  children?: CascaderOption[]
}

// 带图标选项
interface IconOption extends BaseOption {
  icon: string
  description?: string
}
```

**优点：** 相关属性分组，类型更精确

---

### 方案三：泛型（最灵活）

```typescript
interface SelectOption<T = unknown> {
  label: string
  value: string | number
  disabled?: boolean
  extra?: T  // 附加任意数据
}

// 使用
const opts: SelectOption<{ icon: string; color: string }>[] = [
  { label: 'A', value: 1, extra: { icon: 'user', color: 'red' } },
]
```

---

### 方案四：多个专用接口

```typescript
// 通用下拉
interface SelectOption {
  label: string
  value: string | number
  disabled?: boolean
}

// 级联选择
interface CascaderOption {
  label: string
  value: string | number
  children?: CascaderOption[]
}

// 分组选项
interface GroupedOption {
  label: string
  options: SelectOption[]
}
```

**优点：** 职责清晰，不会混入无关属性

---

### 实际项目建议

```typescript
// types/common.d.ts

/** 通用选项（基础属性） */
interface SelectOption {
  label: string
  value: string | number
  disabled?: boolean
}

/** 级联选择选项 */
interface CascaderOption extends SelectOption {
  children?: CascaderOption[]
  /** 仅用于某些业务场景的额外字段 */
  description?: string
}

/** 带图标选项 */
interface IconOption extends SelectOption {
  icon: string
}
```

---

### 总结

| 场景 | 推荐方案 |
|------|---------|
| 属性相对固定 | 可选属性 |
| 相关属性分组 | 继承扩展 |
| 灵活附加数据 | 泛型 |
| 不同业务用途 | 多个专用接口 |

当前项目的做法适合**通用后台**，如果业务复杂建议用**继承扩展**或**多个专用接口**。

---

需要继续了解 **路由配置** 吗？