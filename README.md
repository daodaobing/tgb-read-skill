# 淘股吧精华文章获取技能

## 功能概述

这是一个用于获取淘股吧精华文章和指定博主每日新增文章的技能，支持：

- ✅ 获取淘股吧精华文章（按发帖日期排序）
- ✅ 获取指定博主的文章列表
- ✅ 支持多博主配置（可扩展，后续可添加更多博主）
- ✅ 文章缓存机制，避免重复获取
- ✅ 新增文章检测（与缓存对比）

## 已配置博主

| 博主 | 用户ID | 主页 | 简介 |
|------|--------|------|------|
| 搞钱老兵 | 11255090 | https://www.tgb.cn/blog/11255090 | 专注短线确定性蜂蜜和短线趋势主升多头抓翻倍 |

> 后续可根据需要添加更多博主，只需在 `config.py` 的 `BLOGGERS` 列表中添加即可。

## 目录结构

```
tgb_jinghua_skill/
├── config.py        # 配置文件
├── crawler.py       # 爬虫核心模块
├── skill.py         # 主入口文件
├── requirements.txt # 依赖文件
└── README.md        # 说明文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 基本使用

```python
from skill import get_jinghua_articles, get_blogger_articles, get_all_bloggers_articles

# 获取最近1天的精华文章
result = get_jinghua_articles(days=1)
print(result['formatted_output'])

# 获取指定博主的文章
result = get_blogger_articles('11255090', days=1)
print(result['formatted_output'])

# 获取所有博主的文章
result = get_all_bloggers_articles(days=1)
print(result['formatted_output'])
```

### 3. 命令行使用

```bash
# 获取精华文章
python skill.py jinghua 1

# 获取指定博主文章
python skill.py blogger 11255090 1

# 获取所有博主文章
python skill.py all 1

# 获取新增文章
python skill.py new

# 更新缓存
python skill.py update

# 列出配置的博主
python skill.py list
```

## API 文档

### get_jinghua_articles(days=1)

获取淘股吧精华文章列表。

**参数:**
- `days` (int): 获取最近N天的文章，默认1天

**返回:**
```python
{
    "success": True,
    "skill": "淘股吧精华文章获取",
    "version": "1.0.0",
    "source_url": "https://www.tgb.cn/jinghua/",
    "fetch_time": "2026-03-28 22:00:00",
    "days_range": 1,
    "total_count": 15,
    "articles": [
        {
            "article_id": "2qvrbfH6nwL",
            "article_url": "https://www.tgb.cn/a/2qvrbfH6nwL",
            "title": "[精]文章标题",
            "author_id": "11255090",
            "author_name": "作者名",
            "comments": 100,
            "views": 1000,
            "post_date": "03-27 15:11",
            "reply_date": "03-28 22:43",
            "is_jinghua": True,
            "is_hongbao": False,
            "is_vote": False
        },
        # ...
    ],
    "formatted_output": "..."
}
```

### get_blogger_articles(user_id, days=1)

获取指定博主的文章列表。

**参数:**
- `user_id` (str): 博主用户ID
- `days` (int): 获取最近N天的文章，默认1天

### get_all_bloggers_articles(days=1)

获取所有已配置博主的文章列表。

### get_new_articles()

获取与上次缓存相比的新增文章。

### update_cache()

更新文章缓存。

### list_bloggers()

列出所有已配置的博主。

## 扩展配置

### 添加新博主

在 `config.py` 文件中修改 `BLOGGERS` 列表：

```python
BLOGGERS = [
    {
        "user_id": "11255090",
        "name": "搞钱老兵",
        "description": "专注短线确定性蜂蜜和短线趋势主升多头抓翻倍",
        "enabled": True
    },
    {
        "user_id": "新的用户ID",
        "name": "新博主名称",
        "description": "博主简介",
        "enabled": True
    },
    # 添加更多博主...
]
```

## 文章数据结构

### 精华文章字段

| 字段 | 类型 | 说明 |
|------|------|------|
| article_id | str | 文章ID |
| article_url | str | 文章链接 |
| title | str | 文章标题（含标签） |
| author_id | str | 作者ID |
| author_name | str | 作者名称 |
| author_url | str | 作者主页链接 |
| comments | int | 评论数 |
| views | int | 浏览量 |
| post_date | str | 发帖日期 |
| reply_date | str | 最新回帖日期 |
| is_jinghua | bool | 是否精华 |
| is_hongbao | bool | 是否红包帖 |
| is_vote | bool | 是否投票帖 |

### 博主文章字段

| 字段 | 类型 | 说明 |
|------|------|------|
| article_id | str | 文章ID |
| article_url | str | 文章链接 |
| title | str | 文章标题 |
| user_id | str | 博主用户ID |
| type | str | 文章类型（原/精） |
| views | int | 阅读量 |
| comments | int | 评论数 |
| post_date | str | 发布时间 |
| is_jinghua | bool | 是否精华 |
| is_hongbao | bool | 是否红包帖 |

## 注意事项

1. **请求频率**: 请合理控制请求频率，避免对服务器造成压力
2. **登录限制**: 部分页面可能需要登录才能访问
3. **数据更新**: 建议定期更新缓存以获取最新数据
4. **日期格式**: 返回的日期可能需要根据实际数据格式调整

## 版本历史

- **v1.0.0** (2026-03-28): 初始版本
  - 支持获取淘股吧精华文章
  - 支持获取指定博主文章
  - 支持多博主配置
  - 实现文章缓存机制
