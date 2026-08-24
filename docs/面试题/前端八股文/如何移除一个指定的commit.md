# Git 删除/移除指定 commit

分两种场景：**提交还没推远程**、**已经推送到远程仓库**；两个核心命令：`git rebase -i`（安全删除）、`git reset`（回滚）。

> ⚠️ 已经推送到公共远程分支，删除 commit 会改写历史，需要强推 `git push -f`，多人协作慎用！

## 方式1：交互式 rebase 删除（推荐，删除中间某一条 commit）

适合：想删掉**历史中间某一个 commit**，保留其他提交，不是全部回滚。

示例提交历史：

```
A --- B --- C --- D --- E (HEAD)
           ↑ 要删掉 commit C
```

1. 先找到要删除 commit 的**父 commit hash**（C 的父是 B）

```
git log --oneline
```

输出示例

```
e111 E
d222 D
c333 C  # 要删掉这条
b444 B
a555 A
```

要删除 `c333(C)`，取它父提交 `b444`

```
git rebase -i b444
```

弹出编辑器：

```
pick b444 B
pick c333 C   # 把这一行的 pick 直接删掉 / 修改成 drop
pick d222 D
pick e111 E
```

操作：

- 将要删除那一行开头 `pick` 改为 **`drop`（简写 d）**

```
pick b444 B
d c333 C
pick d222 D
pick e111 E
```

vim：`i`编辑 → 修改 → `Esc` → `:wq`保存退出。

git 会把 C 移除，B 直接接上 D、E。

> 如果出现冲突：解决冲突后 `git add . && git rebase --continue`；放弃操作：`git rebase --abort`

---

## 方式2：git reset 回滚（删除HEAD往前一批提交）

适合：删除**最新的若干连续 commit**。

### 2.1 软重置 --soft：代码保留，删掉commit，代码留在暂存区

```
# 回退到目标hash，该hash之后所有commit全部移除
git reset --soft <commit_hash>
```

- 代码文件不变，只是把后面提交删掉，可以重新 commit。

### 2.2 混合重置 --mixed（默认）：代码保留，回到工作区

```
git reset <commit_hash>
```

### 2.3 硬重置 --hard ⚠️危险：直接删除提交+删除本地修改，文件也恢复到旧版本

```
git reset --hard <commit_hash>
```

> ⚠️ `--hard` 会丢掉本地改动，谨慎使用。

示例：当前 HEAD 在 E，想删掉 D、E，回退到 C

```
git reset --hard c333
```

## 已经 push 到远程之后

本地处理完删除 commit 之后，本地历史已经改写，需要强制推送

```
git push -f origin 你的分支名
```

> ⚠️多人共用分支不要随便 `-f`，会导致别人本地历史错乱。

## 方式3：git revert（不删除历史，新增反向提交，公共分支首选）

**不能物理删除旧commit，新增一条反向提交抵消改动，不会改写历史，不需要强推，团队公共分支优先用这个。**

```
git revert <要移除的commit哈希>
git push
```

> 原理：旧提交还在历史里，新增一个commit把该提交的代码全部撤销掉。适合 main/master 这种公共保护分支，禁止强制推送场景。

---

# 快速选择口诀

1. 删除**中间某一条**提交：`git rebase -i 父commit`，用 `drop`
2. 删除**末尾连续几条**提交：`git reset`
3. **公共分支不能改历史**：用 `git revert`
4. 本地改完已经推远程：`git push -f`（慎用）
5. rebase搞砸随时：`git rebase --abort` 恢复原样

### 小练习

历史：`pick 111` `pick 222` `pick 333` `pick444`，想删除第3条（333）

```
git rebase -i HEAD~4
```

编辑器改为

```
pick 111
pick 222
d 333
pick 444
```

保存退出即可移除333这条提交。

如果你愿意，可以把你的 `git log --oneline` 输出贴出来，我直接给你复制即用的命令。
