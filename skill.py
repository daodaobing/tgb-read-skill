# -*- coding: utf-8 -*-
"""
淘股吧精华文章获取技能 - 主入口
"""

from crawler import (
    TgbCrawler,
    ArticleCache,
    format_article_output,
    get_enabled_bloggers
)
from config import SKILL_NAME, SKILL_VERSION, TGB_JINGHUA_URL, CACHE_FILE
from datetime import datetime


def get_jinghua_articles(days: int = 1) -> dict:
    """
    获取淘股吧精华文章

    Args:
        days: 获取最近N天的文章，默认1天

    Returns:
        dict: 包含文章列表和统计信息
    """
    crawler = TgbCrawler()
    articles = crawler.fetch_recent_jinghua(days=days)

    result = {
        "success": True,
        "skill": SKILL_NAME,
        "version": SKILL_VERSION,
        "source_url": TGB_JINGHUA_URL,
        "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "days_range": days,
        "total_count": len(articles),
        "articles": articles,
        "formatted_output": ""
    }

    # 格式化输出
    if articles:
        output_lines = [
            f"📊 淘股吧精华文章 (最近{days}天)",
            f"=" * 50,
            f"共找到 {len(articles)} 篇精华文章",
            f"抓取时间: {result['fetch_time']}",
            f"来源: {TGB_JINGHUA_URL}",
            "",
            "文章列表:",
            "-" * 50
        ]

        for i, article in enumerate(articles, 1):
            output_lines.append(f"\n[{i}] {format_article_output(article, 'jinghua')}")

        result["formatted_output"] = '\n'.join(output_lines)
    else:
        result["formatted_output"] = "未找到符合条件的文章"

    return result


def get_blogger_articles(user_id: str, days: int = 1) -> dict:
    """
    获取指定博主的文章

    Args:
        user_id: 博主用户ID
        days: 获取最近N天的文章，默认1天

    Returns:
        dict: 包含文章列表和统计信息
    """
    crawler = TgbCrawler()
    articles = crawler.fetch_recent_blogger_articles(user_id, days=days)

    # 获取博主信息
    bloggers = get_enabled_bloggers()
    blogger_info = next((b for b in bloggers if b['user_id'] == user_id), None)

    result = {
        "success": True,
        "skill": SKILL_NAME,
        "version": SKILL_VERSION,
        "source_url": f"https://www.tgb.cn/blog/{user_id}",
        "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "days_range": days,
        "user_id": user_id,
        "blogger_name": blogger_info['name'] if blogger_info else f"用户{user_id}",
        "blogger_description": blogger_info.get('description', '') if blogger_info else '',
        "total_count": len(articles),
        "articles": articles,
        "formatted_output": ""
    }

    # 格式化输出
    if articles:
        output_lines = [
            f"👤 {result['blogger_name']} 的文章 (最近{days}天)",
            f"=" * 50,
            f"共找到 {len(articles)} 篇文章",
            f"抓取时间: {result['fetch_time']}",
            f"主页: https://www.tgb.cn/blog/{user_id}",
            ""
        ]

        if result['blogger_description']:
            output_lines.append(f"简介: {result['blogger_description']}")
            output_lines.append("")

        output_lines.append("文章列表:")
        output_lines.append("-" * 50)

        for i, article in enumerate(articles, 1):
            output_lines.append(f"\n[{i}] {format_article_output(article, 'blogger')}")

        result["formatted_output"] = '\n'.join(output_lines)
    else:
        result["formatted_output"] = f"未找到 {result['blogger_name']} 最近{days}天的文章"

    return result


def get_all_bloggers_articles(days: int = 1) -> dict:
    """
    获取所有已配置博主的文章

    Args:
        days: 获取最近N天的文章，默认1天

    Returns:
        dict: 包含所有博主的文章和统计信息
    """
    bloggers = get_enabled_bloggers()
    all_results = {
        "success": True,
        "skill": SKILL_NAME,
        "version": SKILL_VERSION,
        "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "days_range": days,
        "total_bloggers": len(bloggers),
        "bloggers": [],
        "total_articles": 0,
        "formatted_output": ""
    }

    output_lines = [
        f"📊 所有博主文章汇总 (最近{days}天)",
        f"=" * 50,
        f"博主数量: {len(bloggers)}",
        f"抓取时间: {all_results['fetch_time']}",
        ""
    ]

    for blogger in bloggers:
        user_id = blogger['user_id']
        result = get_blogger_articles(user_id, days)

        blogger_data = {
            "user_id": user_id,
            "name": blogger['name'],
            "description": blogger.get('description', ''),
            "total_count": result['total_count'],
            "articles": result['articles']
        }
        all_results['bloggers'].append(blogger_data)
        all_results['total_articles'] += result['total_count']

        output_lines.append(f"\n{'='*50}")
        output_lines.append(result['formatted_output'])

    # 添加汇总信息
    output_lines.insert(3, f"文章总数: {all_results['total_articles']}")

    all_results["formatted_output"] = '\n'.join(output_lines)

    return all_results


