#!/usr/bin/env python3
"""
智能知识库 - 基于遗忘曲线的复习系统
"""

import json
import os
import re
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 知识库文件路径
KNOWLEDGE_FILE = Path.home() / ".claude" / "memory" / "knowledge_base.json"
SETTINGS_FILE = Path.home() / ".claude" / "settings.json"

# 分类关键词映射
CATEGORY_KEYWORDS = {
    "技术": ["代码", "编程", "python", "go", "rust", "java", "js", "ts", "算法", "数据库", "sql", "api", "接口", "函数", "类", "框架", "库", "git", "docker", "k8s", "linux", "shell", "前端", "后端", "全栈", "web", "http", "tcp", "网络", "服务器", "缓存", "redis", "消息队列", "mq"],
    "工作": ["项目", "需求", "prd", "会议", "汇报", "客户", "同事", "老板", "deadline", "排期", "优先级", "okr", "kpi", "复盘", "总结", "流程", "规范", "文档"],
    "读书": ["书", "作者", "读后感", "笔记", "章节", "理论", "观点", "引用", "推荐", "书单", "阅读", "文学", "哲学", "心理学", "经济学"],
    "生活": ["健康", "运动", "健身", "饮食", "睡眠", "习惯", "记账", "理财", "投资", "旅行", " recipe", "菜谱", "养生", "情绪", "人际关系", "家人", "朋友"],
    "学习": ["单词", "英语", "日语", "外语", "考试", "考证", "课程", "视频", "教程", "学习方法", "记忆", "效率", "专注", "时间管理"]
}

# 遗忘曲线间隔（天）
REVIEW_INTERVALS = [1, 3, 7, 14, 30]


def init_knowledge_base():
    """初始化知识库文件"""
    KNOWLEDGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not KNOWLEDGE_FILE.exists():
        save_knowledge_base({"version": "1.0", "entries": []})


def load_knowledge_base() -> Dict:
    """加载知识库"""
    init_knowledge_base()
    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_knowledge_base(data: Dict):
    """保存知识库"""
    with open(KNOWLEDGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def auto_category(content: str) -> str:
    """根据内容自动分类"""
    content_lower = content.lower()
    scores = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in content_lower)
        if score > 0:
            scores[category] = score

    if not scores:
        return "其他"

    return max(scores, key=scores.get)


def add_entry(content: str, tags: Optional[List[str]] = None) -> str:
    """添加知识条目"""
    data = load_knowledge_base()

    # 自动分类
    category = auto_category(content)

    entry = {
        "id": str(uuid.uuid4())[:8],
        "content": content,
        "tags": tags or [category],
        "category": category,
        "created_at": datetime.now().isoformat(),
        "reviews": [],
        "next_review": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "review_count": 0
    }

    data["entries"].append(entry)
    save_knowledge_base(data)

    return f"✅ 已添加到【{category}】知识库！ID: {entry['id']}"


def get_due_entries(period: str = "today") -> List[Dict]:
    """获取到期复习的条目"""
    data = load_knowledge_base()
    today = datetime.now().date()

    if period == "today":
        check_date = today
    elif period == "week":
        check_date = today + timedelta(days=7)
    elif period == "month":
        check_date = today + timedelta(days=30)
    else:  # all
        check_date = today + timedelta(days=3650)

    due_entries = []
    for entry in data["entries"]:
        next_review = datetime.strptime(entry["next_review"], "%Y-%m-%d").date()
        if next_review <= check_date:
            due_entries.append(entry)

    # 按复习次数排序（优先复习次数少的）
    due_entries.sort(key=lambda x: x["review_count"])
    return due_entries


def review_entry(entry_id: str, remembered: bool = True) -> str:
    """记录复习"""
    data = load_knowledge_base()

    for entry in data["entries"]:
        if entry["id"] == entry_id:
            today = datetime.now().strftime("%Y-%m-%d")
            entry["reviews"].append({
                "date": today,
                "level": entry["review_count"],
                "remembered": remembered
            })

            # 计算下次复习时间
            entry["review_count"] += 1
            interval_idx = min(entry["review_count"] - 1, len(REVIEW_INTERVALS) - 1)
            days = REVIEW_INTERVALS[interval_idx]
            next_date = datetime.now() + timedelta(days=days)
            entry["next_review"] = next_date.strftime("%Y-%m-%d")

            save_knowledge_base(data)

            status = "记住了" if remembered else "需要加强"
            return f"✨ 复习记录已保存！{status}，下次复习：{entry['next_review']}"

    return "❌ 未找到该条目"


