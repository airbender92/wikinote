# int 与 Integer 最清晰对比（小白也能懂）

## 1. 本质区别
- **int**：**基本数据类型**
  - 就是一个简单数字，不是对象
  - 存的是**值本身**

- **Integer**：**包装类（对象）**
  - 是一个类，把 int 包起来变成对象
  - 用于**集合、泛型、面向对象场景**

---

## 2. 声明与赋值
```java
int a = 10;
Integer b = 10;
```

- int 直接存数字
- Integer 是对象，会自动装箱 → 底层就是 `Integer.valueOf(10)`

---

## 3. 能不能存 null？
- **int 不能为 null**
  ```java
  int a = null; // 报错
  ```
- **Integer 可以为 null**
  ```java
  Integer b = null; // 正常
  ```

这就是为什么集合只能用 Integer：
```java
ArrayList<int> 错误
ArrayList<Integer> 正确
```

---

## 4. 比较相等（重点坑）
### ① int 比较
直接用 `==` 没问题：
```java
int a = 100;
int b = 100;
System.out.println(a == b); // true
```

### ② Integer 比较
`==` 比较的是**对象地址**，不是值！
```java
Integer x = new Integer(100);
Integer y = new Integer(100);
System.out.println(x == y);      // false ❌ 地址不同
System.out.println(x.equals(y)); // true  ✅ 比较值
```

---

## 5. 拆箱与装箱
### 装箱：int → Integer
```java
Integer i = Integer.valueOf(10);
// 或简写
Integer i = 10;
```

### 拆箱：Integer → int
```java
Integer i = 10;
int a = i.intValue();
// 或简写
int a = i;
```

---

## 6. 为什么你代码里必须用 Integer？
你的代码：
```java
ArrayList<Integer> locationCells;
```
- **集合只能存对象，不能存基本类型**
- 所以必须用 `Integer`

而你删除时：
```java
list.remove(cell)     // 按索引删
list.remove((Integer)cell) // 按值删
```
就是为了告诉 Java：我要删**这个数值**，不是删这个下标。

---

## 7. 最简单记忆口诀
- 平时算数用 **int**，快、简单、不占内存
- 放进集合、泛型用 **Integer**
- 比较 Integer 一定用 **equals()**
- `int` 不是对象，`Integer` 是对象
- int 不能 null，Integer 可以 null