def get_new_articles() -> dict:
    """
    获取新增文章（与上次获取相比）

    Returns:
        dict: 包含新增的文章列表
    """
    cache = ArticleCache()
    new_jinghua = cache.get_new_articles("jinghua")

    new_blogger = {}
    bloggers = get_enabled_bloggers()
    for blogger in bloggers:
        user_id = blogger['user_id']
        articles = cache.get_new_articles("blogger", user_id)
        if articles:
            new_blogger[blogger['name']] = {
                "user_id": user_id,
                "articles": articles
            }

    result = {
        "success": True,
        "skill": SKILL_NAME,
        "version": SKILL_VERSION,
        "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "new_jinghua_count": len(new_jinghua),
        "new_jinghua_articles": new_jinghua,
        "new_blogger_count": sum(len(v['articles']) for v in new_blogger.values()),
        "new_blogger_articles": new_blogger,
        "formatted_output": ""
    }

    # 格式化输出
    output_lines = [
        f"🆕 新增文章",
        f"=" * 50,
        f"抓取时间: {result['fetch_time']}",
        ""
    ]

    if new_jinghua:
        output_lines.append(f"\n📌 精华文章新增: {len(new_jinghua)} 篇")
        output_lines.append("-" * 50)
        for i, article in enumerate(new_jinghua[:10], 1):  # 最多显示10篇
            output_lines.append(f"\n[{i}] {format_article_output(article, 'jinghua')}")
        if len(new_jinghua) > 10:
            output_lines.append(f"\n... 还有 {len(new_jinghua) - 10} 篇")
    else:
        output_lines.append("\n📌 精华文章: 无新增")

    if new_blogger:
        for name, data in new_blogger.items():
            output_lines.append(f"\n\n👤 {name} 新增: {len(data['articles'])} 篇")
            output_lines.append("-" * 50)
            for i, article in enumerate(data['articles'], 1):
                output_lines.append(f"\n[{i}] {format_article_output(article, 'blogger')}")
    else:
        output_lines.append("\n👤 博主文章: 无新增")

    result["formatted_output"] = '\n'.join(output_lines)

    return result


def update_cache() -> dict:
    """
    更新文章缓存

    Returns:
        dict: 更新结果
    """
    cache = ArticleCache()
    crawler = TgbCrawler()

    # 更新精华文章
    jinghua_articles = crawler.fetch_recent_jinghua(days=7)
    cache.update_jinghua(jinghua_articles)

    # 更新博主文章
    bloggers = get_enabled_bloggers()
    for blogger in bloggers:
        user_id = blogger['user_id']
        articles = crawler.fetch_recent_blogger_articles(user_id, days=7)
        cache.update_blogger(user_id, articles)

    result = {
        "success": True,
        "skill": SKILL_NAME,
        "version": SKILL_VERSION,
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "jinghua_count": len(jinghua_articles),
        "bloggers_count": len(bloggers),
        "formatted_output": f"✅ 缓存已更新\n\n- 精华文章: {len(jinghua_articles)} 篇\n- 博主数量: {len(bloggers)}"
    }

    return result


def list_bloggers() -> dict:
    """
    列出所有已配置的博主

    Returns:
        dict: 博主列表
    """
    bloggers = get_enabled_bloggers()

    result = {
        "success": True,
        "skill": SKILL_NAME,
        "version": SKILL_VERSION,
        "total_count": len(bloggers),
        "bloggers": bloggers,
        "formatted_output": ""
    }

    output_lines = [
        f"👥 已配置的博主列表",
        f"=" * 50,
        f"共 {len(bloggers)} 位博主",
        ""
    ]

    for i, blogger in enumerate(bloggers, 1):
        output_lines.append(f"\n[{i}] {blogger['name']}")
        output_lines.append(f"   用户ID: {blogger['user_id']}")
        output_lines.append(f"   主页: https://www.tgb.cn/blog/{blogger['user_id']}")
        output_lines.append(f"   简介: {blogger.get('description', '暂无')}")

    result["formatted_output"] = '\n'.join(output_lines)

    return result


# CLI 入口
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("""
淘股吧精华文章获取技能
====================

使用方法:
  python skill.py jinghua [天数]     - 获取精华文章
  python skill.py blogger <用户ID> [天数] - 获取博主文章
  python skill.py all [天数]         - 获取所有博主文章
  python skill.py new                 - 获取新增文章
  python skill.py update              - 更新缓存
  python skill.py list               - 列出配置的博主
        """)
        sys.exit(1)

    command = sys.argv[1]

    if command == "jinghua":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        result = get_jinghua_articles(days)
    elif command == "blogger":
        if len(sys.argv) < 3:
            print("错误: 请提供用户ID")
            sys.exit(1)
        user_id = sys.argv[2]
        days = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        result = get_blogger_articles(user_id, days)
    elif command == "all":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        result = get_all_bloggers_articles(days)
    elif command == "new":
        result = get_new_articles()
    elif command == "update":
        result = update_cache()
    elif command == "list":
        result = list_bloggers()
    else:
        print(f"未知命令: {command}")
        sys.exit(1)

    print(result["formatted_output"])
