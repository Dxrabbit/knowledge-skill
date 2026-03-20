---
name: knowledge
description: 智能知识库与遗忘曲线复习系统。当用户想要记录知识点、复习内容、管理学习资料时使用此技能。包括添加知识、基于遗忘曲线的复习提醒、查看统计等功能。
---

# 知识库使用指南

基于艾宾浩斯遗忘曲线的智能记忆管理系统。

## 触发时机

当用户有以下意图时，使用此技能：
- "添加到知识库"、"记一下"、"帮我记住"
- "复习知识"、"今天该复习什么"
- "查看知识库统计"、"我记了多少东西"
- "列出所有知识"

## 核心功能

### 1. 添加知识点

```bash
python3 ~/.claude/skills/knowledge/scripts/knowledge.py add "知识点内容" [标签]
```

示例：
```bash
python3 ~/.claude/skills/knowledge/scripts/knowledge.py add "Python 列表推导式比 for 循环更快"
python3 ~/.claude/skills/knowledge/scripts/knowledge.py add "Go 的 goroutine 是轻量级线程" "技术,Go"
```

**自动分类规则**：
- **技术**：代码、编程、Python、Go、算法、数据库、API、Git、Docker、Linux 等
- **工作**：项目、需求、会议、客户、OKR、复盘、流程等
- **读书**：书籍、作者、笔记、理论、观点等
- **生活**：健康、运动、饮食、理财、旅行等
- **学习**：单词、外语、考试、课程、学习方法等

### 2. 复习到期知识

```bash
# 查看今日待复习（问答模式）
python3 ~/.claude/skills/knowledge/scripts/knowledge.py review today quiz

# 查看今日待复习（展示模式）
python3 ~/.claude/skills/knowledge/scripts/knowledge.py review today show

# 查看本周待复习
python3 ~/.claude/skills/knowledge/scripts/knowledge.py review week quiz

# 查看所有待复习
python3 ~/.claude/skills/knowledge/scripts/knowledge.py review all quiz
```

### 3. 标记复习状态

```bash
# 标记为已记住
python3 ~/.claude/skills/knowledge/scripts/knowledge.py recall <ID> yes

# 标记为未记住（会缩短下次复习间隔）
python3 ~/.claude/skills/knowledge/scripts/knowledge.py recall <ID> no
```

### 4. 查看知识库

```bash
# 列出所有知识
python3 ~/.claude/skills/knowledge/scripts/knowledge.py list

# 按标签筛选
python3 ~/.claude/skills/knowledge/scripts/knowledge.py list 技术

# 查看统计
python3 ~/.claude/skills/knowledge/scripts/knowledge.py stats
```

## 遗忘曲线复习间隔

系统基于艾宾浩斯遗忘曲线设置复习间隔：

| 复习次数 | 间隔时间 |
|---------|---------|
| 第1次 | 1天后 |
| 第2次 | 3天后 |
| 第3次 | 7天后 |
| 第4次 | 14天后 |
| 第5次 | 30天后 |

## 数据存储

知识库文件位置：`~/.claude/memory/knowledge_base.json`

## 快速参考

| 操作 | 命令 |
|-----|------|
| 添加知识 | `knowledge.py add "内容" [标签]` |
| 今日复习 | `knowledge.py review today quiz` |
| 标记记住 | `knowledge.py recall <ID> yes` |
| 标记没记住 | `knowledge.py recall <ID> no` |
| 查看统计 | `knowledge.py stats` |
| 列出全部 | `knowledge.py list` |
