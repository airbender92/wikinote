# Git 定位哪个 commit 引入 bug

核心工具：**`git bisect`（二分查找）**，这是专门用来找出「哪一次提交引入了bug」的神器。

> 思路：找一个**好版本（没有bug）**，找一个**坏版本（存在bug）**，git 自动二分，一步步缩小范围，直到定位出第一个出错的 commit。

## 完整 bisect 实操步骤

### 1. 启动二分查找

```
git bisect start
```

### 2. 标记坏版本（当前有bug）

一般当前HEAD就是坏的：

```
git bisect bad
```

### 3. 标记一个已知正常的提交

找一个确定**没有bug**的commit hash/tag/分支，例如：

```
git bisect good 82ac31
# 也可以用tag：git bisect good v2.1.0
```

> git 会自动切到中间一个 commit，此时你手动跑项目，复现bug。

### 4. 反复标记 good / bad

- 如果当前检出的版本 **有bug**：

```
git bisect bad
```

- 如果当前检出的版本 **没有bug**：

```
git bisect good
```

git 会继续二分，自动切换到下一个中间版本，重复上面操作。

直到最后输出：

```
xxx is the first bad commit
```

这个 hash 就是**引入bug的那次commit**。

### 5. 结束 bisect 模式（非常重要）

查找完成后，退出二分，切回你原来的代码分支：

```
git bisect reset
```

---

## 拿到坏commit之后做什么

```
# 看这个提交详细改动
git show <bad‑commit‑hash>

# 看这个commit改了哪些文件
git diff <bad‑commit‑hash>^!

# 对比上一个版本，看变更
git diff <bad‑commit‑hash>^ <bad‑commit‑hash>
```

> `^` 代表该commit的父提交。

## 🤖 自动化 bisect（可以跑脚本，不用手动点）

如果bug可以用命令行自动化复现（比如单元测试、构建脚本），可以用 `bisect run` 全自动定位。

写一个退出码规则：

- 返回 `0` → good（无bug）
- 返回非0 → bad（有bug）

示例：

```
git bisect run npm run test:bug
```

git 会自动不断切换commit、跑脚本，全自动找出坏commit。

> 适合后端、单元测试；前端浏览器类bug很难自动化，只能人工手动 bisect good/bad。

## 备选方案：手动 revert / 回退排查（适合commit很少）

当改动不多，不想用bisect：

```
# 查看最近提交日志
git log --oneline

# 逐个回退试探
git checkout <commitId>
```

缺点：提交一多效率极低，优先用 bisect。

## 辅助排查命令

```
# 看提交历史，看谁什么时候改了某个文件
git log -p src/utils/request.js

# 只看该文件的提交记录
git log --oneline src/utils/request.js

# 看每行代码最后是谁哪个commit修改（考古神器）
git blame src/utils/request.js
```

`git blame`：定位某一行代码是哪个commit、谁写的。适合已经大概知道哪个文件出错，快速溯源。

## 常见坑

1. **bisect 过程不要修改代码**，不要在切出来的临时commit上改代码；改完bisect结果会乱。
2. bisect 结束必须执行 `git bisect reset`，否则一直停留在二分中间版本。
3. 不要把 `good/bad` 标记反了，标记反会找错提交。
4. 如果中间某个commit编译不过，无法测试：

```
git bisect skip
```

告诉git跳过这个不能测试的版本。

## 场景选择总结

| 场景                                      | 工具           |
| ----------------------------------------- | -------------- |
| 不知道哪个文件错，大范围找引入bug的commit | **git bisect** |
| 已经知道哪个文件出错，看每行代码来源      | git blame      |
| 想看文件改动历史                          | git log -p     |

### 简单记忆流程

```
git bisect start
git bisect bad
git bisect good 正常版本hash
# 反复 git bisect good / bad
git bisect reset
```

如果你需要，我可以举一个模拟bug的完整实操流程。
