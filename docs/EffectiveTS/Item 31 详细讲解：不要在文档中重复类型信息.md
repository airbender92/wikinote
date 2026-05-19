## Item 31 详细讲解：不要在文档中重复类型信息

这一节的核心很简单：**类型信息应该由 TypeScript 的类型系统来维护，而不是写在注释或变量名里。** 注释会过时，变量名中的类型标记（如 `ageNum`）是噪音，而类型注解会被编译器检查，永远是真实的。

书中通过几个具体的反面例子和正面改进，生动说明了这一点。

---

### 1. 函数注释与实现不一致

#### 错误示例

```ts
/**
 * Returns a string with the foreground color.
 * Takes zero or one arguments. With no arguments, returns the
 * standard foreground color. With one argument, returns the foreground color
 * for a particular page.
 */
function getForegroundColor(page?: string) {
  return page === 'login' ? {r: 127, g: 127, b: 127} : {r: 0, g: 0, b: 0};
}
```

**问题**：
- 注释说返回 `string`，但实际返回的是 `{r,g,b}` 对象。
- 注释详细说明了“参数个数”，但类型签名 `page?: string` 已经清楚表明参数可选。
- 注释比代码本身还长，冗余且容易过时。

**改进**：

```ts
/** Get the foreground color for the application or a specific page. */
function getForegroundColor(page?: string): Color {
  // ...
}
```

- 只保留有意义的非类型信息（例如“前景色”的业务含义）。
- 参数个数、返回类型由 TypeScript 负责，不需要注释重复。
- 如果需要说明某个参数的特殊含义，使用 JSDoc 的 `@param` 标记（Item 68）。

---

### 2. 承诺“不修改参数”的注释不可靠

#### 错误示例

```ts
/** Sort the strings by numeric value (i.e. "2" < "10"). Does not modify nums. */
function sortNumerically(nums: string[]): string[] {
  return nums.sort((a, b) => Number(a) - Number(b));
}
```

注释声称不会修改 `nums`，但 `Array.prototype.sort` **会原地修改数组**，所以注释是错的。

#### 改进：使用 `readonly` 让类型系统强制执行

```ts
/** Sort the strings by numeric value (i.e. "2" < "10"). */
function sortNumerically(nums: readonly string[]): string[] {
  return nums.sort((a, b) => Number(a) - Number(b));
  // ~~~~ Property 'sort' does not exist on 'readonly string[]'
}
```

因为 `readonly string[]` 没有 `sort` 方法，TypeScript 直接报错，迫使你修改实现。

**正确的实现**（使用不可变的 `toSorted`，ES2023 方法）：

```ts
function sortNumerically(nums: readonly string[]): string[] {
  return nums.toSorted((a, b) => Number(a) - Number(b));
}
```

或者先复制再排序：`[...nums].sort(...)`。

**原则**：如果你承诺函数不修改参数，就用 `readonly` 在类型层面强制，而不是写在注释里。

---

### 3. 变量名中不要嵌入类型

#### 错误示例

```ts
let ageNum: number = 12;
```

`ageNum` 中的 `Num` 是多余的，因为 TypeScript 已经知道 `age` 是 `number`。更好的写法：

```ts
let age = 12;
```

**例外**：当单位不明显时，可以在变量名中包含单位。

```ts
let timeMs = 1000;        // 毫秒
let temperatureC = 25;    // 摄氏度
```

因为 `number` 类型不能表达单位，所以 `timeMs` 比 `time` 更清晰。如果想用类型系统保证单位正确，可以使用“品牌”（Item 64），例如 `type Milliseconds = number & {_brand: 'ms'}`。

---

### 总结：三个核心建议

1. **不要在注释中重复类型信息**（参数类型、返回类型、参数个数）。这些由 TypeScript 保证。  
   注释只应该描述**为什么**做，或者业务含义。

2. **不要用注释承诺“不修改参数”**，而是将参数声明为 `readonly`，让编译器强制执行。

3. **变量名中避免嵌入类型**（如 `ageNum`、`nameStr`），除非需要表示单位（`timeMs`、`tempC`）。

**记住**：注释和代码不同步时，两者都不可信。类型注解是被编译器验证的唯一真实来源。