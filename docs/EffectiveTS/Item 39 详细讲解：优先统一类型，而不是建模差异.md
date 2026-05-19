## Item 39 详细讲解：优先统一类型，而不是建模差异

这一节的核心是：**当你在两个相似的类型之间来回转换时，与其用复杂的类型体操来建模它们之间的差异，不如直接消除差异，统一成一个类型。** 这样可以减少认知负担、避免转换错误、简化代码。

书中通过一个数据库表类型（snake_case）与应用程序内部类型（camelCase）的例子来说明。

---

### 1. 问题情境：两个版本的 Student 类型

假设数据库返回的列名是 snake_case：

```ts
interface StudentTable {
  first_name: string;
  last_name: string;
  birth_date: string;
}
```

而你的 TypeScript 代码习惯使用 camelCase：

```ts
interface Student {
  firstName: string;
  lastName: string;
  birthDate: string;
}
```

你自然会想写一个转换函数，并可能用模板字面量类型（Item 54）来定义类型映射：

```ts
type Student = ObjectToCamel<StudentTable>;
// 自动生成 { firstName: string; lastName: string; birthDate: string }
```

看起来很高端，类型安全也有了。

---

### 2. 实际使用中遇到的问题

你开始写一个函数将 `Student` 写回数据库：

```ts
async function writeStudentToDb(student: Student) {
  await writeRowToDb(db, 'students', student);
  // 错误：类型 'Student' 不能赋给类型 'StudentTable'
}
```

你忘记调用转换函数 `objectToSnake` 了。TypeScript 报错，但错误信息并不直接提示“你需要先转换”，而是说类型不匹配。你修复它：

```ts
async function writeStudentToDb(student: Student) {
  await writeRowToDb(db, 'students', objectToSnake(student)); // ok
}
```

现在代码能通过类型检查了。但问题依然存在：**你需要在每个与数据库交互的地方都记得转换**。如果某处忘记，就会产生运行时错误或数据不一致。而且转换函数本身也可能有 bug。

---

### 3. 根本矛盾：两个类型代表同一概念

`StudentTable` 和 `Student` 描述的是**同一个业务实体**——学生。它们只是命名风格不同，没有语义差异。维护两个版本意味着：

- 每当你从数据库读取数据，必须转换成 `Student`。
- 每当你向数据库写入数据，必须转换回 `StudentTable`。
- 任何新增字段都需要在两个接口中同步添加，并更新转换函数。
- 转换逻辑分散在各处，容易遗漏。

这会带来**认知负担**（时刻记住当前是哪个版本）和**重复劳动**。

---

### 4. 更好的选择：统一成一个类型

与其在类型层面建模差异，不如**消除差异**，只保留一个版本。有两个方向：

#### 方向一：统一为 camelCase（应用程序风格）

修改数据库访问层，让数据库返回的列名自动映射为 camelCase。例如使用 ORM 的字段别名、视图、或者在查询时重命名列。这样 `StudentTable` 就不再需要了，所有代码都使用 `Student`。

**优点**：与应用程序其余部分一致。  
**代价**：需要修改数据库交互层，可能涉及配置或工具。

#### 方向二：统一为 snake_case（数据库风格）

直接在应用程序中使用 snake_case 的属性名，放弃 camelCase 习惯。这样 `Student` 接口就不需要了，所有代码都使用 `StudentTable`。

```ts
interface Student {
  first_name: string;
  last_name: string;
  birth_date: string;
}
```

**优点**：不需要任何转换，零代价。  
**代价**：属性名与常见的 TypeScript/JavaScript 命名风格不一致，但这是一个表面的不一致（命名风格）换来了深层的类型一致性。

书中指出，第二种方案更简单，因为不需要任何转换或配置。

---

### 5. 何时不能统一？

- **当两个类型并非你完全控制**，例如数据库是第三方提供的，你无法改变它的命名；而应用程序又必须使用另一种命名风格（例如因为前端框架要求）。此时你必须保留两个版本，并在边界处转换。
- **当两个类型虽然相似，但语义上不是同一个东西**。例如 `UserInput` 和 `UserOutput` 可能字段相同但验证规则不同。这种情况下统一反而会导致问题。

- **可辨识联合（tagged union）中的不同类型**不应该统一，因为它们代表不同的状态（例如 `pending`、`success`、`error`）。合并它们会丢失区分度。

---

### 6. 核心原则总结

| 场景 | 推荐做法 |
|------|----------|
| 两个类型表示同一实体，仅命名风格不同（snake_case vs camelCase） | **统一成一个**，放弃其中一个命名风格。通常选择更简单的方案（无需转换的那个）。 |
| 两个类型表示同一实体，但来自不同系统且你无法控制 | 保留两个版本，但集中转换逻辑（例如在数据访问层），避免分散在业务代码中。 |
| 两个类型表示不同状态或不同阶段的同一实体（如未验证输入 vs 已验证输出） | 不要统一，使用不同的类型让类型系统帮你区分。 |

**最终建议**：在引入一个新的类型来“建模差异”之前，先问自己：能否直接改变其中一个，让它们相同？如果代价可以接受（例如改变命名风格、增加一个适配层），那么统一类型会带来更简单的代码和更少的错误。

正如书中所说：**与其费心建模小差异，不如直接消除差异。**