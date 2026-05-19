## Item 35 详细讲解：优先使用比 `string` 更精确的类型

这一节的核心是：**不要把所有字符串都用 `string` 类型表示。应该根据业务含义，使用更精确的类型，比如字面量联合（`'studio' | 'live'`）、`Date` 对象，或者使用 `keyof T` 来约束属性名**。这可以避免“字符串类型”（stringly typed）代码带来的许多错误。

书中通过两个例子来说明：一个是音乐专辑 `Album` 接口，另一个是从对象数组中提取属性值的 `pluck` 函数。

---

### 例子一：专辑类型（Album）

#### 初始的“字符串类型”版本

```ts
interface Album {
  artist: string;
  title: string;
  releaseDate: string;   // 注释说格式是 YYYY-MM-DD
  recordingType: string; // 注释说只能是 "live" 或 "studio"
}
```

**存在的问题**：

1. **格式错误无法被类型检查捕获**  
   下面的对象赋值给 `Album` 是完全合法的，因为所有字段都是 `string`，但 `releaseDate` 的格式明显错误（不是 `YYYY-MM-DD`），`recordingType` 大小写也不对（应该是 `'studio'`）：

   ```ts
   const kindOfBlue: Album = {
     artist: 'Miles Davis',
     title: 'Kind of Blue',
     releaseDate: 'August 17th, 1959',  // 错误格式
     recordingType: 'Studio',           // 错误大小写
   }; // 类型检查通过！
   ```

2. **函数参数顺序错误无法发现**  
   因为两个参数都是 `string`，调用时传反了也不会报错：

   ```ts
   function recordRelease(title: string, date: string) { /* ... */ }
   recordRelease(kindOfBlue.releaseDate, kindOfBlue.title); // 交换了顺序，但类型检查通过
   ```

3. **文档与代码分离**  
   注释中说明了 `releaseDate` 的格式和 `recordingType` 的合法值，但调用者未必会去看注释。类型系统没有强制约束。

#### 改进版本：使用精确类型

```ts
type RecordingType = 'studio' | 'live';

interface Album {
  artist: string;
  title: string;
  releaseDate: Date;
  recordingType: RecordingType;
}
```

**改进效果**：

- `releaseDate` 使用 `Date` 对象，避免字符串格式问题。
- `recordingType` 使用字面量联合 `'studio' | 'live'`，任何拼写错误或大小写错误都会被 TypeScript 捕获：

  ```ts
  const kindOfBlue: Album = {
    artist: 'Miles Davis',
    title: 'Kind of Blue',
    releaseDate: new Date('1959-08-17'),
    recordingType: 'Studio',  // 错误：不能将类型'"Studio"'赋给类型'RecordingType'
  };
  ```

- 函数参数如果期望 `RecordingType`，调用者必须传入正确的字面量，或者使用相同的类型。IDE 会提供自动补全和文档提示（如 `@param` 或 TSDoc）。

**额外好处**：可以给 `RecordingType` 附加 TSDoc 注释，当鼠标悬停在该类型上时，文档会直接显示，无需翻看源码注释。

```ts
/** What type of environment was this recording made in? */
type RecordingType = 'live' | 'studio';
```

---

### 例子二：`pluck` 函数 —— 从对象数组中提取指定属性的值

`pluck` 函数接受一个对象数组和一个属性名，返回该属性值的数组。这是许多工具库（如 Underscore、Lodash）中的常见函数。

#### 初版：使用 `any`

```ts
function pluck(records: any[], key: string): any[] {
  return records.map(r => r[key]);
}
```

**问题**：返回类型是 `any[]`，丢失了所有类型信息，而且参数 `key` 是 `string`，任何字符串都允许，包括不存在的属性名。

#### 第二版：引入泛型 `T`

```ts
function pluck<T>(records: T[], key: string): any[] {
  return records.map(r => r[key]);
  // ~~~~~~ 类型“{}”没有索引签名，因此元素隐式具有“any”类型
}
```

TypeScript 报错，因为 `key` 是 `string`，而 `T` 可以是任何对象类型，不一定有索引签名。我们需要约束 `key` 必须是 `T` 的键之一。

#### 第三版：使用 `keyof T`

```ts
function pluck<T>(records: T[], key: keyof T) {
  return records.map(r => r[key]);
}
```

现在类型检查通过，返回类型被推断为 `T[keyof T][]` —— 即 `T` 中所有可能值类型的联合类型数组。

**但仍有精度问题**：如果传入的 `key` 是 `'releaseDate'`，我们希望返回 `Date[]`，但实际上返回的类型是 `(string | Date)[]`（因为 `Album` 中还有其他字段类型是 `string`）。这是因为 `T[keyof T]` 取了**所有属性值类型的联合**，而不是只取 `key` 对应的那个属性类型。

#### 第四版：引入第二个类型参数 `K extends keyof T`

```ts
function pluck<T, K extends keyof T>(records: T[], key: K): T[K][] {
  return records.map(r => r[key]);
}
```

现在 `key` 被约束为 `T` 的某个具体键（字面量类型），返回值类型为 `T[K][]`，即**该键对应的值类型的数组**。对于 `Album`，如果 `K` 是 `'releaseDate'`，则 `T[K]` 是 `Date`，返回 `Date[]`，完全正确。

**使用示例**：

```ts
const dates = pluck(albums, 'releaseDate');    // Date[]
const artists = pluck(albums, 'artist');       // string[]
const types = pluck(albums, 'recordingType');  // RecordingType[]
const mix = pluck(albums, Math.random() < 0.5 ? 'releaseDate' : 'artist');
// 联合类型键 => 返回 (Date | string)[]
const bad = pluck(albums, 'recordingDate');
// 错误：参数类型'"recordingDate"'不能赋给类型'keyof Album'
```

此外，编辑器现在可以对 `key` 参数提供自动补全，只显示 `Album` 的有效属性名（见图 4-2）。

---

### 核心原则总结

1. **避免“字符串类型”代码**  
   如果一个变量只应该取几个固定值，不要用 `string`，而应该用**字面量联合**。如果字段表示日期，应该用 `Date` 类型，而不是字符串。

2. **使用 `keyof T` 和 `K extends keyof T` 来精确约束属性名**  
   当你需要写一个函数，接受一个对象类型 `T` 和它的某个键时，使用泛型 `K extends keyof T` 可以保持键与返回值类型之间的精确关系。

3. **精确类型带来的好处**  
   - 捕获拼写错误和格式错误  
   - 提供更好的编辑器支持（自动补全、文档提示）  
   - 使函数签名自文档化，无需额外注释  
   - 在重构时（例如重命名属性）类型检查会提示所有调用点

**最终建议**：每当你写下 `string` 时，停下来想一想：这个字符串真的是任意字符串吗？还是它实际上只来自一个小的集合？如果是后者，就用字面量联合；如果是日期，就用 `Date`；如果是对象的键，就用 `keyof T`。这样做可以让 TypeScript 发挥最大的作用。