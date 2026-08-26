# git rebase -i HEAD~4 squash 操作说明

> 现象：进入 git 交互式 rebase 编辑器，**直接打字改不了**，这是 vim 编辑器模式问题，不是 git 不能编辑。

原始内容：

```
pick abc111 feat: 提交1
pick def222 feat: 提交2
pick ghi333 feat: 提交3
pick jkl444 feat: 提交4
```

目标：第一行保持 `pick`，后面3行改为 `s`(squash)

```
pick abc111 feat: 提交1
s def222 feat: 提交2
s ghi333 feat: 提交3
s jkl444 feat: 提交4
```

## vim 操作步骤（重点）

1. 当前打开是 **vim普通模式**，**不能直接输入文字**，按一下 `i` 键，进入 **插入模式**，左下角出现 `-- INSERT --`，此时才可以修改文本。
2. 把第2、3、4行开头 `pick` 改成 `s`。
3. 修改完成，按 `Esc` 退出插入模式。
4. 输入 `:wq` 回车，保存退出编辑器，git 开始执行合并。

### 后续

保存退出后 git 会**再弹出一个编辑器**，让你填写合并之后总的 commit message：

- 删除旧的多条提交注释，写一条新的总提交说明
- 同样 `i`编辑，`Esc`，`:wq` 完成，4个提交就压扁成1个。

## 常见踩坑

1. 误按按键乱码：按 `Esc`，输入 `:q!` 强制放弃退出 rebase，不做任何修改。
2. rebase冲突：出现冲突后，改完文件，`git add .`，然后 `git rebase --continue`；想放弃全部 `git rebase --abort`。

## 如果你不想用vim，换编辑器

临时设置使用 nano（简单编辑器，适合不会vim）

```bash
export GIT_EDITOR=nano
git rebase -i HEAD~4
```

nano 修改完按 `Ctrl+O` 保存，回车确认文件名，`Ctrl+X`退出。

### 口诀

> vim rebase：先i编辑，改完Esc，:wq保存；搞砸 :q! 跑路。

### 效果

- `HEAD~4` 最近4笔提交，**保留第一笔提交哈希abc111**，把后面3笔全部挤压合并到 abc111，最终只剩下1条commit。

> ⚠️ 注意：已经push到远程公共分支的提交不要随便squash，会改写历史，需要强制推送 `git push -f`，多人协作慎用。