def format_quiz(entry: Dict) -> str:
    """格式化为提问卡片"""
    category = entry["category"]
    content = entry["content"]
    count = entry["review_count"]

    # 如果内容太长，提取前50字作为提示
    if len(content) > 50:
        hint = content[:50] + "..."
    else:
        hint = content

    intervals_str = ["1天", "3天", "7天", "14天", "30天"]
    interval = intervals_str[min(count, len(intervals_str)-1)]

    return f"""
📚 【{category}】第{count+1}次复习（间隔{interval}）

💭 还记得这个吗？
   「{hint}」

📝 回复以下指令：
   • "/knowledge recall {entry['id']} yes"  - 记住了
   • "/knowledge recall {entry['id']} no"   - 没记住，再看一遍
"""


def format_show(entry: Dict) -> str:
    """格式化为展示卡片"""
    return f"""
┌─【{entry['category']}】─ ID: {entry['id']} ─┐
│ {entry['content'][:100]}{'...' if len(entry['content']) > 100 else ''}
│ 创建于：{entry['created_at'][:10]} | 已复习：{entry['review_count']}次
└─ 下次复习：{entry['next_review']} ─┘
"""


def get_stats() -> str:
    """获取统计信息"""
    data = load_knowledge_base()
    entries = data["entries"]

    total = len(entries)
    if total == 0:
        return "📭 知识库还是空的，快添加第一条知识吧～"

    # 分类统计
    categories = {}
    for e in entries:
        cat = e["category"]
        categories[cat] = categories.get(cat, 0) + 1

    # 今日到期
    due_today = len(get_due_entries("today"))

    # 本周到期
    due_week = len(get_due_entries("week"))

    # 总复习次数
    total_reviews = sum(e["review_count"] for e in entries)

    lines = [
        "📊 知识库统计",
        f"",
        f"📚 总条目数：{total}",
        f"📝 总复习次数：{total_reviews}",
        f"⏰ 今日待复习：{due_today}",
        f"📅 本周待复习：{due_week}",
        f"",
        "📂 分类分布："
    ]
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        lines.append(f"   • {cat}：{count}条")

    return "\n".join(lines)


def setup_hook() -> str:
    """输出 Hook 配置说明"""
    return r"""
📋 请使用以下命令配置自动识别 Hook：

/update-config add user-prompt-submit-hook "
#!/bin/bash
# 检查是否包含知识库关键词
if echo "$CLAUDE_USER_PROMPT" | grep -qi "知识库"; then
    # 提取内容（去掉触发词）
    content=$(echo "$CLAUDE_USER_PROMPT" | sed 's/加入.*知识库//g; s/添加到.*知识库//g; s/记到.*知识库//g; s/保存到.*知识库//g')
    # 调用脚本添加
    python3 ~/.claude/skills/knowledge/scripts/knowledge.py auto-add "$content"
fi
"

⚠️ 配置完成后请重启 Claude Code 生效！

💡 如果不想使用自动识别，可以手动使用：
   python3 ~/.claude/skills/knowledge/scripts/knowledge.py add "知识点内容"
"""


# CLI 接口
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: knowledge.py <command> [args...]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "add":
        content = sys.argv[2] if len(sys.argv) > 2 else ""
        tags = sys.argv[3].split(",") if len(sys.argv) > 3 else None
        print(add_entry(content, tags))

    elif cmd == "auto-add":
        content = sys.argv[2] if len(sys.argv) > 2 else ""
        print(add_entry(content))

    elif cmd == "review":
        period = sys.argv[2] if len(sys.argv) > 2 else "today"
        mode = sys.argv[3] if len(sys.argv) > 3 else "quiz"

        entries = get_due_entries(period)
        if not entries:
            print(f"🎉 {period} 没有到期复习的知识～")
            sys.exit(0)

        print(f"📚 共有 {len(entries)} 条知识待复习\n")
        for entry in entries:
            if mode == "quiz":
                print(format_quiz(entry))
            else:
                print(format_show(entry))

    elif cmd == "recall":
        entry_id = sys.argv[2] if len(sys.argv) > 2 else ""
        remembered = sys.argv[3] == "yes" if len(sys.argv) > 3 else True
        print(review_entry(entry_id, remembered))

    elif cmd == "list":
        data = load_knowledge_base()
        tag_filter = sys.argv[2] if len(sys.argv) > 2 else None

        for entry in data["entries"]:
            if tag_filter and tag_filter not in entry["tags"]:
                continue
            print(format_show(entry))

    elif cmd == "stats":
        print(get_stats())

    elif cmd == "setup":
        print(setup_hook())

    else:
        print(f"Unknown command: {cmd}")
