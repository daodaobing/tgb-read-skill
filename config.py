# -*- coding: utf-8 -*-
"""
淘股吧精华文章获取技能 - 配置文件
"""

# 技能配置
SKILL_NAME = "淘股吧精华文章获取"
SKILL_VERSION = "1.0.0"
SKILL_AUTHOR = "MiniMax Agent"

# 淘股吧网站配置
TGB_BASE_URL = "https://www.tgb.cn"
TGB_JINGHUA_URL = f"{TGB_BASE_URL}/jinghua/"
TGB_BLOG_URL_TEMPLATE = f"{TGB_BASE_URL}/blog/{{user_id}}"

# 博主配置列表 (可后续添加更多博主)
BLOGGERS = [
    {
        "user_id": "11255090",
        "name": "搞钱老兵",
        "description": "专注短线确定性蜂蜜和短线趋势主升多头抓翻倍",
        "enabled": True
    }
]

# 请求头配置
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
}

# 请求配置
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
PAGES_PER_FETCH = 3  # 每次最多获取的页数

# 时间格式配置
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M"

# 缓存配置
CACHE_FILE = "cache/articles_cache.json"
CACHE_EXPIRY_HOURS = 24
