## Pinia 与 TypeScript 集成：类型推导、安全与增强

Pinia 原生对 TypeScript 支持极佳，大多数情况下**无需手动标注类型**即可获得完善的类型提示和检查。但在高级场景（全局声明、插件扩展）中需要了解一些技巧。

---

### 一、类型推导（自动完成）

Pinia 会**自动推导** `state`、`getters`、`actions` 的类型，你基本不需要写类型注解。

#### Options Store
```ts
const useStore = defineStore('main', {
  state: () => ({
    count: 0,           // 自动推导为 number
    user: { name: 'John' } // 自动推导为 { name: string }
  }),
  getters: {
    // 自动推导返回值类型为 number
    doubleCount: (state) => state.count * 2,
    
    // 通过 this 访问时，也可以推导
    quadrupleCount(): number {
      return this.doubleCount * 2
    }
  },
  actions: {
    // 参数和返回值都可以自动推断
    increment(amount: number) {  // amount 需手动写类型，但 store 调用时能检查
      this.count += amount
    }
  }
})
```

#### Setup Store（更优的类型推导）
```ts
const useStore = defineStore('main', () => {
  const count = ref(0)        // Ref<number>
  const user = ref({ name: 'John' }) // Ref<{ name: string }>
  
  const doubleCount = computed(() => count.value * 2) // ComputedRef<number>
  
  function increment(amount: number) {
    count.value += amount
  }
  
  return { count, user, doubleCount, increment }
})
```
> **坑点**：在 Setup Store 中，如果你使用 `reactive` 包裹整个 state，返回值解构后类型会丢失关联。建议使用 `ref` 或 `reactive` 但返回展开对象。

---

### 二、为 Store 显式定义类型（`defineStore<...>` 泛型）

通常不需要，因为自动推导足够。但在以下场景需要手动定义：
- 需要限制 `state` 的形状（比如从外部接口导入）。
- 需要明确 `getters` 的返回值类型（自动推导可能不精确）。
- Options Store 中 `this` 的类型问题。

#### Options Store 显式类型
```ts
interface State {
  count: number
  user: { name: string }
}

const useStore = defineStore<'main', State>('main', {
  state: (): State => ({
    count: 0,
    user: { name: 'John' }
  }),
  getters: {
    // 显式标注返回值（可选）
    doubleCount(): number {
      return this.count * 2
    }
  }
})
```
> **坑点**：泛型参数顺序是 `Id, State, Getters, Actions`，一般只需传前两个。但 TypeScript 会要求你按顺序提供，所以写全太少？可以只用 `defineStore('id', {...})`，很少需要显式传泛型。

#### Setup Store 显式类型（少见）
Setup Store 的返回值类型会自动推断，如果需要约束返回值的形状，可以给函数加返回类型注解：
```ts
interface Store {
  count: number
  user: { name: string }
  doubleCount: number
  increment: (amount: number) => void
}

const useStore = defineStore('main', (): Store => {
  const count = ref(0)
  // ...
  return { count, user, doubleCount, increment }
})
```

---

### 三、全局 Store 类型声明（扩展 `PiniaCustomProperties`）

当你编写**Pinia 插件**并在 `store` 上添加自定义属性（如 `$http`、`$i18n`）时，TypeScript 不会自动识别。需要通过**模块扩展**来声明。

#### 场景：插件中添加 `$hello` 方法
```ts
// plugins/hello.ts
import { PiniaPluginContext } from 'pinia'

export function helloPlugin({ store }: PiniaPluginContext) {
  store.$hello = (msg: string) => console.log(`Hello ${msg}`)
  return { $hello: store.$hello } // 可选返回，但需要类型声明
}
```

#### 类型声明
```ts
// 在项目中的 .d.ts 文件或 shims-vue.d.ts 中
import 'pinia'

declare module 'pinia' {
  export interface PiniaCustomProperties {
    $hello: (msg: string) => void
  }
}
```

#### 使用
```ts
const store = useStore()
store.$hello('world') // ✅ 有类型提示
```

#### 常见坑点 ⚠️
- **没有扩展模块**：调用 `store.$hello` 报 TS 错误 `Property '$hello' does not exist`。
- **扩展了错误的接口**：应该扩展 `PiniaCustomProperties`（为所有 store 添加属性）或 `PiniaCustomStateProperties`（为 state 添加属性，如 `$state`）。
- **插件返回对象未声明**：如果插件返回一个对象（如 `{ $hello }`），也需要同步扩展，否则类型不匹配。
- **使用了 `PiniaCustomProperties` 但忘记导入 `pinia` 模块**：扩展必须在 `import 'pinia'` 之后。

---

### 四、`$patch` 的类型安全

`$patch` 支持**部分更新**，TypeScript 会检查你传入的对象是否与 `state` 类型兼容。

```ts
store.$patch({ count: 5 })        // ✅ count 是 number
store.$patch({ count: '5' })      // ❌ 类型错误
store.$patch({ nonExist: 1 })     // ❌ 如果 nonExist 不在 state 中，报错
```

#### 函数形式的 `$patch`
```ts
store.$patch((state) => {
  state.count = 10       // ✅ state 参数类型正确
  state.unknown = 1      // ❌ 不允许添加新属性（除非 state 有索引签名）
})
```

