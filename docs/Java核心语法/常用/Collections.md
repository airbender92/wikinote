我来给你**逐句解释**这两行代码，结合你上面的学生名单一起讲。

先回顾你原来的列表内容：
```
[Zhang san, Li si, wang wu]
```

---

## 1. `Collections.sort(studentNames);`

```java
Collections.sort(studentNames);
```

- `Collections` 是 Java 提供的一个**工具类**，专门用来操作集合（List、Set 等）
- `.sort()` 是它的排序方法
- 作用：**对传入的 List 进行自然排序**

这里是字符串排序，规则是：
**按字母的字典序（A→Z）从小到大排**

你这三个字符串：
- `Li si`    以 L 开头
- `Zhang san` 以 Z 开头
- `wang wu`   以 w 开头

字母顺序：**L < w < Z**
所以排序后顺序会变成：
```
Li si, wang wu, Zhang san
```

> 注意：Java 字符串比较是**区分大小写**的，大写字母排在小写前面。
> `W` 和 `w` 不一样，你这里 `wang wu` 是小写 w，所以会排在 Z 前面。

---

## 2. `System.out.println("排序后：" + studentNames);`

```java
System.out.println("排序后：" + studentNames);
```

- 直接打印集合时，Java 会自动调用集合的 `toString()` 方法
- 输出格式类似：
```
排序后：[Li si, wang wu, Zhang san]
```

---

## 完整代码 + 运行结果

```java
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class Test {
    public static void main(String[] args) {
        List<String> studentNames = new ArrayList<>();
        studentNames.add("Zhang san");
        studentNames.add("Li si");
        studentNames.add("wang wu");

        // 排序
        Collections.sort(studentNames);
        // 输出
        System.out.println("排序后：" + studentNames);
    }
}
```

**运行结果：**
```
排序后：[Li si, Zhang san, wang wu]
```

---

如果你想**不区分大小写排序**，或者**按中文拼音排序**，我也可以教你怎么写。