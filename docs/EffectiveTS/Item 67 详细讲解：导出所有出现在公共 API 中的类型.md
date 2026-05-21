## Item 67 详细讲解：导出所有出现在公共 API 中的类型

### 1. 问题：未导出的类型仍然可以被用户提取

假设你正在编写一个库，定义了一些内部辅助类型，但你只导出了一个函数：

```ts
// 未导出（“私有”）
interface SecretName {
  first: string;
  last: string;
}

// 未导出
interface SecretSanta {
  name: SecretName;
  gift: string;
}

// 导出函数
export function getGift(name: SecretName, gift: string): SecretSanta {
  return { name, gift };
}
```

作为库的使用者，我无法直接导入 `SecretName` 或 `SecretSanta`：

```ts
import { getGift } from 'your-library';
// 无法导入 SecretName 或 SecretSanta
```

### 2. 为什么这仅仅是“不便”而非“真正的封装”？

因为 TypeScript 的类型系统是**结构类型**且具有反射能力。使用者可以通过**类型查询**（type query）来提取出现在公共签名中的类型：

```ts
type MySanta = ReturnType<typeof getGift>;
// ^? type MySanta = SecretSanta

type MyName = Parameters<typeof getGift>[0];
// ^? type MyName = SecretName
```

- `ReturnType<T>` 提取函数类型的返回值类型。这里 `getGift` 的类型是 `(name: SecretName, gift: string) => SecretSanta`，所以 `ReturnType<typeof getGift>` 就是 `SecretSanta`。
- `Parameters<T>` 提取函数参数类型的元组，`Parameters<typeof getGift>[0]` 就是第一个参数的类型 `SecretName`。

因此，尽管你没有导出这些类型，用户仍然可以通过这些工具类型获得它们。**类型一旦出现在公共 API 中，实际上就已经是公共 API 的一部分**。

### 3. 为什么要显式导出？

- **方便用户**：用户可以直接 `import { SecretSanta } from 'your-library'`，而不必每次都写 `ReturnType<typeof getGift>` 这种冗长且不易发现的代码。
- **文档作用**：显式导出的类型会在 IDE 的自动补全中显示，用户更容易发现和使用。
- **契约明确**：既然你已经在函数签名中承诺了这些形状，那么导出它们只是让承诺更加透明。隐藏它们并不会给你保留任何自由——改变 `SecretName` 的结构会破坏 `getGift` 的签名，这已经是破坏性变更。
- **避免重复定义**：如果用户需要自己定义相同的类型（例如为了在代码中传递中间值），他们要么重复劳动，要么用花哨的类型体操提取。导出类型是最直接的帮助。

### 4. 反例：什么时候可以不导出？

极少数情况下，你可能会希望某个类型虽然出现在公共签名中，但**故意不导出**，以暗示用户不应直接依赖它（例如它是内部实现细节，未来可能变化）。但正如上述分析，用户仍然可以提取它，所以这种“隐藏”是无效的。更好的做法是：

- 使用命名约定（例如 `_InternalSecretName`）或者将类型放在 `internal.ts` 并只导出必要的部分，但仍可在主入口重新导出。
- 如果真的不想暴露，那就不要让它出现在公共 API 中——例如将函数参数改为简单的基本类型。

但根据本节的原则，**最佳实践是：任何出现在公共签名中的类型都应该被显式导出**。

### 5. 总结

- 出现在公共 API 中的类型（如导出函数的参数或返回值）可以被用户通过 `ReturnType`、`Parameters` 等工具提取，因此“隐藏”是徒劳的。
- 作为库作者，应该显式导出这些类型，以提供更好的开发者体验。
- 这不仅适用于 TypeScript 类型，也适用于接口、类型别名等所有类型声明。

**记住**：如果你在公共函数签名中使用了某个类型，那么它就已经是你的公共 API 的一部分。请直接导出它，让用户更容易使用。