#### 坑点
- **添加未声明的属性**：如果你在 `$patch` 中添加了初始 state 中没有的属性，TypeScript 会报错。如果你确实需要动态属性，可以在 state 类型中声明索引签名。
  ```ts
  interface State {
    [key: string]: any
    count: number
  }
  ```
- **嵌套对象的合并**：对象形式的 `$patch` 是**浅合并**，会替换整个嵌套对象，而不是合并。类型检查会通过，但运行时可能丢失字段。
  ```ts
  // state: { user: { name: string, age: number } }
  store.$patch({ user: { name: 'Bob' } }) // ❌ 丢失 age，但 TS 不会报错（因为 { name } 符合部分结构）
  // 正确做法：store.$patch({ user: { ...store.user, name: 'Bob' } })
  ```

---

### 五、`storeToRefs` 保留类型

使用 `storeToRefs` 解构 store 时，**每个 ref 的类型都会被正确保留**。

```ts
const store = useStore() // 类型推断
const { count, doubleCount } = storeToRefs(store)
// count 类型：Ref<number>
// doubleCount 类型：ComputedRef<number>
```

#### 对比直接解构
```ts
const { count, doubleCount } = store   // ❌ count 变成 number，失去响应式且类型变成普通值
```

#### 坑点
- **对普通方法（action）使用 `storeToRefs`**：这会试图把 action 也转为 ref，导致类型错误或运行时异常。正确做法：action 直接解构。
  ```ts
  const { increment } = store          // ✅ increment 是 function
  const { increment } = storeToRefs(store) // ❌ 错误用法
  ```
- **嵌套 store 的解构**：如果你解构的是另一个 store 的返回值，同样适用 `storeToRefs`。

---

### 六、插件中的类型增强（高级）

除了全局属性，插件有时会为 `store` 添加**方法**或**计算属性**，也需要相应的类型声明。

#### 场景：添加 `$reset` 到所有 store（Setup Store 没有）
```ts
// 插件
function resetPlugin({ store }: PiniaPluginContext) {
  const initialState = JSON.parse(JSON.stringify(store.$state))
  store.$reset = () => {
    store.$patch(initialState)
  }
}
```

#### 类型声明
```ts
declare module 'pinia' {
  export interface PiniaCustomProperties {
    $reset: () => void
  }
}
```

#### 坑点
- **与内置 `$reset` 冲突**：Options Store 已有 `$reset`，如果你强行覆盖会导致类型不一致。建议插件中检查是否存在。
- **为特定 Store 添加属性**：如果你只想为某个 store 添加属性，可以扩展 `PiniaCustomProperties` 但通过条件类型？更好的方式是使用组合式函数（composable）而不是全局插件。

---

### 七、常见综合坑点总结

| 坑点 | 现象 | 解决 |
|------|------|------|
| **忘记使用 `storeToRefs` 导致类型变普通值** | 解构后属性变成 `number` / `string` | 使用 `storeToRefs` |
| **Options Store 中 `this` 类型报错** | `Property 'xxx' does not exist on type 'Store'` | 使用普通函数而非箭头函数；必要时用 `this as any` 或显式泛型 |
| **Setup Store 中返回 `reactive` 对象导致类型丢失** | `store.count` 变成 `unknown` 或无法推断 | 返回展开的 ref，或返回 `reactive` 对象但访问时带 `state.` 前缀 |
| **插件属性无类型** | `store.$custom` 报错 | 扩展 `PiniaCustomProperties` 模块 |
| **`$patch` 丢失嵌套字段** | 运行时 state 结构被破坏 | 使用 `$patch` 函数形式或手动合并 |
| **全局类型声明未生效** | 配置了 `.d.ts` 但 TS 仍然报错 | 确保文件被 `tsconfig.json` 包含，或者在 `vite-env.d.ts` 中导入 `pinia` |
| **`defineStore` 返回的函数类型不明确** | 无法推断 store 实例类型 | 使用 `ReturnType<typeof useStore>` 获取类型 |
| **在插件中修改 `store.$state` 的类型** | 类型不匹配 | 扩展 `PiniaCustomStateProperties` 接口 |

---

### 八、最佳实践

1. **依赖自动推导**：除非万不得已，不要手动写类型。
2. **使用 Setup Store**：类型推断比 Options Store 更可靠。
3. **统一导出 Store 类型**：如果需要将 store 实例作为参数传递，使用 `ReturnType<typeof useStore>`。
   ```ts
   type UserStore = ReturnType<typeof useUserStore>
   ```
4. **全局插件类型扩展**：在 `src/types/pinia.d.ts` 中集中管理。
5. **使用 `storeToRefs` 解构**：永远不要直接解构 store 的属性。
6. **`$patch` 优先用函数形式**：处理嵌套对象更安全。

### 记忆口诀

> **类型推导已够用，手动泛型很少碰；**
> **插件扩展改模块，全局声明别遗漏；**
> **解构请用 toRefs，patch 函数防丢失；**
> **Setup 优选 TS 强，Options 需多标类型。**

掌握以上内容，你就可以在 Pinia 中享受全链路的 TypeScript 安全。